#!/usr/bin/env python3
"""
Single-file Password Generator with GUI (Tkinter)
Save as password_gui.py and run: python3 password_gui.py
Requirements: Python 3.6+ (no external libs required). Optional: pyperclip for clipboard.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import secrets
import string
import math

# Try optional clipboard helper
try:
    import pyperclip
    _HAS_PYPERCLIP = True
except Exception:
    _HAS_PYPERCLIP = False

# Character sets
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>/?"
# Ambiguous characters to optionally exclude
AMBIG = "Il1O0"

def build_charset(include_lower, include_upper, include_digits, include_symbols, exclude_ambig):
    parts = []
    if include_lower: parts.append(LOWER)
    if include_upper: parts.append(UPPER)
    if include_digits: parts.append(DIGITS)
    if include_symbols: parts.append(SYMBOLS)
    charset = ''.join(parts)
    if exclude_ambig:
        charset = ''.join(ch for ch in charset if ch not in AMBIG)
    return charset, parts  # parts used to guarantee one char of each selected category

def ensure_each_category(chosen_parts, exclude_ambig):
    # return parts with ambiguous removed if needed
    out = []
    for p in chosen_parts:
        if exclude_ambig:
            out.append(''.join(ch for ch in p if ch not in AMBIG))
        else:
            out.append(p)
    return out

def generate_password(length, include_lower, include_upper, include_digits, include_symbols, exclude_ambig):
    charset, parts = build_charset(include_lower, include_upper, include_digits, include_symbols, exclude_ambig)
    if not charset:
        raise ValueError("Enable at least one character category.")
    parts = ensure_each_category(parts, exclude_ambig)
    # build password ensuring at least one char from each selected category
    required = [secrets.choice(p) for p in parts if p]  # one from each non-empty selected category
    if len(required) > length:
        # if user asked length smaller than number of categories, just shuffle required and return truncated
        pwd = ''.join(secrets.choice(charset) for _ in range(length - 0))  # fallback
        return pwd
    remaining = length - len(required)
    others = [secrets.choice(charset) for _ in range(remaining)]
    combined = required + others
    # shuffle securely
    for i in range(len(combined)-1, 0, -1):
        j = secrets.randbelow(i+1)
        combined[i], combined[j] = combined[j], combined[i]
    return ''.join(combined)

def estimate_entropy(length, charset_size):
    # approximate entropy in bits: length * log2(charset_size)
    if charset_size <= 0:
        return 0.0
    return length * math.log2(charset_size)

def strength_label(entropy_bits):
    # Simple categorization
    if entropy_bits < 28:
        return "Very weak"
    if entropy_bits < 36:
        return "Weak"
    if entropy_bits < 60:
        return "Reasonable"
    if entropy_bits < 80:
        return "Strong"
    return "Very strong"

class PassGenApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Password Generator")
        root.geometry("520x400")
        root.resizable(False, False)

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)

        # Length
        ttk.Label(frm, text="Length:").grid(row=0, column=0, sticky="w")
        self.length_var = tk.IntVar(value=16)
        ttk.Spinbox(frm, from_=4, to=128, textvariable=self.length_var, width=6).grid(row=0, column=1, sticky="w")

        # Count
        ttk.Label(frm, text="Count:").grid(row=0, column=2, sticky="w", padx=(12,0))
        self.count_var = tk.IntVar(value=1)
        ttk.Spinbox(frm, from_=1, to=50, textvariable=self.count_var, width=6).grid(row=0, column=3, sticky="w")

        # Checkbuttons
        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=False)
        self.ambig_var = tk.BooleanVar(value=True)  # exclude ambiguous by default

        ttk.Checkbutton(frm, text="Lowercase", variable=self.lower_var).grid(row=1, column=0, sticky="w", pady=6)
        ttk.Checkbutton(frm, text="Uppercase", variable=self.upper_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(frm, text="Digits", variable=self.digits_var).grid(row=1, column=2, sticky="w")
        ttk.Checkbutton(frm, text="Symbols", variable=self.symbols_var).grid(row=1, column=3, sticky="w")
        ttk.Checkbutton(frm, text="Exclude ambiguous (Il1O0)", variable=self.ambig_var).grid(row=2, column=0, columnspan=2, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=(10,6), sticky="w")
        gen_btn = ttk.Button(btn_frame, text="Generate", command=self.on_generate)
        gen_btn.grid(row=0, column=0, padx=(0,6))
        copy_btn = ttk.Button(btn_frame, text="Copy", command=self.on_copy)
        copy_btn.grid(row=0, column=1, padx=(0,6))
        save_btn = ttk.Button(btn_frame, text="Save to file", command=self.on_save)
        save_btn.grid(row=0, column=2, padx=(0,6))
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.on_clear)
        clear_btn.grid(row=0, column=3, padx=(0,6))

        # Output box (multi-line for count>1)
        ttk.Label(frm, text="Passwords:").grid(row=4, column=0, sticky="w", pady=(8,0))
        self.text = tk.Text(frm, height=8, width=60, wrap="none")
        self.text.grid(row=5, column=0, columnspan=4, pady=(4,6))
        self.text.configure(font=("Consolas", 10))

        # Strength and entropy
        self.entropy_var = tk.StringVar(value="Entropy: - bits")
        self.strength_var = tk.StringVar(value="Strength: -")
        ttk.Label(frm, textvariable=self.entropy_var).grid(row=6, column=0, sticky="w")
        ttk.Label(frm, textvariable=self.strength_var).grid(row=6, column=1, sticky="w", padx=(8,0))

        # Status
        self.status_var = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.status_var, foreground="green").grid(row=7, column=0, columnspan=4, sticky="w", pady=(6,0))

        # Fill initial
        self.on_generate()

    def on_generate(self):
        length = int(self.length_var.get())
        count = int(self.count_var.get())
        inc_lower = self.lower_var.get()
        inc_upper = self.upper_var.get()
        inc_digits = self.digits_var.get()
        inc_symbols = self.symbols_var.get()
        excl_amb = self.ambig_var.get()

        try:
            charset, parts = build_charset(inc_lower, inc_upper, inc_digits, inc_symbols, excl_amb)
            if not charset:
                messagebox.showwarning("No character set", "Choose at least one character category.")
                return
            # generate multiple
            results = []
            for _ in range(count):
                pwd = generate_password(length, inc_lower, inc_upper, inc_digits, inc_symbols, excl_amb)
                results.append(pwd)
            # display
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, "\n".join(results))
            # entropy estimate for one password
            entropy = estimate_entropy(length, len(charset))
            self.entropy_var.set(f"Entropy: {entropy:.1f} bits")
            self.strength_var.set(f"Strength: {strength_label(entropy)}")
            self.status_var.set("Generated ✓")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_copy(self):
        data = self.text.get("1.0", tk.END).strip()
        if not data:
            messagebox.showinfo("Nothing to copy", "Generate a password first.")
            return
        try:
            if _HAS_PYPERCLIP:
                pyperclip.copy(data)
            else:
                # fallback to tkinter clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(data)
            self.status_var.set("Copied to clipboard ✓")
        except Exception as e:
            messagebox.showerror("Copy failed", str(e))

    def on_save(self):
        data = self.text.get("1.0", tk.END).strip()
        if not data:
            messagebox.showinfo("Nothing to save", "Generate a password first.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Text files","*.txt"),("All files","*.*")],
                                          title="Save passwords to file")
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(data + "\n")
            self.status_var.set(f"Saved to {fn}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def on_clear(self):
        self.text.delete("1.0", tk.END)
        self.status_var.set("Cleared")

if __name__ == "__main__":
    root = tk.Tk()
    app = PassGenApp(root)
    root.mainloop()
