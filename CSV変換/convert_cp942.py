"""
CSV文字コード変換ツール: CP1252 → CP942 (CP932)
exeを起動するとファイル選択ダイアログが開きます
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

SOURCE_ENCODING = "cp1252"
TARGET_ENCODING = "cp932"


def convert_file(filepath: str) -> str:
    if not os.path.isfile(filepath):
        return f"[スキップ] ファイルが見つかりません: {filepath}"

    if os.path.splitext(filepath)[1].lower() != ".csv":
        return f"[スキップ] CSVファイルではありません: {filepath}"

    try:
        with open(filepath, "r", encoding=SOURCE_ENCODING, errors="replace") as f:
            content = f.read()

        backup_path = filepath + ".bak"
        os.replace(filepath, backup_path)

        with open(filepath, "w", encoding=TARGET_ENCODING, errors="replace") as f:
            f.write(content)

        return f"[完了] {os.path.basename(filepath)}"

    except Exception as e:
        return f"[エラー] {os.path.basename(filepath)}: {e}"


def main() -> None:
    root = tk.Tk()
    root.withdraw()

    filepaths = filedialog.askopenfilenames(
        title="変換するCSVファイルを選択",
        filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")],
    )

    if not filepaths:
        return

    results = [convert_file(fp) for fp in filepaths]
    messagebox.showinfo("変換結果", "\n".join(results))


if __name__ == "__main__":
    main()
