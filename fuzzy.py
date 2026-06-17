import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# 1. LAYOUT & CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Evaluasi Dosen - Fuzzy Tsukamoto",
    layout="wide"
)

st.title("Sistem Pendukung Keputusan Pemilihan Dosen Terbaik")
st.subheader("Metode Fuzzy Tsukamoto")
st.write("Menghitung skor kualitas dosen secara otomatis berbasis data multi-kriteria.")

# ==================================================
# 2. DATASET LENGKAP (5 KRITERIA)
# ==================================================
data_dosen = {
    'Alternatif': ['A1', 'A2', 'A3', 'A4', 'A5'],
    'Kode Dosen': ['T043', 'T008', 'T021', 'T039', 'T019'],
    'C1 (Avg Score)': [61.99, 61.00, 46.94, 81.94, 73.97],
    'C2 (Eval Score)': [80.10, 69.20, 64.90, 90.70, 100.00],
    'C3 (Feedback)': [78.40, 75.00, 78.20, 81.60, 97.20],
    'C4 (Completion)': [89.86, 87.49, 81.43, 86.09, 100.00],
    'C5 (Interactive)': [65.49, 100.00, 35.39, 91.87, 83.53]
}

kriteria_info = {
    'C1': {'nama': 'Student_Avg_Score', 'min': 46.94, 'max': 81.94},
    'C2': {'nama': 'Teacher_Evaluation_Score', 'min': 64.90, 'max': 100.00},
    'C3': {'nama': 'Student_Feedback_Rating', 'min': 75.00, 'max': 97.20},
    'C4': {'nama': 'Course_Completion_Rate', 'min': 81.43, 'max': 100.00},
    'C5': {'nama': 'Interactive_Sessions_Percent', 'min': 35.39, 'max': 100.00}
}

Z_MIN = 40.0
Z_MAX = 100.0

df = pd.DataFrame(data_dosen)

# ==================================================
# 3. MEMBERSHIP FUNCTIONS (FUZZIFIKASI)
# ==================================================
def hitung_keanggotaan(x, x_min, x_max):
    if x <= x_min:
        return 1.0, 0.0
    if x >= x_max:
        return 0.0, 1.0
    mu_rendah = (x_max - x) / (x_max - x_min)
    mu_tinggi = (x - x_min) / (x_max - x_min)
    return mu_rendah, mu_tinggi

# ==================================================
# 4. LOGIKA INFERENSI TSUKAMOTO
# ==================================================
def proses_tsukamoto(c1, c2, c3, c4, c5):
    c1_r, c1_t = hitung_keanggotaan(c1, kriteria_info['C1']['min'], kriteria_info['C1']['max'])
    c2_r, c2_t = hitung_keanggotaan(c2, kriteria_info['C2']['min'], kriteria_info['C2']['max'])
    c3_r, c3_t = hitung_keanggotaan(c3, kriteria_info['C3']['min'], kriteria_info['C3']['max'])
    c4_r, c4_t = hitung_keanggotaan(c4, kriteria_info['C4']['min'], kriteria_info['C4']['max'])
    c5_r, c5_t = hitung_keanggotaan(c5, kriteria_info['C5']['min'], kriteria_info['C5']['max'])
    
    alpha1 = min(c1_r, c2_r, c3_r, c4_r, c5_r)
    z1 = Z_MAX - (alpha1 * (Z_MAX - Z_MIN))
    
    alpha2 = min(c2_t, c3_t)
    z2 = Z_MIN + (alpha2 * (Z_MAX - Z_MIN))
    
    alpha3 = min(c1_t, c4_t, c5_t)
    z3 = Z_MIN + (alpha3 * (Z_MAX - Z_MIN))
    
    alpha4 = min(c2_r, c3_r)
    z4 = Z_MAX - (alpha4 * (Z_MAX - Z_MIN))
    
    total_alpha = alpha1 + alpha2 + alpha3 + alpha4
    if total_alpha == 0:
        z_akhir = (Z_MIN + Z_MAX) / 2
    else:
        z_akhir = ((alpha1 * z1) + (alpha2 * z2) + (alpha3 * z3) + (alpha4 * z4)) / total_alpha
        
    return {
        "fuzzifikasi": {"C1": (c1_r, c1_t), "C2": (c2_r, c2_t), "C3": (c3_r, c3_t), "C4": (c4_r, c4_t), "C5": (c5_r, c5_t)},
        "rules": [(alpha1, z1), (alpha2, z2), (alpha3, z3), (alpha4, z4)],
        "z_akhir": round(z_akhir, 2)
    }

