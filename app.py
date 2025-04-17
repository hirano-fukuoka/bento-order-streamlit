
import streamlit as st
import pandas as pd
from datetime import datetime, time

# データ保存用ファイル
ORDER_FILE = "orders.csv"
MENU = ["からあげ弁当", "さば弁当", "日替わり弁当"]
DEADLINE = time(10, 30)  # 締切 10:30

# 初期化
st.set_page_config(page_title="弁当注文アプリ", layout="centered")
st.title("🍱 社内弁当注文システム")

# 社員情報入力
st.sidebar.header("👤 ログイン")
employee_id = st.sidebar.text_input("社員番号", max_chars=10)
employee_name = st.sidebar.text_input("名前")

if employee_id and employee_name:
    st.success(f"{employee_name} さん、こんにちは！")

    now = datetime.now().time()
    if now > DEADLINE:
        st.error("⚠️ 注文締切を過ぎています。")
    else:
        st.subheader("📋 本日のメニュー")
        menu_choice = st.radio("弁当を選択してください", MENU)
        quantity = st.number_input("個数", min_value=1, max_value=5, value=1)

        if st.button("✅ 注文する"):
            order = {
                "社員番号": employee_id,
                "名前": employee_name,
                "メニュー": menu_choice,
                "個数": quantity,
                "注文時刻": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                df = pd.read_csv(ORDER_FILE)
                df = pd.concat([df, pd.DataFrame([order])], ignore_index=True)
            except FileNotFoundError:
                df = pd.DataFrame([order])
            df.to_csv(ORDER_FILE, index=False)
            st.success("✅ 注文が完了しました！")

    # 注文履歴
    st.subheader("📚 今日の注文履歴")
    try:
        df = pd.read_csv(ORDER_FILE)
        today = datetime.now().strftime("%Y-%m-%d")
        df_today = df[df["注文時刻"].str.startswith(today)]
        df_today_user = df_today[df_today["社員番号"] == employee_id]
        if not df_today_user.empty:
            st.table(df_today_user)
        else:
            st.info("まだ注文がありません。")
    except FileNotFoundError:
        st.info("まだ注文がありません。")
else:
    st.warning("左のサイドバーからログインしてください。")
