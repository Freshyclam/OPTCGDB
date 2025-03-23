import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import urllib.parse
import re

# 全局變量
file_path = r"D:\Github\OPTCGDB\TopDeck_2025.json"
reference_json_path = r"D:\Github\OPTCGDB\All_Data_EN.json"
json_data = None
reference_data = None

# 自動加載預設 JSON 路徑（如有）
def auto_load_files():
    if os.path.exists(file_path):
        load_json(file_path, is_reference=False)
    if os.path.exists(reference_json_path):
        load_json(reference_json_path, is_reference=True)

def load_json(path, is_reference):
    global json_data, reference_data
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if is_reference:
                reference_data = data
                reference_label.config(text=f"All Data:     {path}")
            else:
                json_data = data
                file_label.config(text=f"Topdeck:     {path}")
    except Exception as e:
        messagebox.showerror("Error", f"無法加載 JSON 文件:\n{path}\n錯誤: {e}")

def select_json_file():
    global file_path
    path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not path:
        messagebox.showwarning("Warning", "未選擇任何主JSON文件！")
        return
    file_path = path
    load_json(file_path, is_reference=False)

def select_reference_json():
    global reference_json_path
    path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not path:
        messagebox.showwarning("Warning", "未選擇任何參考JSON文件！")
        return
    reference_json_path = path
    load_json(reference_json_path, is_reference=True)

def extract_from_url():
    url = url_field.get()
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        # Deck Info
        deck_name = params.get("dn", [""])[0]
        author = params.get("au", [""])[0]
        date = params.get("date", [""])[0]
        country = params.get("cn", [""])[0]
        tournament = params.get("tn", [""])[0]
        placement = params.get("pl", [""])[0]
        host = params.get("hs", [""])[0]

        additional_info = (
            f"Deck Name: {deck_name}\n"
            f"Author: {author}\n"
            f"Date: {date}\n"
            f"Country: {country}\n"
            f"Tournament: {tournament}\n"
            f"Placement: {placement}\n"
            f"Host: {host}"
        )

        # Decklist
        decklist_raw = params.get("dg", [""])[0]
        decklist = re.findall(r"(\d+)n([A-Z0-9\-]+)", decklist_raw)
        decklist_text = "\n".join([f"{count}x{card}" for count, card in decklist])

        text_field.delete(1.0, tk.END)
        text_field.insert(tk.END, decklist_text)

        additional_field.delete(1.0, tk.END)
        additional_field.insert(tk.END, additional_info)

    except Exception as e:
        messagebox.showerror("Error", f"無法解析 URL：{e}")