def get_kategori(z):
    if z >= 80: return "Sangat Baik (Excellent)"
    if z >= 60: return "Baik (Good)"
    if z >= 50: return "Cukup (Average)"
    return "Kurang (Poor)"

# ==================================================
# 5. INISIALISASI STRUKTUR TAB UTAMA
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    " Dataset", 
    " Penjelasan", 
    " Kurva", 
    " Perangkingan Akhir"
])

# ==================================================
# TAB 1: DATASET
# ==================================================
with tab1:
    st.header("👨‍🏫 Dashboard Informasi & Basis Data CEMP")
    
    st.markdown("""
    Sistem cerdas ini mengevaluasi efektivitas instruksional dosen berdasarkan indikator data *Comprehensive Education Management Platform* (CEMP).
    
    ### Parameter Kriteria Evaluasi:
    | Kode Kriteria | Nama Metrik Pengukuran | Sifat Fitur | Batas Minimum ($X_{min}$) | Batas Maksimum ($X_{max}$) |
    | :---: | :--- | :---: | :---: | :---: |
    | **C1** | Student Average Score | Benefit | 46.94 | 81.94 |
    | **C2** | Teacher Evaluation Score | Benefit | 64.90 | 100.00 |
    | **C3** | Student Feedback Rating | Benefit | 75.00 | 97.20 |
    | **C4** | Course Completion Rate | Benefit | 81.43 | 100.00 |
    | **C5** | Interactive Sessions Percent | Benefit | 35.39 | 100.00 |
    """)
    
    st.write("---")
    st.subheader("📂 Kumpulan Dataset")
    st.dataframe(df, use_container_width=True)

# ==================================================
# TAB 2: PENJELASAN
# ==================================================
with tab2:
    st.header("🧠 Analisis & Penjelasan Alur Komputasi")
    
    # Menempatkan selectbox di area strategis atas
    selected_dosen = st.selectbox("Pilih Kode Alternatif Dosen untuk Inspeksi Alur Rumus:", df["Kode Dosen"])
    row_data = df[df["Kode Dosen"] == selected_dosen].iloc[0]
    
    kalkulasi = proses_tsukamoto(
        row_data['C1 (Avg Score)'], row_data['C2 (Eval Score)'], 
        row_data['C3 (Feedback)'], row_data['C4 (Completion)'], 
        row_data['C5 (Interactive)']
    )
    
    st.write("---")
    
    col_proses, col_skor = st.columns([3, 2], gap="large")
    
    # --- KOLOM KIRI: DETAIL LANGKAH ---
    with col_proses:
        st.subheader("⚙️ Detail Tahapan Komputasi")
        
        with st.expander(" Langkah 1: Proses Fuzzifikasi", expanded=True):
            fuz_list = []
            for k_id, nilai_mu in kalkulasi["fuzzifikasi"].items():
                fuz_list.append({
                    "Kriteria": k_id,
                    "Jenis Kriteria": kriteria_info[k_id]['nama'],
                    "Nilai Riil": row_data[df.columns[df.columns.str.contains(k_id)][0]],
                    "α RENDAH": round(nilai_mu[0], 4),
                    "α TINGGI": round(nilai_mu[1], 4)
                })
            st.dataframe(pd.DataFrame(fuz_list), use_container_width=True)
            
        with st.expander(" Langkah 2: Proses Inferensi Aturan", expanded=True):
            st.write("Mengevaluasi setiap basis aturan menggunakan operator **MIN**:")
            for i, (alpha, z) in enumerate(kalkulasi["rules"]):
                st.write(f" **Rule {i+1}**: Ketinggian $\\alpha_{i+1}$ = **{round(alpha, 4)}** $\\rightarrow$ Nilai $z_{i+1}$ = **{round(z, 2)}**")

    # --- KOLOM KANAN: FORMULA & KELUARAN SKOR ---
    with col_skor:
        st.subheader("🎯 Ringkasan Hasil Defuzzifikasi")
        
        st.latex(r'Z_{akhir} = \frac{\sum_{i=1}^{n} \alpha_i \cdot z_i}{\sum_{i=1}^{n} \alpha_i}')
        
        with st.container(border=True):
            st.markdown(f"### Kode Alternatif: **{row_data['Alternatif']}**")
            st.markdown(f"Nilai riil input yang dievaluasi didasarkan pada data platform CEMP untuk dosen terpilih.")
            st.write("---")
            
            st.metric(label="Skor Final Indeks Kualitas Dosen (Z)", value=f"{kalkulasi['z_akhir']} / 100")
            st.metric(label="Predikat Kualifikasi Kategori", value=get_kategori(kalkulasi['z_akhir']))

