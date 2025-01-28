import json
import tkinter as tk
from tkinter import messagebox, filedialog

# 定義全局變量
file_path = None
reference_json_path = None
json_data = None
reference_data = None

# 定義選擇主JSON文件的函數
def select_json_file():
    global file_path, json_data
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        messagebox.showwarning("Warning", "未選擇任何主JSON文件！")
        return
    try:
        with open(file_path, "r") as file:
            json_data = json.load(file)
        messagebox.showinfo("Success", f"成功加載主JSON文件: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"無法加載主JSON文件: {e}")

# 定義選擇參考JSON文件的函數
def select_reference_json():
    global reference_json_path, reference_data
    reference_json_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not reference_json_path:
        messagebox.showwarning("Warning", "未選擇任何參考JSON文件！")
        return
    try:
        with open(reference_json_path, "r", encoding="utf-8") as file:
            reference_data = json.load(file)
        messagebox.showinfo("Success", f"成功加載參考JSON文件: {reference_json_path}")
    except UnicodeDecodeError:
        try:
            with open(reference_json_path, "r", encoding="utf-8-sig") as file:
                reference_data = json.load(file)
            messagebox.showinfo("Success", f"成功加載參考JSON文件: {reference_json_path} (使用 utf-8-sig 編碼)")
        except Exception as e:
            messagebox.showerror("Error", f"無法加載參考JSON文件: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"無法加載參考JSON文件: {e}")

# 定義添加新數據並參考的函數
def add_to_json():
    if not json_data:
        messagebox.showwarning("Warning", "請先加載主JSON文件！")
        return
    if not reference_data:
        messagebox.showwarning("Warning", "請先加載參考JSON文件！")
        return

    user_input = text_field.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Warning", "請輸入參數！")
        return

    # 解析用戶輸入
    lines = user_input.splitlines()
    leader_id = lines[0][2:]  # 去掉前兩個字符
    members = []

    for line in lines[1:]:
        try:
            count, member_id = line.split('x')
            count = int(count)
            member_id = member_id.strip()

            # 在參考JSON中查找匹配的數據
            reference_entry = next((item for item in reference_data if item.get("id") == member_id), None)

            if reference_entry:
                members.append({
                    "memberCatalog": reference_entry.get("card_catalog", "Unknown"),
                    "memberCost": reference_entry.get("life", "Unknown"),
                    "memberCount": count,
                    "memberID": member_id,
                    "name": reference_entry.get("card_name", member_id)
                })
            else:
                members.append({
                    "memberCatalog": "Unknown",  # 無匹配時默認值
                    "memberCost": "Unknown",    # 無匹配時默認值
                    "memberCount": count,
                    "memberID": member_id,
                    "name": member_id
                })

        except ValueError:
            messagebox.showerror("Error", f"無法解析行: {line}")
            return

    # 創建新的Deck數據
    new_deck = {
        "deckOwner": "Unknown",  # 可根據需求填寫
        "deckFrom": "Unknown",   # 可根據需求填寫
        "placement": "Unknown",  # 可根據需求填寫
        "tournament": "Unknown", # 可根據需求填寫
        "host": "Unknown",       # 可根據需求填寫
        "deckDate": "Unknown",   # 可根據需求填寫
        "leader": leader_id,
        "deckColor": "Unknown",  # 可根據需求填寫
        "leaderID": leader_id,
        "members": members
    }

    # 將新數據添加到JSON的最前面
    json_data.insert(0, new_deck)

    # 保存回JSON文件
    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)

    messagebox.showinfo("Success", "新數據已成功添加！")

# 創建Tkinter窗口
root = tk.Tk()
root.title("JSON數據更新")

# 創建選擇文件按鈕
select_file_button = tk.Button(root, text="選擇主JSON文件", command=select_json_file)
select_file_button.pack(pady=10)

select_reference_button = tk.Button(root, text="選擇參考JSON文件", command=select_reference_json)
select_reference_button.pack(pady=10)

# 創建多行輸入框和確認按鈕
text_field = tk.Text(root, height=20, width=50)
text_field.pack(pady=10)

confirm_button = tk.Button(root, text="Confirm", command=add_to_json)
confirm_button.pack(pady=10)

# 運行Tkinter主循環
root.mainloop()
