# 🤖 Bot Pengunduh Musik Telegram

Bot Telegram sederhana yang ditulis dengan Python untuk mengunduh musik dari YouTube dalam format MP3. Dibuat agar ringan dan mudah dijalankan di Termux maupun server Linux.

## ✨ Fitur

-   Unduh musik berdasarkan **judul lagu**.
-   Unduh musik dari **link YouTube**.
-   Otomatis menghapus file setelah dikirim untuk **menghemat ruang penyimpanan**.
-   Pengecekan ukuran file untuk mencegah error (batas 50 MB).

## ⚙️ Instalasi

Ikuti langkah-langkah berikut untuk menjalankan bot ini.

1.  **Clone repositori ini:**
    ```bash
    git clone http://googleusercontent.com/github.com/
    cd nama-folder-repositori
    ```

2.  **Instal semua dependensi yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```
    *Catatan: Pastikan `python` dan `ffmpeg` sudah terinstal di sistem Anda.*

## 🔧 Konfigurasi

Sebelum menjalankan bot, Anda perlu memasukkan Token API rahasia Anda.

1.  Cari file `config.py.example` di dalam folder proyek.
2.  **Salin dan ganti nama** file tersebut menjadi `config.py`.
3.  Buka file `config.py` dan masukkan token bot Anda yang didapat dari **@BotFather**.

    ```python
    # Ganti dengan token bot Anda
    TOKEN = "12345:ABCDEF...TOKEN_ASLI_ANDA"
    ```

## ▶️ Menjalankan Bot

Setelah konfigurasi selesai, jalankan bot dengan perintah:
```bash
python downloader_bot.py
