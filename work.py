# work.py（最終升級整合版 + 插圖點綴 + UX 強化）by 思宇

import streamlit as st
import random
import json
import os
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="萬用選擇困難救星", page_icon="🎯", layout="centered")
st
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
    "孤單": ["朋友", "社交"],
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
st.title("🎯 萬用選擇困難救星")

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

            st.markdown("---")
            st.markdown("### 🧠 推薦原因（自然語言說明）")
            st.write(f"你現在的目的為「{purpose}」，心情是「{mood}」，又提到「{reason}」，\n所以我們推薦你選擇 **{choice}**，因為它能夠滿足你此刻的需求，並且避免了其他選項的限制與不便。")

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