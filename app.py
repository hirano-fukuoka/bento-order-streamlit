import streamlit as st
import pandas as pd
from datetime import datetime, time
import pytz

# タイムゾーン設定（日本時間）
JST = pytz.timezone('Asia/Tokyo')

# 定数
ORDER_FILE = "orders.csv"
MENU_FILE = "menu.csv"  # メニュー設定ファイル
DEADLINE = time(9, 30)  # 日本時間9:30が締切
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "mkk-bento"

st.set_page_config(page_title="弁当注文アプリ", layout="centered")

# ====================
# ユーザー画面
# ====================
def show_user_view():
    st.title("🍱 社内弁当注文システム")

    st.sidebar.header("👤 ログイン")
    employee_id = st.sidebar.text_input("社員番号", max_chars=10)
    employee_name = st.sidebar.text_input("名前")

    if employee_id and employee_name:
        st.success(f"{employee_name} さん、こんにちは！")
        now_japan = datetime.now(JST)

        if now_japan.time() > DEADLINE:
            st.error("⚠️ 注文締切（9:30）を過ぎています。")
        else:
            # メニュー表示（画像付き）
            st.subheader("📋 本日のメニュー")
            menu_df = pd.read_csv(MENU_FILE)
            selected_bento = st.radio("弁当を選択してください", menu_df['メニュー名'].tolist(), format_func=lambda x: f"{x}")
            selected_bento_row = menu_df[menu_df['メニュー名'] == selected_bento].iloc[0]
            st.image(selected_bento_row['画像URL'], width=200)

            quantity = st.number_input("個数", min_value=1, max_value=5, value=1)

            if st.button("✅ 注文する"):
                order = {
                    "社員番号": employee_id,
                    "名前": employee_name,
                    "メニュー": selected_bento,
                    "個数": quantity,
                    "注文時刻": now_japan.strftime("%Y-%m-%d %H:%M:%S")
                }
                try:
                    df = pd.read_csv(ORDER_FILE)
                    df = pd.concat([df, pd.DataFrame([order])], ignore_index=True)
                except FileNotFoundError:
                    df = pd.DataFrame([order])
                df.to_csv(ORDER_FILE, index=False)
                st.success("✅ 注文が完了しました！")

        # 注文履歴の表示
        st.subheader("📚 今日の注文履歴")
        try:
            df = pd.read_csv(ORDER_FILE)
            today = now_japan.strftime("%Y-%m-%d")
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

# ====================
# 管理者画面
# ====================
def show_admin_view():
    st.title("🛠 管理者パネル")
    st.subheader("📦 本日の全注文一覧")
    try:
        df = pd.read_csv(ORDER_FILE)
        today = datetime.now(JST).strftime("%Y-%m-%d")
        df_today = df[df["注文時刻"].str.startswith(today)]
        st.dataframe(df_today)
    except FileNotFoundError:
        st.info("本日の注文はまだありません。")

    # メニュー編集機能
    st.subheader("🍱 メニュー管理")
    menu_df = pd.read_csv(MENU_FILE)

    edited_menu = []
    for index, row in menu_df.iterrows():
        new_name = st.text_input(f"弁当名 (ID: {row['メニューID']})", value=row['メニュー名'], key=f"{row['メニューID']}_name")
        new_image_url = st.text_input(f"画像URL (ID: {row['メニューID']})", value=row['画像URL'], key=f"{row['メニューID']}_image")

        edited_menu.append({
            'メニューID': row['メニューID'],
            'メニュー名': new_name,
            '画像URL': new_image_url
        })

    if st.button("📥 メニュー更新"):
        updated_menu_df = pd.DataFrame(edited_menu)
        updated_menu_df.to_csv(MENU_FILE, index=False)
        st.success("メニューが更新されました！")

# ====================
# アプリ起動部分
# ====================
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
