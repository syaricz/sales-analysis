"""
Dashboard Analisis Penjualan Supermarket
UTS Visualisasi Data - Universitas Dirgantara Marsekal Suryadarma
Nama / NPM : [ISI NAMA] / [ISI NPM]
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# KONFIGURASI HALAMAN & PALET WARNA (konsisten di seluruh dashboard)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Penjualan Supermarket",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#0F766E"   # teal  -> warna utama / metrik utama
ACCENT = "#F59E0B"    # amber -> pembanding / highlight
NEUTRAL = "#94A3B8"
TEAL_SCALE = ["#E6F4F1", "#99D5CB", "#2BA394", "#0F766E", "#064E48"]

CITY_COLORS = {"Yangon": "#0F766E", "Mandalay": "#F59E0B", "Naypyitaw": "#6366F1"}
CUSTOMER_COLORS = {"Member": "#0F766E", "Normal": "#F59E0B"}
PAYMENT_COLORS = {"Cash": "#0F766E", "Ewallet": "#6366F1", "Credit card": "#F59E0B"}

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_ID = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis",
    "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu",
}

DATA_PATH = Path(__file__).parent / "dataset" / "SuperMarket_Analysis.csv"


def style_fig(fig: go.Figure, height: int = 380) -> go.Figure:
    """Tema seragam untuk semua grafik."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Inter, Arial, sans-serif", size=13),
        title=dict(font=dict(size=16)),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )
    return fig


def fmt(x: float) -> str:
    return f"{x:,.0f}"


# ----------------------------------------------------------------------------
# DATA LOADING & CLEANING (minimal: parsing tanggal & waktu, dataset tidak diubah)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df["Hour"] = pd.to_datetime(df["Time"], format="%I:%M:%S %p").dt.hour
    df["Weekday"] = df["Date"].dt.day_name()
    return df


if not DATA_PATH.exists():
    st.error(f"File dataset tidak ditemukan: {DATA_PATH}")
    st.stop()

df = load_data(DATA_PATH)

# ----------------------------------------------------------------------------
# SIDEBAR - FILTER INTERAKTIF
# ----------------------------------------------------------------------------
st.sidebar.title("🎛️ Filter Data")
st.sidebar.caption("Semua KPI, grafik, dan insight berubah sesuai filter.")

min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Rentang tanggal", value=(min_d, max_d), min_value=min_d, max_value=max_d
)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = date_range
else:  # pengguna baru memilih satu tanggal
    start_d = end_d = date_range[0] if isinstance(date_range, (tuple, list)) else date_range

cities = st.sidebar.multiselect(
    "Kota", sorted(df["City"].unique()), default=sorted(df["City"].unique())
)
products = st.sidebar.multiselect(
    "Product line", sorted(df["Product line"].unique()), default=sorted(df["Product line"].unique())
)
cust_types = st.sidebar.multiselect(
    "Tipe pelanggan", sorted(df["Customer type"].unique()), default=sorted(df["Customer type"].unique())
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "ℹ️ Branch dan City berelasi 1:1: Alex = Yangon, Cairo = Mandalay, Giza = Naypyitaw. "
    "Karena itu filter lokasi cukup memakai **Kota**."
)

mask = (
    (df["Date"].dt.date >= start_d)
    & (df["Date"].dt.date <= end_d)
    & df["City"].isin(cities)
    & df["Product line"].isin(products)
    & df["Customer type"].isin(cust_types)
)
fdf = df.loc[mask].copy()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("🛒 Dashboard Analisis Penjualan Supermarket")
st.markdown(
    f"Ringkasan performa 3 cabang supermarket periode **{min_d:%d %b %Y} – {max_d:%d %b %Y}**. "
    "Gunakan filter di sidebar kiri untuk menelusuri data."
)

if fdf.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Silakan ubah filter di sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------------------------
total_sales = fdf["Sales"].sum()
total_trx = len(fdf)
avg_rating = fdf["Rating"].mean()
gross_income = fdf["gross income"].sum()
avg_basket = fdf["Sales"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
with k1.container(border=True):
    st.metric("💰 Total Sales", fmt(total_sales))
with k2.container(border=True):
    st.metric("🧾 Total Transaksi", fmt(total_trx))
with k3.container(border=True):
    st.metric("⭐ Rata-rata Rating", f"{avg_rating:.2f} / 10")
with k4.container(border=True):
    st.metric("📈 Gross Income", fmt(gross_income))
with k5.container(border=True):
    st.metric("🛍️ Rata-rata per Transaksi", fmt(avg_basket))

st.markdown("")

# ----------------------------------------------------------------------------
# BARIS 1: LINE CHART (tren) + DONUT (proporsi)
# ----------------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    gran = st.radio("Granularitas tren", ["Harian", "Mingguan", "Bulanan"], horizontal=True)
    rule = {"Harian": "D", "Mingguan": "W", "Bulanan": "MS"}[gran]
    trend = fdf.set_index("Date")["Sales"].resample(rule).sum().reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend["Date"], y=trend["Sales"], mode="lines+markers", name="Sales",
            line=dict(color=PRIMARY, width=2.5), marker=dict(size=5),
        )
    )
    if gran == "Harian" and len(trend) >= 7:
        trend["MA7"] = trend["Sales"].rolling(7, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=trend["Date"], y=trend["MA7"], mode="lines", name="Rata-rata bergerak 7 hari",
                line=dict(color=ACCENT, width=2.5, dash="dash"),
            )
        )
    peak = trend.loc[trend["Sales"].idxmax()]
    fig.add_annotation(
        x=peak["Date"], y=peak["Sales"], text=f"Puncak: {fmt(peak['Sales'])}",
        showarrow=True, arrowhead=2, ax=0, ay=-40, font=dict(color=PRIMARY),
    )
    fig.update_layout(title=f"Tren Sales {gran}", xaxis_title="Tanggal", yaxis_title="Total Sales")
    st.plotly_chart(style_fig(fig, 400), use_container_width=True)

