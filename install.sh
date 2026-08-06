#!/usr/bin/env bash
set -e

REPO_URL="https://raw.githubusercontent.com/Husseinuahmedc/devterminal/main/devterminal.py"
INSTALL_PATH="/usr/local/bin/devterminal"

echo " Installing DevTerminal..."

# --- Detect OS ---
OS="$(uname -s)"

# --- Check Python ---
if command -v python3 >/dev/null 2>&1; then
    echo " Python3 is already installed"
else
    echo "python3 not found. Installing..."
    if [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install -y python3
    elif [ -f /etc/arch-release ]; then
        sudo pacman -Sy --noconfirm python
    elif [ -f /etc/fedora-release ]; then
        sudo dnf install -y python3
    elif [[ "$OS" == "Darwin" ]]; then
        echo " Installing via Homebrew..."
        if ! command -v brew >/dev/null 2>&1; then
            echo " Homebrew not found. Install it first: https://brew.sh/"
            exit 1
        fi
        brew install python
    else
        echo "❌ Unsupported OS. Please install Python3 manually."
        exit 1
    fi
fi

# --- Download DevTerminal ---
TEMP_FILE="$(mktemp)"
echo " Downloading DevTerminal..."
curl -fsSL "$REPO_URL" -o "$TEMP_FILE"

# --- Make executable ---
chmod +x "$TEMP_FILE"

# --- Move to PATH (overwrite if exists) ---
if [ -f "$INSTALL_PATH" ]; then
    echo " Existing installation found. Overwriting..."
    sudo rm -f "$INSTALL_PATH"
fi

echo "Installing to $INSTALL_PATH ..."
sudo mv "$TEMP_FILE" "$INSTALL_PATH"

# --- Verify installation ---
if command -v devterminal >/dev/null 2>&1; then
    echo "Installation successful!"
else
    echo " Installation may have failed. Check PATH."
fi

# --- Optional alias ---
SHELL_NAME="$(basename "$SHELL")"
if [[ "$SHELL_NAME" == "bash" ]]; then
    RC_FILE="$HOME/.bashrc"
elif [[ "$SHELL_NAME" == "zsh" ]]; then
    RC_FILE="$HOME/.zshrc"
elif [[ "$SHELL_NAME" == "fish" ]]; then
    RC_FILE="$HOME/.config/fish/config.fish"
else
    RC_FILE=""
fi

if [ -n "$RC_FILE" ]; then
    echo "🔧 Adding alias (dn) to $RC_FILE ..."
    if ! grep -q "alias dn=devterminal" "$RC_FILE" 2>/dev/null; then
        if [[ "$SHELL_NAME" == "fish" ]]; then
            echo "alias dn devterminal" >> "$RC_FILE"
        else
            echo "alias dn='devterminal'" >> "$RC_FILE"
        fi
    fi
fi

echo ""
echo "DevTerminal is ready to use!"
echo "Try:"
echo "  devterminal add Husseinaj .noone"
echo "  devterminal list"
