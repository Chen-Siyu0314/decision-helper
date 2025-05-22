# decision-helper.py（最終升級整合版 + 多情境推薦產生器 + UX 強化）by 思宇
#.\.venv\Scripts\activate
#streamlit run operation/decision-helper.py

import streamlit as st
import random
import json
import os
from collections import Counter
import matplotlib.pyplot as plt
from gtts import gTTS
from io import BytesIO

def play_tts(text):
    tts = gTTS(text=text, lang="zh-tw")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    st.audio(mp3_fp.getvalue(), format="audio/mp3")

st.set_page_config(page_title="選擇困難救星", page_icon="🎯", layout="centered")
# 顯示圖片
st.image("operation/cute_decision_image.png", caption="選擇困難症日常", use_container_width=True)

# ========== 偏好記錄初始化 ========== #
log_file = "choice_log.json"
if not os.path.exists(log_file):
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)

with open(log_file, "r", encoding="utf-8") as f:
    history_preferences = json.load(f)

# ========== 關鍵字對照表 ========== #
mood_keywords = {
    "下雨": ["室內", "避雨", "不濕"],
    "懶": ["外送", "免出門", "省力"],
    "想放鬆": ["泡湯", "按摩", "靜"],
    "壓力大": ["健身", "跑步", "散步"],
    "孤單": ["朋友", "社交"]
}

purpose_keywords = {
    "學習 📚": ["圖書館", "閱讀", "自修", "咖啡廳"],
    "吃東西 🍽": ["火鍋", "餐廳", "外送", "甜點"],
    "放鬆 🧘": ["泡湯", "躺著", "靜"],
    "購物 🛍": ["百貨", "逛街"],
    "約會 ❤️": ["景點", "夜景", "浪漫"],
    "運動 🏃": ["跑步", "健身", "打球"],
    "社交 🗣": ["朋友", "聚會", "聊天"],
    "打發時間 ⏳": ["YouTube", "閒晃", "遊戲"],
    "看電影 📽": ["電影院", "影城", "沙發"],
    "玩遊戲 🎮": ["LOL", "Switch", "電玩"]
}

