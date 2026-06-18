# 🌟 Sistem Pendukung Keputusan Pemilihan Dosen Terbaik — Fuzzy Tsukamoto

Aplikasi berbasis web ini dikembangkan menggunakan **Streamlit** dan **Python** untuk menghitung indeks kualitas kualifikasi dosen secara objektif dan transparan. Sistem menggunakan metode **Fuzzy Logic Tsukamoto** untuk memproses data multi-kriteria yang bersumber dari platform *Teaching Quality Evaluation* (**CEMP**).

Proyek ini disusun untuk memenuhi tugas besar mata kuliah **Sistem Cerdas dan Pendukung Keputusan**, Program Studi Informatika, Universitas Pembangunan Nasional "Veteran" Yogyakarta.

---

## 👥 Tim Pengembang
* **Partawijaya Rihal Dariretci** — (123240181)
* **Muhammad Azfa Imaduddin** — (123240208)

---

## 🎯 Fitur Utama Aplikasi

1. **📂 Master Dataset & Dinamis File Uploader**:
   * Mendukung unggah data riil hasil ekspor platform CEMP berformat `.csv`.
   * Normalisasi otomatis skala kriteria (misal: pengali khusus untuk menyesuaikan rentang nilai evaluasi & umpan balik).
   * Fitur *fallback* otomatis ke data sampel cetak (5 data alternatif default) jika pengguna belum mengunggah file.
2. **🎛️ Panel Filter Interaktif**:
   * **Mode Top N**: Menyaring dan menampilkan peringkat terbaik (*slider* dinamis).
   * **Mode Alternatif Spesifik**: Memilih multi-alternatif dosen tertentu saja secara fleksibel melalui komponen *multi-select*.
3. **🧠 Analisis & Inspeksi Alur Rumus (Bebas Bug)**:
   * Melacak perhitungan langkah demi langkah secara mendalam untuk satu dosen dan kelas tertentu.
   * Menggunakan label unik gabungan (`Teacher_ID - Course_ID`) untuk mencegah duplikasi atau data macet saat dosen mengajar lebih dari satu mata kuliah.
   * Menampilkan visualisasi tabel Fuzzifikasi, nilai ketinggian potong $\alpha$, konsekuen $z$, hingga rumus LaTeX Defuzzifikasi.
4. **📈 Grafik Fungsi Keanggotaan**:
   * Plot kurva keanggotaan fuzzy (`RENDAH` vs `TINGGI`) untuk 5 kriteria secara universal menggunakan *Matplotlib*.
5. **📊 Konvergensi & Visualisasi Perangkingan**:
   * Tabel keputusan akhir yang terurut secara objektif berdasarkan skor tertinggi.
   * Grafik batang komparasi interaktif dengan sorotan khusus (*gold highlight*) pada rekomendasi dosen terbaik.
6. **🎨 Estetika UI Modern (Premium Glassmorphism)**:
   * Kustomisasi CSS internal untuk mempercantik komponen *Tabs* (warna hijau *Emerald* pada tab aktif), *Metric Cards* dengan efek bayangan melayang (*hover effect*), serta tipografi bersih berbasis font *Inter*.

---

## 📐 Pemodelan Kriteria & Semesta Pembicaraan

Sistem ini mengevaluasi kinerja dosen berdasarkan 5 kriteria utama (Benefit):

| Kode | Kriteria | Sifat | Rentang Semesta ($X_{min}$ - $X_{max}$) |
| :---: | :--- | :---: | :---: |
| **C1** | Student Average Score | Benefit | 46.94 - 81.94 |
| **C2** | Teacher Evaluation Score | Benefit | 64.90 - 100.00 |
| **C3** | Student Feedback Rating | Benefit | 75.00 - 97.20 |
| **C4** | Course Completion Rate | Benefit | 81.43 - 100.00 |
| **C5** | Interactive Sessions Percent | Benefit | 35.39 - 100.00 |

### 📜 Basis Aturan Fuzzy (Fuzzy Rules Base)
* **[Rule 1]** IF *C1* RENDAH AND *C2* RENDAH AND *C3* RENDAH AND *C4* RENDAH AND *C5* RENDAH THEN Kualitas Dosen **KURANG**
* **[Rule 2]** IF *C2* TINGGI AND *C3* TINGGI THEN Kualitas Dosen **BAGUS**
* **[Rule 3]** IF *C1* TINGGI AND *C4* TINGGI AND *C5* TINGGI THEN Kualitas Dosen **BAGUS**
* **[Rule 4]** IF *C2* RENDAH AND *C3* RENDAH THEN Kualitas Dosen **KURANG**

---