import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go

st.set_page_config(page_title="Screener Saham Pro", layout="wide")
st.title("Dashboard Monitoring LQ45 & Prediksi Makro")
st.write("Sistem Top-Down Analysis: Prediksi arah IHSG berdasarkan sentimen Global dan Teknikal.")

# --- 1. PENGINGAT WAKTU TRADING ---
tz = pytz.timezone('Asia/Jakarta')
sekarang = datetime.now(tz)
hari_ini = sekarang.weekday() 
jam = sekarang.hour
menit = sekarang.minute

status_waktu, saran_aksi = "", ""
if hari_ini == 4 and (jam >= 15 and menit >= 45) or hari_ini in [5, 6]:
    status_waktu = "🟢 WAKTU EMAS (PERSIAPAN SENIN)"
    saran_aksi = "Bursa tutup. Lakukan scan untuk mencari kandidat Fast Swing."
elif hari_ini == 0 and (jam >= 9 and jam <= 11):
    status_waktu = "🔵 WAKTU ENTRY (SENIN PAGI)"
    saran_aksi = "Waktu eksekusi! Antre beli di area Ideal dan pasang Auto-Sell."
elif hari_ini == 4 and jam < 15:
    status_waktu = "🟠 HARI JUMAT (TAKE PROFIT / CLEARING)"
    saran_aksi = "Evaluasi portofolio. Jual saham yang mandek agar *cash* aman."
elif hari_ini < 4 and jam >= 16:
    status_waktu = "🟡 EVALUASI HARIAN"
    saran_aksi = "Bursa tutup. Pantau apakah harga hari ini menyentuh target TP."
else:
    status_waktu = "🔴 BURSA BERJALAN"
    saran_aksi = "Pasar aktif. Biarkan Auto-Order yang bekerja."

st.markdown("---")
col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="Waktu Sistem (WIB)", value=sekarang.strftime('%A, %H:%M'))
    if st.button("🔄 Update Waktu"):
        st.rerun()
with col2:
    st.info(f"**Status:** {status_waktu}\n\n**Aksi:** {saran_aksi}")
st.markdown("---")

# --- 2. FITUR BARU: PREDIKSI ARAH IHSG (TIME-AWARE) ---
st.subheader("🧭 Radar Cuaca Pasar & Prediksi Eksekusi")

