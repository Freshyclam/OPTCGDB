import json
import os
from tkinter import Tk, Label, Entry, Button, Listbox, END, filedialog, messagebox, Frame

# 全局变量
json_data = []
filtered_data = []
json_file_path = ""

# 选择资料夹并合并 JSON 文件
def merge_json_from_folder():
    folder_path = filedialog.askdirectory(title="选择包含 JSON 文件的文件夹")
    if not folder_path:
        messagebox.showwarning("警告", "未选择文件夹！")
        return

    merged_data = []
    id_set = set()

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for obj in data:
                        if obj.get("id") not in id_set:
                            id_set.add(obj.get("id"))
                            merged_data.append(obj)
            except Exception as e:
                messagebox.showerror("错误", f"读取 {file_name} 失败: {e}")
                return

    save_path = filedialog.asksaveasfilename(
        title="保存合并后的 JSON 文件",
        defaultextension=".json",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )

    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as save_file:
                json.dump(merged_data, save_file, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", f"文件已成功保存到：{save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败：{e}")
    else:
        messagebox.showwarning("警告", "未选择保存位置！")

# UI 设计
root = Tk()
root.title("JSON 编辑器")

frame = Frame(root)
frame.grid(row=0, column=0, columnspan=2, pady=5)

Button(frame, text="加载 JSON 文件", command=load_json).grid(row=0, column=0, padx=5)
search_entry = Entry(frame, width=50)
search_entry.grid(row=0, column=1, padx=5)
Button(frame, text="搜索", command=search_json).grid(row=0, column=2, padx=5)

listbox = Listbox(root, width=30, height=20, selectmode="browse")
listbox.grid(row=1, column=0, rowspan=10, padx=10, pady=5)
listbox.bind("<<ListboxSelect>>", display_selected_object)

button_frame = Frame(root)
button_frame.grid(row=12, column=1, columnspan=2, pady=10)

Button(button_frame, text="合并资料夹内 JSON", width=30, command=merge_json_from_folder).grid(row=6, column=0, pady=5)

root.mainloop()