def process_deck_data(deck, leader_color_map):
    if "deckDate" in deck:
        try:
            original_date = deck["deckDate"]
            formatted_date = datetime.strptime(original_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            deck["deckDate"] = formatted_date
        except ValueError:
            print(f"日期格式錯誤: {deck['deckDate']}")
    if "tournament" in deck and ";" in deck["tournament"]:
        parts = deck["tournament"].split(";")
        deck["tournament"] = parts[0].strip()
        for part in parts[1:]:
            if "Placement:" in part:
                deck["placement"] = part.replace("Placement:", "").strip()
    if deck.get("deckColor", "Unknown") == "Unknown" and "leaderID" in deck:
        leader_id = deck["leaderID"]
        deck["deckColor"] = leader_color_map.get(leader_id, "Unknown")
    return deck

def remove_duplicates():
    if not reference_data:
        messagebox.showwarning("Warning", "請先加載參考JSON文件！")
        return
    try:
        unique_data = []
        seen = set()
        for entry in reference_data:
            entry_str = json.dumps(entry, sort_keys=True)
            if entry_str not in seen:
                unique_data.append(entry)
                seen.add(entry_str)
        with open(reference_json_path, "w", encoding="utf-8") as file:
            json.dump(unique_data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Success", f"去重完成！檔案已儲存至：{reference_json_path}")
    except Exception as e:
        messagebox.showerror("Error", f"去重過程中發生錯誤: {e}")

def remove_topDeckduplicates():
    if not json_data:
        messagebox.showwarning("Warning", "請先加載TOPDECK JSON文件！")
        return
    try:
        unique_data = []
        seen = set()
        for entry in json_data:
            entry_str = json.dumps(entry, sort_keys=True)
            if entry_str not in seen:
                unique_data.append(entry)
                seen.add(entry_str)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(unique_data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Success", f"去重完成！檔案已儲存至：{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"去重過程中發生錯誤: {e}")

def add_to_json():
    if not json_data:
        messagebox.showwarning("Warning", "請先加載主JSON文件！")
        return
    if not reference_data:
        messagebox.showwarning("Warning", "請先加載參考JSON文件！")
        return

    leader_color_map = {entry['id']: entry['color'] for entry in reference_data if 'id' in entry and 'color' in entry}

    user_input = text_field.get("1.0", tk.END).strip()
    additional_input = additional_field.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Warning", "請輸入參數！")
        return

    additional_data = {}
    for line in additional_input.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if key == "Author":
                additional_data["deckOwner"] = value
            elif key == "Date":
                additional_data["deckDate"] = value
            elif key == "Country":
                additional_data["deckFrom"] = value
            elif key == "Tournament":
                additional_data["tournament"] = value
            elif key == "Placement":
                additional_data["placement"] = value
            elif key == "Host":
                additional_data["host"] = value

    lines = user_input.splitlines()
    leader_id = lines[0][2:]
    members = []

    for line in lines[1:]:
        try:
            count, member_id = line.split('x')
            count = int(count)
            member_id = member_id.strip()
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
                    "memberCatalog": "Unknown",
                    "memberCost": "Unknown",
                    "memberCount": count,
                    "memberID": member_id,
                    "name": member_id
                })
        except ValueError:
            messagebox.showerror("Error", f"無法解析行: {line}")
            return

    new_deck = {
        "deckOwner": additional_data.get("deckOwner", "Unknown"),
        "deckFrom": additional_data.get("deckFrom", "Unknown"),
        "placement": additional_data.get("placement", "Unknown"),
        "tournament": additional_data.get("tournament", "Unknown"),
        "host": additional_data.get("host", "Unknown"),
        "deckDate": additional_data.get("deckDate", "Unknown"),
        "leader": leader_id,
        "deckColor": "Unknown",
        "leaderID": leader_id,
        "deckName": f"{leader_id}_{additional_data.get('deckDate', 'Unknown')}_{additional_data.get('deckOwner', 'Unknown')}",
        "members": members
    }

    new_deck = process_deck_data(new_deck, leader_color_map)
    json_data.insert(0, new_deck)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

    messagebox.showinfo("Success", "新數據已成功添加！")

# 建立視窗與 UI
root = tk.Tk()
root.title("One Piece Deck JSON 工具")
root.geometry("820x800")

file_frame = tk.LabelFrame(root, text="JSON 檔案選擇", padx=10, pady=10)
file_frame.pack(fill="x", padx=10, pady=5)

tk.Button(file_frame, text="載入 TopDeck JSON", width=25, command=select_json_file).grid(row=0, column=0, padx=5, pady=5)
file_label = tk.Label(file_frame, text="未選擇")
file_label.grid(row=0, column=1, sticky="w")

tk.Button(file_frame, text="載入 All Data JSON", width=25, command=select_reference_json).grid(row=1, column=0, padx=5, pady=5)
reference_label = tk.Label(file_frame, text="未選擇")
reference_label.grid(row=1, column=1, sticky="w")

url_frame = tk.LabelFrame(root, text="從 Deck URL 提取資料", padx=10, pady=10)
url_frame.pack(fill="x", padx=10, pady=5)

tk.Label(url_frame, text="請輸入 Deck URL").pack(anchor="w")
url_field = tk.Entry(url_frame, width=100)
url_field.pack(pady=5)
tk.Button(url_frame, text="Extract from URL", command=extract_from_url).pack()

decklist_frame = tk.LabelFrame(root, text="Deck List 區域", padx=10, pady=10)
decklist_frame.pack(fill="x", padx=10, pady=5)
text_field = tk.Text(decklist_frame, height=10, width=100)
text_field.pack()

info_frame = tk.LabelFrame(root, text="Deck Info 區域", padx=10, pady=10)
info_frame.pack(fill="x", padx=10, pady=5)
additional_field = tk.Text(info_frame, height=10, width=100)
additional_field.insert("1.0",
    "Deck Name:\nAuthor: \nDate: 1/27/2025\nCountry: \nTournament: \nPlacement: \nHost:"
)
additional_field.pack()

action_frame = tk.Frame(root)
action_frame.pack(pady=10)
tk.Button(action_frame, text="Confirm 新增 Deck", width=25, command=add_to_json).grid(row=0, column=0, padx=10, pady=5)
tk.Button(action_frame, text="Remove Duplicate: All Data", width=25, command=remove_duplicates).grid(row=0, column=1, padx=10, pady=5)
tk.Button(action_frame, text="Remove Duplicate: TopDeck", width=25, command=remove_topDeckduplicates).grid(row=0, column=2, padx=10, pady=5)

auto_load_files()
root.mainloop()