# ==================================================
# TAB 3: KURVA KEANGGOTAAN
# ==================================================
with tab3:
    st.header("📈 Grafik Representasi Fungsi Keanggotaan Kriteria")
    st.write("Fungsi keanggotaan menggunakan model pendekatan kurva **Linear Naik** (Kondisi Tinggi) dan **Linear Turun** (Kondisi Rendah).")
    
    col_k1, col_k2 = st.columns(2)
    grid_cols = [col_k1, col_k2, col_k1, col_k2, col_k1]
    
    for idx, (k_id, info) in enumerate(kriteria_info.items()):
        with grid_cols[idx]:
            fig, ax = plt.subplots(figsize=(6, 3.5))
            x_range = np.linspace(info['min'] - 5, info['max'] + 5, 300)
            y_r = [hitung_keanggotaan(x, info['min'], info['max'])[0] for x in x_range]
            y_t = [hitung_keanggotaan(x, info['min'], info['max'])[1] for x in x_range]
            
            ax.plot(x_range, y_r, label="RENDAH", color="tomato", linewidth=2)
            ax.plot(x_range, y_t, label="TINGGI", color="seagreen", linewidth=2)
            ax.set_title(f"{k_id}: {info['nama']}", fontsize=10, fontweight='bold')
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend(fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

# ==================================================
# TAB 4: PERANGKINGAN AKHIR (FITUR UNDUH DIHAPUS)
# ==================================================
with tab4:
    st.header("📊 Hasil Konvergensi Perangkingan Akhir")
    
    skor_final = []
    for idx, row in df.iterrows():
        res = proses_tsukamoto(
            row['C1 (Avg Score)'], row['C2 (Eval Score)'], 
            row['C3 (Feedback)'], row['C4 (Completion)'], 
            row['C5 (Interactive)']
        )
        skor_final.append(res["z_akhir"])
        
    df_rank = df.copy()
    df_rank["Skor Akhir Fuzzy"] = skor_final
    df_rank["Kategori Kualifikasi"] = df_rank["Skor Akhir Fuzzy"].apply(get_kategori)
    df_rank = df_rank.sort_values(by="Skor Akhir Fuzzy", ascending=False).reset_index(drop=True)
    df_rank.index = df_rank.index + 1
    df_rank.index.name = "Peringkat"
    
    st.dataframe(df_rank, use_container_width=True)
    
    st.write("---")
    # Diagram Batang Komparasi
    fig, ax = plt.subplots(figsize=(10, 4.5))
    warna_grafik = ["gold" if i == 0 else "steelblue" for i in range(len(df_rank))]
    batang = ax.bar(df_rank["Alternatif"] + " (" + df_rank["Kode Dosen"] + ")", df_rank["Skor Akhir Fuzzy"], color=warna_grafik)
    
    for b in batang:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{b.get_height()}", ha="center", fontsize=9, fontweight='bold')
        
    ax.set_title("Grafik Komparasi Hasil Skor Kualitas Dosen", fontsize=11, fontweight='bold')
    ax.set_ylabel("Skor Akhir (Z)")
    ax.set_ylim(0, 110)
    st.pyplot(fig)
    plt.close(fig)
    
    st.write("---")
    best_dosen = df_rank.iloc[0]
    st.success(f"Berdasarkan konvergensi seluruh parameter uji, Dosen Terbaik adalah **{best_dosen['Alternatif']} ({best_dosen['Kode Dosen']})** dengan raihan skor sebesar **{best_dosen['Skor Akhir Fuzzy']}**.")