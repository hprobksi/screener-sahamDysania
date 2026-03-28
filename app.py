import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go
import urllib.request
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components
import google.generativeai as genai

# Set Layout Full Width
st.set_page_config(page_title="Screener Saham Pro", layout="wide", initial_sidebar_state="expanded")

# --- DAFTAR SAHAM (DIPINDAH KE ATAS AGAR MESIN BERITA BISA MEMBACANYA) ---
daftar_lq45 = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", 
    "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", 
    "BRPT.JK", "CPIN.JK", "EMTK.JK", "ESSA.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", 
    "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", "ITMG.JK", 
    "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MTEL.JK", "PGAS.JK", 
    "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SRTG.JK", "TLKM.JK", "TOWR.JK", 
    "UNTR.JK", "UNVR.JK"
]

# --- 2. SUNTIKAN CSS KUSTOM UNTUK MAKRO & SEKTOR ---
st.markdown("""
<style>
    /* CSS UNTUK KARTU MAKRO ATAS (IMAGE 9) */
    .card-blue { background-color: #4e73df; color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .card-green { background-color: #1cc88a; color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .card-yellow { background-color: #f6c23e; color: black; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .card-red { background-color: #e74a3b; color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .card-title { font-size: 14px; font-weight: bold; margin-bottom: 5px; opacity: 0.9; }
    .card-value { font-size: 28px; font-weight: bold; margin: 0; }
    .card-delta { font-size: 14px; margin-top: 5px; }

    /* CSS BARU UNTUK KARTU SEKTOR GAYA STOCKBIT - DIPERBARUI UNTUK 4 KOLOM */
    .sector-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px; }
    .sector-card { background-color: #1e1e1e; color: white; padding: 15px; border-radius: 10px; border: 1px solid #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); }
    .sector-icon-row { display: flex; align-items: center; justify-content: center; flex-direction: column; margin-bottom: 10px; }
    .sector-icon { font-size: 32px; margin-bottom: 5px; color: #1cc88a; }
    .sector-name { font-size: 11px; font-weight: bold; color: #b3b3b3; text-transform: uppercase; letter-spacing: 1px; text-align: center; }
    .sector-perf { font-size: 16px; font-weight: bold; margin-top: 5px; text-align: center; }
    .sector-pred { font-size: 10px; font-weight: bold; margin-top: 10px; color: #4e73df; text-align: center; }
    .text-green { color: #1cc88a; }
    .text-red { color: #e74a3b; }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI PEMBUAT KARTU ---
def create_card(title, value, delta, color_class):
    return f"""
    <div class="{color_class}">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        <div class="card-delta">{delta}</div>
    </div>
    """


# --- 1. SIDEBAR (PANEL SEBELAH KIRI) ---
with st.sidebar:
    st.image("profil.jpg", width=150) 
    st.title("Dysania")
    st.markdown("---")
    
    # MENANAMKAN API KEY SECARA PERMANEN (LOKAL)
    st.subheader("🔑 Status Otak AI")
    
   # MENGAMBIL KUNCI DARI BRANKAS RAHASIA STREAMLIT
    try:
        api_key_dysania = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key_dysania)
        st.success("🧠 Otak Dysania Aktif! (Mode Flash)")
    except Exception as e:
        st.error("⚠️ API Key tidak ditemukan di brankas Secrets.")=api_key_dysania)
        st.success("🧠 Otak Dysania Aktif! (Mode Pro)")
    except Exception as e:
        st.error(f"Gagal menghubungkan otak AI: {e}")
        
    st.markdown("---")
    
    # ... (lanjutkan ke kode Waktu Sistem) ...
    # ... (lanjutkan ke kode Waktu Sistem) ...
    
    tz = pytz.timezone('Asia/Jakarta')
    sekarang = datetime.now(tz)
    hari_ini = sekarang.weekday() 
    jam = sekarang.hour
    menit = sekarang.minute

    st.subheader("🕒 Waktu Sistem (WIB)")
    st.write(f"**{sekarang.strftime('%A, %H:%M')}**")
    if st.button("🔄 Update Waktu", use_container_width=True):
        st.rerun()
        
    st.markdown("---")
    status_waktu, saran_aksi = "", ""
    if hari_ini == 4 and (jam >= 15 and menit >= 45) or hari_ini in [5, 6]:
        status_waktu = "🟢 WAKTU EMAS (PERSIAPAN SENIN)"
        saran_aksi = "Bursa tutup. Lakukan scan untuk mencari kandidat Fast Swing."
    elif hari_ini == 0 and (jam >= 9 and jam <= 11):
        status_waktu = "🔵 WAKTU ENTRY (SENIN PAGI)"
        saran_aksi = "Waktu eksekusi! Antre beli di area Ideal dan pasang Auto-Sell."
    elif hari_ini == 4 and jam < 15:
        status_waktu = "🟠 HARI JUMAT (CLEARING)"
        saran_aksi = "Evaluasi portofolio. Jual saham yang mandek agar cash aman."
    elif hari_ini < 4 and jam >= 16:
        status_waktu = "🟡 EVALUASI HARIAN"
        saran_aksi = "Bursa tutup. Pantau apakah harga hari ini menyentuh target TP."
    else:
        status_waktu = "🔴 BURSA BERJALAN"
        saran_aksi = "Pasar aktif. Biarkan Auto-Order yang bekerja."
        
    st.info(f"**Status:** {status_waktu}\n\n**Aksi:** {saran_aksi}")

# --- HALAMAN UTAMA KANAN ---
st.title("📊 Dashbord Kondisi Pasar & Analisa")
st.write("Sistem Top-Down Analysis: Prediksi arah IHSG berdasarkan sentimen Global dan Teknikal.")
st.markdown("<br>", unsafe_allow_html=True)

# --- 2. FITUR: PREDIKSI ARAH IHSG (TIME-AWARE) ---
try:
    tickers_makro = yf.Tickers("^JKSE ^DJI IDR=X GC=F")
    data_makro = tickers_makro.history(period="5d")
    
    ihsg_close = data_makro['Close']['^JKSE'].dropna()
    ihsg_terakhir = ihsg_close.iloc[-1]
    ihsg_kemarin = ihsg_close.iloc[-2]
    perubahan_ihsg = ihsg_terakhir - ihsg_kemarin
    persen_ihsg = (perubahan_ihsg / ihsg_kemarin) * 100
    ihsg_full = yf.Ticker("^JKSE").history(period="2mo")
    ihsg_full['MA20'] = ihsg_full['Close'].rolling(window=20).mean()
    ihsg_ma20 = ihsg_full['MA20'].iloc[-1]
    tren_teknikal_ihsg = 1 if ihsg_terakhir > ihsg_ma20 else -1

    dji_close = data_makro['Close']['^DJI'].dropna()
    persen_dji = ((dji_close.iloc[-1] - dji_close.iloc[-2]) / dji_close.iloc[-2]) * 100
    skor_dji = 1 if persen_dji > 0 else -1

    idr_close = data_makro['Close']['IDR=X'].dropna()
    persen_idr = ((idr_close.iloc[-1] - idr_close.iloc[-2]) / idr_close.iloc[-2]) * 100
    skor_idr = 1 if persen_idr < 0 else -1 

    gold_close = data_makro['Close']['GC=F'].dropna()
    persen_gold = ((gold_close.iloc[-1] - gold_close.iloc[-2]) / gold_close.iloc[-2]) * 100
    skor_gold = 1 if persen_gold > 0 else -1

    target_prediksi = "SENIN DEPAN" if (hari_ini == 4 and jam >= 16 or hari_ini in [5, 6]) else ("BESOK" if jam >= 16 else "HARI INI")
    total_skor = tren_teknikal_ihsg + skor_dji + skor_idr + skor_gold
    
    # TAMPILAN KARTU WARNA-WARNI
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(create_card("IHSG (Jakarta)", f"{ihsg_terakhir:,.2f}", f"{'▲' if persen_ihsg > 0 else '▼'} {persen_ihsg:.2f}%", "card-blue"), unsafe_allow_html=True)
    with col_m2:
        st.markdown(create_card("Dow Jones (AS)", f"{dji_close.iloc[-1]:,.0f}", f"{'▲' if persen_dji > 0 else '▼'} {persen_dji:.2f}%", "card-green"), unsafe_allow_html=True)
    with col_m3:
        st.markdown(create_card("USD/IDR (Kurs)", f"Rp {idr_close.iloc[-1]:,.0f}", f"{'▲' if persen_idr > 0 else '▼'} {persen_idr:.2f}%", "card-yellow"), unsafe_allow_html=True)
    with col_m4:
        st.markdown(create_card("Emas Global", f"${gold_close.iloc[-1]:,.1f}", f"{'▲' if persen_gold > 0 else '▼'} {persen_gold:.2f}%", "card-red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    alasan_prediksi = f"**Analisa Pembentuk Tren {target_prediksi.title()}:**\n- Bursa AS (Dow Jones): {'Naik 🟢' if skor_dji > 0 else 'Turun 🔴'}\n- Kurs Rupiah: {'Menguat 🟢' if skor_idr > 0 else 'Melemah 🔴'}\n- Emas Global: {'Naik 🟢' if skor_gold > 0 else 'Turun 🔴'}\n- Tren MA20 IHSG Saat Ini: {'Uptrend 🟢' if tren_teknikal_ihsg > 0 else 'Downtrend 🔴'}"

    if total_skor >= 2:
        st.success(f"🚀 **PREDIKSI {target_prediksi}: KEMUNGKINAN BESAR MENGUAT (NAIK)**\n\n{alasan_prediksi}")
    elif total_skor <= -2:
        st.error(f"⚠️ **PREDIKSI {target_prediksi}: KEMUNGKINAN BESAR MELEMAH (TURUN)**\n\n{alasan_prediksi}")
    else:
        st.warning(f"⚖️ **PREDIKSI {target_prediksi}: KONSOLIDASI (SIDEWAYS)**\n\n{alasan_prediksi}")

    # --- GRAFIK INTERAKTIF TRADINGVIEW ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Chart Interaktif (TradingView)")
    
    # Menanamkan Widget HTML resmi dari TradingView
    components.html("""
    <div class="tradingview-widget-container">
      <div id="tradingview_ihsg"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {
      "width": "100%",
      "height": 550,
      "symbol": "IDX:COMPOSITE",
      "interval": "D",
      "timezone": "Asia/Jakarta",
      "theme": "dark",
      "style": "1",
      "locale": "id",
      "enable_publishing": false,
      "backgroundColor": "#1e1e1e",
      "hide_top_toolbar": false,
      "allow_symbol_change": true,
      "save_image": false,
      "container_id": "tradingview_ihsg"
    }
      );
      </script>
    </div>
    """, height=550)

except Exception as e:
    st.error("Gagal menarik data Makro dari server. Lanjut ke pemindaian saham...")

# --- 3. RADAR BERITA SPESIFIK ---
st.markdown("---")
st.subheader("📰 Radar Berita Spesifik (IHSG & LQ45)")
st.write("Sistem otomatis menyaring ratusan berita harian dari CNBC Indonesia dan hanya menampilkan berita yang mengandung kata sandi 'IHSG' atau nama saham LQ45 Anda.")

# Sekarang kode ini aman karena daftar_lq45 sudah ada di barisan paling atas
kata_kunci = ["IHSG", "LQ45"] + [kode.replace(".JK", "") for kode in daftar_lq45]

try:
    url_berita = "https://www.cnbcindonesia.com/market/rss"
    req = urllib.request.Request(url_berita, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        xml_data = response.read()
    root = ET.fromstring(xml_data)
    
    berita_relevan = []
    
    for item in root.findall('.//item'):
        judul = item.find('title').text
        link = item.find('link').text
        waktu = item.find('pubDate').text
        
        if any(keyword in judul.upper() for keyword in kata_kunci):
            berita_relevan.append((judul, link, waktu))
            
        if len(berita_relevan) >= 10:
            break

    if berita_relevan:
        for judul, link, waktu in berita_relevan:
            waktu_rapi = waktu.replace(" +0700", "") 
            st.markdown(f"🔹 **[{judul}]({link})** \n*{waktu_rapi}*")
    else:
        st.info("Sistem belum menemukan berita terbaru yang secara spesifik menyebut IHSG atau saham pantauan Anda siang ini.")

except Exception as e:
    st.error("Gagal menyedot data berita lokal. Pastikan koneksi internet server stabil.")


# --- 4. KACA PEMBESAR SAHAM (SUPER DIAGNOSTIC DENGAN AI) ---
st.markdown("---")
st.subheader("🔍 Cari Saham & Analisa AI Dysania")
st.write("Mendiagnosis anatomi saham secara detail meliputi Tren, Volume, Jejak Smart Money, lalu dianalisis langsung oleh Otak AI Dysania.")

col_search, col_btn = st.columns([3, 1])

with col_search:
    ticker_input = st.text_input("Ketik Kode Saham:", placeholder="Maksimal 4 Huruf, misal: NZIA").upper()

with col_btn:
    st.write(""); st.write("") 
    btn_search = st.button("Bedah Saham Ini", use_container_width=True)

if btn_search and ticker_input:
    ticker_yf = ticker_input + ".JK" if not ticker_input.endswith(".JK") else ticker_input
    ticker_tv = f"IDX:{ticker_input.replace('.JK', '')}"

    with st.spinner(f"Dysania sedang mengunduh anatomi {ticker_input}..."):
        try:
            data_c = yf.Ticker(ticker_yf).history(period="3mo")
            if len(data_c) > 30:
                # 1. KALKULASI INDIKATOR MATEMATIS
                data_c['MA20'] = data_c['Close'].rolling(window=20).mean()
                data_c['Vol_Avg'] = data_c['Volume'].rolling(window=20).mean()
                
                delta = data_c['Close'].diff()
                up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
                rs = up.ewm(com=13, adjust=False).mean() / down.ewm(com=13, adjust=False).mean()
                data_c['RSI'] = 100 - (100 / (1 + rs))
                
                arah_harga = delta.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
                data_c['OBV'] = (arah_harga * data_c['Volume']).cumsum()
                data_c['OBV_MA20'] = data_c['OBV'].rolling(window=20).mean()

                # 2. AMBIL NILAI TERAKHIR
                hc, mc = float(data_c['Close'].iloc[-1]), float(data_c['MA20'].iloc[-1])
                vol, vol_avg = float(data_c['Volume'].iloc[-1]), float(data_c['Vol_Avg'].iloc[-1])
                rsi = float(data_c['RSI'].iloc[-1])
                obv, obv_ma = float(data_c['OBV'].iloc[-1]), float(data_c['OBV_MA20'].iloc[-1])

                # PERBAIKAN: Menyederhanakan teks agar muncul sempurna di kartu metrik
                trend_status = "🟢 UPTREND" if hc > mc else "🔴 DOWNTREND"
                vol_status = "🔥 Meledak" if vol > vol_avg else "💤 Sepi"
                sm_status = "🐳 AKUMULASI" if obv > obv_ma else "🩸 DISTRIBUSI"
                
                if rsi > 70: rsi_status = "🔥 Overbought"
                elif rsi < 30: rsi_status = "❄️ Oversold"
                else: rsi_status = "✅ Normal"

                # 3. TAMPILAN PANEL DIAGNOSTIK ANGKA
                st.markdown(f"### 🩺 Parameter Kuantitatif: **{ticker_input.replace('.JK', '')}**")
                c1, c2, c3, c4 = st.columns(4)
                
                # PERBAIKAN: Memasukkan variabel secara langsung tanpa dipotong (.split)
                c1.metric("Tren (MA20)", trend_status, f"Rp {hc:,.0f}")
                c2.metric("Jejak Smart Money", sm_status)
                c3.metric("Volume Transaksi", vol_status)
                c4.metric("Suhu Saham (RSI)", f"{rsi:.1f}", rsi_status, delta_color="off")

                # 4. MEMBANGUNKAN OTAK AI UNTUK ANALISIS
                st.markdown("### 🧠 Analisis Eksklusif AI Dysania")
                if api_key_dysania:
                    prompt_rahasia = f"""
                    Anda adalah 'Dysania', seorang asisten Pro-Trader saham Indonesia yang sangat jenius, dingin, objektif, dan taktis. 
                    Anda menggunakan pendekatan Top-Down Analysis dan Bandarmologi.
                    
                    Saya baru saja menscan saham {ticker_input.replace('.JK', '')} di Bursa Efek Indonesia. Berikut adalah data kuantitatif penutupan terakhirnya:
                    - Harga Terakhir: Rp {hc:,.0f}
                    - Posisi terhadap MA20: Rp {mc:,.0f} (Status: {trend_status})
                    - Volume Transaksi hari ini: {vol_status}
                    - Jejak Smart Money (Indikator OBV): Bandar sedang {sm_status}
                    - Suhu Saham (RSI): {rsi:.1f} ({rsi_status})
                    
                    Tugas Anda:
                    1. Bicaralah langsung kepada saya sebagai Dysania. Jangan mengulang data angka mentah di atas seperti robot, sintesiskan data tersebut menjadi sebuah cerita pergerakan pasar!
                    2. Bongkar niat Bandar! Apakah kenaikan/penurunan harga ini sinkron dengan volume dan Smart Money? Adakah anomali seperti Bull Trap (naik tapi bandar jualan) atau Mark-Down Accumulation (turun tapi bandar nampung)?
                    3. Berikan 'SOP Swing Trading' yang tegas (contoh: "Antre beli di area X", "Hold ketat", "Pantau dulu", atau "Jauhi/Jangan tangkap pisau jatuh").
                    
                    Format output: Gunakan paragraf yang enak dibaca, gunakan bold untuk penekanan, dan jadilah asisten trading yang elegan dan kejam terhadap risiko.
                    """
                    
                    with st.spinner("Dysania sedang meracik strategi berdasarkan data terkini..."):
                        try:
                            # PERBAIKAN: Mengganti nama model ke versi yang paling stabil untuk API
                            # Menggunakan otak Gemini 1.5 Flash yang super stabil dan cepat
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            respon_ai = model.generate_content(prompt_rahasia)
                            
                            st.info(respon_ai.text)
                        except Exception as e:
                            st.error(f"Gagal memanggil otak AI. Pastikan API Key valid. Error: {e}")
                else:
                    st.warning("⚠️ Otak Dysania tertidur. Masukkan API Key Gemini di Sidebar sebelah kiri untuk mendapatkan analisis taktis otomatis.")
                
                # 5. MENANAMKAN GRAFIK TRADINGVIEW
                st.markdown("<br>", unsafe_allow_html=True)
                components.html(f"""
                <div class="tradingview-widget-container">
                  <div id="tv_kaca_pembesar_{ticker_input}"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget(
                  {{
                  "width": "100%",
                  "height": 500,
                  "symbol": "{ticker_tv}",
                  "interval": "D",
                  "timezone": "Asia/Jakarta",
                  "theme": "light",
                  "style": "1",
                  "locale": "id",
                  "enable_publishing": false,
                  "backgroundColor": "#ffffff",
                  "hide_top_toolbar": false,
                  "hide_legend": false,
                  "save_image": false,
                  "container_id": "tv_kaca_pembesar_{ticker_input}",
                  "studies": [
                    "Volume@tv-basicstudies",
                    "MASimple@tv-basicstudies"
                  ]
                }}
                  );
                  </script>
                </div>
                """, height=500)

            else:
                st.error("Data saham tidak ditemukan. Pastikan kodenya benar (Maksimal 4 huruf).")
        except Exception as e:
            st.error(f"Gagal menarik data. Error: {e}")


# --- 5. SCREENER MASAL LQ45 (RADAR UTAMA) ---
st.markdown("---")
st.subheader("⚙️ Mesin Screener Fast Swing")

if st.button("▶️ Mulai Pemindaian Fast Swing LQ45", use_container_width=True, type="primary"):
    hasil_analisa = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_saham = len(daftar_lq45)
    
    for i, kode in enumerate(daftar_lq45):
        status_text.text(f"Memindai {kode}... ({i+1}/{total_saham})")
        try:
            saham = yf.Ticker(kode)
            data = saham.history(period="3mo") 
            
            if len(data) > 25:
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()
                
                # KALKULASI SENSOR RSI
                delta = data['Close'].diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                data['RSI'] = 100 - (100 / (1 + rs))
                # --- SUNTIKAN SENSOR SMART MONEY (OBV) ---
                # 1. Menghitung Arah Harga dan Volume Kumulatif (OBV)
                delta_harga = data['Close'].diff()
                arah_harga = delta_harga.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
                data['OBV'] = (arah_harga * data['Volume']).cumsum()
                
                # 2. Membuat Rata-rata pergerakan Bandar (MA20 dari OBV)
                data['OBV_MA20'] = data['OBV'].rolling(window=20).mean()
                
                obv_terakhir = float(data['OBV'].iloc[-1])
                obv_ma20_terakhir = float(data['OBV_MA20'].iloc[-1])
                
                # 3. Logika Deteksi Jejak Bandar
                if obv_terakhir > obv_ma20_terakhir:
                    status_bandar = "🐳 AKUMULASI (Uang Masuk)"
                else:
                    status_bandar = "🩸 DISTRIBUSI (Uang Keluar)"
                # --- BATAS SUNTIKAN KODE ---
                
                harga_terakhir = float(data['Close'].iloc[-1])
                ma20_terakhir = float(data['MA20'].iloc[-1])
                vol_terakhir = float(data['Volume'].iloc[-1])
                vol_avg_terakhir = float(data['Vol_Avg'].iloc[-1])
                rsi_terakhir = float(data['RSI'].iloc[-1])
                
                area_beli, stop_loss, risk_level, kekuatan_tren, status_rsi = "-", "-", "-", "-", "-"
                tp1_str, tp2_str, tp3_str = "-", "-", "-"
                sinyal = "WAIT"
                
                if (harga_terakhir > ma20_terakhir) and (vol_terakhir > vol_avg_terakhir):
                    sinyal = "🔥 BUY (MINGGUAN)"
                    
                    if rsi_terakhir > 70:
                        status_rsi = f"🔥 {rsi_terakhir:.0f} (Overbought)"
                    elif rsi_terakhir < 30:
                        status_rsi = f"❄️ {rsi_terakhir:.0f} (Oversold)"
                    else:
                        status_rsi = f"✅ {rsi_terakhir:.0f} (Normal)"
                    
                    rasio_vol = vol_terakhir / vol_avg_terakhir
                    if rasio_vol >= 2.0: kekuatan_tren = "🔥 Sangat Kuat"
                    elif rasio_vol >= 1.5: kekuatan_tren = "⚡ Kuat"
                    else: kekuatan_tren = "✅ Normal"
                    
                    harga_ideal = ma20_terakhir * 1.01
                    support_terdekat = data['Low'].tail(5).min() 
                    batas_sl = support_terdekat if support_terdekat < harga_ideal else (harga_ideal * 0.98)
                    persen_sl = ((batas_sl - harga_ideal) / harga_ideal) * 100
                    
                    keterangan_sl = ""
                    if persen_sl < -7.0:
                        batas_sl = harga_ideal * 0.93 
                        persen_sl = -7.0
                        keterangan_sl = " 🛡️"
                    
                    if abs(persen_sl) <= 3.0: risk_level = "🟢 Low"
                    elif abs(persen_sl) <= 5.0: risk_level = "🟡 Med"
                    else: risk_level = "🔴 High"
                        
                    jarak_risiko = harga_ideal - batas_sl
                    
                    tp1_tech = data['High'].tail(5).max()
                    tp1 = max(tp1_tech, harga_ideal + (jarak_risiko * 1.0)) 
                    tp2_tech = data['High'].tail(10).max()
                    tp2 = max(tp2_tech, tp1 + (jarak_risiko * 0.5)) 
                    tp3_tech = data['High'].tail(20).max()
                    tp3 = max(tp3_tech, tp2 + (jarak_risiko * 0.5))
                    
                    p_tp1 = ((tp1 - harga_ideal) / harga_ideal) * 100
                    p_tp2 = ((tp2 - harga_ideal) / harga_ideal) * 100
                    p_tp3 = ((tp3 - harga_ideal) / harga_ideal) * 100
                    
                    area_beli = f"Rp {harga_ideal:,.0f} - Rp {harga_terakhir:,.0f}"
                    stop_loss = f"Rp {batas_sl:,.0f} ({persen_sl:.2f}%){keterangan_sl}"
                    tp1_str = f"Rp {tp1:,.0f} (+{p_tp1:.2f}%)"
                    tp2_str = f"Rp {tp2:,.0f} (+{p_tp2:.2f}%)"
                    tp3_str = f"Rp {tp3:,.0f} (+{p_tp3:.2f}%)"
                    
                elif harga_terakhir < ma20_terakhir:
                    sinyal = "⚠️ DOWNTREND"
                    
                hasil_analisa.append({
                    "Kode Saham": kode.replace(".JK", ""),
                    "Kode Asli": kode,
                    "Sinyal": sinyal,
                    "RSI (Suhu)": status_rsi,
                    "Tren": kekuatan_tren,
                    "Risiko": risk_level,
                    "Area Beli": area_beli,
                    "SL": stop_loss,
                    "TP1 (5H)": tp1_str,
                    "TP2 (10H)": tp2_str,
                    "TP3 (20H)": tp3_str,
                    "Smart Money": status_bandar,
                })
        except Exception:
            pass 
            
        progress_bar.progress((i + 1) / total_saham)
    
    status_text.text("Pemindaian Selesai!")
    
    if len(hasil_analisa) > 0:
        df_hasil = pd.DataFrame(hasil_analisa)
        df_potensi = df_hasil[df_hasil["Sinyal"] == "🔥 BUY (MINGGUAN)"]
        
        st.subheader("🎯 Trading Plan (Strategi Fast Swing)")
        if not df_potensi.empty:
            kolom_urut = ["Kode Saham", "Sinyal", "Smart Money", "RSI (Suhu)", "Tren", "Risiko", "Area Beli", "SL", "TP1 (5H)", "TP2 (10H)", "TP3 (20H)"]
            st.dataframe(df_potensi[kolom_urut].reset_index(drop=True), use_container_width=True)
            
            st.info("💡 **Tips RSI:** Jika saham bersinyal BUY tapi status RSI-nya **🔥 Overbought (>70)**, pertimbangkan untuk menunda pembelian.")
            
            st.markdown("### 📰 Shortcut Sentimen & Berita")
            kolom_berita = st.columns(len(df_potensi))
            for index, row in df_potensi.iterrows():
                nama_saham = row['Kode Saham']
                with kolom_berita[index % len(kolom_berita)]:
                    st.markdown(f"**{nama_saham}** | 🌐 [Berita](https://www.google.com/search?q=saham+{nama_saham}+berita&tbm=nws) | 📈 [Stockbit](https://stockbit.com/symbol/{nama_saham})")
        else:
            st.warning("Tidak ada emiten yang memenuhi kriteria saat ini.")

        with st.expander("Lihat Status Seluruh 45 Saham LQ45"):
            st.dataframe(df_hasil.drop(columns=['Kode Asli']), use_container_width=True)

# --- 2. COMPASS SEKTOR ---
st.markdown("---")
st.subheader("🧭 Compass Sektor (Analisis & Prediksi Potensi)")
st.write("Menganalisis rotasi sektor berdasarkan input Market dan Berita Terkait untuk memprediksi sektor berpotensi naik.")

# 1. Definisikan Sektor, Ikon, dan Saham Proxy (LENGKAP 11 SEKTOR ALA STOCKBIT)
sektor_data = {
    "TECHNOLOGY": {"icon": "💻", "proxy": ["GOTO.JK", "EMTK.JK", "ARTO.JK"]},
    "ENERGY": {"icon": "🔥", "proxy": ["MEDC.JK", "ADRO.JK", "PTBA.JK", "AKRA.JK"]},
    "BASIC-IND": {"icon": "🏗️", "proxy": ["ANTM.JK", "INCO.JK", "MDKA.JK", "BRPT.JK"]},
    "INFRASTRUC": {"icon": "📡", "proxy": ["TLKM.JK", "TOWR.JK", "EXCL.JK"]},
    "FINANCE": {"icon": "🏦", "proxy": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK"]},
    "TRANSPORT": {"icon": "✈️", "proxy": ["SMDR.JK", "ASSA.JK", "BLUE.JK"]}, # Sektor Baru
    "INDUSTRIAL": {"icon": "🏭", "proxy": ["UNTR.JK", "ASII.JK", "AALI.JK"]}, # Sektor Baru
    "HEALTH": {"icon": "🏥", "proxy": ["KLBF.JK", "MIKA.JK", "HEAL.JK"]}, # Sektor Baru
    "PROPERTY": {"icon": "🏠", "proxy": ["BSDE.JK", "PWON.JK", "CTRA.JK"]},
    "CYCLICAL": {"icon": "🛒", "proxy": ["MAPI.JK", "ACES.JK", "ERAA.JK"]}, # Sektor Baru
    "NON-CYCLICAL": {"icon": "🧴", "proxy": ["UNVR.JK", "ICBP.JK", "INDF.JK"]} # Sektor Baru
}

try:
    hasil_sektor = []
    with st.spinner("Memindai arus dana sektoral..."):
        for nama_s_key, data_s in sektor_data.items():
            avg_perubahan_5d = 0
            valid_count = 0
            t_akhir = 0
            t_kemarin = 0
            
            for ticker in data_s["proxy"]:
                try:
                    data_ticker = yf.Ticker(ticker).history(period="10d")
                    if len(data_ticker) >= 6:
                        t_akhir = data_ticker['Close'].iloc[-1]
                        t_kemarin = data_ticker['Close'].iloc[-2]
                        persen_5d = ((t_akhir - data_ticker['Close'].iloc[-6]) / data_ticker['Close'].iloc[-6]) * 100
                        avg_perubahan_5d += persen_5d
                        valid_count += 1
                except: pass
            
            if valid_count > 0:
                nilai_sektor = avg_perubahan_5d / valid_count
                persen_harian_tampil = ((t_akhir - t_kemarin)/t_kemarin)*100 if t_kemarin > 0 else 0
                
                if nilai_sektor >= 2.0:
                    prediksi_status, prediksi_alasan = "Tinggi 🔥", "Smart Money: News Akumulasi"
                elif nilai_sektor <= -1.0:
                    prediksi_status, prediksi_alasan = "Rendah 🛡️", "Sentimen: News Konsolidasi"
                else:
                    prediksi_status, prediksi_alasan = "Sedang ⚖️", "Market: Sideways"
                    
                hasil_sektor.append({"Sektor": nama_s_key, "Ikon": data_s["icon"], "Persen Harian": persen_harian_tampil, "Potensi": prediksi_status, "Alasan": prediksi_alasan})

    if hasil_sektor:
        # PERBAIKAN FATAL: Menghapus spasi indentasi agar tidak dibaca sebagai Code Block oleh Markdown
        grid_html = '<div class="sector-grid">'
        for row in hasil_sektor:
            color_perf = "text-green" if row["Persen Harian"] > 0 else "text-red"
            grid_html += '<div class="sector-card">'
            grid_html += '<div class="sector-icon-row">'
            grid_html += f'<span class="sector-icon">{row["Ikon"]}</span>'
            grid_html += f'<span class="sector-name">{row["Sektor"]}</span>'
            grid_html += '</div>'
            grid_html += f'<div class="sector-perf {color_perf}">{row["Persen Harian"]:+.2f}%</div>'
            grid_html += f'<div class="sector-pred">POTENSI: {row["Potensi"]} ({row["Alasan"]})</div>'
            grid_html += '</div>'
        grid_html += '</div>'
        
        st.markdown(grid_html, unsafe_allow_html=True)

except Exception as e:
    st.error("Gagal memuat analisis sektoral.")