# ========== 詳細推薦理由資料庫（多情境） ========== #
detail_reasons = {
    "圖書館": "適合需要集中精神準備考試，安靜、儀式感強。",
    "咖啡廳": "有氛圍，適合輕鬆學習或放鬆，但有時較吵雜。",
    "家裡": "方便但容易分心，缺乏明確界線與儀式感。",
    "泡湯": "幫助舒壓、放鬆身心，適合壓力大或天氣冷的時候。",
    "跑步": "簡單執行的運動方式，有助情緒釋放，但需注意天氣。",
    "打球": "社交型運動，能增進互動，但需他人配合。",
    "健身": "自主調整強度，有效率排解壓力。",
    "朋友聚會": "適合社交需求，但若不想互動會造成壓力。",
    "外送": "快速、省力，適合懶惰或不想出門的狀態。",
    "百貨公司": "逛街購物、打發時間，適合想刺激一下的人。",
    "夜景": "浪漫適合約會，提升氛圍但需外出與安排。",
    "電影院": "沉浸式放鬆方式，適合想轉換情緒、無人打擾。",
    "唱歌": "適合宣洩情緒、團體活動，但音量大不適合靜態狀態。",
    "聽音樂": "可單獨進行，調節情緒，輕鬆自在無壓力。",
    "看書": "適合安靜時光，自我充實、深度放鬆。",
    "冥想": "重視內在平靜，幫助睡眠與情緒調節。",
    "打掃房間": "轉移注意力並創造整潔環境，適合焦躁時。",
    "滑手機": "快速打發時間，但長時間可能感到空虛。",
    "看Netflix": "視覺放鬆、劇情沉浸，適合疲累想放空時。",
    "看YouTube": "輕鬆、自由切換內容，適合零碎時間放鬆。",
    "購物網站": "逛網拍轉換情緒，需控制衝動避免後悔。",
    "寫日記": "內在整理自我，適合壓力或情緒低落時。",
    "畫畫": "創意釋放，適合情緒累積、需要出口時。",
    "手作DIY": "專注治癒系活動，慢節奏放鬆心情。",
    "做甜點": "過程有成就感，適合療癒自己也能分享。",
    "看展覽": "文青放鬆方式，適合獨處或靜態社交。",
    "去夜市": "熱鬧有吃有逛，適合打發時間或朋友聚會。",
    "桌遊": "多人互動、建立連結，適合朋友聚會但需人多。",
    "野餐": "與自然接觸的輕社交，適合天氣好、有空閒時。",
    "打工": "轉換環境、有收入感，適合想讓自己更有掌控感時。",
    "面試準備": "提升自信，強迫自己聚焦目標導向。",
    "寫企劃": "需要集中與動腦，適合早上或能量高時。",
    "報名課程": "給自己明確目標與學習節奏，避免茫然。",
    "發呆": "什麼都不做也很好，給自己完全放空的時間。",
    "看日出": "療癒又有儀式感，適合重新出發或低落時。",
    "逛誠品": "人文空間安靜，適合放鬆與靈感刺激。",
    "下棋": "動腦靜態互動，適合宅在家又不想滑手機時。",
    "修圖": "創意輸出與專注結合，適合晚上的靜態時間。",
    "編輯影片": "高集中力，適合全身心投入想忘記煩惱時。",
    "逛植物園": "親近自然、有助緩解焦躁。",
    "逛超市": "小採買可帶來控制感與生活儀式感。",
    "看卡通": "回到童心、放下壓力、適合心累但又不想空白時。",
    "寫信": "對自己或他人抒發，文字療癒感十足。",
    "泡腳": "居家舒壓妙招，幫助身心放鬆與睡眠。",
    "看老照片": "懷舊帶來溫暖回憶，適合內在疲憊時。",
    "做菜": "動手又動腦，適合情緒波動大或想掌控生活節奏時。",
    "曬太陽": "補充能量、提升心情，簡單有效的自然療癒。",
    "玩手遊": "可快可慢、節奏自由，適合片刻逃避。",
    "躺床耍廢": "完全放空、暫時對抗壓力感，適合極度懶或低潮期。",
    "去誠品晃晃": "結合人文書香與空間放鬆，適合低壓狀態恢復。",
    "找人聊天": "人際陪伴舒緩壓力，適合孤單或心事壓抑時。",
    "背英文單字": "短期強制集中，有目標的小挑戰，適合空虛時轉移注意。"
}

# ========== 核心分析 ========== #
def analyze_choices(options, mood, purpose, reason_text):
    scores = {}
    details = {}
    filtered_options = []

    for option in options:
        if "下雨" in mood and any(word in option for word in ["跑步", "登山", "露營"]):
            continue
        if "不想社交" in reason_text and any(word in option for word in ["聚會", "朋友", "聯誼"]):
            continue

        base = history_preferences.get(option, 3)
        mood_bonus = sum(1 for k in mood_keywords if k in mood and any(word in option for word in mood_keywords[k]))
        purpose_bonus = sum(1 for word in purpose_keywords.get(purpose, []) if word in option)
        reason_bonus = sum(1 for word in reason_text.split() if word in option)
        total = base + mood_bonus + purpose_bonus + reason_bonus + random.uniform(-0.5, 0.5)

        scores[option] = total
        details[option] = {
            "base": base,
            "mood_bonus": mood_bonus,
            "purpose_bonus": purpose_bonus,
            "reason_bonus": reason_bonus
        }
        filtered_options.append(option)

    best = max(scores, key=scores.get) if scores else "（無推薦）"
    return best, scores, details, filtered_options

# ========== 儲存紀錄 ========== #
def update_history(choice):
    history_preferences[choice] = history_preferences.get(choice, 0) + 1
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history_preferences, f, indent=2, ensure_ascii=False)

# ========== UI介面開始 ========== #
st.title("🎯 選擇困難救星")

