import os
import requests
from bs4 import BeautifulSoup
import json
import customtkinter as ctk
import urllib.parse
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
from PIL import Image

# --- Data Fetching and Parsing ---
def load_download_list(json_path=None):
    if not json_path:
        json_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
    if not json_path or not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = f.read().strip()
        if not data:
            raise ValueError("The JSON file is empty.")
        return json.loads(data)

stop_event = threading.Event()

def get_card_list_from_website(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    card_data = []
    for section in soup.find_all('dl', class_='modalCol'):
        card_id = section.find('span').get_text(strip=True) if section.find('span') else '-'
        card_name = section.find('div', class_='cardName').get_text(strip=True) if section.find('div', class_='cardName') else '-'
        info_text = section.find('div', class_='infoCol').get_text().upper() if section.find('div', class_='infoCol') else ''

        img_tag = section.find('div', class_='frontCol') and section.find('div', class_='frontCol').find('img', class_='lazy')
        if not img_tag:
            continue

        def clean(div, labels_to_strip=None):
            if not div:
                return '-'
            text = div.get_text(separator='\n').strip()
            if labels_to_strip:
                for label in labels_to_strip:
                    text = text.replace(label + '\n', '')
            return text

        details = section.find('div', class_='backCol')
        life    = clean(details.find('div', class_='cost'), ['Cost', 'Life'])
        power   = clean(details.find('div', class_='power'), ['Power'])
        color   = clean(details.find('div', class_='color'), ['Color'])
        feature = clean(details.find('div', class_='feature'), ['Effect'])
        text    = clean(details.find('div', class_='text'), [])
        get_info= clean(details.find('div', class_='getInfo'), [])
        counter = clean(details.find('div', class_='counter'), ['Counter'])
        trigger = clean(details.find('div', class_='trigger'), [])
        block   = clean(details.find('div', class_='block'), [])

        if 'SP CARD' in info_text:
            card_grade = 'AA_SP' if '異圖卡' in card_name else 'SP'
        elif 'SEC' in info_text:
            card_grade = 'AA_SEC' if '異圖卡' in card_name else 'SEC'
        elif info_text.startswith('L '):
            card_grade = 'AA_L' if '異圖卡' in card_name else 'L'
        elif 'R ' in info_text:
            card_grade = 'AA_R' if '異圖卡' in card_name else 'R'
        elif 'UC' in info_text:
            card_grade = 'AA_UC' if '異圖卡' in card_name else 'UC'
        elif 'SR' in info_text:
            card_grade = 'AA_SR' if '異圖卡' in card_name else 'SR'
        else:
            card_grade = 'C'

        if 'LEADER' in info_text:
            card_type = 'Leader'
        elif 'CHARACTER' in info_text:
            card_type = 'Character'
        elif 'STAGE' in info_text:
            card_type = 'Stage'
        elif 'EVENT' in info_text:
            card_type = 'Event'
        else:
            card_type = 'Unknown'

        src = img_tag.get('data-src', '')
        img_url = urllib.parse.urljoin(url, src.split('?')[0])
        series = card_id.split('-', 1)[0]
        img_folder = Path(series) / card_id
        unreal_path = f"/Script/Engine.Texture2D'/Game/Datas/Arts/{series}/{card_id}.{card_id}'"

        card_data.append({
            'id': card_id,
            'card_name': card_name,
            'card_grade': card_grade,
            'life': life,
            'power': power,
            'color': color,
            'feature': feature,
            'text': text,
            'get_info': get_info,
            'counter': counter,
            'trigger': trigger,
            'block': block,
            'card_catalog': card_type,
            'series': series,
            'image_url': img_url,
            'image_path': str(img_folder) + '.png',
            'unreal_texture': unreal_path
        })
    return card_data

# --- JSON Saving with Duplicate Handling ---
def save_to_json(data, save_path):
    seen = {}
    for card in data:
        key = card['id']
        count = seen.get(key, 0)
        if count:
            card['id'] = f"{key}_p{count}"
        seen[key] = count + 1
        path = card['image_path']
        pcount = seen.get(path, 0)
        if pcount:
            card['image_path'] = path.replace('.png', f'_p{pcount}.png')
        seen[path] = pcount + 1

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # Display success message in output_text
        root.after(0, lambda: update_progress(1, f"Data saved to {save_path}"))
    except Exception as e:
        # Display error message in output_text
        root.after(0, lambda: update_progress(1, f"Failed to save data: {e}"))

# --- Image Download with Progress ---
def download_images(card_list, download_dir):
    stop_event.clear()
    total = len(card_list)
    for idx, card in enumerate(card_list, 1):
        if stop_event.is_set():
            break
        url = card['image_url']
        out_dir = Path(download_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{card['id']}.png"
        dst = out_dir / fname
        cnt = 1
        while dst.exists():
            dst = out_dir / f"{card['id']}_p{cnt}.png"
            cnt += 1
        try:
            resp = requests.get(url, stream=True)
            resp.raise_for_status()
            with open(dst, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    if stop_event.is_set():
                        break
                    f.write(chunk)
            Image.open(dst).save(dst)
            progress = idx/total
            root.after(0, lambda p=progress, msg=f"Downloaded {dst}": update_progress(p, msg))
        except Exception as e:
            root.after(0, lambda p=idx/total, msg=str(e): update_progress(p, msg))
    root.after(0, lambda: update_progress(1, "Download complete"))

# --- Batch Save Functionality ---
def batch_save():
    batch_file = filedialog.askopenfilename(
        title="Select batch list JSON",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if not batch_file:
        return
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_list = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load batch list: {e}")
        return
    for entry in batch_list:
        url = entry.get("URL")
        save_path = entry.get("FILENAME")
        try:
            data = get_card_list_from_website(url)
            save_to_json(data, save_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error processing {url}: {e}")

# --- UI and Helpers ---

def update_progress(progress, text):
    progress_bar.set(progress)
    output_text.insert('end','\n'+ text )
    output_text.see('end')

root = ctk.CTk()
root.title("OPTCG Data Fetcher")
root.geometry("500x600")

# CardList URL Input
frame_url = ctk.CTkFrame(root)
frame_url.pack(padx=10, pady=5, fill='x')
ctk.CTkLabel(frame_url, text="CardList URL:").pack(side='left')
url_entry = ctk.CTkEntry(frame_url, width=350)
url_entry.pack(side='left', padx=5)
url_entry.insert(0, "https://asia-en.onepiece-cardgame.com/cardlist/?series=556108")

# Save JSON Path Input
frame_file = ctk.CTkFrame(root)
frame_file.pack(padx=10, pady=5, fill='x')
ctk.CTkLabel(frame_file, text="Save JSON to:").pack(side='left')
file_entry = ctk.CTkEntry(frame_file, width=250)
file_entry.pack(side='left', padx=5)
file_entry.insert(0, "OPTCG_cards.json")
ctk.CTkButton(
    frame_file,
    text="Browse",
    command=lambda: (file_entry.delete(0, 'end'), file_entry.insert(0, filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')])))
).pack(side='left', padx=5)

# Buttons Frame
frame_btn = ctk.CTkFrame(root)
frame_btn.pack(padx=10, pady=10)

ctk.CTkButton(
    frame_btn,
    text="Fetch & Save",
    command=lambda: threading.Thread(
        target=lambda: save_to_json(get_card_list_from_website(url_entry.get()), file_entry.get())
    ).start()
).pack(side='left', padx=5)

ctk.CTkButton(
    frame_btn,
    text="Download Images",
    command=lambda: threading.Thread(
        target=lambda: download_images(
            get_card_list_from_website(url_entry.get()),
            Path(file_entry.get()).stem
        )
    ).start()
).pack(side='left', padx=5)

ctk.CTkButton(
    frame_btn,
    text="Batch Save",
    command=lambda: threading.Thread(target=batch_save).start()
).pack(side='left', padx=5)

ctk.CTkButton(
    frame_btn,
    text="Stop",
    command=lambda: stop_event.set()
).pack(side='left', padx=5)

# Progress and Output
frame_prog = ctk.CTkFrame(root)
frame_prog.pack(padx=10, pady=10, fill='both', expand=True)

progress_bar = ctk.CTkProgressBar(frame_prog, width=400)
progress_bar.pack(pady=(0,5))

output_text = ctk.CTkTextbox(frame_prog, height=200)
output_text.pack(fill='both', expand=True)
output_text.insert('0.0', '')

root.mainloop()
