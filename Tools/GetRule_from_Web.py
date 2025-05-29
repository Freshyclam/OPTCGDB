import sys
import requests
import json
from bs4 import BeautifulSoup

# 設置標準輸出的默認編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 指定多個 HTML 頁面的網址
urls = [
    #EB
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=EXTRA%20BOOSTER%20-Memorial%20Collection-%20[EB-01]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=EXTRA%20BOOSTER%20-Anime%2025th%20collection-%20[EB-02]",
    #OP
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-A%20Fist%20of%20Divine%20Speed-%20[OP-11]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Royal%20Blood-%20[OP-10]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Emperors%20in%20the%20New%20World-%20[OP-09]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Two%20Legends-%20[OP-08]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-500%20Years%20in%20the%20Future-%20[OP-07]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Wings%20of%20Captain-%20[OP-06]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Awakening%20of%20the%20New%20Era-%20[OP-05]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Kingdoms%20of%20Intrigue-%20[OP-04]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Pillars%20of%20Strength-%20[OP-03]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-Paramount%20War-%20[OP-02]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=BOOSTER%20PACK%20-ROMANCE%20DAWN-%20[OP-01]",
    #ST
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Ace%20%26%20Newgate-%20[ST-22]"
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20EX%20-GEAR5-%20[ST-21]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Yellow%20Charlotte%20Katakuri-%20[ST-20]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Black%20Smoker-%20[ST-19]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Purple%20Monkey.D.Luffy-%20[ST-18]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Blue%20Donquixote%20Doflamingo-%20[ST-17]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Green%20Uta-%20[ST-16]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Red%20Edward.Newgate-%20[ST-15]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-3D2Y-%20[ST-14]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=ULTIMATE%20DECK%20-The%20Three%20Brothers%27%20Bond-%20[ST-13]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Zoro%20%26%20Sanji-%20[ST-12]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Side%20Uta-%20[ST-11]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=ULTIMATE%20DECK%20-The%20Three%20Captains-%20[ST-10]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Side%20Yamato-%20[ST-09]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Side%20Monkey.D.Luffy-%20[ST-08]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Big%20Mom%20Pirates-%20[ST-07]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-The%20Navy-%20[ST-06]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-ONE%20PIECE%20FILM%20edition-%20[ST-05]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Animal%20Kingdom%20Pirates-%20[ST-04]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-The%20Seven%20Warlords%20of%20the%20Sea-%20[ST-03]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Worst%20Generation-%20[ST-02]",
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=STARTER%20DECK%20-Straw%20Hat%20Crew-%20[ST-01]",
    #PRB
    "https://asia-en.onepiece-cardgame.com/rules/qa.php?tab=cardqa&type=1&series=PREMIUM%20BOOSTER%20-ONE%20PIECE%20CARD%20THE%20BEST-%20[PRB-01]"
    
    # 可以繼續新增網址...
]

# 指定輸出 JSON 文件的路徑
output_path = "D:\Github\OPTCGDB\Rule.json"

# 初始化存儲所有 QA 數據的列表
qa_data = []

# 遍歷每個網址進行爬取
for url in urls:
    print(f"正在處理: {url}")

    # 嘗試獲取網頁內容
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
        html_content = response.text
    except requests.RequestException as e:
        print(f"錯誤：無法獲取網頁內容 - {e}")
        continue  # 如果某個網址無法訪問，跳過該網址

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # 提取 <dd class="qaTit">, <dl class="questions"> 和 <dl class="answer">
    qa_titles = soup.find_all("dd", class_="qaTit")
    questions = soup.find_all("dl", class_="questions")
    answers = soup.find_all("dl", class_="answer")

    # 確保三者數量一致
    if len(qa_titles) != len(questions) or len(qa_titles) != len(answers):
        print("警告：QA Titles、Questions 和 Answers 的數量不一致！可能導致輸出對應錯誤。")

    # 遍歷並處理每個 QA 項目
    for i in range(len(qa_titles)):
        # 移除 title 第一個空白後的所有內容
        id = qa_titles[i].get_text(strip=True).split(" ")[0]
        title_text = qa_titles[i].get_text(strip=True)

        # 處理問題文本，確保第一個 "Q" 變為 "Q: "
        question_text = questions[i].get_text(strip=True)
        if question_text.startswith("Q"):
            question_text = "Q: " + question_text[1:].strip()

        # 處理答案文本，確保第一個 "A" 變為 "A: "
        answer_text = answers[i].get_text(strip=True)
        if answer_text.startswith("A"):
            answer_text = "A: " + answer_text[1:].strip()

        # 過濾掉 title 為 "Booster" 的項目
        if title_text not in [
            "BOOSTER","STARTER DECK -Straw Hat Crew- [ST-01]",
            "STARTER DECK -Worst Generation- [ST-02]",
            "STARTER DECK -The Seven Warlords of the Sea- [ST-03]",
            "STARTER DECK -Animal Kingdom Pirates- [ST-04]",
            "STARTER DECK -ONE PIECE FILM edition- [ST-05]",
            "STARTER DECK -The Navy- [ST-06]",
            "STARTER DECK -Big Mom Pirates- [ST-07]",
            "STARTER DECK -Side Monkey.D.Luffy- [ST-08]",
            "STARTER DECK -Side Yamato- [ST-09]",
            "ULTIMATE DECK -The Three Captains- [ST-10]",
            "STARTER DECK -Side Uta- [ST-11]",
            "STARTER DECK -Zoro & Sanji- [ST-12]",
            "ULTIMATE DECK -The Three Brothers' Bond- [ST-13]",
            "STARTER DECK -3D2Y- [ST-14]",
            "STARTER DECK -Red Edward.Newgate- [ST-15]",
            "STARTER DECK -Green Uta- [ST-16]",
            "STARTER DECK -Blue Donquixote Doflamingo- [ST-17]",
            "STARTER DECK -Purple Monkey.D.Luffy- [ST-18]",
            "STARTER DECK -Black Smoker- [ST-19]",
            "STARTER DECK -Yellow Charlotte Katakuri- [ST-20]",
            "STARTER DECK EX -GEAR5- [ST-21]",
            "BOOSTER PACK -ROMANCE DAWN- [OP-01]",
            "BOOSTER PACK -Paramount War- [OP-02]",
            "BOOSTER PACK -Pillars of Strength- [OP-03]",
            "BOOSTER PACK -Kingdoms of Intrigue- [OP-04]",
            "BOOSTER PACK -Awakening of the New Era- [OP-05]",
            "BOOSTER PACK -Wings of Captain- [OP-06]",
            "BOOSTER PACK -500 Years in the Future- [OP-07]",
            "BOOSTER PACK -Two Legends- [OP-08]",
            "BOOSTER PACK -Emperors in the New World- [OP-09]",
            "BOOSTER PACK -Royal Blood- [OP-10]",
            "BOOSTER PACK -A Fist of Divine Speed- [OP-11]",
            "EXTRA BOOSTER -Memorial Collection- [EB-01]",
            "EXTRA BOOSTER -Anime 25th collection- [EB-02]",
                ]:
            qa_entry = {
                "id": id,
                "title": title_text,
                "question": question_text,
                "answer": answer_text,
            }
            qa_data.append(qa_entry)

# 檢查是否有數據需要寫入
if qa_data:
    # 將合併後的 JSON 數據寫入文件
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(qa_data, json_file, indent=4, ensure_ascii=False)

    print(f"提取結果已成功保存至 {output_path}")
else:
    print("沒有有效的數據可寫入 JSON 文件。")
