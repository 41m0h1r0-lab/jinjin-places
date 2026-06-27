import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from PIL import Image, ImageOps

# ページの設定
st.set_page_config(page_title="韓国聖地巡礼 2026", layout="wide", page_icon="✈️")

st.title("✈️ 2026.05 韓国聖地巡礼メモリーズ ✨")
st.write("CSVデータから自動で読み込んだ聖地巡礼の記録です。")

# 📸 画像の回転を自動で正しい向きに直す関数
def open_corrected_image(image_path):
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    return img

# -----------------------------------------------------------------------------
# 1. データの読み込みと写真パスの自動生成
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_process_data():
    # 同一フォルダ内のCSVファイルを読み込む
    csv_path = "korea_places.csv"
    
    if not os.path.exists(csv_path):
        st.error(f"CSVファイルが見つかりません。 '{csv_path}' という名前でスクリプトと同じフォルダに配置してください。")
        st.stop()
        
    df = pd.read_csv(csv_path)
    
    # 写真の相対パス（アプリのフォルダ内に配置したフォルダ名に指定）
    base_dir = "202605korea"
    
    # 規則性に基づいて写真パスを自動生成
    df["my_img"] = df.apply(lambda row: os.path.join(base_dir, f"my_{row['Number']}_{row['Name'].lower()}.jpg"), axis=1)
    df["oshi_img"] = df.apply(lambda row: os.path.join(base_dir, f"oshi_{row['Number']}_{row['Name'].lower()}.jpg"), axis=1)
    
    # セレクトボックスに表示する用の文字（No.1: タイトル名）
    df["display_select"] = df.apply(lambda row: f"No.{row['Number']}: {row['Title']}", axis=1)
    
    return df

df = load_and_process_data()

# -----------------------------------------------------------------------------
# 2. 地図セクション
# -----------------------------------------------------------------------------
st.header("🗺️ 聖地マップ")

# 最初の聖地を中心に地図を初期化
m = folium.Map(location=[df.iloc[0]["Latitude"], df.iloc[0]["Longitude"]], zoom_start=13)

for idx, row in df.iterrows():
    popup_text = f"<b>No.{row['Number']}: {row['Title']}</b><br><small>{row['Address']}</small>"
    
    # 📍 地図上のアイコン（ピン）のカスタマイズ
    # color: red, pink, purple, orange などに変更可能
    # icon: info-sign, star, heart, cloud などに変更可能
    custom_icon = folium.Icon(color="pink", icon="star", prefix="glyphicon")
    
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row["Title"],
        icon=custom_icon  # 👈 カスタマイズしたアイコンを適用！
    ).add_to(m)

st_folium(m, width="100%", height=500)

st.write("---")

# -----------------------------------------------------------------------------
# 3. 聖地詳細セクション
# -----------------------------------------------------------------------------
st.header("📸 聖地詳細・写真比較")

selected_display = st.selectbox("確認したい聖地を選択してください：", df["display_select"])
selected_place = df[df["display_select"] == selected_display].iloc[0]

# 詳細表示
st.subheader(f"📍 {selected_place['Title']}")
st.markdown(f"**住所:** `{selected_place['Address']}`")

# 👈 メッセージを表示（CSVの「Message」カラムから自動取得）
# もしCSVが空欄（NaN）の場合は「思い出を書き込みましょう！」と表示
if pd.isna(selected_place["Message"]):
    st.info("💡 ここに当日の思い出や推しへの愛を語る文を差し込めます。")
else:
    st.info(f"💬 **思い出メモ:** \n{selected_place['Message']}")

st.write("")

# 2カラムで写真を横並び表示
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎬 推し（公式アングル）")
    if os.path.exists(selected_place["oshi_img"]):
        oshi_img_corrected = open_corrected_image(selected_place["oshi_img"])
        st.image(oshi_img_corrected, use_container_width=True)
    else:
        st.warning(f"画像が見つかりません: {os.path.basename(selected_place['oshi_img'])}")

with col2:
    st.markdown("### 📷 私が撮影した写真")
    if os.path.exists(selected_place["my_img"]):
        my_img_corrected = open_corrected_image(selected_place["my_img"])
        st.image(my_img_corrected, use_container_width=True)
    else:
        st.warning(f"画像が見つかりません: {os.path.basename(selected_place['my_img'])}")