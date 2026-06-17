"""
Sayfa 1: Pazar Panoramasi
=========================
KPI kartlari + 11 yillik pazar trendi + hikaye kartlari + 6 bulgu
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import time_series_genre_yukle


def goster(df):
    """Sayfa 1: Pazar Panoramasi"""
    
    # ─────────────────────────────────────────────────────
    # 4 KPI KART
    # ─────────────────────────────────────────────────────
    st.markdown("## Genel Bakis")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.metric(
            label="📊 Toplam Oyun",
            value=f"{len(df):,}",
            delta="113K analiz edildi",
            delta_color="off"
        )
    
    with kpi2:
        st.metric(
            label="💰 2025 Pazar Buyuklugu",
            value="$16.25B",
            delta="11 yilda 5x buyume",
            delta_color="normal"
        )
    
    with kpi3:
        st.metric(
            label="🎯 Pareto Sertligi",
            value="%93.3",
            delta="Cluster_6 hegemonyasi",
            delta_color="off",
            help="Pazarin %93'unu sadece %4 oyun kontrol ediyor"
        )
    
    with kpi4:
        st.metric(
            label="🤖 Model Dogrulugu",
            value="R² = 0.84",
            delta="Hybrid Stacking",
            delta_color="off",
            help="Ensemble learning: K-NN + Content-Based + Linear Regression"
        )
    
    st.divider()
    
    # ─────────────────────────────────────────────────────
    # 11 YILLIK PAZAR TRENDI + 2027 PROJEKSIYONU
    # ─────────────────────────────────────────────────────
    st.markdown("## 11 Yillik Pazar Trendi + 2027 Projeksiyonu")
    
    # Veriyi yukle
    ts_genre = time_series_genre_yukle()
    yillik_toplam = ts_genre['GERCEK_PAZAR'].values
    yillar = list(ts_genre.index)
    
    # 2027 projeksiyon noktasi (GUVENILIR rakami - notebook'tan)
    forecast_yillar = [2026, 2027]
    forecast_degerler = [16.50, 17.06]  # GUVENILIR projeksiyon
    
    # Plotly grafigi
    fig = go.Figure()
    
    # Gercek veriler (2015-2025)
    fig.add_trace(go.Scatter(
        x=yillar,
        y=yillik_toplam,
        mode='lines+markers+text',
        name='Gercek (2015-2025)',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=10, color='#2E86AB'),
        text=[f'${v:.1f}B' for v in yillik_toplam],
        textposition='top center',
        textfont=dict(size=10, color='#2E86AB')
    ))
    
    # 2025 -> 2027 baglanti (projeksiyon)
    forecast_x_full = [2025] + forecast_yillar
    forecast_y_full = [yillik_toplam[-1]] + forecast_degerler
    
    fig.add_trace(go.Scatter(
        x=forecast_x_full,
        y=forecast_y_full,
        mode='lines+markers+text',
        name='Projeksiyon (2026-2027)',
        line=dict(color='#9b59b6', width=3, dash='dash'),
        marker=dict(size=12, color='#9b59b6', symbol='diamond'),
        text=['', f'${forecast_degerler[0]:.1f}B', f'${forecast_degerler[1]:.1f}B'],
        textposition='top center',
        textfont=dict(size=10, color='#9b59b6')
    ))
    
    # COVID 2020 vurgu
    fig.add_annotation(
        x=2020, y=yillik_toplam[5],
        text="COVID sicramasi",
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        ax=0, ay=-40,
        font=dict(size=10, color="red")
    )
    
    fig.update_layout(
        title=dict(
            text="Steam Toplam Pazar - 2015'ten 2027'ye",
            font=dict(size=18)
        ),
        xaxis_title="Yil",
        yaxis_title="Toplam Revenue (Milyar $)",
        hovermode='x unified',
        height=450,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    # Forecast bolgesini gri ile vurgula
    fig.add_vrect(
        x0=2025, x1=2027.5,
        fillcolor="purple", opacity=0.05,
        line_width=0
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # CAGR bilgisi
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        gecmis_cagr = (((yillik_toplam[-1] / yillik_toplam[0]) ** (1/10)) - 1) * 100
        st.info(f"**Gecmis 10 Yil CAGR:** +%{gecmis_cagr:.1f}")
    with col_b:
        gelecek_cagr = (((forecast_degerler[1] / yillik_toplam[-1]) ** 0.5) - 1) * 100
        st.warning(f"**Model 2-Yil CAGR:** +%{gelecek_cagr:.1f}")
    with col_c:
        st.error(f"**Paradoks:** ~{gecmis_cagr/gelecek_cagr:.1f}x fark")
    
    st.caption("📌 Geçmiş büyüme oranı ile model projeksiyonu arasındaki fark, **Bölüm 7'nin ana akademik bulgularından biridir** (Metodoloji sekmesinde detay).")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────
    # 3 HIKAYE KARTI
    # ─────────────────────────────────────────────────────
    st.markdown("## Carpici Bulgular")
    
    h1, h2, h3 = st.columns(3)
    
    with h1:
        with st.container(border=True):
            st.markdown("### 🎯 Action Anomalisi")
            st.markdown("""
            Action oyunlari sayica **sadece %7.9** (8.995 oyun) ama 
            pazarin **%57.9'unu** uretiyor.
            
            Mega oyunlar (CS2, PUBG, Apex) bu farki yaratiyor.
            """)
            st.metric("Pazar Payi / Oyun Oran", "7.3x", 
                     help="%57.9 pazar / %7.9 oyun")
    
    with h2:
        with st.container(border=True):
            st.markdown("### ⚠️ Indie Yanilgisi")
            st.markdown("""
            81.463 Indie oyun var (pazarin %71.8'i) ama 
            **medyan revenue sadece $622**.
            
            Tipik bir indie oyun **mali olarak basarisiz**.
            """)
            st.metric("Medyan Indie Revenue", "$622", 
                     delta="-99.8% vs Action median",
                     delta_color="inverse")
    
    with h3:
        with st.container(border=True):
            st.markdown("### 🌟 Cluster_6 Hegemonyasi")
            st.markdown("""
            Sadece **4.580 oyun (%4)** pazarin **%93.3'unu** kontrol ediyor.
            
            Klasik 80/20 kuralinin **4 kat sertligi**.
            """)
            st.metric("Pareto Carpani", "19.9x", 
                     help="Pazar % / Oyun % orani")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────
    # 6 AKADEMIK BULGU (Akordeon)
    # ─────────────────────────────────────────────────────
    st.markdown("## 6 Ampirik Bulgu Mirasi")
    st.caption("Bu projenin akademik katkisi - asagidaki bulgular bagimsiz testlerle dogrulanmistir.")
    
    bulgular = [
        {
            "baslik": "Bulgu 1: Taksonomik Karsilasma Yogunlugu",
            "icerik": """
            **Bolum 6:** Icerik etiketleri (genre + tag), iki oyunun finansal benzerligini 
            tek basina ayirt edemez. %19 tam etiket eslesmesinde bile revenue farki 100x'e 
            kadar cikabilir.
            
            **Sonuc:** Icerik benzerligi != finansal basari. Sosyal sinyaller (wishlist, 
            followers) kritik onem tasiyor.
            """
        },
        {
            "baslik": "Bulgu 2: Finansal Korluk Testi (Content-Based)",
            "icerik": """
            **Bolum 6.7:** 10 hit oyun icin Content-Based'in onerdigi benzer oyunlarin 
            ortalama revenue'su, hit oyunun **%15.3'u** kadardir (sistematik alt-tahmin).
            
            **Sonuc:** Content-Based, finansal tahmin icin tek basina yetersiz - cold-start 
            disinda kullanilmamali.
            """
        },
        {
            "baslik": "🌟 Bulgu 3: Negatif Meta-Learner Agirligi (AKADEMIK ALTIN)",
            "icerik": """
            **Bolum 6.8:** Hybrid Stacking meta-learner'i, Content-Based'e **NEGATIF agirlik** 
            (-0.1511) atadi. |w_cb|/w_knn = **0.130 (%13)**.
            
            **Carpici detay:** Bu oran, Bolum 6.7'deki finansal korluk %15.3 oraniyla 
            **bagimsiz testle dogrulandi** (~2 puan fark). Meta-learner, bias buyuklugunu 
            **veriden kendi kesfetti** - aciktan programlanmadi.
            
            **Sonuc:** Veri-odakli modellerin gizli yapilari otomatik kesfetme kapasitesinin 
            somut bir ornegi.
            """
        },
        {
            "baslik": "Bulgu 4: Parsimony Principle (Occam's Razor)",
            "icerik": """
            **Bolum 7:** Yillik 11 noktali veride basit modeller karmasik olanlari yendi:
            - HoltWinters: 5 segmentte birinci (sampiyon)
            - **LightGBM: 0 segmentte birinci** (catastrophic failure, %52 MAPE)
            
            **Sonuc:** Karmasiklik != Performans. Veri yapisi dogru algoritmayi belirler.
            """
        },
        {
            "baslik": "Bulgu 5: No Free Lunch Pratik Uygulamasi (Wolpert 1997)",
            "icerik": """
            **Bolum 7:** 5 algoritmadan hicbiri tum segmentlerde en iyi degil:
            - HoltWinters: Trend-dominant segmentler
            - ARIMA: Otokorelasyonlu segmentler (Cluster_6)
            - Prophet: Orta buyuklukteki segmentler
            
            **Sonuc:** Tek model yetmez - **Best-of-Best yaklasimi** zorunlu.
            """
        },
        {
            "baslik": "🌟 Bulgu 6: Gecmis-Gelecek CAGR Paradoksu",
            "icerik": """
            **Bolum 7:** Carpici celiski:
            - Gecmis 10 yil CAGR (2015-2025): **+%17.4**
            - Model projeksiyon CAGR (2025-2027): **+%2.7**
            - Fark: **~7.1 kat**
            
            **Olasi nedenler:** ARIMA mean-reversion, Action segmentinde stagnasyon, 
            pazar doygunlugu.
            
            **Cikarim:** Tek bir CAGR rakami yerine senaryo bazli yaklasim (Worst/Base/Best) 
            akademik durustluk acisindan gerekli.
            """
        },
    ]
    
    for bulgu in bulgular:
        with st.expander(bulgu["baslik"]):
            st.markdown(bulgu["icerik"])
            