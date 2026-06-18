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
st.write("Menghitung skor kualitas dosen secara otomatis berbasis data riil multi-kriteria.")

# ==================================================
# 2. KOMPONEN UNGGAH BERKAS (FILE UPLOADER)
# ==================================================
st.markdown("### 📂 Unggah Data Evaluasi")
uploaded_file = st.file_uploader("Pilih dan unggah berkas CSV dari platform CEMP Anda jika ada:", type=["csv"])

# Data default 5 dosen (sebagai fallback jika belum ada file diunggah)
data_dosen_default = {
    'Alternatif': ['A1', 'A2', 'A3', 'A4', 'A5'],
    'Kode Dosen': ['T043', 'T008', 'T021', 'T039', 'T019'],
    'C1 (Avg Score)': [61.99, 61.00, 46.94, 81.94, 73.97],
    'C2 (Eval Score)': [80.10, 69.20, 64.90, 90.70, 100.00],
    'C3 (Feedback)': [78.40, 75.00, 78.20, 81.60, 97.20],
    'C4 (Completion)': [89.86, 87.49, 81.43, 86.09, 100.00],
    'C5 (Interactive)': [65.49, 100.00, 35.39, 91.87, 83.53]
}

if uploaded_file is not None:
    try:
        df_mentah = pd.read_csv(uploaded_file)
        df = pd.DataFrame()
        df['Alternatif'] = df_mentah['Teacher_ID']
        df['Kode Dosen'] = df_mentah['Course_ID']
        df['C1 (Avg Score)'] = df_mentah['Student_Avg_Score']
        df['C2 (Eval Score)'] = df_mentah['Teacher_Evaluation_Score'] * 10
        df['C3 (Feedback)'] = df_mentah['Student_Feedback_Rating'] * 20
        df['C4 (Completion)'] = df_mentah['Course_Completion_Rate']
        df['C5 (Interactive)'] = df_mentah['Interactive_Sessions_Percent']
        st.success(f"✔️ Berhasil memuat dan menormalisasi {len(df)} baris data dari berkas CEMP!")
    except Exception as e:
        st.error(f"Gagal memproses file CSV. Error: {e}")
        df = pd.DataFrame(data_dosen_default)
else:
    df = pd.DataFrame(data_dosen_default)
    st.info("💡 Menampilkan data sampel default. Unggah berkas CSV Anda di atas untuk menguji seluruh data institusi.")

# ==================================================
# 3. KONTROL FILTER DINAMIS (SLIDER & MULTI-SELECT)
# ==================================================
st.write("---")
st.markdown("###  Panel Filter & Pengaturan Tampilan")

col_control1, col_control2 = st.columns(2)

with col_control1:
    mode_filter = st.radio(
        "Pilih Metode Penyaringan Data Dosen:",
        ["Berdasarkan Peringkat Teratas (Top N)", "Berdasarkan Peringkat Spesifik Alternatif Pilihan"]
    )

with col_control2:
    if mode_filter == "Berdasarkan Peringkat Teratas (Top N)":
        max_display = len(df)
        default_slider = min(10, max_display)
        top_n = st.slider("Tentukan jumlah peringkat terbaik yang ingin ditampilkan:", 2, min(50, max_display), default_slider)
        list_alternatif_terpilih = None
    else:
        opsi_alternatif_all = df['Alternatif'].unique().tolist()
        list_alternatif_terpilih = st.multiselect(
            "Pilih satu atau beberapa Alternatif Dosen secara spesifik:",
            options=opsi_alternatif_all,
            default=opsi_alternatif_all[:5]
        )
        top_n = None

# Batas Crisp Boundaries berdasarkan teori sebaran data
kriteria_info = {
    'C1': {'nama': 'Student_Avg_Score', 'min': 46.94, 'max': 81.94},
    'C2': {'nama': 'Teacher_Evaluation_Score', 'min': 64.90, 'max': 100.00},
    'C3': {'nama': 'Student_Feedback_Rating', 'min': 75.00, 'max': 97.20},
    'C4': {'nama': 'Course_Completion_Rate', 'min': 81.43, 'max': 100.00},
    'C5': {'nama': 'Interactive_Sessions_Percent', 'min': 35.39, 'max': 100.00}
}

Z_MIN = 40.0
Z_MAX = 100.0

# ==================================================
# 4. MEMBERSHIP FUNCTIONS & LOGIKA TSUKAMOTO
# ==================================================
def hitung_keanggotaan(x, x_min, x_max):
    if x <= x_min: return 1.0, 0.0
    if x >= x_max: return 0.0, 1.0
    mu_rendah = (x_max - x) / (x_max - x_min)
    mu_tinggi = (x - x_min) / (x_max - x_min)
    return mu_rendah, mu_tinggi

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
    z_akhir = (Z_MIN + Z_MAX) / 2 if total_alpha == 0 else ((alpha1 * z1) + (alpha2 * z2) + (alpha3 * z3) + (alpha4 * z4)) / total_alpha
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

