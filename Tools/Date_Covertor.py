import json
from datetime import datetime
import sys

# 確保 stdout 使用 UTF-8 編碼
sys.stdout.reconfigure(encoding='utf-8')

# 讀取 JSON 文件
input_file = 'D:\\Github\\OPTCGDB\\TopDeck_2025.json'
output_file = 'D:\\Github\\OPTCGDB\\TopDeck_2025.json'
data_file = 'D:\\Github\\OPTCGDB\\All_Data_EN.json'

with open(input_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

with open(data_file, 'r', encoding='utf-8') as file:
    all_data = json.load(file)

# 建立 leaderID 與 color 的對應表
leader_color_map = {entry['id']: entry['color'] for entry in all_data if 'id' in entry and 'color' in entry}

# 更新日期格式
def update_date_format(data):
    for entry in data:
        if "deckDate" in entry:
            try:
                original_date = entry["deckDate"]
                formatted_date = datetime.strptime(original_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                entry["deckDate"] = formatted_date
            except ValueError:
                print(f"日期格式錯誤: {entry['deckDate']}")
        # 處理 tournament 和 placement
        if "tournament" in entry and ";" in entry["tournament"]:
            parts = entry["tournament"].split(";")
            entry["tournament"] = parts[0].strip()
            for part in parts[1:]:
                if "Placement:" in part:
                    entry["placement"] = part.replace("Placement:", "").strip()
        # 更新 deckColor
        if entry.get("deckColor", "Unknown") == "Unknown" and "leaderID" in entry:
            leader_id = entry["leaderID"]
            entry["deckColor"] = leader_color_map.get(leader_id, "Unknow")
    return data

# 更新資料
updated_data = update_date_format(data)

# 寫回更新後的 JSON 文件
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(updated_data, file, indent=4, ensure_ascii=False)

print(f"更新完成！已保存到 {output_file}")
