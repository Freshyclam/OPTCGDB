import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys

# 確保 stdout 使用 UTF-8 編碼
sys.stdout.reconfigure(encoding='utf-8')

json_data = None  # 全域變數存 JSON 資料

def open_json_file():
    global json_data
    filepath = filedialog.askopenfilename(title="Open JSON File", filetypes=[("JSON files", "*.json")])
    if not filepath:
        return
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        messagebox.showinfo("Success", "JSON file loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def replace_series():
    global json_data
    if json_data is None:
        messagebox.showerror("Error", "No JSON file loaded!")
        return

    series_to_replace = entry_series.get().strip()
    replacement_string = entry_replacement.get().strip()
    string_to_replace = entry_string_to_replace.get().strip()

    if not series_to_replace or not replacement_string or not string_to_replace:
        messagebox.showerror("Error", "Please enter all fields")
        return

    updated = False
    try:
        # 遍歷 JSON 的所有對象
        for item in json_data:
            if 'image_url' in item and isinstance(item['image_url'], str):
                if string_to_replace in item['image_url']:
                    item['image_url'] = item['image_url'].replace(string_to_replace, replacement_string)
                    updated = True

        if updated:
            output_filepath = os.path.join(os.getcwd(), 'output.json')
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"JSON file updated successfully!\nSaved as: {output_filepath}")
        else:
            messagebox.showwarning("Info", "No matching text found in image_url.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# 建立 GUI
root = tk.Tk()
root.title("JSON File Editor")

tk.Label(root, text="Select JSON file:").pack()
tk.Button(root, text="Open JSON file", command=open_json_file).pack()

tk.Label(root, text="Enter series to replace:").pack()
entry_series_var = tk.StringVar()  # 預留，這裡沒預設值
entry_series = tk.Entry(root, textvariable=entry_series_var)
entry_series.pack()

tk.Label(root, text="image_url to replace (default: asia-en):").pack()
entry_string_to_replace_var = tk.StringVar(value="asia-en")  # 預設值
entry_string_to_replace = tk.Entry(root, textvariable=entry_string_to_replace_var)
entry_string_to_replace.pack()

tk.Label(root, text="Replacement (default: en):").pack()
entry_replacement_var = tk.StringVar(value="en")  # 預設值
entry_replacement = tk.Entry(root, textvariable=entry_replacement_var)
entry_replacement.pack()

tk.Button(root, text="Replace series", command=replace_series).pack()

root.mainloop()