# PROSES HITUNG GLOBAL & FILTERING DATA
skor_final = []
for idx, row in df.iterrows():
    res = proses_tsukamoto(row['C1 (Avg Score)'], row['C2 (Eval Score)'], row['C3 (Feedback)'], row['C4 (Completion)'], row['C5 (Interactive)'])
    skor_final.append(res["z_akhir"])
    
df_rank_global = df.copy()
df_rank_global["Skor Akhir Fuzzy"] = skor_final
df_rank_global["Kategori Kualifikasi"] = df_rank_global["Skor Akhir Fuzzy"].apply(get_kategori)
df_rank_global = df_rank_global.sort_values(by="Skor Akhir Fuzzy", ascending=False).reset_index(drop=True)
df_rank_global.index = df_rank_global.index + 1
df_rank_global.index.name = "Peringkat Asli"

if mode_filter == "Berdasarkan Peringkat Teratas (Top N)":
    df_filtered = df_rank_global.head(top_n).copy()
else:
    df_filtered = df_rank_global[df_rank_global['Alternatif'].isin(list_alternatif_terpilih)].copy()
    df_filtered = df_filtered.sort_values(by="Skor Akhir Fuzzy", ascending=False)

df_filtered = df_filtered.reset_index()
df_filtered.index = df_filtered.index + 1
df_filtered.index.name = "No"

# ==================================================
# 5. STRUKTUR TAB UTAMA
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs(["📂 Dataset", "🧠 Penjelasan", "📈 Kurva", "📊 Perangkingan Akhir"])

# --- TAB 1: DATASET (DIPERBAIKI) ---
with tab1:
    st.header(" Dashboard Informasi & Basis Data CEMP")
    
    st.subheader("📋 Parameter Batas Kamus Kriteria")
    st.markdown("""
    | Kode Kriteria | Nama Metrik Pengukuran | Sifat Fitur | Batas Minimum ($X_{min}$) | Batas Maksimum ($X_{max}$) |
    | :---: | :--- | :---: | :---: | :---: |
    | **C1** | Student Average Score | Benefit | 46.94 | 81.94 |
    | **C2** | Teacher Evaluation Score | Benefit | 64.90 | 100.00 |
    | **C3** | Student Feedback Rating | Benefit | 75.00 | 97.20 |
    | **C4** | Course Completion Rate | Benefit | 81.43 | 100.00 |
    | **C5** | Interactive Sessions Percent | Benefit | 35.39 | 100.00 |
    """)
    
    st.write("---")
    st.subheader("📋 Data Mentah Alternatif Terpilih (Sesuai Panel Filter)")
    df_mentah_filtered = df[df['Alternatif'].isin(df_filtered['Alternatif'])]
    st.dataframe(df_mentah_filtered, use_container_width=True)
    
    st.write("---")
    with st.expander(f"👁️ Lihat Seluruh Master Dataset Institusi (Total: {len(df)} Baris Data)", expanded=False):
        st.dataframe(df, use_container_width=True)

