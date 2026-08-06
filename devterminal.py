#!/usr/bin/env python3
import sqlite3
import sys
import os

DB_FILE = os.path.expanduser("~/.devterminal_notes.db")


# --- Database setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tag TEXT
    )
    """)
    conn.commit()
    conn.close()


# --- Core functions ---
def add_note(content, tag=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (content, tag) VALUES (?, ?)",
        (content, tag)
    )
    conn.commit()

    count = cursor.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    conn.close()

    print(f"Note saved. Total notes: {count}.")


def search_notes(keyword):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content, created_at, tag FROM notes WHERE content LIKE ?",
        ('%' + keyword + '%',)
    )

    results = cursor.fetchall()
    conn.close()

    if results:
        print(f"Found {len(results)} note(s) containing '{keyword}':")
        for r in results:
            tag_display = f" [{r[3]}]" if r[3] else ""
            print(f"[{r[0]}]{tag_display} {r[1]} (added {r[2]})")
    else:
        print(f"No notes found containing '{keyword}'.")


def list_notes(tag=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = "SELECT id, content, created_at, tag FROM notes"
    params = ()

    if tag:
        query += " WHERE tag = ?"
        params = (tag,)

    cursor.execute(query, params)
    notes = cursor.fetchall()
    conn.close()

    if notes:
        print(f"Listing {len(notes)} notes:")
        for n in notes:
            tag_display = f" [{n[3]}]" if n[3] else ""
            print(f"[{n[0]}]{tag_display} {n[1]} (added {n[2]})")
    else:
        print("No notes to display.")


# --- Remove functions ---
def remove_by_id(note_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()

    if not note:
        print(f"Note with ID {note_id} not found.")
        conn.close()
        return

    confirm = input(f"Delete note [{note_id}]: '{note[0]}'? (y/N): ")
    if confirm.lower() != "y":
        print("Cancelled.")
        conn.close()
        return

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

    print(f"Note [{note_id}] deleted.")


def remove_by_tag(tag):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content FROM notes WHERE tag = ?",
        (tag,)
    )
    notes = cursor.fetchall()

    if not notes:
        print(f"No notes found with tag '{tag}'.")
        conn.close()
        return

    print(f"Found {len(notes)} note(s) with tag '{tag}':")
    for n in notes:
        print(f"[{n[0]}] {n[1]}")

    confirm = input(f"Delete ALL notes with tag '{tag}'? (y/N): ")
    if confirm.lower() != "y":
        print("Cancelled.")
        conn.close()
        return

    cursor.execute("DELETE FROM notes WHERE tag = ?", (tag,))
    conn.commit()
    conn.close()

    print(f"All notes with tag '{tag}' deleted.")


# --- CLI parsing ---
def main():
    init_db()

    args = sys.argv[1:]

    if not args:
        print("Usage examples:")
        print("  add Buy milk .personal")
        print("  search keyword")
        print("  list [.tag]")
        print("  remove <id | .tag>")
        sys.exit(0)

    command = args[0]

    if command == "add":
        if len(args) < 2:
            print("Usage: add note [.tag]")
            return

        if args[-1].startswith("."):
            tag = args[-1][1:]
            content = " ".join(args[1:-1])
        else:
            tag = None
            content = " ".join(args[1:])

        add_note(content, tag)

    elif command == "search":
        if len(args) < 2:
            print("Usage: search keyword")
            return

        search_notes(" ".join(args[1:]))

    elif command == "list":
        tag = args[1][1:] if len(args) > 1 and args[1].startswith(".") else None
        list_notes(tag)

    elif command == "remove":
        if len(args) < 2:
            print("Usage: remove <id | .tag>")
            return

        target = args[1]

        if target.startswith("."):
            tag = target[1:]
            remove_by_tag(tag)
        else:
            try:
                note_id = int(target)
                remove_by_id(note_id)
            except ValueError:
                print("Invalid input. Use note ID or .tag")

    else:
        print("Unknown command. Available: add, search, list, remove")


if __name__ == "__main__":
    main()
