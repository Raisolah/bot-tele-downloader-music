#!/bin/bash

# 1. Update Sistem & Install Semua Alat Sekaligus
echo ">>> Mengupdate sistem dan menginstall alat (Python, Git, FFmpeg, Screen)..."
apt update && apt upgrade -y && apt install python3 python3-pip git ffmpeg screen -y
Git Clone https://github.com/Raisolah/bot-tele-downloader-music.git
cd bot-tele-downloader-music


# 2. Install Semua Pustaka Python dari requirements.txt
echo ">>> Menginstall semua pustaka Python yang dibutuhkan..."
pip3 install -r requirements.txt

# 3. Memberikan Instruksi Terakhir
echo ""
echo "✅ INSTALASI TEKNIS SELESAI!"
echo "========================================================"
echo "SEKARANG, LAKUKAN 2 LANGKAH MANUAL INI:"
echo ""
echo "1. BUAT FILE KONFIGURASI:"
echo "   - Buat file token: nano Config.py (isi dengan: TOKEN = \"TOKEN_ANDA\")"
echo "   - Buat file cookies: nano cookies.txt (tempel isi cookies Anda)"
echo ""
echo "2. JALANKAN BOT DI DALAM 'SCREEN':"
echo "   - Buat sesi baru: screen -S bot"
echo "   - Jalankan bot: python3 downloader_bot.py"
echo "   - Keluar dari screen (agar bot tetap jalan): Tekan Ctrl+A lalu D"
echo "========================================================"
