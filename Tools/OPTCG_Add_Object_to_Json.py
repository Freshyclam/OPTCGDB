import json
from tkinter import Tk, Label, Entry, Button, Listbox, END, filedialog, messagebox, Frame

# 全局变量
json_data = []
filtered_data = []
json_file_path = ""

# 加载 JSON 文件
def load_json():
    global json_data, json_file_path, filtered_data
    file_path = filedialog.askopenfilename(
        title="选择 JSON 文件",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if file_path:
        json_file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        filtered_data = json_data  # 初始化筛选数据为完整数据
        refresh_listbox()
        messagebox.showinfo("成功", f"成功加载文件：{file_path}")
    else:
        messagebox.showwarning("警告", "未选择文件！")

# 搜索 JSON
def search_json():
    global filtered_data
    query = search_entry.get().strip().lower()
    if query:
        filtered_data = [obj for obj in json_data if query in obj.get("name", "").lower()]
    else:
        filtered_data = json_data
    refresh_listbox()

# 保存 JSON 文件
def save_json():
    global json_file_path
    file_path = filedialog.asksaveasfilename(
        title="保存 JSON 文件",
        defaultextension=".json",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if file_path:
        json_file_path = file_path
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)
        messagebox.showinfo("成功", f"文件已成功保存到：{file_path}")
    else:
        messagebox.showwarning("警告", "未选择保存位置！")

# 新增或更新 Object
def add_or_update_object():
    if not json_data:
        messagebox.showwarning("警告", "请先加载 JSON 文件！")
        return

    new_obj = create_object_from_entries()
    input_id = new_obj["id"]

    # 检查是否存在相同的 ID
    for obj in json_data:
        if obj["id"] == input_id:
            obj.update(new_obj)  # 更新已有对象
            search_json()  # 更新筛选结果
            messagebox.showinfo("成功", f"ID 为 {input_id} 的对象已更新！")
            return

    # 如果不存在相同的 ID，则新增
    json_data.append(new_obj)
    search_json()  # 更新筛选结果
    messagebox.showinfo("成功", "新增对象成功！")

# 删除选中 Object
def delete_object():
    selected_index = listbox.curselection()
    if not selected_index:
        messagebox.showwarning("警告", "请选择要删除的对象！")
        return
    index = selected_index[0]
    original_index = json_data.index(filtered_data[index])  # 找到原始数据的索引
    deleted_obj = json_data.pop(original_index)
    search_json()  # 更新筛选结果
    messagebox.showinfo("成功", f"已删除对象：{deleted_obj['name']}")

# 删除 Ban 内含 TEMP 的对象
def delete_temp_objects():
    global json_data
    initial_count = len(json_data)
    json_data = [obj for obj in json_data if obj.get("Ban", "") != "TEMP"]
    deleted_count = initial_count - len(json_data)
    search_json()  # 更新筛选结果
    messagebox.showinfo("成功", f"已删除 {deleted_count} 个 Ban 内含 TEMP 的对象！")

# 合并两个 JSON 文件
def merge_json_files():
    file1_path = filedialog.askopenfilename(
        title="选择第一个 JSON 文件",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if not file1_path:
        messagebox.showwarning("警告", "未选择第一个文件！")
        return

    file2_path = filedialog.askopenfilename(
        title="选择第二个 JSON 文件",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if not file2_path:
        messagebox.showwarning("警告", "未选择第二个文件！")
        return

    # 加载两个文件
    try:
        with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
            data1 = json.load(file1)
            data2 = json.load(file2)
    except Exception as e:
        messagebox.showerror("错误", f"加载文件失败：{e}")
        return

    # 合并数据（如果 id 已存在，则不重复添加）
    id_set = {obj["id"] for obj in data1}  # 获取第一个文件的所有 ID
    merged_data = data1.copy()  # 复制第一个文件的内容

    for obj in data2:
        if obj["id"] not in id_set:
            merged_data.append(obj)

    # 保存合并结果
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

# 从表单创建 Object
def create_object_from_entries():
    return {
        "name": entry_name.get(),
        "id": entry_id.get(),
        "card_name": entry_card_name.get(),
        "card_grade": entry_card_grade.get(),
        "life": entry_life.get(),
        "attribute": entry_attribute.get(),
        "power": entry_power.get(),
        "color": entry_color.get(),
        "counter": entry_counter.get(),
        "feature": entry_feature.get(),
        "text": entry_text.get(),
        "get_info": entry_get_info.get(),
        "card_catalog": entry_card_catalog.get(),
        "Ban": entry_ban.get(),
        "series": entry_series.get(),
        "trigger": entry_trigger.get(),
        "image_path": entry_image_path.get(),
        "image_url": entry_image_url.get(),
        "image": entry_image.get(),
        "QNA": entry_qna.get()
    }

# 显示选中对象到表单
def display_selected_object(event):
    selected_index = listbox.curselection()
    if not selected_index:
        return
    index = selected_index[0]
    selected_obj = filtered_data[index]
    for key, entry in entries.items():
        entry.delete(0, END)
        entry.insert(0, selected_obj.get(key, ""))

# 刷新列表
def refresh_listbox():
    listbox.delete(0, END)
    for obj in filtered_data:
        listbox.insert(END, obj["name"])

# 增加去重功能
def deduplicate_json():
    file_path = filedialog.askopenfilename(
        title="选择需要去重的 JSON 文件",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if not file_path:
        messagebox.showwarning("警告", "未选择文件！")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        unique_data = []
        seen = set()

        for entry in data:
            entry_str = json.dumps(entry, sort_keys=True)
            if entry_str not in seen:
                unique_data.append(entry)
                seen.add(entry_str)

        save_path = filedialog.asksaveasfilename(
            title="保存去重后的 JSON 文件",
            defaultextension=".json",
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
        )

        if save_path:
            with open(save_path, 'w', encoding='utf-8') as save_file:
                json.dump(unique_data, save_file, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", f"文件已成功保存到：{save_path}")
        else:
            messagebox.showwarning("警告", "未选择保存位置！")

    except Exception as e:
        messagebox.showerror("错误", f"去重过程中出现错误：{e}")

# UI 设计
root = Tk()
root.title("JSON 编辑器")

# 搜索栏位
frame = Frame(root)
frame.grid(row=0, column=0, columnspan=2, pady=5)

Button(frame, text="加载 JSON 文件", command=load_json).grid(row=0, column=0, padx=5)
search_entry = Entry(frame, width=50)
search_entry.grid(row=0, column=1, padx=5)
Button(frame, text="搜索", command=search_json).grid(row=0, column=2, padx=5)

# 显示现有内容
listbox = Listbox(root, width=30, height=20, selectmode="browse")
listbox.grid(row=1, column=0, rowspan=10, padx=10, pady=5)
listbox.bind("<<ListboxSelect>>", display_selected_object)

# 输入表单
fields = [
    "name", "id", "card_name", "card_grade", "life", "attribute", "power",
    "color", "counter", "feature", "text", "get_info", "card_catalog",
    "Ban", "series", "trigger", "image_path", "image_url", "image", "QNA"
]

entries = {}
row_index = 1
for field in fields:
    Label(root, text=field).grid(row=row_index, column=1, sticky="e", padx=5, pady=2)
    entry = Entry(root, width=50)
    entry.grid(row=row_index, column=2, padx=5, pady=2)
    entries[field] = entry
    row_index += 1

entry_name = entries["name"]
entry_id = entries["id"]
entry_card_name = entries["card_name"]
entry_card_grade = entries["card_grade"]
entry_life = entries["life"]
entry_attribute = entries["attribute"]
entry_power = entries["power"]
entry_color = entries["color"]
entry_counter = entries["counter"]
entry_feature = entries["feature"]
entry_text = entries["text"]
entry_get_info = entries["get_info"]
entry_card_catalog = entries["card_catalog"]
entry_ban = entries["Ban"]
entry_series = entries["series"]
entry_trigger = entries["trigger"]
entry_image_path = entries["image_path"]
entry_image_url = entries["image_url"]
entry_image = entries["image"]
entry_qna = entries["QNA"]

# 操作按钮
button_frame = Frame(root)
button_frame.grid(row=row_index, column=1, columnspan=2, pady=10)

Button(button_frame, text="Add/Update Object", width=30, command=add_or_update_object).grid(row=0, column=0, pady=5)
Button(button_frame, text="Remove Selected Object", width=30, command=delete_object).grid(row=1, column=0, pady=5)
Button(button_frame, text="删除 Ban 内含 TEMP 的对象", width=30, command=delete_temp_objects).grid(row=2, column=0, pady=5)
Button(button_frame, text="Combine JSON ", width=30, command=merge_json_files).grid(row=3, column=0, pady=5)
Button(button_frame, text="Save JSON ", width=30, command=save_json).grid(row=4, column=0, pady=5)
Button(button_frame, text="[Tools] Remove Duplicate from Json", width=30, command=deduplicate_json).grid(row=5, column=0, pady=5)

root.mainloop()
