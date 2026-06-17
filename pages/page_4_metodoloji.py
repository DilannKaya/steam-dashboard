"""
Sayfa 4: Metodoloji ve Akademik Miras
======================================
10 oneri modeli + 5 zaman serisi algoritmasi karsilastirmasi
6 ampirik bulgu + Lewis 1982 esikleri + akademik atiflar
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.data_loader import (
    oneri_modelleri_yukle,
    knn_karsilastirma_yukle,
    time_series_en_iyi_yukle,
    lewis_kategorisi,
)


def goster(df):
    """Sayfa 4: Metodoloji"""
    
    st.markdown("## Metodoloji ve Akademik Miras")
    st.caption("113.456 oyun, 5 algoritma, 6 ampirik bulgu - sistematik karsilastirma")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Model Karsilastirma",
        "🎯 MAPE & Lewis 1982",
        "🌟 6 Ampirik Bulgu",
        "📚 Atiflar & EM Cerçevesi"
    ])
    
    with tab1:
        _model_karsilastirma()
    
    with tab2:
        _mape_lewis()
    
    with tab3:
        _ampirik_bulgular()
    
    with tab4:
        _atiflar_em()


# ═══════════════════════════════════════════════════════
# TAB 1: MODEL KARSILASTIRMA
# ═══════════════════════════════════════════════════════
def _model_karsilastirma():
    st.markdown("### Model Karsilastirma")
    
    # ── ONERI MODELLERI (BOLUM 6) ──
    st.markdown("#### 1. Oneri Algoritmalari (Bolum 6) - 10 Model")
    
    knn_df = knn_karsilastirma_yukle()
    oneri_df = oneri_modelleri_yukle()
    
    # 8 K-NN + 1 CB + 1 Hybrid = 10 model
    knn_etiketli = knn_df.copy()
    knn_etiketli['Model'] = knn_etiketli['Normalizasyon'] + ' + ' + knn_etiketli['Metrik']
    knn_etiketli = knn_etiketli[['Model', 'R²', 'RMSE', 'MAE']]
    
    # CB ve Hybrid'i ekle
    cb_row = oneri_df[oneri_df['Model'].str.contains('Content', case=False, na=False)]
    hybrid_row = oneri_df[oneri_df['Model'].str.contains('Hybrid', case=False, na=False)]
    
    if len(cb_row) > 0:
        knn_etiketli = pd.concat([
            knn_etiketli,
            cb_row[['Model', 'R²', 'RMSE', 'MAE']].rename(columns={'Model': 'Model'})
        ], ignore_index=True)
    
    if len(hybrid_row) > 0:
        knn_etiketli = pd.concat([
            knn_etiketli,
            hybrid_row[['Model', 'R²', 'RMSE', 'MAE']]
        ], ignore_index=True)
    
    # R²'ye gore sirala
    knn_etiketli = knn_etiketli.sort_values('R²', ascending=False).reset_index(drop=True)
    knn_etiketli.insert(0, 'Rank', range(1, len(knn_etiketli) + 1))
    
    # Bar chart
    fig = go.Figure()
    
    renkler = []
    for _, row in knn_etiketli.iterrows():
        if 'Hybrid' in row['Model']:
            renkler.append('#FFD700')  # Altın - şampiyon
        elif 'Content' in row['Model']:
            renkler.append('#9b59b6')  # Mor - CB
        elif row['R²'] < 0:
            renkler.append('#e74c3c')  # Kırmızı - başarısız
        elif 'ZScore' in row['Model']:
            renkler.append('#2E86AB')  # Mavi - Z-Score
        else:
            renkler.append('#95a5a6')  # Gri - Min-Max
    
    fig.add_trace(go.Bar(
        y=knn_etiketli['Model'],
        x=knn_etiketli['R²'],
        orientation='h',
        marker=dict(color=renkler),
        text=knn_etiketli['R²'].apply(lambda x: f"R²={x:.4f}"),
        textposition='outside'
    ))
    
    # R²=0.8 esiği
    fig.add_vline(x=0.8, line_dash="dash", line_color="green",
                  annotation_text="0.8 esik")
    fig.add_vline(x=0, line_dash="dot", line_color="red",
                  annotation_text="R²=0 (kotu)")
    
    fig.update_layout(
        title="10 Oneri Modeli - R² Karsilastirmasi",
        xaxis_title="R² Skoru",
        height=500,
        yaxis=dict(autorange="reversed"),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detayli tablo
    with st.expander("📋 Detayli Karsilastirma Tablosu"):
        st.dataframe(knn_etiketli, use_container_width=True, hide_index=True)
    
    # ── Akademik bulgular ──
    with st.container(border=True):
        st.markdown("##### 🏆 Sampiyon Analizi")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🥇 Sampiyon", "Hybrid Stacking", "R² = 0.8388")
        with col2:
            st.metric("🥈 En iyi tek model", "K-NN Z-Score + Manhattan", "R² = 0.836")
        with col3:
            st.metric("❌ Catastrophic failure", "Min-Max + Chebyshev", "R² = -0.054")
    
    st.divider()
    
    # ── ZAMAN SERISI (BOLUM 7) ──
    st.markdown("#### 2. Zaman Serisi Algoritmalari (Bolum 7) - 5 Algoritma × 13 Segment")
    
    ts_df = time_series_en_iyi_yukle()
    
    # Algoritma birinci sayilari
    algo_birinci = ts_df['Algoritma'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Boyut 1: Birinci Olma Sayisi")
        
        fig = go.Figure(go.Bar(
            x=algo_birinci.values,
            y=algo_birinci.index,
            orientation='h',
            marker=dict(color=['#27ae60', '#3498db', '#9b59b6', '#f39c12', '#e74c3c']),
            text=algo_birinci.values,
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Hangi Algoritma Kac Segmentte Birinci?",
            xaxis_title="Birinci Olma Sayisi",
            height=350,
            yaxis=dict(autorange="reversed"),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Boyut 2: Best-of-Best Segment Sonuclari")
        
        # MAPE renkli badge'lerle gosterim
        ts_goster = ts_df[['Tip', 'Segment', 'Algoritma', 'MAPE', 'Forecast_2027']].copy()
        ts_goster = ts_goster.sort_values('MAPE').reset_index(drop=True)
        
        ts_goster['MAPE'] = ts_goster['MAPE'].apply(lambda x: f"%{x:.1f}")
        ts_goster['Forecast_2027'] = ts_goster['Forecast_2027'].apply(lambda x: f"${x:.2f}B")
        ts_goster.columns = ['Tip', 'Segment', 'Algoritma', 'MAPE', '2027 Tahmin']
        
        st.dataframe(ts_goster, use_container_width=True, hide_index=True, height=350)
    
    # Akademik vurgu
    with st.container(border=True):
        st.markdown("##### 🔬 Parsimony Principle Dogrulanmasi")
        st.markdown("""
        **Sampiyon: HoltWinters** (5 segmentte birinci, ortalama MAPE %21.9)
        
        **Catastrophic failure: LightGBM** (0 segment, ortalama MAPE %52.0)
        
        9 yillik veride **basit modeller** karmasik olanlari yendi. Bu, Occam's Razor 
        prensibinin ampirik kanitidir. Wolpert & Macready (1997) No Free Lunch teoremi 
        ile uyumlu.
        """)


# ═══════════════════════════════════════════════════════
# TAB 2: MAPE & LEWIS 1982
# ═══════════════════════════════════════════════════════
def _mape_lewis():
    st.markdown("### MAPE Esik Sistemi (Lewis 1982)")
    st.caption("Endustri standardi tahmin kalitesi siniflandirmasi")
    
    # ── 4 Renkli Kart ──
    st.markdown("#### Lewis 1982 Esikleri")
    
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        with st.container(border=True):
            st.markdown("##### 🟢 Yuksek")
            st.markdown("**MAPE < %10**")
            st.markdown("*Guvenle yatirim*")
    
    with k2:
        with st.container(border=True):
            st.markdown("##### 🟡 Iyi/Orta")
            st.markdown("**%10 - %20**")
            st.markdown("*Yatirim + uyari*")
    
    with k3:
        with st.container(border=True):
            st.markdown("##### 🟠 Makul/Dusuk")
            st.markdown("**%20 - %50**")
            st.markdown("*Alternatif degerlendir*")
    
    with k4:
        with st.container(border=True):
            st.markdown("##### 🔴 Guvenilmez")
            st.markdown("**> %50**")
            st.markdown("*Kullanma!*")
    
    st.divider()
    
    # ── 13 Segment Guven Siniflandirmasi ──
    st.markdown("#### 13 Anlamli Segment - Guven Hiyerarsisi")
    
    ts_df = time_series_en_iyi_yukle()
    ts_df = ts_df.sort_values('MAPE').reset_index(drop=True)
    
    # Her segment icin renkli kart
    for i in range(0, len(ts_df), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(ts_df):
                row = ts_df.iloc[i + j]
                guven, emoji, _ = lewis_kategorisi(row['MAPE'])
                
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"### {emoji} {row['Segment']}")
                        st.markdown(f"**{row['Tip']}** - {row['Algoritma']}")
                        m1, m2 = st.columns(2)
                        with m1:
                            st.metric("MAPE", f"%{row['MAPE']:.1f}")
                        with m2:
                            st.metric("Guven", guven)
                        st.metric("2027", f"${row['Forecast_2027']:.2f}B")
    
    st.divider()
    
    # ── Yapilan Yatirim Onerileri ──
    with st.container(border=True):
        st.markdown("##### 💡 Yatirim Karar Matrisi")
        
        st.markdown("""
        | Senaryo | MAPE | Karar |
        |---------|------|-------|
        | **Cluster_6 yatirimi** | %2.8 | 🟢 Guvenle yatirim |
        | **Indie yatirimi** | %2.7 | 🟢 Guvenle yatirim |
        | **Action yatirimi** | %8.2 | 🟢 Guvenle yatirim (paradoks dikkat) |
        | **Simulation yatirimi** | %10.1 | 🟡 Yatirim + risk uyarisi |
        | **Adventure** | %19.2 | 🟡 Iyi - dikkatli yatirim |
        | **RPG** | %20.2 | 🟠 Alternatif degerlendir (dustes paradoksu) |
        | **Sports** | %54.8 | 🔴 Karar destek icin kullanilamaz |
        """)


# ═══════════════════════════════════════════════════════
# TAB 3: 6 AMPIRIK BULGU
# ═══════════════════════════════════════════════════════
def _ampirik_bulgular():
    st.markdown("### Projenin 6 Ampirik Bulgu Mirasi")
    st.caption("Bolum 6'nin 3 + Bolum 7'nin 3 - bagimsiz testlerle dogrulanmis bulgular")
    
    bulgular = [
        {
            "no": 1,
            "baslik": "Taksonomik Karsilasma Yogunlugu",
            "kaynak": "Bolum 6",
            "altin": False,
            "icerik": """
            Icerik etiketleri (genre + tag), iki oyunun finansal benzerligini tek basina 
            ayirt edemez. %19 tam etiket eslesmesinde bile revenue farki 100x'e kadar cikabilir.
            
            **Sonuc:** Icerik benzerligi != finansal basari. Sosyal sinyaller (wishlist, 
            followers) kritik onem tasiyor.
            """
        },
        {
            "no": 2,
            "baslik": "Finansal Korluk Testi (Content-Based)",
            "kaynak": "Bolum 6.7",
            "altin": False,
            "icerik": """
            10 hit oyun icin Content-Based'in onerdigi benzer oyunlarin ortalama revenue'su, 
            hit oyunun **%15.3'u** kadardir (sistematik alt-tahmin).
            
            **Sonuc:** Content-Based, finansal tahmin icin tek basina yetersiz - cold-start 
            disinda kullanilmamali.
            """
        },
        {
            "no": 3,
            "baslik": "Negatif Meta-Learner Agirligi (AKADEMIK ALTIN)",
            "kaynak": "Bolum 6.8",
            "altin": True,
            "icerik": """
            Hybrid Stacking meta-learner'i, Content-Based'e **NEGATIF agirlik** 
            (-0.1511) atadi. |w_cb|/w_knn = **0.130 (%13)**.
            
            **🌟 Carpici detay:** Bu oran, Bolum 6.7'deki finansal korluk %15.3 oraniyla 
            **bagimsiz testle dogrulandi** (~2 puan fark). Meta-learner, bias buyuklugunu 
            **veriden kendi kesfetti** - aciktan programlanmadi.
            
            **Sonuc:** Veri-odakli modellerin gizli yapilari otomatik kesfetme 
            kapasitesinin somut bir ornegi.
            """
        },
        {
            "no": 4,
            "baslik": "Parsimony Principle (Occam's Razor)",
            "kaynak": "Bolum 7",
            "altin": False,
            "icerik": """
            Yillik 11 noktali veride basit modeller karmasik olanlari yendi:
            - **HoltWinters:** 5 segmentte birinci (sampiyon)
            - **LightGBM:** 0 segmentte birinci (catastrophic failure, %52 MAPE)
            
            **Sonuc:** Karmasiklik != Performans. Veri yapisi dogru algoritmayi belirler.
            """
        },
        {
            "no": 5,
            "baslik": "No Free Lunch Pratik Uygulamasi (Wolpert 1997)",
            "kaynak": "Bolum 7",
            "altin": False,
            "icerik": """
            5 algoritmadan hicbiri tum segmentlerde en iyi degil:
            - **HoltWinters:** Trend-dominant segmentler
            - **ARIMA:** Otokorelasyonlu segmentler (Cluster_6)
            - **Prophet:** Orta buyuklukteki segmentler
            - **Linear:** Kucuk segmentler
            
            **Sonuc:** Tek model yetmez - **Best-of-Best yaklasimi** zorunlu.
            """
        },
        {
            "no": 6,
            "baslik": "Gecmis-Gelecek CAGR Paradoksu (AKADEMIK ALTIN)",
            "kaynak": "Bolum 7",
            "altin": True,
            "icerik": """
            Carpici celiski:
            - **Gecmis 10 yil CAGR** (2015-2025): **+%17.4**
            - **Model projeksiyon CAGR** (2025-2027): **+%2.7**
            - **Fark:** ~**7.1 kat**
            
            **🌟 Olasi nedenler:** ARIMA mean-reversion egilimi, Action segmentinde 
            stagnasyon, pazar doygunlugu sinyali.
            
            **Cikarim:** Tek bir CAGR rakami yerine **senaryo bazli yaklasim** 
            (Worst/Base/Best) akademik durustluk acisindan gerekli.
            """
        },
    ]
    
    # Her bulgu icin acilabilir kart
    for b in bulgular:
        # Altin bulgu vurgusu
        emoji = "🌟" if b['altin'] else "📌"
        with st.expander(f"{emoji} **Bulgu {b['no']}:** {b['baslik']} _{b['kaynak']}_"):
            st.markdown(b['icerik'])
            
            if b['altin']:
                st.success("🌟 **AKADEMIK ALTIN BULGU** - bu projenin en degerli katkilarindan biri.")
    
    st.divider()
    
    # ── Bulgu Sentezi ──
    with st.container(border=True):
        st.markdown("### 🎯 Bulgular Sentezi - Dort Akademik Mesaj")
        
        st.markdown("""
        Bu 6 bulgu dort temel akademik mesaj iletir:
        
        1. **Veri-odakli modeller, programlanmamis ilişkileri kesfedebilir** (Bulgu 3)
        2. **Karmasiklik != Performans - veri yapisi algoritmayi belirler** (Bulgu 4, 5)
        3. **Sistematik bias'lar bagimsiz testlerle dogrulanabilir** (Bulgu 2 + 3)
        4. **Tek tahmin yerine senaryo bandi - belirsizligi iletme zorunlulugu** (Bulgu 6)
        """)


# ═══════════════════════════════════════════════════════
# TAB 4: ATIFLAR & EM CERÇEVESI
# ═══════════════════════════════════════════════════════
def _atiflar_em():
    st.markdown("### Akademik Atiflar ve Endustri Muhendisligi Cerçevesi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 Birincil Atiflar")
        
        st.markdown("""
        **Onerme & Ensemble Learning:**
        - **Wolpert, D. H.** (1992). "Stacked Generalization". *Neural Networks*, 5(2), 241-259.
        - **Wolpert, D. H. & Macready, W. G.** (1997). "No Free Lunch Theorems for Optimization". 
          *IEEE Trans. Evolutionary Computation*, 1(1), 67-82.
        - **Aggarwal, C. C.** vd. (2001). "On the Surprising Behavior of Distance Metrics 
          in High Dimensional Space".
        - **Schein, A. I.** vd. (2002). "Methods and Metrics for Cold-Start Recommendations". *SIGIR '02*.
        - **Bobadilla, J.** vd. (2013). "Recommender Systems Survey". *Knowledge-Based Systems*, 46.
        
        **Zaman Serisi & Tahmin:**
        - **Box, G. E. P. & Jenkins, G. M.** (1970). *Time Series Analysis: Forecasting and Control*.
        - **Holt, C. C.** (1957) & **Winters, P. R.** (1960). Exponential Smoothing.
        - **Taylor, S. J. & Letham, B.** (2018). "Forecasting at Scale". *The American Statistician*. (Prophet)
        - **Lewis, C. D.** (1982). *Industrial and Business Forecasting Methods*. Butterworth.
        - **Hyndman, R. J. & Koehler, A. B.** (2006). "Another Look at Measures of Forecast Accuracy".
        - **Makridakis, S.** vd. (2020). M4 Competition.
        """)
    
    with col2:
        st.markdown("#### 🏛️ DSS & Karar Verme")
        
        st.markdown("""
        **Karar Destek Sistemleri:**
        - **Sprague, R. H. Jr.** (1980). "A Framework for DSS Development". *MIS Quarterly*, 4(4).
        - **Turban, E.** vd. (2011). *Decision Support and Business Intelligence Systems* (9th ed.).
        - **Damodaran, A.** (2012). *Investment Valuation* (3rd ed.). Wiley.
        - **Saaty, T. L.** (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
        
        **Pazarlama & Segmentasyon:**
        - **Smith, W. R.** (1956). "Product Differentiation and Market Segmentation". 
          *Journal of Marketing*, 21(1).
        - **Kotler, P.** Pazarlama yonetimi pozisyonlama haritasi metodolojisi.
        """)
    
    st.divider()
    
    # ── EM CERÇEVESI ──
    st.markdown("### 🏭 Endustri Muhendisligi Cerçevesi")
    
    st.markdown("""
    Bu proje, klasik endustri muhendisligi disiplinlerinin **somut uygulamasi**dir:
    """)
    
    em_tablo = pd.DataFrame([
        {"EM Disiplini": "Talep Tahmini", "Bu Projedeki Karsiligi": "5 zaman serisi algoritmasi - Bolum 7"},
        {"EM Disiplini": "Stok Yonetimi (ABC)", "Bu Projedeki Karsiligi": "Pareto analizi - Cluster_6 %93.3"},
        {"EM Disiplini": "Karar Destek Sistemi (Sprague 1980)", "Bu Projedeki Karsiligi": "Bolum 8 - 3 alt sistem (DBMS, MBMS, Dialog)"},
        {"EM Disiplini": "Multi-Criteria Decision Making", "Bu Projedeki Karsiligi": "Algoritma secimi MCDM tablosu - Bolum 6.8"},
        {"EM Disiplini": "Stokastik Programlama", "Bu Projedeki Karsiligi": "Worst/Base/Best senaryolar (±%30)"},
        {"EM Disiplini": "Kalite Yonetimi", "Bu Projedeki Karsiligi": "MAPE esikleri ile guven sınıflandırma"},
        {"EM Disiplini": "Yoneylem Arastirmasi (OR)", "Bu Projedeki Karsiligi": "Ensemble learning + facility location analogy"},
        {"EM Disiplini": "Bayesian Decision Theory", "Bu Projedeki Karsiligi": "Hybrid Stacking - BMA'nin frequentist esdegeri"},
        {"EM Disiplini": "DMAIC Metodolojisi", "Bu Projedeki Karsiligi": "Define-Measure-Analyze-Improve-Control: Bolumler 1-8"},
    ])
    
    st.dataframe(em_tablo, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ── PROJE ISTATISTIK ──
    st.markdown("### 📊 Proje Istatistikleri")
    
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Veri Boyutu", "113.456 oyun", "63 → 156 sutun")
    with s2:
        st.metric("Model Sayisi", "15 model", "10 oneri + 5 zaman serisi")
    with s3:
        st.metric("Akademik Atif", "15+ atif", "1956-2020 donem")
    with s4:
        st.metric("Ampirik Bulgu", "6 bulgu", "2 altin bulgu")
    
    st.divider()
    
    # ── PROJE ALCI ──
    with st.container(border=True):
        st.markdown("### 🎓 Proje Bilgileri")
        st.markdown("""
        **Proje Adi:** Steam Marketplace Karar Destek Sistemi  
        **Kurum:** Dokuz Eylul Universitesi - Endustri Muhendisligi  
        **Donem:** Mayis 2026  
        **Veri Saglayicisi:** DataHumble (proxy veri)  
        **Veri Buyuklugu:** 113.456 oyun, 11 yil (2015-2025)  
        **Metodoloji:** CRISP-DM, DMAIC, ISO/IEC 25010
        """)
        