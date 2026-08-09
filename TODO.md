# TODO - Pembuatan Sidebar Food Vision

- [x] Membaca file proyek (appfood.py, model.py, api_llm.py, requirements.txt)
- [x] Mengecek kelas makanan pada model best.pt (29 kelas)
- [x] Menyusun rencana dan konfirmasi dengan user
- [x] Mengubah `initial_sidebar_state` menjadi `expanded`
- [x] Menambahkan styling CSS untuk sidebar
- [x] Mengisi konten sidebar dengan logo, deskripsi, dan 29 kelas makanan
- [x] Menjalankan/testing aplikasi

# TODO - Penyempurnaan Data Gizi (10 Kelas Makanan)

- [x] Memeriksa kondisi file (appfood.py, modelfoodvision.py, api_llm.py)
- [x] Mengubah import appfood.py menjadi `from modelfoodvision import detect_food`
- [x] Menyinkronkan FOOD_EMOJI, food_classes, dan kartu info menjadi 10 makanan
- [x] Menambahkan data NUTRITION_FALLBACK untuk Mie Ayam, Rendang, Sambal, Soto
- [x] Memperbaiki indentasi pada bagian hasil deteksi (st.image & st.dataframe)
- [x] Memverifikasi sintaks appfood.py & api_llm.py (SYNTAX OK)

# TODO - Perbaikan Kamera & Tampilan

- [x] Mengecilkan kotak kamera (max-width 520px, max-height 340px) & di tengah
- [x] Menyamakan ukuran pratinjau & hasil deteksi (width=480px)
- [x] Menambahkan CSS centering [data-testid="stImage"] agar pratinjau & hasil deteksi di tengah
- [x] Mencegah scroll horizontal pada tabel "Deteksi Objek Terdeteksi" (overflow hidden)
- [ ] Kamera HP: perlu HTTPS (akses via HTTP IP LAN diblokir browser) - gunakan tunnel/HTTPS

# TODO - Visualisasi Kandungan Gizi

- [x] Menambahkan fungsi `get_nutrition_dataframe` di api_llm.py (data gizi terstruktur)
- [x] Menambahkan import matplotlib & pandas di appfood.py
- [x] Menyimpan `food_list` ke session_state saat deteksi
- [x] Menambahkan Bar Chart perbandingan Kalori per makanan
- [x] Menambahkan Bar Chart makronutrien (Protein, Lemak, Karbohidrat) grouped
- [x] Meletakkan visualisasi di bawah tabel Kandungan Gizi
- [x] Menyelaraskan appfood.py dengan modelfoodvision.py (import sudah benar)
- [x] Melengkapi NUTRITION_FALLBACK di api_llm.py untuk 10 kelas model (Mie Ayam, Sambal, Soto, dan perbaikan nama Rendang)
- [x] Verifikasi fungsi fallback gizi untuk 10 makanan (semua ter-cover, tidak ada lagi yang default)

# TODO - Filter 10 Kelas Makanan Saja

- [x] Menambahkan `ALLOWED_CLASSES` (10 kelas) di modelfoodvision.py
- [x] Memfilter objek yang bukan termasuk 10 kelas (misal Nasi Goreng Telur tidak akan dideteksi)
- [x] Menggambar bounding box & label secara manual hanya untuk 10 kelas saja
- [x] Mengecek isi best.pt -> ternyata hanya 10 kelas (persis sama dengan daftar aplikasi)
- [x] Memperbaiki case-sensitive ALLOWED_CLASSES (huruf kecil) agar cocok dengan model.names
- [x] Menaikkan MIN_CONFIDENCE dari 0.5 -> 0.7 untuk mengurangi false positive
- [x] Menaikkan MIN_CONFIDENCE menjadi 0.85 untuk menekan false positive
      (Sambal Terong->Sate, Tempe Bertepung->Pempek, Nasi Goreng Telur->Mie Ayam)
- [x] Verifikasi sintaks (EXIT: 0)

# TODO - Pembersihan File Tidak Digunakan

- [x] Menghapus `train_yolo.py` (script training yang tidak dipakai aplikasi runtime)
- [x] Menghapus `test_out.txt` (file output test)
- [x] Menghapus folder `uploads/` (kosong)
- [x] Menghapus folder `results/` (kosong)
- [x] Mempertahankan `CalorEase/` (dataset milik user) dan `best.pt`, `assets/` (inti aplikasi)
- [x] Memperkecil ukuran pratinjau & hasil deteksi dari 480px menjadi 420px

# TODO - Persiapan Deploy (Streamlit Cloud)

- [x] Integrasi `st.secrets` sebagai fallback API key di api_llm.py
      (GROQ_API_KEY dari env/local .env ATAU Streamlit Secrets)
- [x] Membuat `.gitignore` (abaikan .env, .venv, __pycache__, dsb)
- [x] Membuat `.streamlit/config.toml` (tema & headless mode)
- [x] Membuat `packages.txt` (libgl1, libglib2.0-0 untuk OpenCV di Linux)
- [x] Verifikasi sintaks api_llm.py, appfood.py, modelfoodvision.py
- [ ] Inisialisasi git & push ke GitHub (pastikan best.pt & assets/logo.png ikut ter-commit)
- [ ] Connect ke Streamlit Cloud, pilih branch, atur python version
- [ ] Set Streamlit Secrets di dashboard: st.secrets `GROQ_API_KEY`
- [ ] Test deploy (upload gambar & kamera)
