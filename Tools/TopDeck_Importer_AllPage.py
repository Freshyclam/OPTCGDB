
import json
import re
import os
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading

# === Configurable paths ===
html_path = r"C:/Users/USER/Desktop/OPTCG_TopDeck/aaa.htm"
topdeck_path = "D:/Github/OPTCGDB/TopDeck_2025.json"
reference_path = "D:/Github/OPTCGDB/All_Data_EN.json"

# === Logging function for GUI ===
def log(msg):
    log_area.config(state='normal')
    log_area.insert(tk.END, msg + "\n")
    log_area.see(tk.END)
    log_area.config(state='disabled')

# === Core JSON Functions ===
def process_deck_data(deck, leader_color_map):
    if "deckDate" in deck:
        try:
            original_date = deck["deckDate"]
            formatted_date = datetime.strptime(original_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            deck["deckDate"] = formatted_date
        except ValueError:
            log(f"[WARNING] Invalid date format: {deck['deckDate']}")
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

def extract_deck_links_from_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True) if "deckgen?" in a["href"]]
    return list(set(links))

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def remove_duplicates(data):
    unique = []
    seen = set()
    for entry in data:
        key = json.dumps(entry, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(entry)
    return unique

def sort_by_deck_date(data):
    def get_date(entry):
        try:
            return datetime.strptime(entry.get("deckDate", "1900-01-01"), "%Y-%m-%d")
        except ValueError:
            return datetime.strptime("1900-01-01", "%Y-%m-%d")
    return sorted(data, key=get_date, reverse=True)

# === Batch Processing with Logging ===
def batch_process(deck_links, json_data, reference_data):
    leader_color_map = {e["id"]: e["color"] for e in reference_data if "id" in e and "color" in e}
    for url in deck_links:
        try:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)

            author = params.get("au", [""])[0]
            date = params.get("date", [""])[0]
            country = params.get("cn", [""])[0]
            tournament = params.get("tn", [""])[0]
            placement = params.get("pl", [""])[0]
            host = params.get("hs", [""])[0]
            dg = params.get("dg", [""])[0]

            decklist = re.findall(r"(\d+)n([A-Z0-9\-]+)", dg)
            if not decklist:
                log(f"[WARNING] Could not parse decklist: {url}")
                continue

            leader_id = decklist[0][1]
            members = []
            for count, card_id in decklist:
                count = int(count)
                ref = next((x for x in reference_data if x.get("id") == card_id), None)
                if ref:
                    members.append({
                        "memberCatalog": ref.get("card_catalog", "Unknown"),
                        "memberCost": ref.get("life", "Unknown"),
                        "memberCount": count,
                        "memberID": card_id,
                        "name": ref.get("card_name", card_id)
                    })
                else:
                    members.append({
                        "memberCatalog": "Unknown",
                        "memberCost": "Unknown",
                        "memberCount": count,
                        "memberID": card_id,
                        "name": card_id
                    })

            new_deck = {
                "deckOwner": author,
                "deckFrom": country,
                "placement": placement,
                "tournament": tournament,
                "host": host,
                "deckDate": date,
                "leader": leader_id,
                "deckColor": "Unknown",
                "leaderID": leader_id,
                "deckName": f"{leader_id}_{date}_{author}",
                "members": members
            }

            new_deck = process_deck_data(new_deck, leader_color_map)
            json_data.insert(0, new_deck)
            log(f"[ADDED] {new_deck['deckName']}")

        except Exception as e:
            log(f"[ERROR] Failed to process: {url}\n{e}")

    return json_data

# === Main Process Trigger ===
def run_batch_process():
    try:
        if not os.path.exists(html_path):
            log("[ERROR] Cannot find HTML file.")
            return

        log("[INFO] Extracting deck links...")
        deck_links = extract_deck_links_from_html(html_path)
        log(f"[INFO] Found {len(deck_links)} deck links.")

        json_data = load_json(topdeck_path)
        reference_data = load_json(reference_path)

        log("[INFO] Processing deck entries...")
        json_data = batch_process(deck_links, json_data, reference_data)

        log("[INFO] Removing duplicates...")
        json_data = remove_duplicates(json_data)

        log("[INFO] Sorting by deck date...")
        json_data = sort_by_deck_date(json_data)

        save_json(topdeck_path, json_data)
        log("[SUCCESS] TopDeck JSON updated.\n")

    except Exception as e:
        log(f"[FATAL ERROR] {e}")

def run_in_thread():
    threading.Thread(target=run_batch_process).start()

# === GUI Setup ===
gui = tk.Tk()
gui.title("One Piece Deck Batch Importer")
gui.geometry("800x600")

tk.Label(gui, text="One Piece Deck Batch Importer", font=("Arial", 16)).pack(pady=10)

tk.Button(gui, text="Start Processing", command=run_in_thread, height=2, width=20).pack(pady=10)

log_area = scrolledtext.ScrolledText(gui, width=100, height=25, state='disabled', font=("Consolas", 10))
log_area.pack(padx=10, pady=10)

gui.mainloop()
