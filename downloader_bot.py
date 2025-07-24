
import logging
import os
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Impor pustaka pihak ketiga
import yt_dlp
from tqdm import tqdm

# Mengimpor TOKEN dari file config.py
from config import TOKEN

# --- Konfigurasi Awal ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)
BUSY_LOCK = threading.Lock() # Kunci untuk sistem antrean

# Batas ukuran file dalam MB
MAX_FILE_SIZE_MB = 25

# --- FUNGSI-FUNGSI COMMAND HANDLER ---

def start(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan sambutan ketika pengguna mengirim /start."""
    user = update.effective_user
    update.message.reply_html(
        f"👋 Halo, {user.mention_html()}!\n\n"
        "Saya adalah bot pengunduh musik versi canggih. Kirim perintah `/music` diikuti judul lagu, dan saya akan bekerja untukmu.\n\n"
        "Fitur: Batas unduh 25 MB, sistem antrean, dan tampilan loading keren!",
        reply_to_message_id=update.message.message_id
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan bantuan."""
    update.message.reply_text(
        "Cara Penggunaan:\n"
        "Kirim perintah `/music <judul lagu atau link youtube>`\n\n"
        "Bot akan mencari, mengunduh, dan mengirimkannya kepadamu.",
        reply_to_message_id=update.message.message_id
    )

def music(update: Update, context: CallbackContext) -> None:
    """Fungsi utama untuk mencari, mengunduh, dan mengirim musik."""
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text(
            "Tolong berikan judul lagu atau link YouTube setelah perintah /music.",
            reply_to_message_id=update.message.message_id
        )
        return

    # --- Sistem Antrean ---
    if BUSY_LOCK.locked():
        update.message.reply_text(
            "⏳ Bot sedang sibuk memproses permintaan lain. Mohon tunggu sebentar, ya!",
            reply_to_message_id=update.message.message_id
        )
        return

    with BUSY_LOCK:
        chat_id = update.message.chat_id
        status_message = context.bot.send_message(
            chat_id, 
            "🔎 Mencari lagu...",
            reply_to_message_id=update.message.message_id
        )
        
        downloaded_file_path = None
        try:
            # --- Tampilan Loading di Terminal (dengan TQDM) ---
            class TqdmLogger:
                def __init__(self, pbar):
                    self.pbar = pbar
                def debug(self, msg):
                    if msg.startswith('[download]'):
                         self.pbar.update(1)
                def info(self, msg): pass
                def warning(self, msg): pass
                def error(self, msg): pass

            # Opsi untuk yt-dlp
            ydl_opts = {
                'cookiefile': 'cookies.txt', # <-- Menggunakan file cookies
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
                'logger': logging.getLogger('yt_dlp_process'),
                'progress_hooks': [],
            }
            
            # Mendapatkan info video terlebih dahulu
            with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True, 'cookiefile': 'cookies.txt'}) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                if not info['entries']:
                    raise ValueError("Lagu tidak ditemukan.")
                video_info = info['entries'][0]
                title = video_info.get('title', 'audio')
                context.bot.edit_message_text(
                    text=f"✅ Lagu ditemukan: *{title}*\n\n📥 Mulai mengunduh...",
                    chat_id=chat_id,
                    message_id=status_message.message_id,
                    parse_mode='Markdown'
                )

            # --- Proses Unduhan dengan Progress Bar ---
            with tqdm(total=100, unit='%', desc=f"Downloading '{title}'") as pbar:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        total_bytes = d.get('total_bytes')
                        downloaded_bytes = d.get('downloaded_bytes')
                        if total_bytes and downloaded_bytes:
                            percentage = (downloaded_bytes / total_bytes) * 100
                            pbar.n = round(percentage)
                            pbar.refresh()
                    elif d['status'] == 'finished':
                        pbar.n = 100
                        pbar.refresh()
                
                ydl_opts['progress_hooks'] = [progress_hook]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_info['webpage_url']])
                    downloaded_file_path = ydl.prepare_filename(video_info).rsplit('.', 1)[0] + '.mp3'

            # --- Cek Ukuran File & Kirim ---
            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size_mb = os.path.getsize(downloaded_file_path) / (1024 * 1024)
                logger.info(f"File '{downloaded_file_path}' berhasil diunduh. Ukuran: {file_size_mb:.2f} MB")

                if file_size_mb > MAX_FILE_SIZE_MB:
                    context.bot.edit_message_text(
                        text=f"❌ Unduhan dibatalkan. File lagu terlalu besar ({file_size_mb:.2f} MB). Batas maksimal adalah {MAX_FILE_SIZE_MB} MB.",
                        chat_id=chat_id,
                        message_id=status_message.message_id
                    )
                    return

                context.bot.edit_message_text(text="🚀 Mengirim file audio...", chat_id=chat_id, message_id=status_message.message_id)
                with open(downloaded_file_path, 'rb') as audio_file:
                    context.bot.send_audio(
                        chat_id=chat_id, 
                        audio=audio_file, 
                        caption=f"🎧 {os.path.basename(downloaded_file_path)}\n\nDiunduh oleh @{context.bot.username}",
                        reply_to_message_id=update.message.message_id,
                        timeout=300
                    )
            else:
                raise FileNotFoundError("File MP3 tidak ditemukan setelah proses unduh.")

        except Exception as e:
            logger.error(f"Terjadi error: {e}", exc_info=True)
            context.bot.edit_message_text(
                text=f"❌ Maaf, terjadi kesalahan.\n`{str(e)}`",
                chat_id=chat_id,
                message_id=status_message.message_id,
                parse_mode='Markdown'
            )
        
        finally:
            # --- Hapus Pesan Status & File Lokal ---
            context.bot.delete_message(chat_id, status_message.message_id)
            if downloaded_file_path and os.path.exists(downloaded_file_path):
                os.remove(downloaded_file_path)
                logger.info(f"File '{downloaded_file_path}' telah dihapus.")

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("music", music))

    updater.start_polling()
    logger.info("✅ Bot Canggih telah berhasil dimulai!")
    updater.idle()

if __name__ == '__main__':
    main()
