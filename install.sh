#!/bin/bash

# 1. Hentikan skrip jika ada perintah yang gagal
set -e

# 2. Update Sistem & Install Semua Alat Sekaligus
echo ">>> Mengupdate sistem dan menginstall alat (Python, Git, FFmpeg, Screen)..."
apt-get update && apt-get install -y python3 python3-pip git ffmpeg screen

# 3. Hapus folder lama (jika ada) dan unduh yang baru
echo ">>> Mengunduh file bot dari GitHub..."
rm -rf bot-tele-downloader-music
git clone https://github.com/Raisolah/bot-tele-downloader-music.git
cd bot-tele-downloader-music

# 4. Install semua pustaka Python
echo ">>> Menginstall semua pustaka Python yang dibutuhkan..."
pip3 install -r requirements.txt

# 5. Minta input dari user untuk membuat file konfigurasi secara otomatis
echo "========================================================"
echo "SEKARANG, MASUKKAN DATA KONFIGURASI ANDA:"
read -p "   ➡️ Masukkan TOKEN Bot Anda: " user_token
read -p "   ➡️ Masukkan COOKIE Anda: " user_cookie

# 6. Buat file Config.py dan cookies.txt
echo ">>> Membuat file Config.py dan cookies.txt..."
echo "TOKEN = \"${user_token}\"" > Config.py
echo "${user_cookie}" > cookies.txt

# 7. Memberikan Instruksi Terakhir
echo "========================================================"
echo "✅ SEMUA SELESAI & SUDAH TERKONFIGURASI!"
echo "Anda sekarang sudah berada di dalam folder bot."
echo ""
echo "Untuk menjalankan bot, cukup ketik perintah di bawah ini:"
echo "   screen -S bot python3 downloader_bot.py"
echo ""
echo "Untuk keluar dari screen (agar bot tetap jalan), tekan Ctrl+A lalu D."
echo "========================================================"
