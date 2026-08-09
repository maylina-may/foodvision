# ==========================================
# IMPORT LIBRARY
# ==========================================

import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import cv2
import io
import base64
import matplotlib.pyplot as plt

from modelfoodvision import detect_food
from api_llm import get_nutrition, get_nutrition_dataframe

# ==========================================
# LOGO 
# ==========================================

def get_logo_b64():
    with open("assets/logo.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"

LOGO_B64 = get_logo_b64()

# ==========================================
# MAPPING EMOJI MAKANAN
# ==========================================

FOOD_EMOJI = {
    "Ayam Goreng": "🍗",
    "Mie Ayam": "🍜",
    "Nasi Putih": "🍚",
    "Pempek": "🥟",
    "Rendang": "🍛",
    "Sambal": "🌶️",
    "Sate": "🍢",
    "Soto": "🍲",
    "Tahu Goreng": "🧈",
    "Tempe Goreng": "🧆",
}

def get_food_emoji(name):
    return FOOD_EMOJI.get(name.title(), "🍽️")

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================

st.set_page_config(
    page_title="Food Vision",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# STYLING CSS 
# ==========================================

st.markdown(
    """
    <style>
        /* ====== GLOBAL ====== */
        .stApp {
            background: linear-gradient(180deg, #FFFDFD 0%, #FFF7F8 50%, #FDEFF2 100%);
        }

        .stMarkdown, .stMarkdown p, .stMarkdown li {
            color: #2D2D2D !important;
        }

        /* ====== SIDEBAR (PINK TUA) ====== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #E86A9C 0%, #D94A7F 55%, #B93368 100%);
            border-right: 1px solid rgba(255,255,255,0.3);
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.25);
        }

        .sidebar-logo {
            display: flex;
            justify-content: center;
            margin-bottom: 0.5rem;
        }

        .sidebar-logo img {
            border-radius: 50%;
            box-shadow: 0 8px 24px rgba(232,93,133,0.45);
            border: 3px solid rgba(255,255,255,0.8);
        }

        .sidebar-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0.2rem;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }

        .sidebar-subtitle {
            text-align: center;
            font-size: 0.85rem;
            color: #FFFFFF;
            font-weight: 600;
            margin-bottom: 0.8rem;
            text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }

        .sidebar-info {
            background: rgba(255,255,255,0.25);
            border-left: 4px solid #FFFFFF;
            border-radius: 10px;
            padding: 0.7rem 0.9rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            line-height: 1.55;
            color: #FFFFFF;
            font-weight: 500;
            backdrop-filter: blur(4px);
        }

        .food-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.28);
            border: 1px solid rgba(255,255,255,0.5);
            border-radius: 999px;
            padding: 4px 12px;
            margin: 3px 3px;
            font-size: 0.78rem;
            font-weight: 700;
            color: #FFFFFF;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }

        .food-chip:hover {
            background: rgba(255,255,255,0.45);
            border-color: #FFFFFF;
            transform: translateY(-1px);
            cursor: default;
        }

        .sidebar-section-title {
            font-size: 0.95rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-top: 0.4rem;
            margin-bottom: 0.3rem;
            letter-spacing: 0.3px;
            text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }

        .sidebar-footer {
            text-align: center;
            font-size: 0.75rem;
            color: #FFFFFF;
            font-weight: 600;
            margin-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.35);
            padding-top: 0.8rem;
        }

        /* ====== HERO BANNER (Main) ====== */
        .hero-banner {
            background: linear-gradient(135deg, #E86A9C 0%, #D94A7F 50%, #B93368 100%);
            border-radius: 20px;
            padding: 2rem 2rem;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(185,51,104,0.35);
            color: #FFFFFF;
        }

        .hero-banner img {
            border-radius: 50%;
            border: 4px solid rgba(255,255,255,0.9);
            box-shadow: 0 10px 30px rgba(232,93,133,0.5);
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin: 0.3rem 0;
            letter-spacing: 0.5px;
            text-shadow: 0 3px 10px rgba(232,93,133,0.4);
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: rgba(255,255,255,0.95);
            margin: 0 auto 0.8rem auto;
            max-width: 600px;
            line-height: 1.6;
        }

        /* ====== KARTU INFO ====== */
        .info-card {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 1rem 1rem;
            text-align: center;
            box-shadow: 0 4px 14px rgba(232,93,133,0.18);
            border: 1px solid #FBD9E0;
            margin-bottom: 0.8rem;
        }

        .info-card .icon {
            font-size: 1.6rem;
        }

        .info-card .value {
            font-size: 1.3rem;
            font-weight: 800;
            color: #E85D85;
            margin: 0.2rem 0;
        }

        .info-card .label {
            font-size: 0.8rem;
            color: #8A6A75;
            font-weight: 600;
        }

        /* ====== JUDUL UTAMA ====== */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #B93368 !important;
            font-weight: 800 !important;
        }

        .stSubheader, .stMarkdown h3, .stMarkdown h2 {
            font-weight: 800 !important;
        }

        /* Tombol */
        .stButton > button {
            background: linear-gradient(135deg, #D94A7F, #B93368);
            color: #FFFFFF;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1.2rem;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px rgba(185,51,104,0.35);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(185,51,104,0.45);
            background: linear-gradient(135deg, #C93F75, #9E2B5B);
            color: #FFFFFF;
        }

        /* Radio */
        .stRadio > div {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 0.5rem;
            border: 1px solid #F0C3D0;
        }

        .stRadio label {
            color: #2D2D2D !important;
            font-weight: 600 !important;
        }

        /* Label upload / camera */
        .stFileUploader label, .stCameraInput label {
            color: #2D2D2D !important;
            font-weight: 600 !important;
        }

        .stFileUploader > div, .stCameraInput > div {
            border-radius: 12px;
            border: 2px dashed #E85D85 !important;
            background: rgba(255,255,255,0.7);
        }

/* Tengahkan gambar pratinjau & hasil deteksi agar berada di tengah */
[data-testid="stImage"] {
            display: flex;
            justify-content: center;
        }

[data-testid="stImage"] img {
            margin: 0 auto;
            max-width: 420px !important;
            max-height: 420px !important;
            width: auto !important;
            height: auto !important;
            object-fit: contain;
        }

        /* Ukuran kotak kamera dibuat proporsional & di tengah */
        [data-testid="stCameraInput"] video {
            max-width: 100% !important;
            max-height: 340px !important;
            object-fit: contain;
            margin: 0 auto;
        }

        [data-testid="stCameraInput"] {
            max-width: 520px;
            margin: 0 auto;
        }

/* Dataframe: cegah scroll horizontal agar tabel tidak bisa digeser */
        [data-testid="stDataFrame"] {
            overflow-x: hidden !important;
            width: 100% !important;
        }
        [data-testid="stDataFrame"] [data-testid="stElementContainer"] {
            overflow-x: hidden !important;
        }
        [data-testid="stDataFrame"] [data-testid="stDataFrameGlideColumn"] {
            overflow: hidden !important;
        }
        [data-testid="stDataFrame"] [data-testid="StyledDataFrameDataCell"] {
            white-space: nowrap;
        }
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #FBD9E0;
        }
        /* Rapatkan tabel deteksi objek agar tidak terlalu melebar */
        [data-testid="stDataFrame"] [data-testid="StyledDataFrameColumn"] {
            min-width: 0 !important;
        }
        [data-testid="stDataFrame"] [data-testid="StyledDataFrameDataCell"],
        [data-testid="stDataFrame"] [data-testid="StyledDataFrameColumnHeader"] {
            padding-left: 8px !important;
            padding-right: 8px !important;
        }

        /* ====== RESPONSIVE (MOBILE) ====== */
@media (max-width: 768px) {
            .hero-banner {
                padding: 1.2rem 1rem;
            }
            .hero-title {
                font-size: 1.5rem;
            }
            .hero-subtitle {
                font-size: 0.9rem;
            }
            .sidebar-logo img {
                width: 90px !important;
            }
/* Pratinjau & hasil deteksi: jangan terlalu besar di HP */
[data-testid="stImage"] img {
                max-width: 100% !important;
                max-height: 420px !important;
                width: auto !important;
                height: auto !important;
                object-fit: contain;
            }
            [data-testid="stImage"] {
                width: 100% !important;
            }
        }

        @media (max-width: 480px) {
            .hero-title {
                font-size: 1.3rem;
            }
            .info-card .value {
                font-size: 1.1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# LOAD MODEL YOLO
# ==========================================

@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

# ==========================================
# HEADER / HERO BANNER
# ==========================================

st.markdown(
    f"""
    <div class="hero-banner">
        <img src="{LOGO_B64}" width="120">
        <div class="hero-title">🍽️ Food Vision</div>
        <div class="hero-subtitle">
            Deteksi jenis makanan secara otomatis dan dapatkan informasi
            kandungan gizinya dengan mudah, cepat, dan akurat!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# KARTU INFO
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
<div class="info-card">
            <div class="icon">🍲</div>
            <div class="value">10</div>
            <div class="label">Jenis Makanan</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <div class="icon">🥗</div>
            <div class="value">Nutrisi</div>
            <div class="label">Kalori & Protein</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="info-card">
            <div class="icon">🧠</div>
            <div class="value">YOLOv11</div>
            <div class="label">Deep Learning</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    # Logo
    st.markdown(
        f"""
        <div class="sidebar-logo">
            <img src="{LOGO_B64}" width="110">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Judul & Subjudul
    st.markdown(
        """
<div class="sidebar-title">🍽️ Food Vision</div>
        <div class="sidebar-subtitle">Deteksi Makanan & Informasi Gizi</div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Informasi singkat
    st.markdown(
        """
        <div class="sidebar-info">
            <b>✨ Fitur:</b><br>
            🔎 Deteksi 10 jenis makanan<br>
            🥗 Kandungan gizi & kalori<br>
            📥 Unduh hasil deteksi
        </div>
        """,
        unsafe_allow_html=True
    )

    # Daftar kelas makanan
    st.markdown(
        """
        <div class="sidebar-section-title">🥗 Kelas Makanan</div>
        """,
        unsafe_allow_html=True
    )

    food_classes = [
        "🍗 Ayam Goreng", "🍜 Mie Ayam", "🍚 Nasi Putih",
        "🥟 Pempek", "🍛 Rendang", "🌶️ Sambal",
        "🍢 Sate", "🍲 Soto", "🧈 Tahu Goreng",
        "🧆 Tempe Goreng",
    ]

    chips_html = ""

    for food in food_classes:
        chips_html += f'<span class="food-chip">{food}</span>'

    st.markdown(
        f"""
        <div style="line-height:1.5;">
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Footer
    st.markdown(
        """
        <div class="sidebar-footer">
            Powered by Maylina 🔥
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# UPLOAD GAMBAR / AMBIL FOTO
# ==========================================

st.subheader("Upload Gambar atau Ambil Foto")

input_method = st.radio(
    "Pilih metode input",
    options=["📁 Upload Gambar", "📸 Ambil Foto"],
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)

image_byte = None
image_source = None
preview_image = None

# ==========================================
# UPLOAD GAMBAR
# ==========================================

if input_method == "📁 Upload Gambar":

    uploaded_file = st.file_uploader(
        "Upload Gambar",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        label_visibility="collapsed"
    )

    if uploaded_file is not None:

        image_bytes = uploaded_file.read()

        image_source = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        preview_image = image_source.copy()

        # Simpan ukuran gambar asli untuk menyamakan hasil deteksi
        st.session_state["preview_shape"] = (preview_image.size[1], preview_image.size[0])

        # Gambar baru diupload -> hapus hasil deteksi lama
        for key in ["hasil_gambar", "detected_objects", "hasil_llm"]:
            st.session_state.pop(key, None)

# ==========================================
# AMBIL FOTO
# ==========================================

else:
    camera_file = st.camera_input(
        "Ambil Foto",
        label_visibility="collapsed",
        key="camera_main"
    )

    if camera_file is not None:

        image_bytes = camera_file.read()

        image_source = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        preview_image = image_source.copy()

        # Simpan ukuran gambar asli untuk menyamakan hasil deteksi
        st.session_state["preview_shape"] = (preview_image.size[1], preview_image.size[0])

        # Foto baru diambil -> hapus hasil deteksi lama
        for key in ["hasil_gambar", "detected_objects", "hasil_llm"]:
            st.session_state.pop(key, None)

# ==========================================
# PREVIEW GAMBAR
# ==========================================

st.subheader("🖼️ Pratinjau Gambar")

if preview_image is not None:

    st.image(
        preview_image,
        caption="Pratinjau Gambar",
        width=420,
        use_container_width=False
    )

else:

    st.info("Silakan upload gambar atau ambil foto terlebih dahulu.")

# ==========================================
# TOMBOL DETEKSI GIZI
# ==========================================

deteksi = st.button(
    "🔎 Deteksi Gizi",
    type="primary",
    width="stretch"
)

st.divider()

# ==========================================
# PROSES DETEKSI
# ==========================================

if deteksi:

    if preview_image is None:

        st.warning("Silakan upload gambar atau ambil foto terlebih dahulu.")

    else:

        try:

            with st.spinner("Sedang mendeteksi makanan..."):
                hasil_gambar, detected_objects = detect_food(
                    np.array(preview_image)
                )

            # Simpan hasil ke session state agar tetap tampil
            st.session_state["hasil_gambar"] = hasil_gambar
            st.session_state["detected_objects"] = detected_objects

            # Siapkan data gizi
            food_list = []
            for obj in detected_objects:
                if obj["Nama"] not in food_list:
                    food_list.append(obj["Nama"])

            # Simpan food_list untuk visualisasi gizi
            st.session_state["food_list"] = food_list

            with st.spinner("Menganalisis kandungan gizi..."):
                hasil_llm = get_nutrition(food_list)

            st.session_state["hasil_llm"] = hasil_llm

        except Exception as e:

            st.error(f"Terjadi kesalahan : {e}")

# ==========================================
# TAMPILKAN HASIL DETEKSI (Jika sudah ada)
# ==========================================

if "hasil_gambar" in st.session_state:

    st.subheader("🎯 Hasil Deteksi")

    hasil_gambar = st.session_state["hasil_gambar"]
    detected_objects = st.session_state["detected_objects"]

    hasil_rgb = cv2.cvtColor(hasil_gambar, cv2.COLOR_BGR2RGB)

    # Resize hasil agar memiliki ukuran yang SAMA dengan gambar pratinjau
    if "preview_shape" in st.session_state:
        p_h, p_w = st.session_state["preview_shape"]
        hasil_rgb = cv2.resize(hasil_rgb, (p_w, p_h))

# Tampilkan gambar hasil dengan ukuran sama dengan pratinjau (420px)
    st.image(
        hasil_rgb,
        caption="Hasil Deteksi",
        width=420,
        use_container_width=False
    )

    # Tombol unduh
    _, buffer = cv2.imencode(".jpg", hasil_gambar)
    st.download_button(
        label="📥 Unduh Gambar Hasil",
        data=buffer.tobytes(),
        file_name="hasil_deteksi.jpg",
        mime="image/jpeg",
        width="stretch"
    )

    st.divider()

    # ==========================================
    # TABEL DETEKSI OBJEK
    # ==========================================

    st.subheader("📋 Deteksi Objek Terdeteksi")

    if len(detected_objects) == 0:

        st.warning("Tidak ada objek makanan yang berhasil dideteksi.")

    else:

        df_rows = []

        for i, obj in enumerate(detected_objects, start=1):

            emoji = get_food_emoji(obj["Nama"])

            # Ambil nilai dengan .get() agar aman jika data lama
            # tidak memiliki kolom "Confidence (%)"
            confidence_pct = obj.get("Confidence (%)", obj.get("Confidence", 0) * 100)

            df_rows.append({
                "No": i,
                "Makanan": f"{emoji} {obj['Nama']}",
                "Confidence (%)": round(confidence_pct, 1),
                "Luas (px²)": obj.get("Luas (px²)", 0),
                "Bounding Box": obj.get("Bounding Box", []),
            })

        df = pd.DataFrame(df_rows)

# Atur lebar kolom agar tabel tidak terlalu melebar / jarak antar kolom tidak jauh
        column_config = {
            "No": st.column_config.NumberColumn(
                "No",
                width="small",
            ),
            "Makanan": st.column_config.TextColumn(
                "Makanan",
                width="medium",
            ),
            "Confidence (%)": st.column_config.NumberColumn(
                "Confidence (%)",
                width="small",
            ),
            "Luas (px²)": st.column_config.NumberColumn(
                "Luas (px²)",
                width="small",
                help="Luas area bounding box dalam piksel persegi",
            ),
            "Bounding Box": st.column_config.TextColumn(
                "Bounding Box",
                width="medium",
            ),
        }

        st.dataframe(
            df,
            hide_index=True,
            column_config=column_config
        )

    st.divider()

    # ==========================================
    # KANDUNGAN GIZI
    # ==========================================

    st.subheader("🥗 Kandungan Gizi")

    if "hasil_llm" in st.session_state:
        st.markdown(
            st.session_state["hasil_llm"],
            unsafe_allow_html=False
        )

    # ==========================================
    # VISUALISASI DATA GIZI
    # ==========================================

    if "food_list" in st.session_state and st.session_state["food_list"]:

        st.markdown("")
        st.markdown("### 📊 Visualisasi Kandungan Gizi")

        # Buat konfigurasi matplotlib agar kuat menangani teks
        try:
            plt.rcParams["font.family"] = "DejaVu Sans"
        except Exception:
            pass

        # Ambil data terstruktur untuk visualisasi
        df_gizi = get_nutrition_dataframe(st.session_state["food_list"])

        if not df_gizi.empty:

            # --- BAR CHART KALORI ---
            st.markdown("**🔥 Perbandingan Kalori per Makanan**")

            fig1, ax1 = plt.subplots(figsize=(10, 6.5))
            labels = df_gizi["Nama Makanan"].tolist()
            kalori = df_gizi["Kalori"].tolist()

            colors = ["#E85D85", "#D94A7F", "#B93368",
                      "#F08AB0", "#C93F75", "#E86A9C",
                      "#D0608F", "#F2A0BD", "#B34A74", "#E98FB0"]

            bars = ax1.bar(labels, kalori, color=colors[:len(labels)],
                           edgecolor="white", linewidth=1.2)

            ax1.set_ylabel("Kalori (kkal/100 g)", fontsize=10)
            ax1.set_title("Kalori per Makanan (per 100 g)", fontsize=12, fontweight="bold")
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)

            # Tambahkan nilai di atas bar
            for bar, val in zip(bars, kalori):
                ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                         f"{int(val)}", ha="center", va="bottom", fontsize=9, fontweight="bold")

            plt.xticks(rotation=30, ha="right", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)

            # --- BAR CHART MAKRONUTRIEN (GROUPED) ---
            st.markdown("**🥩 Perbandingan Makronutrien (Protein, Lemak, Karbohidrat)**")

            fig2, ax2 = plt.subplots(figsize=(10, 6.5))

            x = np.arange(len(labels))  # posisi label
            width = 0.25  # lebar tiap bar

            protein = df_gizi["Protein"].tolist()
            lemak = df_gizi["Lemak"].tolist()
            karbo = df_gizi["Karbohidrat"].tolist()

            ax2.bar(x - width, protein, width, label="Protein", color="#E85D85", edgecolor="white")
            ax2.bar(x, lemak, width, label="Lemak", color="#F2A0BD", edgecolor="white")
            ax2.bar(x + width, karbo, width, label="Karbohidrat", color="#B93368", edgecolor="white")

            ax2.set_ylabel("Gram (g/100 g)", fontsize=10)
            ax2.set_title("Makronutrien per Makanan (per 100 g)", fontsize=12, fontweight="bold")
            ax2.set_xticks(x)
            ax2.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
            ax2.legend(fontsize=9)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)

            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
