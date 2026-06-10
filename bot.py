print("BOT STARTED")

import sqlite3
import datetime
import pytz
from telegram.ext import Updater, MessageHandler, Filters
import os

TOKEN = os.environ.get("TOKEN")

# Zona waktu Indonesia (WIB = UTC+7)
WIB = pytz.timezone('Asia/Jakarta')


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
Kode Toko : {result[0]}
Nama Toko : {result[1]}
ASPV     : {result[2]}
AMGR     : {result[3]}
Alamat   : {result[4]}
Jam Buka : {result[5]}
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

            # Ambil waktu sekarang dalam WIB
            now = datetime.datetime.now(WIB)
            periode = now.strftime("%y%m")

            # Ambil nama bulan Bahasa Indonesia
            bulan = int(periode[2:])
            nama_bulan = [
                "JANUARI","FEBRUARI","MARET","APRIL","MEI","JUNI",
                "JULI","AGUSTUS","SEPTEMBER","OKTOBER","NOVEMBER","DESEMBER"
            ][bulan-1]

            nama_file_even = f"EVEN_{periode}.DB"

            try:
                conn = sqlite3.connect("toko.db")
                cursor = conn.cursor()

                # Attach database tambahan
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
PERIODE     : {nama_bulan}
TGL EVEN    : {result[2]}
JADWAL KIRIM: {result[3]} {result[4]}
"""
                else:
                    balasan = "Data EVEN tidak ditemukan."

            except Exception as e:
                balasan = f"Terjadi error: {str(e)}"

            update.message.reply_text(balasan)

    # ======================
    # CASE TODAYEVEN
    # ======================
    elif text.startswith("TODAYEVEN"):
        # Ambil waktu sekarang dalam WIB
        now = datetime.datetime.now(WIB)
        today_day = str(now.day)  # tanggal (1-31)
        periode = now.strftime("%y%m")  # contoh: "2604"
        
        nama_file_even = f"EVEN_{periode}.DB"
        nama_bulan = [
            "JANUARI","FEBRUARI","MARET","APRIL","MEI","JUNI",
            "JULI","AGUSTUS","SEPTEMBER","OKTOBER","NOVEMBER","DESEMBER"
        ][now.month-1]
        
        try:
            conn = sqlite3.connect("toko.db")
            cursor = conn.cursor()
            
            # Attach database even
            cursor.execute(f"ATTACH DATABASE '{nama_file_even}' AS even_db")
            
            # Query mencari toko yang punya even hari ini (TGL = tanggal hari ini)
            query = f"""
            SELECT 
                TOKO,
                NAMA
            FROM even_db.EVEN_{periode}
            WHERE TGL = ?
            ORDER BY TOKO
            """
            
            cursor.execute(query, (today_day,))
            results = cursor.fetchall()
            conn.close()
            
            if results:
                # Format balasan
                jam_sekarang = now.strftime("%H:%M:%S")
                balasan = f"📅 EVEN HARI INI ({now.day} {nama_bulan} {now.year})\n"
                balasan += f"⏰ Waktu: {jam_sekarang} WIB\n"
                balasan += "=" * 30 + "\n\n"
                
                for row in results:
                    balasan += f"🏪 {row[0]} - {row[1]}\n"
                
                balasan += f"\n✅ Total toko: {len(results)}"
            else:
                balasan = f"❌ Tidak ada toko yang memiliki jadwal even pada tanggal {now.day} {nama_bulan} {now.year}"
        
        except Exception as e:
            balasan = f"Terjadi error: {str(e)}"
        
        update.message.reply_text(balasan)

    # ======================
    # CASE DAYEVEN
    # ======================
    elif text.startswith("DAYEVEN "):
        parts = text.split()
        
        if len(parts) >= 2:
            tgl_yang_dicari = parts[1]  # contoh: "21" atau "23"
            
            # Validasi: pastikan input adalah angka 1-31
            if not tgl_yang_dicari.isdigit() or int(tgl_yang_dicari) < 1 or int(tgl_yang_dicari) > 31:
                balasan = "❌ Format salah! Gunakan: DAYEVEN 21 (angka 1-31)"
                update.message.reply_text(balasan)
                return
            
            # Ambil waktu sekarang dalam WIB
            now = datetime.datetime.now(WIB)
            periode = now.strftime("%y%m")
            nama_file_even = f"EVEN_{periode}.DB"
            nama_bulan = [
                "JANUARI","FEBRUARI","MARET","APRIL","MEI","JUNI",
                "JULI","AGUSTUS","SEPTEMBER","OKTOBER","NOVEMBER","DESEMBER"
            ][now.month-1]
            
            try:
                conn = sqlite3.connect("toko.db")
                cursor = conn.cursor()
                
                # Attach database even
                cursor.execute(f"ATTACH DATABASE '{nama_file_even}' AS even_db")
                
                # Query mencari toko yang punya even pada tanggal yang diminta
                query = f"""
                SELECT 
                    TOKO,
                    NAMA
                FROM even_db.EVEN_{periode}
                WHERE TGL = ?
                ORDER BY TOKO
                """
                
                cursor.execute(query, (tgl_yang_dicari,))
                results = cursor.fetchall()
                conn.close()
                
                if results:
                    # Format balasan
                    balasan = f"📅 EVEN TANGGAL {tgl_yang_dicari} {nama_bulan} {now.year}\n"
                    balasan += "=" * 35 + "\n\n"
                    
                    for row in results:
                        balasan += f"🏪 {row[0]} - {row[1]}\n"
                    
                    balasan += f"\n✅ Total toko: {len(results)}"
                else:
                    balasan = f"❌ Tidak ada toko yang memiliki jadwal even pada tanggal {tgl_yang_dicari} {nama_bulan} {now.year}"
            
            except Exception as e:
                balasan = f"Terjadi error: {str(e)}"
            
            update.message.reply_text(balasan)
        else:
            update.message.reply_text("❌ Format salah! Gunakan: DAYEVEN 21")
            
    # ======================
    # CASE TRENSONE
    # ======================
    elif text.startswith("TRENSONE "):
        parts = text.split()
        
        if len(parts) >= 2:
            kdtk = parts[1].upper()
            
            try:
                conn = sqlite3.connect("TRENSO_FIXED.DB")
                cursor = conn.cursor()
                
                query = """
                SELECT KDTK, NAMA, TGL_SO, BULAN_SO, SOTIME, RP_NKL, RP_GANTI_NKL 
                FROM TRENSO 
                WHERE KDTK = ?
                ORDER BY BULAN_SO DESC 
                LIMIT 24
                """
                
                cursor.execute(query, (kdtk,))
                results = cursor.fetchall()
                conn.close()
                
                if results:
                    # Ambil nama toko dari record pertama
                    nama_toko = results[0][1] if results[0][1] else "-"
                    
                    # Header dengan nama toko
                    balasan = f"📊 DATA TRENSO - {kdtk} : {nama_toko}\n"
                    balasan += "──────────────────────────────────────────────────────────────────────\n"
                    balasan += "No TGL SO    | BLN SO | SOTIME   | RP_NKL     | RP_GANTI_NKL\n"
                    balasan += "──────────────────────────────────────────────────────────────────────\n"
                    
                    for i, row in enumerate(results, 1):
                        tgl_so = row[2] if row[2] else "-"
                        # Format tanggal dari YYYY-MM-DD ke DD/MM/YYYY
                        if tgl_so != "-" and "-" in tgl_so:
                            parts_tgl = tgl_so.split("-")
                            tgl_so = f"{parts_tgl[2]}/{parts_tgl[1]}/{parts_tgl[0]}"
                        
                        bulan_so = row[3] if row[3] else "-"
                        sotime = row[4] if row[4] else "-"
                        rp_nkl = f"{row[5]:,.0f}" if row[5] else "0"
                        rp_ganti = f"{row[6]:,.0f}" if row[6] else "0"
                        
                        balasan += f"{i:2} {tgl_so} | {bulan_so} | {sotime:8} | {rp_nkl:>10} | {rp_ganti:>12}\n"
                    
                    balasan += "──────────────────────────────────────────────────────────────────────\n"
                    balasan += f"✅ Total: {len(results)} record"
                    
                    if len(balasan) > 4000:
                        balasan = balasan[:4000] + "\n\n... (data terpotong)"
                else:
                    balasan = f"❌ Data TRENSO tidak ditemukan untuk kode: {kdtk}"
            
            except Exception as e:
                balasan = f"Terjadi error: {str(e)}"
            
            update.message.reply_text(balasan)
        else:
            update.message.reply_text("❌ Format salah! Gunakan: TRENSONE KDTK")
    else:
        update.message.reply_text(
            "Format tidak dikenali.\nGunakan:\n"
            "AREA KODETOKO\n"
            "EVEN KODETOKO\n"
            "TODAYEVEN\n"
            "DAYEVEN 21\n"
            "TRENSO"
        )


print("TOKEN:", TOKEN)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
