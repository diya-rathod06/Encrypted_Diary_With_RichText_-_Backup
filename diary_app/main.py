# diary_app/main.py
import re
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from . import db, encryption, utils

CURRENT_USER = None
FERNET = None


def ask_login(root):
    global CURRENT_USER, FERNET
    while True:
        username = simpledialog.askstring("Login", "Enter username:", parent=root)
        if not username:
            messagebox.showerror("Error", "Username required!")
            continue
        password = simpledialog.askstring("Password", "Enter password:", show="*", parent=root)
        if not password:
            messagebox.showerror("Error", "Password required!")
            continue

        CURRENT_USER = username
        FERNET = encryption.fernet_from_password(password, username)
        if not encryption.check_password_for_user(username, FERNET):
            messagebox.showerror("Error", "Incorrect password!")
            continue
        encryption.ensure_verifier(username, FERNET)
        break
    messagebox.showinfo("Logged In", f"Welcome {CURRENT_USER}!")


def run_app(root):
    db.init_db()
    root.title("Secure Personal Diary")
    root.geometry("1100x750")

    # --- Main Title ---
    title_label = ttk.Label(root, text="Secure Personal Diary", font=("TkDefaultFont", 20, "bold"))
    title_label.pack(pady=10)

    # --- Top bar ---
    top_bar = ttk.Frame(root, padding=5)
    top_bar.pack(fill="x", padx=10, pady=5)

    ttk.Label(top_bar, text="Search:").pack(side="left")
    search_var = tk.StringVar()
    search_entry = ttk.Entry(top_bar, textvariable=search_var, width=40)
    search_entry.pack(side="left", padx=5)
    ttk.Button(top_bar, text="Search", command=lambda: refresh_entries()).pack(side="left", padx=2)
    ttk.Button(top_bar, text="Show All", command=lambda: show_all_entries()).pack(side="left", padx=2)
    ttk.Button(top_bar, text="Backup", command=lambda: backup_db()).pack(side="right", padx=5)

    # --- Middle frame: editor, entries list, preview ---
    middle_frame = ttk.Frame(root)
    middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # --- Editor ---
    editor_frame = ttk.Frame(middle_frame)
    editor_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    ttk.Label(editor_frame, text="Write Entry (Markdown Supported):", font=("TkDefaultFont", 12)).pack(anchor="w", pady=(0, 5))

    editor_container = ttk.Frame(editor_frame)
    editor_container.pack(fill="both", expand=True)

    editor_scrollbar = ttk.Scrollbar(editor_container, orient="vertical")
    editor_scrollbar.pack(side="right", fill="y")

    editor = tk.Text(editor_container, wrap="word", yscrollcommand=editor_scrollbar.set)
    editor.pack(side="left", fill="both", expand=True)
    editor_scrollbar.config(command=editor.yview)

    # --- Toolbar for Markdown formatting ---
    toolbar_frame = ttk.Frame(editor_frame)
    toolbar_frame.pack(fill="x", pady=5)

    def wrap_selection(text_widget, before, after=None):
        after = after if after else before
        try:
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
        except tk.TclError:
            text_widget.insert("insert", before + after)
            update_preview()
            return
        selected = text_widget.get(start, end)
        text_widget.delete(start, end)
        text_widget.insert(start, f"{before}{selected}{after}")
        update_preview()

    def insert_header(text_widget, level):
        try:
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            selected = text_widget.get(start, end)
            text_widget.delete(start, end)
            text_widget.insert(start, f"{'#'*level} {selected.strip()}")
        except tk.TclError:
            text_widget.insert("insert", f"{'#'*level} ")
        update_preview()

    def insert_list(text_widget):
        try:
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            selected = text_widget.get(start, end)
            text_widget.delete(start, end)
            lines = selected.splitlines()
            lines = [f"- {line.strip()}" for line in lines]
            text_widget.insert(start, "\n".join(lines))
        except tk.TclError:
            text_widget.insert("insert", "- ")
        update_preview()

    for label, code in [("B", "**"), ("I", "*"), ("U", "__")]:
        ttk.Button(toolbar_frame, text=label, command=lambda c=code: wrap_selection(editor, c)).pack(side="left", padx=2)

    ttk.Button(toolbar_frame, text="H1", command=lambda: insert_header(editor, 1)).pack(side="left", padx=2)
    ttk.Button(toolbar_frame, text="H2", command=lambda: insert_header(editor, 2)).pack(side="left", padx=2)
    ttk.Button(toolbar_frame, text="H3", command=lambda: insert_header(editor, 3)).pack(side="left", padx=2)
    ttk.Button(toolbar_frame, text="• List", command=lambda: insert_list(editor)).pack(side="left", padx=2)

    # --- CRUD buttons ---
    crud_frame = ttk.Frame(editor_frame)
    crud_frame.pack(fill="x", pady=5)
    ttk.Button(crud_frame, text="Add Entry", command=lambda: add_entry()).pack(side="left", padx=2)
    ttk.Button(crud_frame, text="Save Entry", command=lambda: save_entry()).pack(side="left", padx=2)
    ttk.Button(crud_frame, text="Edit Entry", command=lambda: edit_entry()).pack(side="left", padx=2)
    ttk.Button(crud_frame, text="Delete Entry", command=lambda: delete_entry()).pack(side="left", padx=2)

    # --- Entries list ---
    list_frame = ttk.Frame(middle_frame)
    list_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)
    ttk.Label(list_frame, text="Entries:", font=("TkDefaultFont", 12)).pack(anchor="w")
    listbox = tk.Listbox(list_frame, width=60)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)

    # --- Preview panel ---
    preview_frame = ttk.Frame(middle_frame)
    preview_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    ttk.Label(preview_frame, text="Preview:", font=("TkDefaultFont", 12)).pack(anchor="w")

    preview_container = ttk.Frame(preview_frame)
    preview_container.pack(fill="both", expand=True)

    preview_scrollbar = ttk.Scrollbar(preview_container, orient="vertical")
    preview_scrollbar.pack(side="right", fill="y")

    preview = tk.Text(preview_container, wrap="word", state="disabled", bg="#f4f4f4",
                      yscrollcommand=preview_scrollbar.set)
    preview.pack(side="left", fill="both", expand=True)
    preview_scrollbar.config(command=preview.yview)

    selected_entry_id = None
    current_entries = []

    # --- Regex for inline markdown ---
    inline_pattern = re.compile(
        r"(?P<bold>\*\*(?P<bold_text>.*?)\*\*)"
        r"|(?P<italic>\*(?P<italic_text>.*?)\*)"
        r"|(?P<uline>__(?P<uline_text>.*?)__)",
        flags=re.DOTALL
    )

    def parse_inline_and_spans(text_line):
        cleaned, spans = [], []
        last, out_len = 0, 0
        for m in inline_pattern.finditer(text_line):
            s, e = m.start(), m.end()
            before = text_line[last:s]
            cleaned.append(before)
            out_len += len(before)
            if m.group("bold"):
                inner = m.group("bold_text")
                cleaned.append(inner)
                spans.append(("bold", out_len, out_len + len(inner)))
                out_len += len(inner)
            elif m.group("italic"):
                inner = m.group("italic_text")
                cleaned.append(inner)
                spans.append(("italic", out_len, out_len + len(inner)))
                out_len += len(inner)
            elif m.group("uline"):
                inner = m.group("uline_text")
                cleaned.append(inner)
                spans.append(("underline", out_len, out_len + len(inner)))
                out_len += len(inner)
            last = e
        tail = text_line[last:]
        cleaned.append(tail)
        out_len += len(tail)
        return "".join(cleaned), spans

    # --- Live Markdown preview ---
    def update_preview(event=None):
        md_text = editor.get("1.0", tk.END).replace("\r", "")
        preview.configure(state="normal")
        preview.delete("1.0", tk.END)

        # --- Tag configs ---
        preview.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        preview.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        preview.tag_configure("underline", font=("TkDefaultFont", 10, "underline"))
        preview.tag_configure("h1", font=("TkDefaultFont", 16, "bold"), spacing1=10, spacing3=10)
        preview.tag_configure("h2", font=("TkDefaultFont", 14, "bold"), spacing1=8, spacing3=8)
        preview.tag_configure("h3", font=("TkDefaultFont", 12, "bold"), spacing1=6, spacing3=6)
        preview.tag_configure("list", lmargin1=20, lmargin2=40, spacing1=2, spacing3=2)

        for raw_line in md_text.split("\n"):
            tag = None
            content_line = raw_line.rstrip()
            if content_line.startswith("### "):
                tag = "h3"
                content_line = content_line[4:].rstrip("#").rstrip()
            elif content_line.startswith("## "):
                tag = "h2"
                content_line = content_line[3:].rstrip("#").rstrip()
            elif content_line.startswith("# "):
                tag = "h1"
                content_line = content_line[2:].rstrip("#").rstrip()
            elif content_line.startswith("- "):
                tag = "list"
                content_line = "• " + content_line[2:].rstrip("#").rstrip()
            else:
                content_line = content_line.rstrip("#").rstrip()

            cleaned, spans = parse_inline_and_spans(content_line)
            start_index = preview.index(tk.INSERT)
            preview.insert(tk.END, cleaned + "\n")
            end_index = preview.index(tk.INSERT)

            if tag:
                preview.tag_add(tag, start_index, end_index)
            for span_tag, s, e in spans:
                s_idx = f"{start_index}+{s}c"
                e_idx = f"{start_index}+{e}c"
                preview.tag_add(span_tag, s_idx, e_idx)

        preview.configure(state="disabled")

    # --- CRUD functions ---
    def refresh_entries():
        nonlocal current_entries
        query = search_var.get().strip()
        all_entries = db.get_entries(CURRENT_USER)
        if query:
            ids = db.search_entries(CURRENT_USER, query)
            current_entries = [e for e in all_entries if e[0] in ids]
        else:
            current_entries = all_entries

        listbox.delete(0, tk.END)
        for idx, entry in enumerate(current_entries, 1):
            entry_id, title, created_at, updated_at, _, _ = entry
            dt_created = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            created_str = dt_created.strftime('%a %b %d %H:%M:%S %Y')
            display_text = f"{idx}. {title} | Created: {created_str}"
            if updated_at != created_at:
                dt_updated = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                updated_str = dt_updated.strftime('%a %b %d %H:%M:%S %Y')
                display_text += f" | Updated: {updated_str}"
            listbox.insert(tk.END, display_text)

    def show_all_entries():
        search_var.set("")
        refresh_entries()

    def on_select(event=None):
        nonlocal selected_entry_id
        sel = listbox.curselection()
        if not sel: return
        idx = sel[0]
        entry = current_entries[idx]
        selected_entry_id = entry[0]
        decrypted = encryption.decrypt_text(FERNET, entry[4])
        editor.delete("1.0", tk.END)
        editor.insert(tk.END, decrypted)
        update_preview()

    def add_entry():
        nonlocal selected_entry_id
        selected_entry_id = None
        editor.delete("1.0", tk.END)
        update_preview()

    def save_entry():
        nonlocal selected_entry_id
        content = editor.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Content empty!")
            return
        title = simpledialog.askstring("Title", "Entry title:")
        if not title: return
        encrypted = encryption.encrypt_text(FERNET, content)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if selected_entry_id:
            db.update_entry(selected_entry_id, CURRENT_USER, title, encrypted, content, updated_at=now)
            messagebox.showinfo("Saved", "Entry updated!")
        else:
            db.add_entry(CURRENT_USER, title, encrypted, content, created_at=now, updated_at=now)
            messagebox.showinfo("Saved", "New entry added!")
        refresh_entries()

    def delete_entry():
        nonlocal selected_entry_id
        if not selected_entry_id:
            messagebox.showwarning("Warning", "No entry selected!")
            return
        if messagebox.askyesno("Delete", "Are you sure?"):
            db.delete_entry(selected_entry_id, CURRENT_USER)
            selected_entry_id = None
            editor.delete("1.0", tk.END)
            preview.configure(state="normal")
            preview.delete("1.0", tk.END)
            preview.configure(state="disabled")
            refresh_entries()

    def edit_entry():
        nonlocal selected_entry_id
        if not selected_entry_id:
            messagebox.showwarning("Warning", "No entry selected!")
            return
        entry = next((e for e in current_entries if e[0] == selected_entry_id), None)
        if not entry: return
        decrypted = encryption.decrypt_text(FERNET, entry[4])

        popup = tk.Toplevel(root)
        popup.title("Edit Entry")
        popup.geometry("700x500")

        popup_editor = tk.Text(popup, wrap="word")
        popup_editor.pack(fill="both", expand=True, padx=5, pady=5)
        popup_editor.insert("1.0", decrypted)

        popup_toolbar = ttk.Frame(popup)
        popup_toolbar.pack(fill="x", pady=2)

        def wrap_selection_popup(text_widget, before, after=None):
            after = after if after else before
            try:
                start = text_widget.index("sel.first")
                end = text_widget.index("sel.last")
            except tk.TclError:
                text_widget.insert("insert", before + after)
                return
            selected = text_widget.get(start, end)
            text_widget.delete(start, end)
            text_widget.insert(start, f"{before}{selected}{after}")

        for label, code in [("B", "**"), ("I", "*"), ("U", "__")]:
            ttk.Button(popup_toolbar, text=label, command=lambda c=code: wrap_selection_popup(popup_editor, c)).pack(side="left", padx=2)

        ttk.Button(popup_toolbar, text="H1", command=lambda: insert_header(popup_editor, 1)).pack(side="left", padx=2)
        ttk.Button(popup_toolbar, text="H2", command=lambda: insert_header(popup_editor, 2)).pack(side="left", padx=2)
        ttk.Button(popup_toolbar, text="H3", command=lambda: insert_header(popup_editor, 3)).pack(side="left", padx=2)
        ttk.Button(popup_toolbar, text="• List", command=lambda: insert_list(popup_editor)).pack(side="left", padx=2)

        def save_changes():
            new_content = popup_editor.get("1.0", tk.END).strip()
            if not new_content:
                messagebox.showwarning("Warning", "Content empty!")
                return
            title = simpledialog.askstring("Title", "Edit title:", initialvalue=entry[1], parent=popup)
            if not title: return
            encrypted = encryption.encrypt_text(FERNET, new_content)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.update_entry(selected_entry_id, CURRENT_USER, title, encrypted, new_content, updated_at=now)
            messagebox.showinfo("Updated", "Entry updated successfully!")
            editor.delete("1.0", tk.END)
            editor.insert(tk.END, new_content)
            update_preview()
            refresh_entries()
            popup.destroy()

        ttk.Button(popup, text="Save Changes", command=save_changes).pack(pady=5)

    def backup_db():
        try:
            path = utils.create_encrypted_backup(FERNET)
            messagebox.showinfo("Backup Created", f"Encrypted backup saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e))

    listbox.bind("<<ListboxSelect>>", on_select)
    editor.bind("<KeyRelease>", lambda e: update_preview())
    refresh_entries()


if __name__ == "__main__":
    root = tk.Tk()
    ask_login(root)
    run_app(root)
    root.mainloop()
