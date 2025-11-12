#!/usr/bin/env python3
"""
Basic Text Hashing Tool — GUI (Tkinter)
Save as hash_gui.py and run: python hash_gui.py
"""
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# optional clipboard support via pyperclip (not required)
try:
    import pyperclip
except Exception:
    pyperclip = None

APP_TITLE = "Basic Text Hashing Tool (GUI) v1.0"

def compute_hash_bytes(data: bytes, algo: str) -> str:
    algo = algo.lower()
    if algo == "md5":
        h = hashlib.md5()
    else:
        h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

class HashGUI:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("760x520")
        root.minsize(640, 420)

        # top frame: controls
        top = ttk.Frame(root, padding=(10,10))
        top.pack(fill="x", padx=6, pady=6)

        ttk.Label(top, text="Algorithm:").pack(side="left")
        self.algo_var = tk.StringVar(value="sha256")
        algo_box = ttk.Combobox(top, textvariable=self.algo_var, values=["sha256","md5"], width=8, state="readonly")
        algo_box.pack(side="left", padx=(6,12))

        ttk.Button(top, text="Open File...", command=self.open_file).pack(side="left", padx=6)
        ttk.Button(top, text="Clear", command=self.clear_text).pack(side="left", padx=6)

        ttk.Button(top, text="Compute Hash", command=self.compute).pack(side="right", padx=6)
        ttk.Button(top, text="Save Hash...", command=self.save_hash_to_file).pack(side="right", padx=6)

        # center: text input and result
        center = ttk.Frame(root, padding=(10,0,10,10))
        center.pack(fill="both", expand=True)

        # Text input
        ttk.Label(center, text="Input text (paste or type):").pack(anchor="w")
        self.text_widget = tk.Text(center, wrap="word", height=12)
        self.text_widget.pack(fill="both", expand=True, pady=(4,8))
        self.text_widget.focus_set()

        # result frame
        res_frame = ttk.Frame(center)
        res_frame.pack(fill="x", pady=(4,0))

        ttk.Label(res_frame, text="Computed Hash:").grid(row=0, column=0, sticky="w")
        self.hash_var = tk.StringVar(value="")
        self.hash_entry = ttk.Entry(res_frame, textvariable=self.hash_var, width=96)
        self.hash_entry.grid(row=0, column=1, sticky="ew", padx=6)
        res_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(center)
        btn_frame.pack(fill="x", pady=(8,0))

        ttk.Button(btn_frame, text="Copy Hash", command=self.copy_hash).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Load Hash From File...", command=self.load_hash_file).pack(side="left", padx=6)

        # verify area
        verify_frame = ttk.Frame(center)
        verify_frame.pack(fill="x", pady=(12,0))
        ttk.Label(verify_frame, text="Verify against:").grid(row=0, column=0, sticky="w")
        self.verify_var = tk.StringVar()
        verify_entry = ttk.Entry(verify_frame, textvariable=self.verify_var, width=72)
        verify_entry.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(verify_frame, text="Verify", command=self.verify).grid(row=0, column=2, padx=6)
        verify_frame.columnconfigure(1, weight=1)

        # status bar
        self.status = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w", padding=(6,4))
        status_bar.pack(fill="x", side="bottom")

    def open_file(self):
        path = filedialog.askopenfilename(title="Open text file", filetypes=[("Text files", "*.txt *.md *.log *.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, content)
            self.status.set(f"Loaded file: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Open file", f"Failed to open file:\n{e}")

    def clear_text(self):
        self.text_widget.delete("1.0", tk.END)
        self.hash_var.set("")
        self.verify_var.set("")
        self.status.set("Cleared")

    def compute(self):
        raw = self.text_widget.get("1.0", tk.END)
        if raw.strip() == "":
            messagebox.showinfo("Compute", "Please enter or load some text to hash.")
            return
        data = raw.encode("utf-8")
        algo = self.algo_var.get()
        digest = compute_hash_bytes(data, algo)
        self.hash_var.set(digest)
        self.status.set(f"Computed {algo.upper()} hash")

    def copy_hash(self):
        val = self.hash_var.get().strip()
        if not val:
            messagebox.showinfo("Copy", "No hash to copy. Compute a hash first.")
            return
        try:
            if pyperclip:
                pyperclip.copy(val)
            else:
                # use Tk clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(val)
            self.status.set("Hash copied to clipboard")
        except Exception as e:
            messagebox.showwarning("Copy", f"Copy failed: {e}")

    def save_hash_to_file(self):
        val = self.hash_var.get().strip()
        if not val:
            messagebox.showinfo("Save", "No hash to save. Compute a hash first.")
            return
        path = filedialog.asksaveasfilename(title="Save hash", defaultextension=".txt", filetypes=[("Text file", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(val)
            self.status.set(f"Hash saved to: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Save", f"Failed to save hash:\n{e}")

    def load_hash_file(self):
        path = filedialog.askopenfilename(title="Open hash file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()
            self.hash_var.set(content)
            self.status.set(f"Loaded hash from: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Load hash", f"Failed to load file:\n{e}")

    def verify(self):
        provided = self.verify_var.get().strip().lower()
        computed = self.hash_var.get().strip().lower()
        if not provided:
            messagebox.showinfo("Verify", "Enter a hash string in 'Verify against' field.")
            return
        if not computed:
            # compute if not present
            self.compute()
            computed = self.hash_var.get().strip().lower()
        if provided == computed:
            messagebox.showinfo("Verify", "Verification: MATCH ✅")
            self.status.set("Verification: MATCH")
        else:
            messagebox.showerror("Verify", "Verification: MISMATCH ❌")
            self.status.set("Verification: MISMATCH")

def main():
    root = tk.Tk()
    app = HashGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
