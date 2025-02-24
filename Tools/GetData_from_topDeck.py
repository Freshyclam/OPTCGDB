import requests
from bs4 import BeautifulSoup
import re
import sys

# 確保 stdout 使用 UTF-8 編碼
sys.stdout.reconfigure(encoding='utf-8')

def extract_decklist_from_url(url):
    if not url.startswith("http"):
        return "錯誤：請提供有效的 URL，例如 'https://example.com'"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 403:
        return "403 Forbidden: 伺服器拒絕訪問，請嘗試其他方法"
    elif response.status_code != 200:
        return f"請求失敗，狀態碼: {response.status_code}"
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 嘗試找到包含牌組資訊的區塊
    target_element = soup.select("article div:nth-of-type(2) div:nth-of-type(2) div:nth-of-type(2) div b:nth-of-type(2) b div")
    
    if not target_element:
        return "未找到對應的元素"
    
    text_content = target_element[0].get_text(strip=True)
    
    # 使用正則表達式提取牌組信息
    pattern = re.findall(r'\d+x[A-Z0-9-]+', text_content)
    
    return pattern

# **請輸入一個有效的網址**
url = "https://onepiecetopdecks.com/deck-list/japan-op-10-the-royal-bloodline-decks/deckgen/"

decklist = extract_decklist_from_url(url)

# 輸出結果
if isinstance(decklist, list):
    for card in decklist:
        print(card)
else:
    print(decklist)
