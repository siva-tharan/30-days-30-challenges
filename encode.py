#!/usr/bin/env python3
"""
Caesar Cipher Encoder/Decoder — Tkinter GUI (Pure Python)

Features
--------
• Encode / Decode with adjustable shift (0–25)
• Optional digit rotation (0–9) alongside letters
• Preserves punctuation, spaces, and symbols
• Brute-force helper (try all 25 shifts) in a separate window
• File menu: Open text, Save output, Save both panes, Quit
• Edit menu: Copy/Paste/Clear, Select All, Clear Output
• Tools: Toggle Light/Dark theme, Brute Force, Swap Panes, Validate
• Keyboard shortcuts (Windows/Linux/macOS):
    - Ctrl/Cmd+O : Open file to Input
    - Ctrl/Cmd+S : Save Output
    - Ctrl/Cmd+E : Encode
    - Ctrl/Cmd+D : Decode
    - Ctrl/Cmd+B : Brute Force
    - Ctrl/Cmd+L : Toggle Theme (Light/Dark)
    - Ctrl/Cmd+W or Ctrl/Cmd+Q : Quit
• Status bar with live character counts

Repository-ready
----------------
Single-file app with no external dependencies. Just commit this file to GitHub.

License
-------
MIT — Do whatever you like, but attribution appreciated.
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Tuple

APP_TITLE = "Caesar Cipher — Encoder / Decoder"
APP_VERSION = "1.0.0"

# ---------------------------
# Core Caesar/Digit functions
# ---------------------------

def _shift_alpha(ch: str, k: int, encode: bool = True) -> str:
    if not ch.isalpha():
        return ch
    base = ord('A') if ch.isupper() else ord('a')
    off = ord(ch) - base
    k = k % 26
    val = (off + k) % 26 if encode else (off - k) % 26
    return chr(base + val)


def _shift_digit(d: str, k: int, encode: bool = True) -> str:
    if not d.isdigit():
        return d
    k = k % 10
    off = ord(d) - ord('0')
    val = (off + k) % 10 if encode else (off - k) % 10
    return chr(ord('0') + val)


def caesar_transform(text: str, shift: int, mode: str = 'encode', rotate_digits: bool = True) -> str:
    """Transform text using Caesar for letters and optional rotation for digits.

    Args:
        text: Input text
        shift: integer shift (any int; modulo applied)
        mode: 'encode' or 'decode'
        rotate_digits: if True, rotate 0-9 by same shift
    """
    encode = (mode.lower() == 'encode')
    out_chars = []
    s26 = shift % 26
    s10 = shift % 10

    for ch in text:
        if ch.isalpha():
            out_chars.append(_shift_alpha(ch, s26, encode))
        elif rotate_digits and ch.isdigit():
            out_chars.append(_shift_digit(ch, s10, encode))
        else:
            out_chars.append(ch)
    return ''.join(out_chars)


# ---------------------------
# GUI Application
# ---------------------------
class CaesarApp(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master.title(APP_TITLE)
        self.master.geometry("980x640")
        self.master.minsize(820, 520)

        # State vars
        self.shift_var = tk.IntVar(value=3)
        self.mode_var = tk.StringVar(value='encode')
        self.rotate_digits_var = tk.BooleanVar(value=True)
        self.theme_var = tk.StringVar(value='dark')  # default theme

        # Build UI
        self._setup_style()
        self._build_menu()
        self._build_controls()
        self._build_text_panes()
        self._build_statusbar()
        self._bind_shortcuts()
        self._apply_theme(self.theme_var.get())

        self.update_counts()

    # ---------- Styling / Theme ----------
    def _setup_style(self):
        self.style = ttk.Style()
        try:
            # Use platform-appropriate theme as base
            base = 'clam' if sys.platform.startswith('linux') else 'vista' if sys.platform.startswith('win') else 'aqua'
            self.style.theme_use(base)
        except Exception:
            pass

    def _apply_theme(self, theme: str):
        is_dark = (theme == 'dark')
        bg = '#0f172a' if is_dark else '#f8fafc'
        fg = '#e5e7eb' if is_dark else '#0f172a'
        pane_bg = '#111827' if is_dark else '#ffffff'
        acc = '#2563eb' if is_dark else '#1d4ed8'
        entry_bg = '#111827' if is_dark else '#ffffff'
        entry_fg = fg

        # Configure style colors
        self.master.configure(bg=bg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=fg)
        self.style.configure('TCheckbutton', background=bg, foreground=fg)
        self.style.configure('TRadiobutton', background=bg, foreground=fg)
        self.style.configure('TButton', background=bg, foreground=fg)
        self.style.configure('Accent.TButton', foreground=fg)
        self.style.map('TButton', foreground=[('active', fg)])

        # Text widgets need manual config
        for widget in (self.input_text, self.output_text):
            widget.configure(bg=entry_bg, fg=entry_fg, insertbackground=fg, selectbackground=acc)

        # Status bar
        self.statusbar.configure(bg=bg)
        self.status_label.configure(bg=bg, fg=fg)

        # Remember theme
        self.theme_var.set('dark' if is_dark else 'light')

    # ---------- Menus ----------
    def _build_menu(self):
        mbar = tk.Menu(self.master)

        # File
        m_file = tk.Menu(mbar, tearoff=0)
        m_file.add_command(label='Open to Input…', accelerator=self._accel('O'), command=self.open_file)
        m_file.add_separator()
        m_file.add_command(label='Save Output…', accelerator=self._accel('S'), command=self.save_output)
        m_file.add_command(label='Save Both Panes…', command=self.save_both)
        m_file.add_separator()
        quit_accel = 'Cmd+Q' if self._is_macos() else 'Ctrl+Q'
        m_file.add_command(label='Quit', accelerator=f'{quit_accel} / {self._accel("W")}', command=self.quit_app)
        mbar.add_cascade(label='File', menu=m_file)

        # Edit
        m_edit = tk.Menu(mbar, tearoff=0)
        m_edit.add_command(label='Copy Output', accelerator=self._accel('C'), command=self.copy_output)
        m_edit.add_command(label='Paste to Input', accelerator=self._accel('V'), command=self.paste_to_input)
        m_edit.add_separator()
        m_edit.add_command(label='Select All (Input)', accelerator=self._accel('A'), command=lambda: self._select_all(self.input_text))
        m_edit.add_command(label='Clear Input', command=lambda: self._clear_text(self.input_text))
        m_edit.add_command(label='Clear Output', command=lambda: self._clear_text(self.output_text))
        mbar.add_cascade(label='Edit', menu=m_edit)

        # Tools
        m_tools = tk.Menu(mbar, tearoff=0)
        m_tools.add_command(label='Encode', accelerator=self._accel('E'), command=self.encode)
        m_tools.add_command(label='Decode', accelerator=self._accel('D'), command=self.decode)
        m_tools.add_command(label='Brute Force (Try All Shifts)', accelerator=self._accel('B'), command=self.bruteforce)
        m_tools.add_separator()
        m_tools.add_command(label='Swap Panes', command=self.swap_panes)
        m_tools.add_command(label='Toggle Theme (Light/Dark)', accelerator=self._accel('L'), command=self.toggle_theme)
        mbar.add_cascade(label='Tools', menu=m_tools)

        # Help
        m_help = tk.Menu(mbar, tearoff=0)
        m_help.add_command(label='About', command=self.show_about)
        m_help.add_command(label='Algorithm Notes', command=self.show_notes)
        mbar.add_cascade(label='Help', menu=m_help)

        self.master.config(menu=mbar)

    # ---------- Top Controls ----------
    def _build_controls(self):
        top = ttk.Frame(self.master)
        top.pack(fill='x', padx=14, pady=(10, 6))

        # Shift selector
        ttk.Label(top, text='Shift:').pack(side='left', padx=(0, 6))
        self.shift_spin = ttk.Spinbox(top, from_=0, to=25, width=4, textvariable=self.shift_var, wrap=True, justify='center')
        self.shift_spin.pack(side='left')

        # Mode radio buttons
        ttk.Label(top, text='   Mode:').pack(side='left', padx=(12, 6))
        rb1 = ttk.Radiobutton(top, text='Encode', value='encode', variable=self.mode_var)
        rb2 = ttk.Radiobutton(top, text='Decode', value='decode', variable=self.mode_var)
        rb1.pack(side='left')
        rb2.pack(side='left', padx=(6, 0))

        # Options
        ttk.Label(top, text='   Options:').pack(side='left', padx=(12, 6))
        cb_digits = ttk.Checkbutton(top, text='Rotate digits (0–9)', variable=self.rotate_digits_var)
        cb_digits.pack(side='left')

        # Action buttons
        ttk.Button(top, text='Encode', style='Accent.TButton', command=self.encode).pack(side='right')
        ttk.Button(top, text='Decode', command=self.decode).pack(side='right', padx=(0, 8))

    # ---------- Text Panes ----------
    def _build_text_panes(self):
        main = ttk.Frame(self.master)
        main.pack(fill='both', expand=True, padx=12, pady=(0, 8))

        paned = ttk.Panedwindow(main, orient='horizontal')
        paned.pack(fill='both', expand=True)

        # Input
        f_left = ttk.Frame(paned)
        self.input_text = tk.Text(f_left, wrap='word', undo=True)
        scroll_in = ttk.Scrollbar(f_left, command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=scroll_in.set)
        ttk.Label(f_left, text='Input (Plain / Cipher)').pack(anchor='w', pady=(0, 4))
        self.input_text.pack(side='left', fill='both', expand=True)
        scroll_in.pack(side='right', fill='y')
        paned.add(f_left, weight=1)

        # Output
        f_right = ttk.Frame(paned)
        self.output_text = tk.Text(f_right, wrap='word', undo=True)
        scroll_out = ttk.Scrollbar(f_right, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scroll_out.set)
        ttk.Label(f_right, text='Output').pack(anchor='w', pady=(0, 4))
        self.output_text.pack(side='left', fill='both', expand=True)
        scroll_out.pack(side='right', fill='y')
        paned.add(f_right, weight=1)

        # Live updates
        self.input_text.bind('<<Modified>>', self._on_modified)
        self.output_text.bind('<<Modified>>', self._on_modified)

    # ---------- Status Bar ----------
    def _build_statusbar(self):
        self.statusbar = tk.Frame(self.master, height=22)
        self.statusbar.pack(fill='x', side='bottom')
        self.status_label = tk.Label(self.statusbar, anchor='w')
        self.status_label.pack(fill='x')

    def update_counts(self, *_):
        in_text = self._get_text(self.input_text)
        out_text = self._get_text(self.output_text)
        self.status_label.config(
            text=f"Shift={self.shift_var.get()} | Mode={self.mode_var.get()} | RotateDigits={'On' if self.rotate_digits_var.get() else 'Off'}  ||  Input: {len(in_text)} chars  |  Output: {len(out_text)} chars"
        )

    # ---------- Core Actions ----------
    def encode(self, *_):
        try:
            shift = int(self.shift_var.get())
        except ValueError:
            messagebox.showerror('Invalid Shift', 'Shift must be an integer (0–25).')
            return
        text = self._get_text(self.input_text)
        res = caesar_transform(text, shift, 'encode', self.rotate_digits_var.get())
        self._set_text(self.output_text, res)
        self.mode_var.set('encode')
        self.update_counts()

    def decode(self, *_):
        try:
            shift = int(self.shift_var.get())
        except ValueError:
            messagebox.showerror('Invalid Shift', 'Shift must be an integer (0–25).')
            return
        text = self._get_text(self.input_text)
        res = caesar_transform(text, shift, 'decode', self.rotate_digits_var.get())
        self._set_text(self.output_text, res)
        self.mode_var.set('decode')
        self.update_counts()

    def bruteforce(self, *_):
        text = self._get_text(self.input_text)
        if not text.strip():
            messagebox.showinfo('Brute Force', 'Type or paste some cipher text into the Input pane first.')
            return
        w = tk.Toplevel(self.master)
        w.title('Brute Force — Try All Shifts (1–25)')
        w.geometry('720x520')
        txt = tk.Text(w, wrap='word')
        scr = ttk.Scrollbar(w, command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        txt.pack(side='left', fill='both', expand=True)
        scr.pack(side='right', fill='y')

        rotate_digits = self.rotate_digits_var.get()
        lines = []
        for k in range(1, 26):
            res = caesar_transform(text, k, 'decode', rotate_digits)
            lines.append(f"Shift {k:2d}:\n{res}\n{'-'*40}\n")
        txt.insert('1.0', ''.join(lines))
        txt.focus_set()

    def swap_panes(self, *_):
        a = self._get_text(self.input_text)
        b = self._get_text(self.output_text)
        self._set_text(self.input_text, b)
        self._set_text(self.output_text, a)
        self.update_counts()

    def toggle_theme(self, *_):
        self._apply_theme('light' if self.theme_var.get() == 'dark' else 'dark')

    # ---------- File Ops ----------
    def open_file(self, *_):
        path = filedialog.askopenfilename(title='Open Text File', filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror('Open Failed', f'Could not read file:\n{e}')
            return
        self._set_text(self.input_text, data)
        self.update_counts()

    def save_output(self, *_):
        path = filedialog.asksaveasfilename(title='Save Output', defaultextension='.txt', filetypes=[('Text Files', '*.txt')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self._get_text(self.output_text))
        except Exception as e:
            messagebox.showerror('Save Failed', f'Could not save file:\n{e}')
            return
        messagebox.showinfo('Saved', f'Output saved to:\n{path}')

    def save_both(self, *_):
        path_in = filedialog.asksaveasfilename(title='Save Input As…', defaultextension='.txt', filetypes=[('Text Files', '*.txt')])
        if not path_in:
            return
        try:
            with open(path_in, 'w', encoding='utf-8') as f:
                f.write(self._get_text(self.input_text))
        except Exception as e:
            messagebox.showerror('Save Failed', f'Could not save input:\n{e}')
            return
        path_out = filedialog.asksaveasfilename(title='Save Output As…', defaultextension='.txt', filetypes=[('Text Files', '*.txt')])
        if not path_out:
            return
        try:
            with open(path_out, 'w', encoding='utf-8') as f:
                f.write(self._get_text(self.output_text))
        except Exception as e:
            messagebox.showerror('Save Failed', f'Could not save output:\n{e}')
            return
        messagebox.showinfo('Saved', f'Saved both files.\nInput → {path_in}\nOutput → {path_out}')

    def copy_output(self, *_):
        text = self._get_text(self.output_text)
        if not text:
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.master.update()  # keep on clipboard after exit

    def paste_to_input(self, *_):
        try:
            text = self.master.clipboard_get()
        except Exception:
            text = ''
        if text:
            self.input_text.insert('insert', text)
            self.update_counts()

    def quit_app(self, *_):
        self.master.quit()

    # ---------- Help ----------
    def show_about(self, *_):
        messagebox.showinfo(
            'About',
            f"{APP_TITLE}\nVersion {APP_VERSION}\n\nPure-Python Tkinter app.\nMIT Licensed."
        )

    def show_notes(self, *_):
        messagebox.showinfo(
            'Algorithm Notes',
            (
                "Caesar Cipher (substitution cipher)\n\n"
                "Encryption: C = (P + K) mod 26\n"
                "Decryption: P = (C - K) mod 26\n\n"
                "P,C are 0–25 letter indices; K is the integer key (shift).\n"
                "This tool optionally rotates digits with mod 10."
            )
        )

    # ---------- Events / utils ----------
    def _bind_shortcuts(self):
        accel = 'Command' if self._is_macos() else 'Control'
        b = self.master.bind
        b(f'<{accel}-o>', self.open_file)
        b(f'<{accel}-s>', self.save_output)
        b(f'<{accel}-e>', self.encode)
        b(f'<{accel}-d>', self.decode)
        b(f'<{accel}-b>', self.bruteforce)
        b(f'<{accel}-l>', self.toggle_theme)
        b(f'<{accel}-c>', self.copy_output)
        b(f'<{accel}-v>', self.paste_to_input)
        b(f'<{accel}-a>', lambda e: self._select_all(self.input_text))
        b(f'<{accel}-w>', self.quit_app)
        # macOS standard quit
        b(f'<{accel}-q>', self.quit_app)

    def _on_modified(self, event):
        widget = event.widget
        widget.edit_modified(False)  # reset flag
        self.update_counts()

    @staticmethod
    def _get_text(w: tk.Text) -> str:
        return w.get('1.0', 'end-1c')

    @staticmethod
    def _set_text(w: tk.Text, text: str):
        w.delete('1.0', 'end')
        w.insert('1.0', text)

    @staticmethod
    def _clear_text(w: tk.Text):
        w.delete('1.0', 'end')

    @staticmethod
    def _select_all(w: tk.Text):
        w.tag_add('sel', '1.0', 'end')
        w.mark_set('insert', '1.0')

    @staticmethod
    def _is_macos() -> bool:
        return sys.platform == 'darwin'

    @staticmethod
    def _accel(letter: str) -> str:
        return f"Cmd+{letter}" if CaesarApp._is_macos() else f"Ctrl+{letter}"


# ---------------------------
# Entrypoint
# ---------------------------

def main():
    root = tk.Tk()
    app = CaesarApp(root)
    app.pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()