purpose = st.selectbox("你的主要目的：", list(purpose_keywords.keys()))
mood = st.text_input("你現在的心情是？")
reason = st.text_area("做這個選擇的背景 / 原因")
options_input = st.text_area("請輸入選項（用逗號分隔）：", placeholder="如：跑步, 泡湯, 打電動")

if st.button("幫我選！"):
    options = [opt.strip() for opt in options_input.split(",") if opt.strip()]
    if not options:
        st.warning("請輸入至少一個選項")
    else:
        choice, scores, details, filtered = analyze_choices(options, mood, purpose, reason)
        if choice != "（無推薦）":
            update_history(choice)
            st.success(f"✅ 推薦你選擇：**{choice}**")
            tts_text = f"推薦你選擇 {choice}，因為：{detail_reasons.get(choice, '這項選擇最適合你目前的情境。')}"
            play_tts(tts_text)

            # ========== 升級推薦說明區 ========== #
            st.markdown("---")
            st.markdown("### 🧠 推薦原因")

            st.markdown(f"你提到「**{reason}**」，當下心情是「**{mood}**」，目的是「**{purpose}**」。\n\n")

            st.markdown("我們根據你的需求分析各選項如下：")
            for opt in filtered:
                line = f"🔹 **{opt}**：{detail_reasons.get(opt, '此選項相關程度中等，依情況可考慮。')}"
                if opt == choice:
                    st.markdown(f"✅ {line} **→ 最推薦**")
                else:
                    st.markdown(f"❌ {line} **→ 不推薦**")

            st.markdown("\n🧠 綜合判斷，我們認為 **{choice}** 最能對應你目前的狀況與需求。")

            # ========== 星等評比表格 ========== #
            st.markdown("---")
            st.markdown("### 🌟 各選項推薦程度")
            table_data = []
            for opt in filtered:
                score = scores[opt]
                star = "⭐️" * int(round(min(score, 5)))
                reason_str = []
                if details[opt]["purpose_bonus"] > 0:
                    reason_str.append("符合主要目的")
                if details[opt]["mood_bonus"] > 0:
                    reason_str.append("貼近你目前心情")
                if details[opt]["reason_bonus"] > 0:
                    reason_str.append("與你的描述相關")
                table_data.append(f"**{opt}** ｜ {star} ｜ {', '.join(reason_str) if reason_str else '關聯較少'}")

            for row in table_data:
                st.markdown(row)

# ========== 歷史推薦紀錄圖表 ========== #
if st.checkbox("📊 查看我最常被推薦的選項圖表"):
    if history_preferences:
        st.markdown("### 🔁 歷史推薦次數")
        count = Counter(history_preferences)
        st.bar_chart(count)
    else:
        st.info("目前還沒有累積推薦紀錄喔～")

# ========== UX 回饋互動 ========== #
st.markdown("---")
st.subheader("🎈 我接受這個選擇！")

if st.button("✅ 這就是我的選擇！"):
    st.success("太棒了！選擇不是問題，是認識自己的開始！✨")
    st.balloons()
    st.markdown("📜 **「每一次決定，都是更靠近目標的一步。」**")
    st.markdown("🧠 **「你不是選最對的，而是選最適合當下的自己。」**")

# ========== 創新互動遊戲 ========== #
st.markdown("---")
st.subheader("🕹️ 你來猜猜我會推薦什麼？")

game_options_input = st.text_area("請輸入幾個選項來讓我預測（逗號分隔）", placeholder="例如：咖啡廳, 圖書館, 跑步, 看Netflix")
user_guess = st.text_input("你覺得我會選哪一個？")

if st.button("🎯 讓我來預測！"):
    game_opts = [x.strip() for x in game_options_input.split(",") if x.strip()]
    if not game_opts:
        st.warning("請先輸入選項喔！")
    else:
        guess_result = random.choice(game_opts)
        st.markdown(f"🤖 我預測的選項是：**{guess_result}**")
        if user_guess.strip() == guess_result:
            st.success("🎉 猜對啦！我們想的一樣！")
        else:
            st.info("🙈 可惜猜錯了，不過每個選擇都值得試試！")

st.caption("🧠 by 思宇｜從目的、心情與背景出發，做出有邏輯的推薦")
