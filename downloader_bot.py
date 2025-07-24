import logging
import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Mengimpor TOKEN dari file config.py
from config import TOKEN

# Konfigurasi logging untuk menampilkan info di terminal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- FUNGSI-FUNGSI COMMAND HANDLER ---

def start(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan sambutan ketika pengguna mengirim /start."""
    user = update.effective_user
    update.message.reply_html(
        f"👋 Halo, {user.mention_html()}!\n\n"
        "Saya adalah bot pengunduh musik. Kirim perintah `/music` diikuti judul lagu, dan saya akan mengirimkan filenya dalam format MP3.\n\n"
        "Contoh: `/music Alan Walker Faded`"
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan bantuan."""
    update.message.reply_text(
        "Cara Penggunaan:\n"
        "Kirim perintah `/music <judul lagu atau link youtube>`\n\n"
        "Bot akan mencari, mengunduh, dan mengirimkannya kepadamu."
    )

def music(update: Update, context: CallbackContext) -> None:
    """Mencari, mengunduh, dan mengirim musik dari YouTube."""
    query = ' '.join(context.args)

    if not query:
        update.message.reply_text("Tolong berikan judul lagu atau link YouTube setelah perintah /music.")
        return

    chat_id = update.message.chat_id
    processing_message = context.bot.send_message(
        chat_id, 
        f"🔎 Sedang mencari dan memproses: *{query}*...", 
        parse_mode='Markdown'
    )

    downloaded_file = None
    try:
        command = [
            'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
            '--audio-quality', '0', '-o', '%(title)s.%(ext)s',
            f"ytsearch1:{query}"
        ]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)

        for file in os.listdir('.'):
            if file.endswith('.mp3'):
                downloaded_file = file
                break
        
        if downloaded_file:
            file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
            logger.info(f"Ukuran file: {file_size_mb:.2f} MB")

            if file_size_mb > 49:
                context.bot.send_message(chat_id, f"❌ Gagal mengirim: File lagu terlalu besar ({file_size_mb:.2f} MB). Batas maksimal adalah 50 MB.")
            else:
                context.bot.send_message(chat_id, "✅ Unduhan selesai! Mengirim file audio...")
                with open(downloaded_file, 'rb') as audio_file:
                    context.bot.send_audio(
                        chat_id=chat_id, 
                        audio=audio_file, 
                        caption=f"🎧 {os.path.basename(downloaded_file)}\n\nDiunduh oleh @{context.bot.username}",
                        timeout=300 # Memberi waktu 5 menit untuk upload
                    )
        else:
            raise FileNotFoundError("File MP3 tidak ditemukan setelah proses unduh selesai.")

    except subprocess.CalledProcessError:
        logger.error(f"Gagal mengunduh '{query}'. Mungkin tidak ditemukan.")
        context.bot.send_message(chat_id, "❌ Maaf, lagu tidak ditemukan atau terjadi kesalahan saat mengunduh.")
    
    except Exception as e:
        logger.error(f"Terjadi error tak terduga: {e}", exc_info=True)
        context.bot.send_message(chat_id, f"❌ Gagal mengirim file. Kemungkinan karena koneksi upload putus atau masalah lain.\n\n`Error: {e}`")
    
    finally:
        # Hapus pesan "sedang memproses"
        if 'processing_message' in locals():
            context.bot.delete_message(chat_id, processing_message.message_id)
        # Pastikan file yang mungkin tersisa terhapus
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("music", music))

    updater.start_polling()
    logger.info("✅ Bot telah berhasil dimulai!")
    updater.idle()

if __name__ == '__main__':
    main()
