import json
from datetime import datetime
import sys

# 確保 stdout 使用 UTF-8 編碼
sys.stdout.reconfigure(encoding='utf-8')

# 讀取 JSON 文件
input_file = 'D:\\Github\\OPTCGDB\\TopDeck_2025.json'
output_file = 'D:\\Github\\OPTCGDB\\TopDeck_2025.json'

with open(input_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 更新日期格式
def update_date_format(data):
    for entry in data:
        if "deckDate" in entry:
            try:
                original_date = entry["deckDate"]
                formatted_date = datetime.strptime(original_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                entry["deckDate"] = formatted_date
            except ValueError:
                print(f"日期格式錯誤: {entry["deckDate"]}")
    return data

# 更新日期
updated_data = update_date_format(data)

# 寫回更新後的 JSON 文件
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(updated_data, file, indent=4, ensure_ascii=False)

print(f"更新完成！已保存到 {output_file}")
