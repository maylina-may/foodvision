# ==========================================
# IMPORT LIBRARY
# ==========================================

import os
from groq import Groq
from dotenv import load_dotenv

# ==========================================
# LOAD API KEY
# ==========================================

# Muat .env untuk pengembangan lokal
load_dotenv()

# Ambil API key:
# 1. Dari environment variable (os.getenv)
# 2. Dari Streamlit Secrets (st.secrets) untuk deployment cloud
try:
    import streamlit as st
    _SECRETS_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    _SECRETS_KEY = ""

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or _SECRETS_KEY or ""

client = Groq(
    api_key=GROQ_API_KEY
) if GROQ_API_KEY else None

# ==========================================
# DATA GIZI STATIS (FALLBACK)
# ==========================================

NUTRITION_FALLBACK = {
    "Ayam Goreng": {"Kalori": 246, "Protein": 25, "Lemak": 15, "Karbohidrat": 2},
    "Mie Ayam": {"Kalori": 320, "Protein": 11, "Lemak": 10, "Karbohidrat": 45},
    "Nasi Putih": {"Kalori": 130, "Protein": 2.7, "Lemak": 0.3, "Karbohidrat": 28},
    "Pempek": {"Kalori": 180, "Protein": 8, "Lemak": 5, "Karbohidrat": 28},
    "Rendang": {"Kalori": 350, "Protein": 25, "Lemak": 24, "Karbohidrat": 10},
    "Sambal": {"Kalori": 60, "Protein": 2, "Lemak": 4, "Karbohidrat": 5},
    "Sate": {"Kalori": 200, "Protein": 18, "Lemak": 13, "Karbohidrat": 4},
    "Soto": {"Kalori": 90, "Protein": 6, "Lemak": 4, "Karbohidrat": 8},
    "Tahu Goreng": {"Kalori": 140, "Protein": 15, "Lemak": 10, "Karbohidrat": 4},
    "Tempe Goreng": {"Kalori": 190, "Protein": 18, "Lemak": 12, "Karbohidrat": 8},
}

# ==========================================
# MEMBUAT PROMPT
# ==========================================

def create_prompt(food_list):

    foods = ", ".join(food_list)

    prompt = f"""
Anda adalah seorang ahli gizi profesional.

Makanan yang berhasil dideteksi oleh sistem YOLOv11 adalah:

{foods}

Berikan informasi gizi dalam format tabel Markdown.

Gunakan format berikut:

| Nama Makanan | Kalori (kkal/100 g) | Protein (g) | Lemak (g) | Karbohidrat (g) |
|--------------|--------------------:|------------:|----------:|----------------:|

Ketentuan:

1. Gunakan satu nilai saja (angka).
2. Gunakan data gizi yang akurat dan umum digunakan (basis per 100 gram).
3. HANYA tampilkan makanan yang terdeteksi, jangan menambahkan makanan lain.
4. Setelah tabel buat bagian:

## Ringkasan Gizi

Maksimal 3 kalimat.

## Saran Konsumsi

Maksimal 3 kalimat.

Gunakan Bahasa Indonesia yang baik dan benar.
"""

    return prompt

# ==========================================
# MEMINTA INFORMASI GIZI KE GROQ
# ==========================================

def get_nutrition(food_list):

    # Jika tidak ada makanan, langsung kembalikan pesan
    if not food_list:
        return "Tidak ada makanan yang terdeteksi."

    # Coba panggil API Groq terlebih dahulu
    try:
        result = _call_groq(food_list)
        if result:
            return result
    except Exception as e:
        print(f"[get_nutrition] Groq API gagal, fallback dipakai: {e}")

    # Jika gagal / tidak ada API key, gunakan tabel gizi statis
    return _build_fallback(food_list)


# ==========================================
# PANGGIL API GROQ (LLM)
# ==========================================

