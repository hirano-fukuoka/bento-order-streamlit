import streamlit as st
import pandas as pd
import pytz
from datetime import datetime, time

ORDER_FILE = "orders.csv"
MENU = ["からあげ弁当", "さば弁当", "日替わり弁当"]
JST = pytz.timezone('Asia/Tokyo')
now_japan = datetime.now(JST).time()
DEADLINE = time(9, 30)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "mkk-bento"

st.set_page_config(page_title="弁当注文アプリ", layout="centered")

def show_user_view():
    st.title("🍱 社内弁当注文システム")

    st.sidebar.header("👤 ログイン")
    employee_id = st.sidebar.text_input("社員番号", max_chars=10)
    employee_name = st.sidebar.text_input("名前")

    if employee_id and employee_name:
        st.success(f"{employee_name} さん、こんにちは！")
        now = datetime.now().time()

        if now_japan > DEADLINE:
            st.error("⚠️ 注文締切（9:30）を過ぎています。")
        else:
            # 注文フォーム表示
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

def show_admin_view():
    st.title("🛠 管理者パネル")

    st.subheader("📦 本日の全注文一覧")
    try:
        df = pd.read_csv(ORDER_FILE)
        today = datetime.now().strftime("%Y-%m-%d")
        df_today = df[df["注文時刻"].str.startswith(today)]
        st.dataframe(df_today)
    except FileNotFoundError:
        st.info("本日の注文はまだありません。")

st.sidebar.title("モード選択")
mode = st.sidebar.radio("アプリモードを選択", ["ユーザー", "管理者"])

if mode == "ユーザー":
    show_user_view()
else:
    st.sidebar.subheader("🔑 管理者ログイン")
    username = st.sidebar.text_input("ユーザー名")
    password = st.sidebar.text_input("パスワード", type="password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        show_admin_view()
    elif username and password:
        st.sidebar.error("認証に失敗しました。")

