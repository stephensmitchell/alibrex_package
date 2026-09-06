"""Port of AlibreScript ``Utilities/Image to Python.py``.

No Alibre interaction. Emits a Python source file containing the
binary contents of an image as a ``list`` of ``int``. Uses tkinter for
file pickers (the AlibreScript ``File`` / ``SaveFile`` types).
"""
from __future__ import annotations

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

def _ask_open(prompt: str, filetypes) -> str | None:
    root = tk.Tk()
    root.withdraw()
    try:
        path = filedialog.askopenfilename(title=prompt, filetypes=filetypes)
    finally:
        root.destroy()
    return path or None

def _ask_save(prompt: str, default_ext: str, filetypes) -> str | None:
    root = tk.Tk()
    root.withdraw()
    try:
        path = filedialog.asksaveasfilename(
            title=prompt, defaultextension=default_ext, filetypes=filetypes,
        )
    finally:
        root.destroy()
    return path or None

def main() -> None:
    img_path = _ask_open(
        "Choose an image",
        [("PNG", "*.png"), ("JPEG", "*.jpg"), ("Bitmap", "*.bmp"), ("All files", "*.*")],
    )
    if not img_path:
        sys.exit("User cancelled")
    out_path = _ask_save(
        "Python file to generate", ".py",
        [("Python", "*.py"), ("All files", "*.*")],
    )
    if not out_path:
        sys.exit("User cancelled")

    var_name = "Img_" + os.path.splitext(os.path.basename(img_path))[0].replace(" ", "_")
    data = Path(img_path).read_bytes()

    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"{var_name} = [\n")
        for i in range(0, len(data), 20):
            chunk = data[i:i + 20]
            out.write("  " + ", ".join(f"0x{b:02X}" for b in chunk) + ",\n")
        out.write("]\n")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
