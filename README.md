# 🛒 Dashboard Analisis Penjualan Supermarket

**UTS Visualisasi Data – Ganjil TA 2026/2027**
Universitas Dirgantara Marsekal Suryadarma (UNSURYA) | Dosen: Muryan Awaludin, S.Kom., M.Kom.

| | |
|---|---|
| **Nama** | `Syamsurizal` |
| **NIM** | `241051004` |
| **Live Dashboard** | `https://sales-analysis-dashboard-app.streamlit.app/` |
| **Dataset (Kaggle)** | `https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales?resource=download` |

---

## 📌 Latar Belakang

Supermarket dengan beberapa cabang menghasilkan ribuan transaksi yang sulit dibaca dalam bentuk tabel mentah.
Dashboard ini mengubah 1.000 transaksi (Januari–Maret 2019, 3 cabang/kota) menjadi gambaran visual agar
manajemen dapat menjawab: *produk dan kota mana yang paling berkontribusi, siapa pelanggan bernilai tinggi,
kapan toko paling ramai, dan apakah kepuasan pelanggan berkaitan dengan nilai belanja.*

**Dataset:** 1.000 baris × 17 kolom (kategorik: Branch, City, Customer type, Gender, Product line, Payment;
numerik: Unit price, Quantity, Tax 5%, Sales, cogs, gross income, Rating; waktu: Date, Time).
Tidak ada missing value maupun duplikat. Pra-pemrosesan hanya parsing `Date`/`Time` dan penambahan kolom
bantu `Hour`, `Weekday`, `Month`; isi data tidak diubah.

## ✨ Fitur Dashboard

- **5 KPI Card:** Total Sales, Total Transaksi, Rata-rata Rating, Gross Income, Rata-rata per Transaksi.
- **8 grafik Plotly dari 6 jenis berbeda:** line chart (tren + moving average), donut (proporsi),
  bar horizontal, grouped bar, heatmap (hari × jam), scatter (Quantity vs Sales), box plot (rating per kota).
- **4 filter interaktif:** rentang tanggal, Kota, Product line, Tipe pelanggan (+ pilihan granularitas tren
  dan dimensi donut).
- **Desain:** palet warna konsisten (teal = utama, amber = pembanding), layout kolom responsif.
- **Insight & Storytelling:** insight otomatis yang menyesuaikan filter + temuan utama.

## 🔑 Key Insights

1. **Kinerja antar-cabang seimbang.** Naypyitaw unggul tipis (34,2% Sales; rata-rata transaksi 337,10),
   Yangon dan Mandalay masing-masing 32,9%. Mandalay punya rating terendah (6,82).
2. **Produk merata, preferensi kota berbeda.** *Food and beverages* teratas (17,4%), *Health and beauty*
   terendah (15,2%). Namun *Food and beverages* kuat di Naypyitaw, *Home and lifestyle* di Yangon, dan
   *Health and beauty* di Mandalay → stok/promosi perlu disesuaikan per kota.
3. **Member (58,7% Sales) dan pelanggan perempuan (60,3% Sales)** belanja lebih besar per transaksi
   (±9,6% dan ±14% lebih tinggi dari pembandingnya).
4. **Pola waktu:** Sabtu paling ramai (17,4%), Senin paling sepi (11,7%); puncak harian pukul 19:00.
   Penurunan Februari sebagian disebabkan jumlah hari yang lebih sedikit.
5. **Quantity (r ≈ 0,71) lebih menentukan Sales** daripada harga satuan (r ≈ 0,63), sedangkan Rating tidak
   berkorelasi dengan Sales (r ≈ −0,04).

> ⚠️ **Catatan kualitas data:** `gross margin percentage` konstan (4,76%) dan `gross income` identik dengan
> `Tax 5%`, sehingga analisis profitabilitas per segmen tidak informatif. Branch dan City berelasi 1:1
> (Alex = Yangon, Cairo = Mandalay, Giza = Naypyitaw).

## 🗂️ Struktur Repositori

```
.
├── app.py                         # aplikasi dashboard Streamlit
├── analysis.py                    # cleaning + analisis eksploratif
├── requirements.txt
├── README.md
└── dataset/
    ├── SuperMarket_Analysis.csv   # data asli
    └── supermarket_clean.csv      # hasil analysis.py (opsional)
```

## ▶️ Menjalankan Secara Lokal

```bash
git clone <URL-REPO-ANDA>
cd <nama-repo>
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Buka `http://localhost:8501`. Untuk melihat hasil analisis di terminal: `python analysis.py`.

## 🚀 Deploy ke Streamlit Community Cloud

1. Push repositori ke GitHub (set **Public**).
2. Buka <https://share.streamlit.io> → **New app** → pilih repo, branch `main`, file `app.py`.
3. Klik **Deploy**, lalu salin URL ke bagian *Live Dashboard* di atas.

## 🛠️ Teknologi

Python · Streamlit · Pandas · Plotly

## 📚 Sumber Data

Dataset sekunder dari Kaggle: `[ISI URL DATASET KAGGLE]`.
