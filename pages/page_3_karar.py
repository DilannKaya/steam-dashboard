"""
Sayfa 3: Karar Destek Sistemi
==============================
Senaryo A: Mevcut Oyun Analizi (Hybrid Stacking + Cluster CAGR)
Senaryo B: Yeni Oyun Planlama (Content-Based + Genre CAGR)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity

from utils.data_loader import (
    df_dashboard_yukle,
    knn_model_egit,
    content_based_matris_hazirla,
    cagr_sozlukleri_hazirla,
    cluster_id_to_isim,
    lewis_kategorisi,
    META_W_KNN,
    META_W_CB,
    META_B,
    SAYISAL_OZELLIKLER,
)


def goster(df):
    """Sayfa 3: Karar Destek"""
    
    st.markdown("## Karar Destek Sistemi")
    st.caption("Sprague (1980) DSS Framework - Hybrid Stacking + Best-of-Best zaman serisi modelleri")
    
    # Iki senaryo sekmesi
    tab_a, tab_b = st.tabs([
        "🔍 Senaryo A: Mevcut Oyun Analizi",
        "🚀 Senaryo B: Yeni Oyun Planlama"
    ])
    
    # ════════════════════════════════════════════════════
    # TAB A: MEVCUT OYUN
    # ════════════════════════════════════════════════════
    with tab_a:
        _senaryo_a(df)
    
    # ════════════════════════════════════════════════════
    # TAB B: YENI OYUN
    # ════════════════════════════════════════════════════
    with tab_b:
        _senaryo_b(df)


# ════════════════════════════════════════════════════════
# SENARYO A: MEVCUT OYUN ANALIZI
# ════════════════════════════════════════════════════════
def _senaryo_a(df):
    st.markdown("### Mevcut Oyun Analizi")
    st.caption("Yayinci/Yatirimci icin - bir oyunun 2027 performansini tahmin et")
    
    # Model ve verileri yukle (cache'li)
    with st.spinner("K-NN modeli yukleniyor..."):
        knn_model, scaler, X_zscore = knn_model_egit()
        cluster_cagr, genre_cagr, FALLBACK_CAGR = cagr_sozlukleri_hazirla()
    
    # ── GIRDI: Oyun secimi ──
    st.markdown("#### 1. Oyun Sec")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # NSFW disinda en yuksek revenue 100 oyun
        df_secim = df[df['Revenue'] > 0].nlargest(200, 'Revenue').copy()
        df_secim['etiket'] = df_secim.apply(
            lambda r: f"{r['Name']} ({r['primary_genre']}, ${r['Revenue']:,.0f})",
            axis=1
        )
        
        secili_etiket = st.selectbox(
            "Bir oyun secin (top 200 revenue):",
            options=df_secim['etiket'].tolist(),
            index=0,
            help="Bu listeyi en yuksek revenue'lu 200 oyunla sinirladik"
        )
        
        secili_steam_id = df_secim[df_secim['etiket'] == secili_etiket]['Steam Id'].iloc[0]
    
    with col2:
        st.markdown("##### Veya")
        manuel_id = st.text_input("Steam ID gir:", value="", help="Direkt Steam ID")
        if manuel_id.isdigit() and int(manuel_id) in df['Steam Id'].values:
            secili_steam_id = int(manuel_id)
    
    # Oyun bilgileri
    oyun = df[df['Steam Id'] == secili_steam_id].iloc[0]
    
    st.divider()
    
    # ── OYUN PROFILI ──
    st.markdown(f"#### 2. Oyun Profili: **{oyun['Name']}**")
    
    # Ust satir: 4 ana metrik
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Primary Genre", oyun['primary_genre'])
    with p2:
        cluster_isim = cluster_id_to_isim(int(oyun['kmeans_cluster']))
        st.metric("Cluster", cluster_isim)
    with p3:
        st.metric("2025 Revenue", f"${oyun['Revenue']:,.0f}")
    with p4:
        st.metric("Wishlist", f"{int(oyun['Wishlists']):,}")
    
    # Alt satir: 3 ek metrik
    p5, p6, p7 = st.columns(3)
    with p5:
        review_skor = oyun['Review Score']
        if pd.notna(review_skor):
            if review_skor >= 80:
                renk = "🟢"
            elif review_skor >= 60:
                renk = "🟡"
            else:
                renk = "🔴"
            st.metric("Review Score", f"{renk} {review_skor:.1f}")
        else:
            st.metric("Review Score", "N/A")
    
    with p6:
        review_sayisi = oyun['Review count'] if 'Review count' in oyun else None
        if pd.notna(review_sayisi):
            st.metric("Inceleme Sayisi", f"{int(review_sayisi):,}")
        else:
            st.metric("Inceleme Sayisi", "N/A")
    
    with p7:
        fiyat = oyun['price_usd'] if 'price_usd' in oyun else oyun.get('price_usd_clipped', 0)
        st.metric("Fiyat", f"${fiyat:.2f}" if fiyat > 0 else "Free")
    
    st.divider()
    
    # ── HYBRID STACKING TAHMINI ──
    st.markdown("#### 3. Hybrid Stacking Tahmini (Bolum 6.8)")
    
    # Oyunun ozellik vektoru
    oyun_index = df[df['Steam Id'] == secili_steam_id].index[0]
    df_idx = df.index.get_loc(oyun_index)
    
    oyun_vector = X_zscore[df_idx].reshape(1, -1)
    
    # K-NN tahmini
    y_knn_log = float(knn_model.predict(oyun_vector)[0])
    
    # K=6 komsu cek (1 fazla, kendisini ayiklamak icin)
    mesafeler_raw, komsu_idx_raw = knn_model.kneighbors(oyun_vector, n_neighbors=6)
    
    # Kendisini cikar (Steam ID karsilastirmasi - guvenilir)
    maske = komsu_idx_raw[0] != df_idx
    komsu_idx = komsu_idx_raw[0][maske][:5]
    mesafeler = mesafeler_raw[0][maske][:5]
    
    # Content-Based tahmini (basitlestirilmis: K-NN ile ayni komsularin log_revenue ortalamasi)
    y_cb_log = float(df.iloc[komsu_idx]['log_revenue'].mean())
    
    # Hybrid Stacking formulu
    y_hat_hybrid_log = META_W_KNN * y_knn_log + META_W_CB * y_cb_log + META_B
    revenue_baz_usd = float(np.expm1(y_hat_hybrid_log))
    
    # Hybrid bilesenleri goster
    h1, h2, h3 = st.columns(3)
    with h1:
        st.metric("K-NN Tahmini", f"${np.expm1(y_knn_log):,.0f}",
                  help="ZScore + Manhattan + K=5")
    with h2:
        st.metric("Content-Based", f"${np.expm1(y_cb_log):,.0f}",
                  help="K-NN komsularinin ortalamasi (basitlestirilmis)")
    with h3:
        st.metric("Hybrid Stacking", f"${revenue_baz_usd:,.0f}",
                  delta=f"vs Gercek: {(revenue_baz_usd - oyun['Revenue']) / oyun['Revenue'] * 100:+.1f}%"
                  if oyun['Revenue'] > 0 else None,
                  delta_color="off")
    
    st.code(f"Formul: {META_W_KNN:+.4f} × y_knn + ({META_W_CB:+.4f}) × y_cb + ({META_B:+.4f})",
            language="text")
    
    # Negatif w_cb akademik aciklama
    with st.expander("🔬 Neden Negatif Content-Based Agirligi?"):
        st.markdown("""
        **Bolum 6.8'in en buyuk akademik bulgusu:** 
        
        Meta-learner, Content-Based modelin tahminine **negatif agirlik (-0.1511)** atadi. 
        Bu, Content-Based'in sistematik olarak **alt-tahmin yaptiginin** matematiksel kanitidir 
        (Bolum 6.7 finansal korluk testi: %15.3 alt-tahmin).
        
        **|w_cb| / w_knn = 0.130 (%13)** ≈ Bolum 6.7'deki %15.3 oraniyla 
        **bagimsiz testle dogrulandi** (~2 puan fark). Meta-learner, bias buyuklugunu 
        veriden bagimsiz kesfetti.
        """)
    
    st.divider()
    
    # ── EN BENZER 5 OYUN ──
    st.markdown("#### 4. En Benzer 5 Oyun (K-NN, Manhattan)")
    
    # Cosine benzerligi - 7 boyutlu Z-Score uzayinda
    cosine_skorlari = cosine_similarity(oyun_vector, X_zscore[komsu_idx])[0]
    
    # Manhattan mesafesini boyut basina normalize et (7 boyut)
    mesafe_per_boyut = mesafeler / len(SAYISAL_OZELLIKLER)
    
    benzer = df.iloc[komsu_idx].copy()
    benzer['Mesafe'] = mesafe_per_boyut
    benzer['Cosine'] = cosine_skorlari
    
    tablo = benzer[['Name', 'primary_genre', 'Revenue', 'Review Score', 'Cosine', 'Mesafe']].copy()
    tablo['Revenue'] = tablo['Revenue'].apply(lambda x: f"${x:,.0f}")
    tablo['Review Score'] = tablo['Review Score'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
    tablo['Cosine'] = tablo['Cosine'].apply(lambda x: f"{x:.4f}")
    tablo['Mesafe'] = tablo['Mesafe'].apply(lambda x: f"{x:.3f}")
    tablo.columns = ['Oyun', 'Genre', '2025 Revenue', 'Review', 'Cosine Benzerligi', 'Mesafe/Boyut']
    
    st.dataframe(tablo, use_container_width=True, hide_index=True)
    
    # Akademik aciklama
    with st.expander("📐 Benzerlik Metriklerinin Yorumu"):
        st.markdown("""
        - **Cosine Benzerligi:** 7 boyutlu Z-Skor uzayinda iki vektor arasindaki acinin kosinusu. 
          [-1, +1] araliginda olcek. **+1.000** tipatip ayni, **0** ilgisiz, **negatif** ters yon.
          113.456 oyun arasinda en yakin 5 olduklari icin **genelde 0.85+ degerleri beklenir**.
        - **Mesafe/Boyut:** Manhattan mesafesinin boyut sayisina (7) bolunmesi. 
          Yorumu kolaylastirir. Dusuk deger = yakin komsu.
        - **Metodoloji kaynagi:** Aggarwal vd. (2001) yuksek boyutlu uzayda Manhattan'in 
          Euclidean'a ustunlugunu gostermistir; Bobadilla vd. (2013) oneri sistemlerinde 
          cosine'in standart kullanimi vurgulamistir.
        """)
    
    st.divider()

    # ── CLUSTER CAGR + 2027 PROJEKSIYONU ──
    st.markdown("#### 5. 2027 Revenue Projeksiyonu")
    
    cluster_id = int(oyun['kmeans_cluster'])
    fallback_kullanildi = False
    
    if cluster_id in cluster_cagr:
        cagr_bilgi = cluster_cagr[cluster_id]
        cagr_kaynagi = f"Cluster_{cluster_id} ({cluster_isim})"
    elif oyun['primary_genre'] in genre_cagr:
        cagr_bilgi = genre_cagr[oyun['primary_genre']]
        cagr_kaynagi = f"{oyun['primary_genre']} (Genre fallback - cluster filtreli)"
        fallback_kullanildi = True
    else:
        cagr_bilgi = {'cagr': FALLBACK_CAGR, 'mape': 50.0, 'algo': 'FALLBACK',
                      'forecast_2027': 0, 'gercek_2025': 0}
        cagr_kaynagi = "Toplam pazar (genel fallback)"
        fallback_kullanildi = True
    
    cagr = cagr_bilgi['cagr']
    mape = cagr_bilgi['mape']
    
    # 2027 hesaplari
    revenue_2027_base = revenue_baz_usd * ((1 + cagr) ** 2)
    revenue_2027_worst = revenue_2027_base * 0.70
    revenue_2027_best = revenue_2027_base * 1.30
    
    # CAGR + algoritma bilgisi
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("CAGR Kaynagi", cagr_kaynagi.split(' (')[0])
        if fallback_kullanildi:
            st.caption("⚠️ Fallback kullanildi")
    with c2:
        st.metric("Yillik CAGR", f"{cagr * 100:+.2f}%")
    with c3:
        st.metric("Algoritma", cagr_bilgi['algo'])
    with c4:
        st.metric("MAPE", f"%{mape:.1f}")
    
    # Lewis 1982 etiketi
    guven, emoji, oneri = lewis_kategorisi(mape)
    st.info(f"**{emoji} Lewis 1982 Guven Seviyesi: {guven}** — {oneri}")
    
    st.markdown("##### Worst / Base / Best Senaryolar (±%30 Yonetimsel Bant)")
    
    # 3 senaryo gosterimi
    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(border=True):
            st.markdown("##### 🔴 Worst Case")
            st.markdown("**-30% Pesimist**")
            st.metric("2027 Tahmini", f"${revenue_2027_worst:,.0f}",
                      delta=f"{(revenue_2027_worst / revenue_baz_usd - 1) * 100:+.1f}% vs 2025 baz",
                      delta_color="inverse")
    
    with s2:
        with st.container(border=True):
            st.markdown("##### 🎯 Base Case")
            st.markdown("**Hybrid + CAGR**")
            st.metric("2027 Tahmini", f"${revenue_2027_base:,.0f}",
                      delta=f"{(revenue_2027_base / revenue_baz_usd - 1) * 100:+.1f}% vs 2025 baz")
    
    with s3:
        with st.container(border=True):
            st.markdown("##### 🟢 Best Case")
            st.markdown("**+30% Optimist**")
            st.metric("2027 Tahmini", f"${revenue_2027_best:,.0f}",
                      delta=f"{(revenue_2027_best / revenue_baz_usd - 1) * 100:+.1f}% vs 2025 baz")
    
    # ± %30 yorum
    st.caption(
        "**±%30 bandi gerekçesi:** Damodaran (2012, *Investment Valuation*) - "
        "finansal projeksiyonlarda yaygin yonetimsel bant. Modelin gercek MAE'si (log uzayinda 1.078, "
        "dolar uzayinda ~2.94x) cok daha genis ama yatirim karari icin kullanilamaz."
    )
    
    # ── PROJEKSIYON GRAFIGI ──
    st.markdown("#### 6. Gorselleştirme")
    
    fig = go.Figure()
    
    # Gercek 2025
    fig.add_trace(go.Scatter(
        x=[2025], y=[oyun['Revenue']],
        mode='markers+text',
        name='2025 Gercek',
        marker=dict(size=15, color='#2E86AB'),
        text=[f"${oyun['Revenue']:,.0f}"],
        textposition='top center'
    ))
    
    # Hybrid Baz (2025 model tahmini)
    fig.add_trace(go.Scatter(
        x=[2025], y=[revenue_baz_usd],
        mode='markers+text',
        name='2025 Hybrid Tahmin',
        marker=dict(size=12, color='#9b59b6', symbol='diamond'),
        text=[f"${revenue_baz_usd:,.0f}"],
        textposition='bottom center'
    ))
    
    # 2027 senaryolar
    fig.add_trace(go.Scatter(
        x=[2027, 2027, 2027],
        y=[revenue_2027_worst, revenue_2027_base, revenue_2027_best],
        mode='markers+text',
        name='2027 Senaryolar',
        marker=dict(size=[12, 18, 12], 
                    color=['#e74c3c', '#27ae60', '#f39c12']),
        text=[f"Worst: ${revenue_2027_worst:,.0f}",
              f"Base: ${revenue_2027_base:,.0f}",
              f"Best: ${revenue_2027_best:,.0f}"],
        textposition=['middle left', 'top center', 'middle right']
    ))
    
    # Base trajectory
    fig.add_trace(go.Scatter(
        x=[2025, 2027],
        y=[revenue_baz_usd, revenue_2027_base],
        mode='lines',
        name='Base Trajectory',
        line=dict(color='#27ae60', dash='dash', width=2),
        showlegend=False
    ))
    
    fig.update_layout(
        title=f"{oyun['Name']} - 2025 → 2027 Projeksiyon",
        xaxis_title="Yil",
        yaxis_title="Revenue (USD)",
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════
# SENARYO B: YENI OYUN PLANLAMA (COLD-START)
# ════════════════════════════════════════════════════════
def _senaryo_b(df):
    st.markdown("### Yeni Oyun Planlama (Cold-Start)")
    st.caption("Gelistirici stüdyo icin - henuz var olmayan bir oyunun profil bazli tahmini")
    
    # Cache'li veriler
    cluster_cagr, genre_cagr, FALLBACK_CAGR = cagr_sozlukleri_hazirla()
    X_content, feature_isimleri, anlamli_genres, top_30_tag, top_30_feature = content_based_matris_hazirla()
    
    df_yardimci = df_dashboard_yukle()
    
    # ── AKADEMIK UYARI - EN BASTA ──
    with st.container(border=True):
        st.warning("""
        **⚠️ Cold-Start Sınırlılığı (Bölüm 6.7 — Bulgu 2)**
        
        Bu senaryo, **henüz piyasaya çıkmamış bir oyun** için Content-Based Filtering kullanmaktadır. 
        Bölüm 6.7'de yapılan finansal körlük testi, bu yaklaşımın sistematik olarak **%15.3 alt-tahmin** 
        yaptığını göstermiştir. Bölüm 6.8'deki Hybrid Stacking meta-öğrenicisi bu eksikliği -0.1511 
        negatif ağırlık ile telafi etmiş; ancak yeni oyun için K-NN modeli kullanılamadığından 
        Senaryo B'de bu telafi mümkün değildir.
        
        **Sonuç:** Bu tahmin bir **referans noktası**dır, kesin projeksiyon değildir.
        """)
    
    st.divider()
    
    st.markdown("#### 1. Yeni Oyun Profili Tanimla")
    
    col1, col2 = st.columns(2)
    
    with col1:
        secili_genre = st.selectbox(
            "Primary Genre:",
            options=anlamli_genres,
            index=0,
            help="Planladiginiz oyunun ana kategorisi"
        )
    
    with col2:
        secili_tagler = st.multiselect(
            "Tags (Steam Etiketleri):",
            options=top_30_tag,
            default=[top_30_tag[0]] if top_30_tag else [],
            max_selections=10,
            help="En cok 10 tag secebilirsiniz"
        )
    
    secili_features = st.multiselect(
        "Features (Steam Ozellikleri):",
        options=top_30_feature,
        default=[top_30_feature[0]] if top_30_feature else [],
        max_selections=10,
        help="Oyununuza dahil etmeyi planladiginiz teknik ozellikler"
    )
    
    st.divider()
    
    # ── CONTENT-BASED TAHMINI ──
    st.markdown("#### 2. Content-Based Filtering Tahmini")
    
    # Yeni oyun vektoru olustur
    yeni_vektor = np.zeros(len(feature_isimleri), dtype=np.float32)
    
    for i, isim in enumerate(feature_isimleri):
        if isim.startswith('genre_') and isim.replace('genre_', '') == secili_genre:
            yeni_vektor[i] = 1
        elif isim.startswith('tag_') and isim.replace('tag_', '') in secili_tagler:
            yeni_vektor[i] = 1
        elif isim.startswith('feature_') and isim.replace('feature_', '') in secili_features:
            yeni_vektor[i] = 1
    
    aktif_ozellik_sayisi = int(yeni_vektor.sum())
    
    if aktif_ozellik_sayisi == 0:
        st.error("⚠️ En az 1 tag, feature veya genre secmelisiniz.")
        return
    
    # ÖNEMLİ: Revenue > 0 filtresi - cold-start için anlamlı tahmin
    revenue_mask = df_yardimci['Revenue'] > 0
    X_content_filtered = X_content[revenue_mask.values]
    df_filtered = df_yardimci[revenue_mask].reset_index(drop=True)
    
    # En benzer 5 oyun (Revenue > 0 olanlar arasından)
    similarities = cosine_similarity(yeni_vektor.reshape(1, -1), X_content_filtered)[0]
    top_5_idx = np.argsort(-similarities)[:5]
    
    # Tahmin: top-5 log_revenue ortalamasi
    benzer_oyunlar = df_filtered.iloc[top_5_idx].copy()
    y_benzer_log = float(benzer_oyunlar['log_revenue'].mean())
    revenue_baz_usd = float(np.expm1(y_benzer_log))
    
    # Genre CAGR
    if secili_genre in genre_cagr:
        cagr_bilgi = genre_cagr[secili_genre]
        cagr_kaynagi = f"{secili_genre} genre"
    else:
        cagr_bilgi = {'cagr': FALLBACK_CAGR, 'mape': 50.0, 'algo': 'FALLBACK'}
        cagr_kaynagi = "Toplam pazar (fallback)"
    
    cagr = cagr_bilgi['cagr']
    mape = cagr_bilgi['mape']
    
    # 2027 projeksiyonu
    revenue_2027_base = revenue_baz_usd * ((1 + cagr) ** 2)
    revenue_2027_worst = revenue_2027_base * 0.70
    revenue_2027_best = revenue_2027_base * 1.30
    
    # Profil ozeti
    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric("Genre", secili_genre)
    with p2:
        st.metric("Aktif Ozellik", aktif_ozellik_sayisi)
    with p3:
        st.metric("Tahmin Tabani", f"${revenue_baz_usd:,.0f}")
    
    # Lewis etiketi
    guven, emoji, oneri = lewis_kategorisi(mape)
    st.info(f"**{emoji} Lewis 1982 Guven: {guven}** — {oneri} (MAPE %{mape:.1f}, {cagr_bilgi['algo']})")
    
    st.divider()
    
    # ── BENZER 5 OYUN ──
    st.markdown("#### 3. Profile En Benzer 5 Oyun (Revenue > 0 filtresi)")
    
    tablo = benzer_oyunlar[['Name', 'primary_genre', 'Revenue', 'Review Score', 'price_usd']].copy()
    tablo['Cosine Sim'] = similarities[top_5_idx]
    
    tablo['Revenue'] = tablo['Revenue'].apply(lambda x: f"${x:,.0f}")
    tablo['Review Score'] = tablo['Review Score'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
    tablo['price_usd'] = tablo['price_usd'].apply(lambda x: f"${x:.2f}" if x > 0 else "Free")
    tablo['Cosine Sim'] = tablo['Cosine Sim'].apply(lambda x: f"{x:.4f}")
    tablo.columns = ['Oyun', 'Genre', '2025 Revenue', 'Review', 'Fiyat', 'Cosine Benzerligi']
    
    st.dataframe(tablo, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ── 2027 SENARYOLAR ──
    st.markdown("#### 4. 2027 Revenue Projeksiyonu (Worst / Base / Best)")
    
    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(border=True):
            st.markdown("##### 🔴 Worst Case")
            st.markdown("**-30% Pesimist**")
            st.metric("2027", f"${revenue_2027_worst:,.0f}")
    
    with s2:
        with st.container(border=True):
            st.markdown("##### 🎯 Base Case")
            st.markdown(f"**CB + {secili_genre} CAGR**")
            st.metric("2027", f"${revenue_2027_base:,.0f}",
                      delta=f"CAGR +%{cagr * 100:.1f}/yil")
    
    with s3:
        with st.container(border=True):
            st.markdown("##### 🟢 Best Case")
            st.markdown("**+30% Optimist**")
            st.metric("2027", f"${revenue_2027_best:,.0f}")
    
    st.divider()
    
    # ── COLD-START DETAYLI UYARI ──
    with st.expander("📚 Cold-Start Probleminin Akademik Sinirlilig​i"):
        st.markdown("""
        Bu tahmin, **cold-start probleminin** (Schein vd., 2002) dogasi geregi bazi sinirlamalara sahiptir:
        
        | Sinirlamadi | Etkisi | Atif |
        |-------------|--------|------|
        | Bulgu 1: Taksonomik Karsilasma Yogunlugu | Etiketler tek basina finansal basariyi belirleyemez | Bolum 6.1 |
        | Bulgu 2: Finansal Korluk Testi | %15.3 sistematik alt-tahmin | Bolum 6.7 |
        | Wishlist gercek degil tahmini | Sosyal sinyal eksik | - |
        | Marketing butçesi modellenmedi | Ayni profilin farkli çikti olabilir | - |
        | Lansman zamanlamasi yok | Sezon, indirim faktorleri yok | - |
        | Studyo itibari yok | Yeni AAA vs yeni indie farki | - |
        | Tag uzayi dar (30 etiket) | Eksik kategoriler | Bolum 6.8 |
        
        **Telafi mekanizmasi:** Bolum 6.8 Hibrit Stacking meta-ogrenicisi, K-NN ve Content-Based 
        modeli birlikte kullanarak %15.3 alt-tahmin biasini -0.1511 negatif agirlik ile telafi etmektedir. 
        Ancak yeni oyun icin K-NN kullanilamadigindan bu telafi Senaryo B'de mumkun degildir.
        """)