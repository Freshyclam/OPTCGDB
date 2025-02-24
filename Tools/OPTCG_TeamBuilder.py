import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from PIL import Image, ImageTk
import requests
from io import BytesIO

# 定義 JSON 文件名
JSON_FILE = "teams.json"
LEADER_DATA_FILE = "D:\\Github\\OPTCGDB\\All_Data_EN.json"  # 存放 Leader 數據的 JSON 文件

# 讀取隊伍數據
def load_teams():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 保存隊伍數據
def save_teams(teams):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(teams, f, indent=4, ensure_ascii=False)

# 讀取 Leader 數據
def load_leader_data():
    if os.path.exists(LEADER_DATA_FILE):
        with open(LEADER_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [card for card in data if card.get("card_catalog") == "Leader"]
    return []

# 選擇隊長窗口
def select_leader(teams, name):
    leader_window = Toplevel(root)
    leader_window.title("選擇隊長")
    leader_window.geometry("600x500")

    leaders = load_leader_data()
    
    frame = tk.Frame(leader_window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    leader_images = {}

    def confirm_selection(leader):
        teams.append({
            "deckname": name,
            "leader": leader["card_name"],
            "leaderID": leader["id"],
            "leaderColor": leader["color"],
            "members": [],
            "leaderImage": leader["image_url"]
        })
        save_teams(teams)
        refresh_list()
        leader_window.destroy()

    for leader in leaders:
        image_url = leader.get("image_url", "")
        if image_url:
            try:
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((100, 150))
                img = ImageTk.PhotoImage(img)
                leader_images[leader["card_name"]] = img
            except Exception as e:
                print(f"無法加載圖片 {leader['card_name']}: {e}")
        
        frame = tk.Frame(scroll_frame, padx=5, pady=5)
        frame.pack(fill=tk.X)
        
        if leader["card_name"] in leader_images:
            lbl_img = tk.Label(frame, image=leader_images[leader["card_name"]])
            lbl_img.pack(side=tk.LEFT)
        
        lbl_text = tk.Label(frame, text=leader["card_name"], padx=10)
        lbl_text.pack(side=tk.LEFT)

        btn_select = tk.Button(frame, text="選擇", command=lambda l=leader: confirm_selection(l))
        btn_select.pack(side=tk.RIGHT)

# 新增隊伍
def add_team():
    name = simpledialog.askstring("新增隊伍", "請輸入隊伍名稱:")
    if name:
        select_leader(teams, name)

# 刪除隊伍
def delete_team():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        del teams[index]
        save_teams(teams)
        refresh_list()

# 複製隊伍
def duplicate_team():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        new_team = teams[index].copy()
        new_team["deckname"] += "_copy"
        teams.append(new_team)
        save_teams(teams)
        refresh_list()

# 編輯隊伍
def edit_team():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        team = teams[index]
        new_name = simpledialog.askstring("編輯隊伍", "請輸入新的隊伍名稱:", initialvalue=team["deckname"])
        if new_name:
            teams[index]["deckname"] = new_name
            save_teams(teams)
            refresh_list()

# 刷新隊伍列表
def refresh_list():
    listbox.delete(0, tk.END)
    for team in teams:
        listbox.insert(tk.END, team["deckname"])

# 匯入 JSON
def import_json():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            imported_teams = json.load(f)
        teams.extend(imported_teams)
        save_teams(teams)
        refresh_list()

# 匯出 JSON
def export_json():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(teams, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("匯出成功", "JSON 文件已匯出")

# 初始化 Tkinter 應用
root = tk.Tk()
root.title("OPTCG 隊伍管理工具")
root.geometry("400x400")

teams = load_teams()

listbox = tk.Listbox(root)
listbox.pack(fill=tk.BOTH, expand=True)
refresh_list()

btn_add = tk.Button(root, text="新增隊伍", command=add_team)
btn_add.pack(fill=tk.X)
btn_edit = tk.Button(root, text="編輯隊伍", command=edit_team)
btn_edit.pack(fill=tk.X)
btn_delete = tk.Button(root, text="刪除隊伍", command=delete_team)
btn_delete.pack(fill=tk.X)
btn_duplicate = tk.Button(root, text="複製隊伍", command=duplicate_team)
btn_duplicate.pack(fill=tk.X)
btn_import = tk.Button(root, text="匯入 JSON", command=import_json)
btn_import.pack(fill=tk.X)
btn_export = tk.Button(root, text="匯出 JSON", command=export_json)
btn_export.pack(fill=tk.X)

root.mainloop()
