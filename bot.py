print("BOT STARTED")

import sqlite3
import datetime
from telegram.ext import Updater, MessageHandler, Filters
import os

TOKEN = os.environ.get("TOKEN")


def handle_message(update, context):
    text = update.message.text.strip().upper()

    # ======================
    # CASE AREA
    # ======================
    if text.startswith("AREA "):
        kode = text.split(" ")[1]

        conn = sqlite3.connect("toko.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM data WHERE KODETOKO=?", (kode,))
        result = cursor.fetchone()
        conn.close()

        if result:
            balasan = f"""
KODETOKO : {result[0]}
NAMATOKO : {result[1]}
ASPV     : {result[2]}
AMGR     : {result[3]}
ALAMAT   : {result[4]}
JAM      : {result[5]}
KORDINAT : {result[6]}
"""
        else:
            balasan = "Data toko tidak ditemukan."

        update.message.reply_text(balasan)

    # ======================
    # CASE EVEN
    # ======================
    elif text.startswith("EVEN "):
        parts = text.split()

        if len(parts) >= 2:
            kode = parts[1]

            # Ambil periode otomatis (contoh: 2602)
            now = datetime.datetime.now()
            periode = now.strftime("%y%m")

            nama_file_even = f"EVEN_{periode}.DB"

            try:
                conn = sqlite3.connect("toko.db")
                cursor = conn.cursor()

                # Attach database
                cursor.execute(f"ATTACH DATABASE '{nama_file_even}' AS even_db")
                cursor.execute("ATTACH DATABASE 'RITSBY.DB' AS rit_db")

                query = f"""
                SELECT 
                    A.TOKO,
                    A.NAMA,
                    GROUP_CONCAT(A.TGL),
                    B.RIT,
                    B.KIRIM
                FROM even_db.EVEN_{periode} A
                LEFT JOIN rit_db.RITSBY B
                ON A.TOKO = B.TOKO
                WHERE A.TOKO = ?
                GROUP BY A.TOKO
                """

                cursor.execute(query, (kode,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    balasan = f"""
TOKO        : {result[0]}
NAMA        : {result[1]}
TGL EVEN    : {result[2]}
JADWAL KIRIM: {result[3]} {result[4]}
"""
                else:
                    balasan = "Data EVEN tidak ditemukan."

            except Exception as e:
                balasan = f"Terjadi error: {str(e)}"

            update.message.reply_text(balasan)




print("TOKEN:", TOKEN)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