with c2:
    dim = st.radio("Proporsi berdasarkan", ["Customer type", "Payment", "Gender"], horizontal=True)
    color_map = {"Customer type": CUSTOMER_COLORS, "Payment": PAYMENT_COLORS,
                 "Gender": {"Female": PRIMARY, "Male": ACCENT}}[dim]
    share = fdf.groupby(dim, as_index=False)["Sales"].sum()
    fig = px.pie(
        share, names=dim, values="Sales", hole=0.55, color=dim, color_discrete_map=color_map,
    )
    fig.update_traces(textinfo="percent+label", textposition="outside", showlegend=False)
    fig.update_layout(title=f"Proporsi Sales per {dim}")
    st.plotly_chart(style_fig(fig, 400), use_container_width=True)

# ----------------------------------------------------------------------------
# BARIS 2: BAR (product line) + GROUPED BAR (product line x kota)
# ----------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    pl = fdf.groupby("Product line", as_index=False)["Sales"].sum().sort_values("Sales")
    fig = px.bar(
        pl, x="Sales", y="Product line", orientation="h", text="Sales",
        color_discrete_sequence=[PRIMARY],
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        title="Total Sales per Product Line (terurut)", xaxis_title="Total Sales", yaxis_title="",
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

with c4:
    pc = fdf.groupby(["Product line", "City"], as_index=False)["Sales"].sum()
    fig = px.bar(
        pc, x="Product line", y="Sales", color="City", barmode="group",
        color_discrete_map=CITY_COLORS,
    )
    fig.update_layout(
        title="Sales Product Line di Tiap Kota", xaxis_title="Product line", yaxis_title="Total Sales",
        legend_title_text="Kota",
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------------------------------------------------------
# BARIS 3: HEATMAP (hari x jam) + SCATTER (Quantity vs Sales)
# ----------------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    hm = (
        fdf.pivot_table(index="Weekday", columns="Hour", values="Sales", aggfunc="sum", fill_value=0)
        .reindex(DAY_ORDER)
        .fillna(0)
    )
    hm.index = [DAY_ID[d] for d in hm.index]
    fig = px.imshow(
        hm, aspect="auto", color_continuous_scale=TEAL_SCALE,
        labels=dict(x="Jam (24 jam)", y="Hari", color="Sales"),
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(title="Heatmap Sales: Hari × Jam")
    st.plotly_chart(style_fig(fig), use_container_width=True)

with c6:
    corr = fdf["Quantity"].corr(fdf["Sales"]) if len(fdf) > 2 else float("nan")
    fig = px.scatter(
        fdf, x="Quantity", y="Sales", color="Product line", opacity=0.7,
        hover_data=["Invoice ID", "City", "Unit price"],
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(
        title=f"Quantity vs Sales (korelasi r = {corr:.2f})",
        xaxis_title="Quantity (unit)", yaxis_title="Sales",
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------------------------------------------------------
# BARIS 4: BOX PLOT (rating per kota) + BAR (sales per hari)
# ----------------------------------------------------------------------------
c7, c8 = st.columns(2)

with c7:
    fig = px.box(
        fdf, x="City", y="Rating", color="City", color_discrete_map=CITY_COLORS, points="outliers",
    )
    fig.update_layout(
        title="Sebaran Rating Pelanggan per Kota", xaxis_title="Kota", yaxis_title="Rating (skala 1-10)",
        showlegend=False,
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

with c8:
    wd = (
        fdf.groupby("Weekday", as_index=False)["Sales"].sum()
        .set_index("Weekday").reindex(DAY_ORDER).fillna(0).reset_index()
    )
    wd["Hari"] = wd["Weekday"].map(DAY_ID)
    top_day = wd.loc[wd["Sales"].idxmax(), "Hari"]
    wd["Warna"] = wd["Hari"].apply(lambda d: "Tertinggi" if d == top_day else "Lainnya")
    fig = px.bar(
        wd, x="Hari", y="Sales", color="Warna",
        color_discrete_map={"Tertinggi": ACCENT, "Lainnya": PRIMARY},
        category_orders={"Hari": [DAY_ID[d] for d in DAY_ORDER]},
    )
    fig.update_layout(
        title="Total Sales per Hari dalam Seminggu", xaxis_title="Hari", yaxis_title="Total Sales",
        showlegend=False,
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------------------------------------------------------
# INSIGHT & STORYTELLING
# ----------------------------------------------------------------------------
st.markdown("---")
st.header("📖 Insight & Storytelling")

# --- insight dinamis (mengikuti filter) ---
top_pl = pl.iloc[-1]
low_pl = pl.iloc[0]
city_sales = fdf.groupby("City")["Sales"].sum().sort_values(ascending=False)
member_share = fdf.loc[fdf["Customer type"] == "Member", "Sales"].sum() / total_sales * 100
hour_sales = fdf.groupby("Hour")["Sales"].sum()
peak_hour = int(hour_sales.idxmax())
r_qty = fdf["Quantity"].corr(fdf["Sales"]) if len(fdf) > 2 else float("nan")
r_rate = fdf["Rating"].corr(fdf["Sales"]) if len(fdf) > 2 else float("nan")

st.subheader("🔎 Insight otomatis sesuai filter aktif")
i1, i2 = st.columns(2)
with i1:
    st.info(
        f"**Product line:** **{top_pl['Product line']}** memimpin dengan Sales {fmt(top_pl['Sales'])} "
        f"({top_pl['Sales'] / total_sales * 100:.1f}% dari total), sedangkan **{low_pl['Product line']}** "
        f"terendah ({fmt(low_pl['Sales'])})."
    )
    st.info(
        f"**Waktu:** hari tersibuk adalah **{top_day}** dan jam tersibuk pukul **{peak_hour:02d}:00** "
        f"(Sales {fmt(hour_sales.max())})."
    )
with i2:
    st.info(
        f"**Kota:** **{city_sales.index[0]}** menyumbang Sales tertinggi "
        f"({fmt(city_sales.iloc[0])}, {city_sales.iloc[0] / total_sales * 100:.1f}%)."
    )
    st.info(
        f"**Pelanggan:** pelanggan **Member** menyumbang **{member_share:.1f}%** Sales. "
        f"Korelasi Quantity–Sales r = {r_qty:.2f}, Rating–Sales r = {r_rate:.2f}."
    )

# --- insight utama (seluruh data, Jan–Mar 2019) ---
st.subheader("⭐ Temuan utama (seluruh data, Jan–Mar 2019)")
st.markdown(
    """
1. **Kinerja antar-cabang sangat seimbang.** Naypyitaw (Giza) unggul tipis dengan 34,2% total Sales dan
   rata-rata transaksi tertinggi (337,10); Yangon dan Mandalay masing-masing 32,9%. Mandalay punya rating
   rata-rata terendah (6,82) → prioritas evaluasi layanan.
2. **Portofolio produk merata, tetapi preferensi tiap kota berbeda tajam.** *Food and beverages* teratas
   (17,4%) dan *Health and beauty* terendah (15,2%). Namun *Food and beverages* jauh lebih kuat di Naypyitaw
   (23.767 vs 15.215 di Mandalay), *Home and lifestyle* dominan di Yangon (22.417), dan *Health and beauty*
   kuat di Mandalay (19.981) → stok & promosi sebaiknya disesuaikan per kota.
3. **Member dan pelanggan perempuan bernilai lebih tinggi.** Member menyumbang 58,7% Sales dengan belanja
   rata-rata ±9,6% lebih besar dari non-member; pelanggan perempuan menyumbang 60,3% Sales dengan belanja
   ±14% lebih besar dari laki-laki.
4. **Pola waktu jelas.** Sabtu paling ramai (17,4% Sales), Senin paling sepi (11,7%). Jam 19:00 adalah puncak
   harian; titik terpanas ada di Sabtu 19:00 dan Selasa 19:00 → waktu ideal untuk promo & penjadwalan staf.
   Sales Februari (97.219) lebih rendah dari Januari (116.292), sebagian karena Februari hanya 28 hari
   (rata-rata per hari turun ±7%).
5. **Nilai belanja ditentukan jumlah barang, bukan kepuasan.** Quantity berkorelasi kuat dengan Sales
   (r ≈ 0,71), lebih kuat daripada harga satuan (r ≈ 0,63), sementara Rating hampir tidak berkorelasi dengan
   Sales (r ≈ −0,04) → strategi *bundling*/upselling lebih efektif daripada sekadar menaikkan harga.
"""
)
st.caption(
    "Catatan data: kolom *gross margin percentage* bernilai konstan (4,76%) dan *gross income* identik dengan "
    "*Tax 5%*, sehingga analisis profitabilitas per segmen tidak informatif pada dataset ini. "
    "Mata uang tidak dispesifikasikan oleh dataset."
)

with st.expander("🔍 Lihat data transaksi (hasil filter)"):
    st.dataframe(
        fdf.drop(columns=["Weekday"]).sort_values("Date"), use_container_width=True, hide_index=True
    )
    st.download_button(
        "⬇️ Unduh data terfilter (CSV)",
        fdf.to_csv(index=False).encode("utf-8"),
        file_name="supermarket_filtered.csv",
        mime="text/csv",
    )

st.caption("Sumber data: Kaggle – Supermarket Sales/Analysis | UTS Visualisasi Data 2026/2027")