# --- TAB 2: PENJELASAN ---
with tab2:
    st.header("🧠 Analisis & Penjelasan Alur Komputasi")
    
    if len(df_filtered) == 0:
        st.warning("⚠️ Tidak ada alternatif dosen yang terpilih pada panel filter di atas.")
    else:
        df_filtered['Label_Unik'] = df_filtered['Alternatif'] + " - " + df_filtered['Kode Dosen']
        opsi_dosen_inspeksi = df_filtered["Label_Unik"].tolist()
        
        selected_label = st.selectbox(
            "Pilih Kode Alternatif Dosen & Kelas untuk Inspeksi Alur Rumus (Sesuai Filter Aktif):", 
            opsi_dosen_inspeksi
        )
        
        row_data = df_filtered[df_filtered['Label_Unik'] == selected_label].iloc[0]
        
        kalkulasi = proses_tsukamoto(
            row_data['C1 (Avg Score)'], 
            row_data['C2 (Eval Score)'], 
            row_data['C3 (Feedback)'], 
            row_data['C4 (Completion)'], 
            row_data['C5 (Interactive)']
        )
        
        st.write("---")
        st.subheader("📜 Informasi Basis Aturan Fuzzy (Fuzzy Rules Base)")
        st.markdown("""
        * **[Rule 1]** IF *Student_Avg_Score* RENDAH AND *Teacher_Evaluation_Score* RENDAH AND *Student_Feedback_Rating* RENDAH AND *Course_Completion_Rate* RENDAH AND *Interactive_Sessions_Percent* RENDAH THEN Kualitas Dosen **KURANG**
        * **[Rule 2]** IF *Teacher_Evaluation_Score* TINGGI AND *Student_Feedback_Rating* TINGGI THEN Kualitas Dosen **BAGUS**
        * **[Rule 3]** IF *Student_Avg_Score* TINGGI AND *Course_Completion_Rate* TINGGI AND *Interactive_Sessions_Percent* TINGGI THEN Kualitas Dosen **BAGUS**
        * **[Rule 4]** IF *Teacher_Evaluation_Score* RENDAH AND *Student_Feedback_Rating* RENDAH THEN Kualitas Dosen **KURANG**
        """)
        
        st.write("---")
        col_proses, col_skor = st.columns([3, 2], gap="large")
        
        with col_proses:
            st.subheader("⚙️ Detail Tahapan Komputasi")
            with st.expander("🔍 Langkah 1: Proses Fuzzifikasi (Nilai Keanggotaan)", expanded=True):
                fuz_list = []
                for k_id, nilai_mu in kalkulasi["fuzzifikasi"].items():
                    nama_kolom_riil = df_filtered.columns[df_filtered.columns.str.contains(k_id)][0]
                    fuz_list.append({
                        "Kriteria": k_id,
                        "Jenis Kriteria": kriteria_info[k_id]['nama'],
                        "Nilai Riil Sesuai Skala": round(row_data[nama_kolom_riil], 2),
                        "$\mu$ RENDAH": round(nilai_mu[0], 4),
                        "$\mu$ TINGGI": round(nilai_mu[1], 4)
                    })
                st.dataframe(pd.DataFrame(fuz_list), use_container_width=True)
                
            with st.expander("🧩 Langkah 2: Proses Inferensi Aturan", expanded=True):
                st.write("Mengevaluasi basis aturan di atas menggunakan operator **MIN** (Mencari Tinggi Potong $\\alpha$):")
                for i, (alpha, z) in enumerate(kalkulasi["rules"]):
                    st.write(f"👉 **Rule {i+1}**: Ketinggian $\\alpha_{i+1}$ = **{round(alpha, 4)}** $\\rightarrow$ Nilai Konsekuen $z_{i+1}$ = **{round(z, 2)}**")

        with col_skor:
            st.subheader("🎯 Ringkasan Hasil Defuzzifikasi")
            st.latex(r'Z_{akhir} = \frac{\sum_{i=1}^{n} \alpha_i \cdot z_i}{\sum_{i=1}^{n} \alpha_i}')
            with st.container(border=True):
                st.markdown(f"### ID Dosen: **{row_data['Alternatif']}**")
                st.markdown(f"Kode Kelas/Matkul: **{row_data['Kode Dosen']}**")
                st.write("---")
                st.metric(label="Skor Final Indeks Kualitas Dosen (Z)", value=f"{kalkulasi['z_akhir']} / 100")
                st.metric(label="Predikat Kualifikasi Kategori", value=get_kategori(kalkulasi['z_akhir']))

# --- TAB 3: KURVA ---
with tab3:
    st.header("📈 Grafik Representasi Fungsi Keanggotaan Kriteria")
    st.write("Kurva pembatas himpunan bagian fuzzy yang berlaku universal untuk seluruh dataset.")
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

# --- TAB 4: PERANGKINGAN AKHIR ---
with tab4:
    st.header("📊 Hasil Konvergensi Perangkingan")
    
    if len(df_filtered) == 0:
        st.warning("⚠️ Tidak ada alternatif dosen yang terpilih pada panel filter di atas.")
    else:
        c_r1, c_r2, c_r3 = st.columns(3)
        c_r1.metric("Total Alternatif Terfilter", len(df_filtered))
        c_r2.metric("Metode Inferensi", "Tsukamoto")
        c_r3.metric(f"Rekomendasi Terbaik dari Hasil Filter", f"{df_filtered.iloc[0]['Alternatif']} ({df_filtered.iloc[0]['Kode Dosen']})")
        
        st.write("---")
        st.subheader("📋 Tabel Peringkat Dosen Hasil Penyaringan (Terurut Objektif)")
        st.dataframe(df_filtered, use_container_width=True)
        
        st.write("---")
        st.subheader("📊 Grafik Komparasi Hasil Skor Kualitas Dosen")
        
        fig, ax = plt.subplots(figsize=(12, 5))
        warna_grafik = ["gold" if i == 0 else "steelblue" for i in range(len(df_filtered))]
        batang = ax.bar(df_filtered["Alternatif"] + "\n(" + df_filtered["Kode Dosen"] + ")", df_filtered["Skor Akhir Fuzzy"], color=warna_grafik)
        
        if len(df_filtered) <= 15:
            for b in batang:
                ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{b.get_height()}", ha="center", fontsize=8, fontweight='bold')
                
        ax.set_ylabel("Skor Final (Z)")
        ax.set_ylim(0, 110)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)