try:
    tickers_makro = yf.Tickers("^JKSE ^DJI IDR=X GC=F")
    data_makro = tickers_makro.history(period="5d")
    
    # 1. Data IHSG
    ihsg_close = data_makro['Close']['^JKSE'].dropna()
    ihsg_terakhir = ihsg_close.iloc[-1]
    ihsg_kemarin = ihsg_close.iloc[-2]
    perubahan_ihsg = ihsg_terakhir - ihsg_kemarin
    persen_ihsg = (perubahan_ihsg / ihsg_kemarin) * 100
    
    ihsg_full = yf.Ticker("^JKSE").history(period="2mo")
    ihsg_full['MA20'] = ihsg_full['Close'].rolling(window=20).mean()
    ihsg_ma20 = ihsg_full['MA20'].iloc[-1]
    tren_teknikal_ihsg = 1 if ihsg_terakhir > ihsg_ma20 else -1

    # 2. Data Dow Jones
    dji_close = data_makro['Close']['^DJI'].dropna()
    persen_dji = ((dji_close.iloc[-1] - dji_close.iloc[-2]) / dji_close.iloc[-2]) * 100
    skor_dji = 1 if persen_dji > 0 else -1

    # 3. Data Kurs Rupiah
    idr_close = data_makro['Close']['IDR=X'].dropna()
    persen_idr = ((idr_close.iloc[-1] - idr_close.iloc[-2]) / idr_close.iloc[-2]) * 100
    skor_idr = 1 if persen_idr < 0 else -1 

    # 4. Data Emas
    gold_close = data_makro['Close']['GC=F'].dropna()
    persen_gold = ((gold_close.iloc[-1] - gold_close.iloc[-2]) / gold_close.iloc[-2]) * 100
    skor_gold = 1 if persen_gold > 0 else -1

    # --- LOGIKA TARGET HARI PREDIKSI ---
    target_prediksi = ""
    if hari_ini == 4 and jam >= 16 or hari_ini in [5, 6]:
        target_prediksi = "SENIN DEPAN"
    elif jam >= 16:
        target_prediksi = "BESOK"
    else:
        target_prediksi = "HARI INI"

    # --- LOGIKA SKORING AI ---
    total_skor = tren_teknikal_ihsg + skor_dji + skor_idr + skor_gold
    
    prediksi_teks = ""
    warna_prediksi = ""
    alasan_prediksi = f"**Analisa Pembentuk Tren {target_prediksi.title()}:**\n- Bursa AS (Dow Jones): {'Naik 🟢' if skor_dji > 0 else 'Turun 🔴'}\n- Kurs Rupiah: {'Menguat 🟢' if skor_idr > 0 else 'Melemah 🔴'}\n- Emas Global: {'Naik 🟢' if skor_gold > 0 else 'Turun 🔴'}\n- Tren MA20 IHSG Saat Ini: {'Uptrend 🟢' if tren_teknikal_ihsg > 0 else 'Downtrend 🔴'}"

    if total_skor >= 2:
        prediksi_teks = f"🚀 PREDIKSI {target_prediksi}: KEMUNGKINAN BESAR MENGUAT (NAIK)"
        warna_prediksi = "success"
    elif total_skor <= -2:
        prediksi_teks = f"⚠️ PREDIKSI {target_prediksi}: KEMUNGKINAN BESAR MELEMAH (TURUN)"
        warna_prediksi = "error"
    else:
        prediksi_teks = f"⚖️ PREDIKSI {target_prediksi}: KONSOLIDASI (SIDEWAYS)"
        warna_prediksi = "warning"

    # --- TAMPILAN DASHBOARD MAKRO ---
    st.markdown("#### Indikator Makro Global (Penutupan Terakhir)")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("IHSG (Jakarta)", f"{ihsg_terakhir:,.0f}", f"{persen_ihsg:.2f}%")
    col_m2.metric("Dow Jones (AS)", f"{dji_close.iloc[-1]:,.0f}", f"{persen_dji:.2f}%")
    col_m3.metric("USD/IDR (Kurs)", f"Rp {idr_close.iloc[-1]:,.0f}", f"{persen_idr:.2f}%", delta_color="inverse")
    col_m4.metric("Emas Global", f"${gold_close.iloc[-1]:,.1f}", f"{persen_gold:.2f}%")

    if warna_prediksi == "success":
        st.success(f"{prediksi_teks}\n\n{alasan_prediksi}")
    elif warna_prediksi == "error":
        st.error(f"{prediksi_teks}\n\n{alasan_prediksi}")
    else:
        st.warning(f"{prediksi_teks}\n\n{alasan_prediksi}")

    # Grafik Candlestick IHSG
    df_chart = ihsg_full.tail(40) 
    fig = go.Figure(data=[go.Candlestick(x=df_chart.index,
                    open=df_chart['Open'], high=df_chart['High'],
                    low=df_chart['Low'], close=df_chart['Close'], name='IHSG')])
    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA20'], line=dict(color='orange', width=2), name='MA20'))
    fig.update_layout(title='Grafik Candlestick IHSG & MA20 (40 Hari Terakhir)', yaxis_title='Level IHSG', xaxis_rangeslider_visible=False, height=350, margin=dict(l=0, r=0, t=40, b=0), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("Gagal menarik data Makro dari server. Lanjut ke pemindaian saham...")

st.markdown("---")

# --- 3. DAFTAR SAHAM & SCREENER FAST SWING ---
daftar_lq45 = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", 
    "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", 
    "BRPT.JK", "CPIN.JK", "EMTK.JK", "ESSA.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", 
    "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", "ITMG.JK", 
    "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MTEL.JK", "PGAS.JK", 
    "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SRTG.JK", "TLKM.JK", "TOWR.JK", 
    "UNTR.JK", "UNVR.JK"
]

if st.button("Mulai Pemindaian Fast Swing"):
    hasil_analisa = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_saham = len(daftar_lq45)
    
    for i, kode in enumerate(daftar_lq45):
        status_text.text(f"Memindai {kode}... ({i+1}/{total_saham})")
        try:
            saham = yf.Ticker(kode)
            data = saham.history(period="2mo") 
            
            if len(data) > 25:
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()
                
                harga_terakhir = float(data['Close'].iloc[-1])
                ma20_terakhir = float(data['MA20'].iloc[-1])
                vol_terakhir = float(data['Volume'].iloc[-1])
                vol_avg_terakhir = float(data['Vol_Avg'].iloc[-1])
                
                area_beli, stop_loss, risk_level, kekuatan_tren = "-", "-", "-", "-"
                tp1_str, tp2_str, tp3_str = "-", "-", "-"
                sinyal = "WAIT"
                
                if (harga_terakhir > ma20_terakhir) and (vol_terakhir > vol_avg_terakhir):
                    sinyal = "🔥 BUY (MINGGUAN)"
                    
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
                    "Tren": kekuatan_tren,
                    "Risiko": risk_level,
                    "Area Beli": area_beli,
                    "SL": stop_loss,
                    "TP1 (5H)": tp1_str,
                    "TP2 (10H)": tp2_str,
                    "TP3 (20H)": tp3_str
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
            kolom_urut = ["Kode Saham", "Sinyal", "Tren", "Risiko", "Area Beli", "SL", "TP1 (5H)", "TP2 (10H)", "TP3 (20H)"]
            st.dataframe(df_potensi[kolom_urut].reset_index(drop=True), use_container_width=True)
            
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