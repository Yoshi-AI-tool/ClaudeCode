import sys
import os
import chardet
import tkinter as tk
from tkinter import filedialog, messagebox

def find_nonascii(raw: bytes, count: int = 30) -> str:
    found = []
    i = 0
    while i < len(raw) and len(found) < count:
        if raw[i] > 0x7F:
            found.append(f"[{i}] {raw[i:i+4].hex()}")
            i += 2
        else:
            i += 1
    return ", ".join(found) if found else "(非ASCIIバイトなし)"

def try_decode(raw: bytes, enc: str) -> str:
    try:
        text = raw.decode(enc, errors="strict")
        # 日本語らしい文字が含まれるか確認
        sample = [c for c in text if '　' <= c <= '鿿' or '＀' <= c <= '￯']
        return f"OK (日本語候補: {''.join(sample[:10])})"
    except Exception as e:
        return f"NG ({e})"

def main():
    root = tk.Tk()
    root.withdraw()

    filepaths = filedialog.askopenfilenames(
        title="エンコードを確認するCSVファイルを選択",
        filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")],
    )

    if not filepaths:
        return

    lines = []
    for filepath in filepaths:
        with open(filepath, "rb") as f:
            raw = f.read()
        result = chardet.detect(raw)
        lines.append(f"ファイル: {os.path.basename(filepath)}")
        lines.append(f"サイズ: {len(raw)} bytes")
        lines.append(f"chardet: {result}")
        lines.append(f"非ASCIIバイト位置: {find_nonascii(raw)}")
        lines.append("")
        for enc in ["utf-8", "cp932", "utf-8-sig", "euc-jp", "cp1252", "iso-2022-jp"]:
            lines.append(f"  {enc}: {try_decode(raw, enc)}")
        lines.append("")

    log_path = os.path.join(os.path.expanduser("~"), "Desktop", "エンコード確認結果.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    messagebox.showinfo("完了", f"デスクトップに保存しました:\nエンコード確認結果.txt")

if __name__ == "__main__":
    main()
