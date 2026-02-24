import sqlite3
from telegram.ext import Updater, MessageHandler, Filters

import os
TOKEN = os.environ.get("TOKEN")


def handle_message(update, context):
    text = update.message.text.strip().upper()

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

print("TOKEN:", TOKEN)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


