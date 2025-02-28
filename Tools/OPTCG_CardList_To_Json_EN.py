import os
import requests
from bs4 import BeautifulSoup
import json
import customtkinter as ctk
import urllib.parse
from tkinter import filedialog
import threading
from pathlib import Path
from PIL import Image


def load_download_list():
    json_path = r'G:\My Drive\[Python]\Onepiece CSV\Get_Data_From_Web\data_download_Path_EN.json'
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"The file does not exist at the path: {json_path}")

    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            # Check if the file is not empty before attempting to parse JSON
            content = file.read().strip()
            if not content:
                raise ValueError("The JSON file is empty.")
            file.seek(0)  # Reset file pointer to the beginning to read again
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
    except ValueError as ve:
        print(f"File issue: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return []  # Return an empty list or handle as appropriate for your application

def batch_fetch_and_save():
    download_list = load_download_list()
    for item in download_list:
        url = item['URL']
        filename = item['FILENAME']
        card_list = get_card_list_from_website(url, filename)
        save_to_json(card_list, filename)
        # 移除或注释掉以下行，以避免启动图片下载线程
        # threading.Thread(target=download_images, args=(card_list, filename)).start()
        
        # 如果需要，保留一个短暂的暂停以避免过度频繁的请求
        # time.sleep(1)  # 暂停1秒钟


def batch_fetch_and_saveimage():
    download_list = load_download_list()
    for item in download_list:
        url = item['URL']
        filename = item['FILENAME']
        card_list = get_card_list_from_website(url, filename)
        save_to_json(card_list, filename)
        # 如果需要下载图片，可以在这里调用下载图片的函数
        # 注意：如果图片下载需要json文件名，需要在这之前传递
        threading.Thread(target=download_images, args=(card_list, filename)).start()
        
        # 这里可以添加一个短暂的暂停，避免太过频繁的请求
        # time.sleep(1) # 暂停1秒钟



def get_card_list_from_website(url, json_filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    card_data = []

    card_sections = soup.find_all('dl', class_='modalCol')
    

    for section in card_sections:
        card_id = section.find('span').text.strip() if section.find('span') else '-'
        card_name = section.find('div', class_='cardName').text.strip() if section.find('div', class_='cardName') else '-'
        
        
        details = section.find('div', class_='backCol')
        info_col = section.find('div', class_='infoCol')
        front_col = section.find('div', class_='frontCol')
        img_tag = front_col.find('img', class_='lazy') if front_col else None

        if details and info_col and img_tag:
           
            life = extract_and_clean_text(details.find('div', class_='cost'))
            attribute_div = details.find('div', class_='attribute')
            attribute = '-'
            if attribute_div:
                attribute_img = attribute_div.find('img')
                if attribute_img and 'alt' in attribute_img.attrs:
                    attribute = attribute_img['alt']
            power = extract_and_clean_text(details.find('div', class_='power'))
            color = extract_and_clean_text(details.find('div', class_='color'))
            feature = extract_and_clean_text(details.find('div', class_='feature'))
            text = extract_and_clean_text(details.find('div', class_='text'))
            get_info = extract_and_clean_text(details.find('div', class_='getInfo'))
            counter = extract_and_clean_text(details.find('div', class_='counter'))
            trigger = extract_and_clean_text(details.find('div', class_='trigger'))

            # 檢查 infoCol 中的內容來決定卡牌類型
            
            card_type = "Unknown"
            if "LEADER" in info_col.get_text().upper():
                card_type = "Leader"
            if "CHARACTER" in info_col.get_text().upper():
                card_type = "Character"
            if "STAGE" in info_col.get_text().upper():
                card_type = "Stage"
            if "EVENT" in info_col.get_text().upper():
                card_type = "Event"

            card_grade ="-"
            if "SP CARD" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_SP"
                else:
                    card_grade = "SP"
                card_grade = "SP"
            if "SEC" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_SEC"
                else:
                    card_grade = "SEC"
                card_grade = "SEC"
            if "L" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_L"
                else:
                    card_grade = "L"
                card_grade = "Leader"
            if "R" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_R"
                else:
                    card_grade = "R"
                card_grade = "R"
            if "C" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_C"
                else:
                    card_grade = "C"

            if "UC" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_UC"
                else:
                    card_grade = "UC"
            if "SR" in info_col.get_text():
                if "異圖卡" in card_name:
                    card_grade = "AA_SR"
                else:
                    card_grade = "SR"

            #檢查nfoCol 中的內容來決定卡牌級別

            # 獲取圖片URL
            img_url = img_tag.get('data-src', '')
            if not img_url.startswith(('http://', 'https://')):
                # 如果是相對路徑，進行處理
                img_url = urllib.parse.urljoin(url, img_url.split('?')[0])  # 移除 ? 及其後的數字
            #Card folder for image location
            img_path = os.path.join(card_id.split('-',1)[0],card_id)

            #Unreal 的Texture path
            image01_engine_path = f"/Script/Engine.Texture2D'/Game/Datas/Arts/{card_id.split('-',1)[0]}/{card_id}.{card_id}'"

            card_details = {
                'name': card_id,
                'id': card_id,
                'card_name':card_name,
                'card_grade':card_grade,
                'life': life,
                'attribute': attribute,  # 使用提取的 attribute
                'power': power,
                'color': color,
                'counter':counter,
                'feature': feature,
                'text': text,
                'get_info': get_info,
                'card_catalog': card_type,
                'Ban':"-",
                'series': card_id.split('-',1)[0],
                'trigger':trigger,
                'image_path':img_path,
                'image_url': img_url, # 添加图片URL到JSON
                'image': image01_engine_path, #for unreal engine texture #disalve for now 

            }
            card_data.append(card_details)

    return card_data

def extract_and_clean_text(div):
    """提取文本并清理不需要的字眼"""
    if div:
        text = div.get_text(separator='\n').strip()
        # 替换掉不需要的字眼
        text = text.replace("Cost\n", "").replace("Power\n", "").replace("Color\n", "").replace("Type\n", "").replace("Effect\n", "").replace("Card Set(s)\n", "").replace("Counter\n","").replace("Life\n","")
        return text
    return '-'

def save_to_json(data, filename):
    """將數據保存為 JSON 文件，如果文件已存在則覆蓋，並處理重複的卡牌 ID"""
    # 創建一個字典來跟踪已存在的 ID
    existing_ids = {}
    
    # 遍歷所有的卡牌數據
    for card in data:
        card_id = card['id']
        # 如果 ID 已經存在，添加 _p1, _p2 等
        if card_id in existing_ids:
            counter = existing_ids[card_id] + 1
            card['id'] = f"{card_id}_p{counter}"
            card['name']= f"{card_id}_p{counter}"
            existing_ids[card_id] = counter
        else:
            existing_ids[card_id] = 0
    
    for card in data:
        card_imagepath = card['image_path']
        # 如果 ImagePath 已經存在，添加 _p1, _p2 等
        if card_imagepath in existing_ids:
            counter = existing_ids[card_imagepath] + 1
            card['image_path'] = f"{card_imagepath}_p{counter}.png"
            existing_ids[card_imagepath] = counter
            print (card['image_path'])
        else:
            card['image_path'] = f"{card_imagepath}.png"
            existing_ids[card_imagepath] = 0
    
    for card in data:
        card_image = card['image']
        card_id = card['id']
        # 如果 Image 已經存在，添加 _p1, _p2 等
        if card_image in existing_ids:
            counter = existing_ids[card_image] + 1
            card['image'] = f"/Script/Engine.Texture2D'/Game/Datas/Arts/{card_id.split('-',1)[0]}/{card_id}.{card_id}'"
            existing_ids[card_image] = counter
            print (card['image'])
            
        else:
            existing_ids[card_image] = 0
    
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        root.after(0, update_progress_and_output, 1, f"卡牌數據已保存為 {filename}")
    except PermissionError:
        root.after(0, update_progress_and_output, 1, f"權限錯誤：無法保存文件 {filename}。請檢查文件權限或路徑是否正確。")
    except Exception as e:
        root.after(0, update_progress_and_output, 1, f"發生錯誤：{e}")

def fetch_and_save():
    url = url_entry.get()
    json_filename = file_path_entry.get() or r"D:\CardData.json"  # 如果沒有輸入路徑，使用默認路徑
    card_list = get_card_list_from_website(url, json_filename)  # 傳遞 json_filename
    save_to_json(card_list, json_filename)

# 進度條和文本更新函數
def update_progress_and_output(progress, text):
    progress_bar.set(progress)
    output_text.insert("end", text + "\n")
    output_text.see("end")  # 滾動到最後面

# 停止事件
stop_event = threading.Event()

def download_images(card_list, json_filename):
    """下载卡牌图片，如果图片已存在则在文件名后加上-P1, -P2等"""
    total = len(card_list)
    for i, card in enumerate(card_list):
        if stop_event.is_set():
            print_text = "下载已停止"
            root.after(0, update_progress_and_output, progress_bar.get(), print_text)
            return
        
        if 'image_url' in card:
            img_url = card['image_url']
            base_filename = f"{card['id']}.png"
            img_path = os.path.join(os.path.dirname(json_filename), base_filename)
            counter = 1
            while os.path.exists(img_path):
                img_path = os.path.join(os.path.dirname(json_filename), f"{card['id']}_p{counter}.png")
                counter += 1

            try:
                with open(img_path, 'wb') as f:
                    img_response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
                    img_response.raise_for_status()
                    for chunk in img_response.iter_content(1024):
                        if stop_event.is_set():
                            print_text = "下载已停止"
                            root.after(0, update_progress_and_output, progress_bar.get(), print_text)
                            return
                        f.write(chunk)
                print_text = f"已下载图片到 {img_path}"
                
                #Image clean by using PIL
                img = Image.open(img_path)
                img.save(img_path)

                root.after(0, update_progress_and_output, (i + 1) / total, print_text)
            except requests.exceptions.RequestException as e:
                print_text = f"下载图片时发生网络错误: {e}"
                root.after(0, update_progress_and_output, (i + 1) / total, print_text)
            except Exception as e:
                print_text = f"下载图片时发生错误: {e}"
                root.after(0, update_progress_and_output, (i + 1) / total, print_text)
        
        # 更新進度條
        root.after(0, update_progress_and_output, (i + 1) / total, "")
    
    # 完成後更新進度條為100%
    root.after(0, update_progress_and_output, 1, "下载完成")

# 停止下載按鈕
def stop_download():
    stop_event.set()

#設置主窗口
root = ctk.CTk()
root.title("One Piece Card Game Data Fetcher")
root.geometry("450x500")  # 增加窗口高度以容納所有元素

# URL 輸入框
url_frame = ctk.CTkFrame(root)
url_frame.pack(pady=10, fill='x')
ctk.CTkLabel(url_frame, text="Enter URL:").pack(side='left', padx=(0, 5))
url_entry = ctk.CTkEntry(url_frame, width=300)
url_entry.pack(side='left')
url_entry.insert(0, "https://asia-en.onepiece-cardgame.com/cardlist/?series=556108")

# 文件路径输入框和瀏覽按鈕
file_frame = ctk.CTkFrame(root)
file_frame.pack(pady=5, fill='x')
ctk.CTkLabel(file_frame, text="Enter File Path (optional):").pack(side='top', pady=(0, 5))
file_path_entry = ctk.CTkEntry(file_frame, width=300)
file_path_entry.pack(side='left', padx=(0, 5), expand=True)
file_path_entry.insert(0,"G:/我的雲端硬碟/[Python]/Onepiece CSV/Card_Browser/Datas/OP01_Data_EN.json")

def browse_file_path():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        file_path_entry.delete(0, ctk.END)
        file_path_entry.insert(0, file_path)

browse_button = ctk.CTkButton(file_frame, text="Browse", command=browse_file_path)
browse_button.pack(side='left')

# 按鈕框架
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10, fill='x')

# Fetch and Save 按鈕
fetch_button = ctk.CTkButton(button_frame, text="Fetch and Save", command=fetch_and_save)
fetch_button.pack(side='left', padx=(0, 10))

# Download Images 按鈕
download_button = ctk.CTkButton(button_frame, text="Download Images", command=lambda: threading.Thread(target=lambda: download_images(get_card_list_from_website(url_entry.get(), file_path_entry.get() or r"D:\CardData.json"), file_path_entry.get() or r"D:\CardData.json")).start())
download_button.pack(side='left', padx=(10, 0))

# 停止下載按鈕
stop_button = ctk.CTkButton(button_frame, text="Stop Download", command=stop_download)
stop_button.pack(side='left', padx=(10, 0))


# 在UI部分添加新的按键
batch_download_button = ctk.CTkButton(button_frame, text="Batch Fetch and Save", command=batch_fetch_and_save)
batch_download_button.pack(side='left', padx=(10, 0))

# 在UI部分添加新的按键
batch_download_button = ctk.CTkButton(button_frame, text="Batch Download", command=batch_fetch_and_saveimage)
batch_download_button.pack(side='left', padx=(10, 0))

# 進度條和文本框框架
progress_output_frame = ctk.CTkFrame(root)
progress_output_frame.pack(pady=10, fill='both', expand=True)

# 添加進度條和文本框
progress_bar = ctk.CTkProgressBar(progress_output_frame, width=300)
progress_bar.pack(pady=(0, 5), fill='x')

output_text = ctk.CTkTextbox(progress_output_frame, width=300, height=100)
output_text.pack(pady=5, fill='both', expand=True)
output_text.insert("0.0", "Output will appear here.\n")

# 運行主循環
root.mainloop()