def _call_groq(food_list):

    if client is None:
        return None

    prompt = create_prompt(food_list)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Anda adalah ahli gizi profesional yang menjawab dalam Bahasa Indonesia."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        return content

    except Exception as e:
        print(f"[Groq] Error: {e}")
        return None

# ==========================================
# FALLBACK TABEL GIZI STATIS
# ==========================================

def _build_fallback(food_list):

    # Header tabel
    lines = []
    lines.append("| Nama Makanan | Kalori (kkal/100 g) | Protein (g) | Lemak (g) | Karbohidrat (g) |")
    lines.append("|--------------|--------------------:|------------:|----------:|----------------:|")

    total_kalori = 0

    for food in food_list:

        # Cari fallback berdasarkan nama (case-insensitive)
        matched = None
        for key, value in NUTRITION_FALLBACK.items():
            if key.lower() == food.strip().lower():
                matched = (key, value)
                break

        if matched is None:
            # Jika tidak ketemu, gunakan data default
            matched = (
                food,
                {"Kalori": 100, "Protein": 5, "Lemak": 5, "Karbohidrat": 15}
            )

        name, nut = matched
        total_kalori += nut["Kalori"]

        lines.append(
            f"| {name} | {nut['Kalori']} | {nut['Protein']} | "
            f"{nut['Lemak']} | {nut['Karbohidrat']} |"
        )

    # Ringkasan gizi
    lines.append("")
    lines.append("## Ringkasan Gizi")
    lines.append(
        f"Total perkiraan kalori dari makanan yang terdeteksi adalah sekitar "
        f"**{total_kalori} kkal per 100 gram**. Kandungan gizi bervariasi "
        f"berdasarkan jenis dan porsi makanan."
    )
    lines.append(
        "Makanan dengan kalori tertinggi umumnya adalah makanan yang digoreng, "
        "berlemak, atau berbahan dasar tepung."
    )
    lines.append(
        "Data ini merupakan perkiraan umum berdasarkan tabel komposisi pangan "
        "dan dapat berbeda tergantung metode pengolahan."
    )

    # Saran konsumsi
    lines.append("")
    lines.append("## Saran Konsumsi")
    lines.append(
        "Konsumsi makanan secara bervariasi dan seimbang sesuai kebutuhan "
        "kalori harian Anda."
    )
    lines.append(
        "Batasi makanan yang tinggi kalori, lemak, dan gula agar tidak "
        "melebihi kebutuhan energi harian."
    )
    lines.append(
        "Kombinasikan dengan sayuran dan buah-buahan untuk memenuhi kebutuhan "
        "serat, vitamin, dan mineral."
    )

    return "\n".join(lines)

# ==========================================
# DATA GIZI TERSTRUKTUR (untuk visualisasi)
# ==========================================

def get_nutrition_dataframe(food_list):

    import pandas as pd

    # Jika tidak ada makanan, kembalikan DataFrame kosong
    if not food_list:
        return pd.DataFrame(
            columns=["Nama Makanan", "Kalori", "Protein", "Lemak", "Karbohidrat"]
        )

    rows = []

    for food in food_list:

        # Cari fallback berdasarkan nama (case-insensitive)
        matched = None
        for key, value in NUTRITION_FALLBACK.items():
            if key.lower() == food.strip().lower():
                matched = value
                break

        if matched is None:
            # Jika tidak ketemu, gunakan data default
            matched = {"Kalori": 100, "Protein": 5, "Lemak": 5, "Karbohidrat": 15}

        rows.append({
            "Nama Makanan": food,
            "Kalori": matched["Kalori"],
            "Protein": matched["Protein"],
            "Lemak": matched["Lemak"],
            "Karbohidrat": matched["Karbohidrat"],
        })

    return pd.DataFrame(rows)

# ==========================================
# TEST / DEBUG (jalankan langsung)
# ==========================================

if __name__ == "__main__":

    print(get_nutrition(["Pizza", "Nasi Goreng", "Stroberi"]))
