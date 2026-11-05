"""
Pembersihan & analisis data (di luar Streamlit).
Jalankan: python analysis.py
"""

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "dataset" / "SuperMarket_Analysis.csv"

# ---------------------------------------------------------------- 2. LOAD & CLEAN
df = pd.read_csv(DATA_PATH)
df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
df["Hour"] = pd.to_datetime(df["Time"], format="%I:%M:%S %p").dt.hour
df["Weekday"] = df["Date"].dt.day_name()
df["Month"] = df["Date"].dt.to_period("M").astype(str)

print("=== INFO ===")
df.info()
print("\n=== MISSING VALUES ===")
print(df.isna().sum())
print("\nBaris duplikat:", df.duplicated().sum(), "| Invoice ID duplikat:", df["Invoice ID"].duplicated().sum())
print("\n=== STATISTIK DESKRIPTIF ===")
print(df.describe().round(2).to_string())
print("\nRentang tanggal:", df["Date"].min().date(), "s/d", df["Date"].max().date())

# Validasi konsistensi kolom turunan
print("\nSales = cogs + Tax 5% :", ((df["Sales"] - df["cogs"] - df["Tax 5%"]).abs() < 1e-6).all())
print("gross income == Tax 5% :", ((df["gross income"] - df["Tax 5%"]).abs() < 1e-6).all())
print("Relasi Branch-City:\n", pd.crosstab(df["Branch"], df["City"]))

# Simpan versi bersih (isi tidak diubah, hanya kolom tambahan Hour/Weekday/Month)
df.to_csv(DATA_PATH.parent / "supermarket_clean.csv", index=False)

# ---------------------------------------------------------------- 3. ANALISIS
total = df["Sales"].sum()


def summarize(col):
    t = df.groupby(col).agg(
        Total_Sales=("Sales", "sum"),
        Transaksi=("Invoice ID", "count"),
        Rata_rata_Sales=("Sales", "mean"),
        Gross_Income=("gross income", "sum"),
        Rata_rata_Rating=("Rating", "mean"),
    )
    t["Persen_Sales"] = t["Total_Sales"] / total * 100
    print(f"\n=== Per {col} ===")
    print(t.sort_values("Total_Sales", ascending=False).round(2).to_string())


for c in ["Product line", "City", "Branch", "Customer type", "Gender", "Payment", "Month", "Weekday"]:
    summarize(c)

print("\n=== Product line x City (Sales) ===")
print(df.pivot_table(index="Product line", columns="City", values="Sales", aggfunc="sum").round(0).to_string())

print("\n=== Sales per jam ===")
print(df.groupby("Hour")["Sales"].agg(["sum", "count"]).round(0).to_string())

print("\n=== Korelasi ===")
print(df[["Sales", "Rating", "Quantity", "Unit price"]].corr().round(3))

print("\nRata-rata Rating keseluruhan:", round(df["Rating"].mean(), 2))
