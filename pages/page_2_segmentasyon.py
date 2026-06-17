"""
Sayfa 2: Segmentasyon ve Pazar Haritasi
========================================
3 segmentasyon yaklasimi: Genre, Genre x Fiyat, KMeans Cluster
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import (
    segment_genre_yukle,
    segment_genre_fiyat_oyun_yukle,
    segment_genre_fiyat_revenue_yukle,
    segment_kmeans_yukle,
    cluster_id_to_isim,
)
from utils.styles import CLUSTER_RENKLERI


def goster(df):
    """Sayfa 2: Segmentasyon"""
    
    st.markdown("## Pazar Segmentasyonu - 3 Yaklasim")
    st.caption("Steam pazari **uc farkli stratejiyle** parcalara ayrildi. Her yaklasim farkli bir karar destek perspektifi sunar.")
    
    # 3 segmentasyon sekmesi
    tab1, tab2, tab3 = st.tabs([
        "📊 Genre Bazli (12)",
        "🗺️ Genre x Fiyat (Matrix)",
        "🎯 KMeans Cluster (10)"
    ])
    
    # ═══════════════════════════════════════════════════
    # TAB 1: GENRE BAZLI
    # ═══════════════════════════════════════════════════
    with tab1:
        _genre_sekmesi(df)
    
    # ═══════════════════════════════════════════════════
    # TAB 2: GENRE x FIYAT
    # ═══════════════════════════════════════════════════
    with tab2:
        _genre_fiyat_sekmesi()
    
    # ═══════════════════════════════════════════════════
    # TAB 3: KMEANS CLUSTER
    # ═══════════════════════════════════════════════════
    with tab3:
        _kmeans_sekmesi()


# ═══════════════════════════════════════════════════════
# TAB 1: GENRE BAZLI SEGMENTASYON
# ═══════════════════════════════════════════════════════
def _genre_sekmesi(df):
    st.markdown("### Genre Bazli Segmentasyon")
    st.caption("12 anlamli genre - manuel atama, basit yapi, yuksek yorumlanabilirlik")
    
    genre_profil = segment_genre_yukle()
    
    # Toplam revenue'ye gore sirala
    genre_profil = genre_profil.sort_values('toplam_revenue', ascending=False)
    
    # Pazar payi hesapla
    toplam_pazar = genre_profil['toplam_revenue'].sum()
    genre_profil['pazar_pay'] = (genre_profil['toplam_revenue'] / toplam_pazar) * 100
    
    # ── 2 sutun: Sol bar chart, Sag pasta grafik ──
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Oyun Sayisi vs Pazar Payi")
        
        # Iki bar chart yan yana
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=genre_profil['primary_genre'],
            x=genre_profil['oyun_sayisi'],
            name='Oyun Sayisi',
            orientation='h',
            marker=dict(color='#3498db'),
            text=genre_profil['oyun_sayisi'].apply(lambda x: f"{x:,.0f}"),
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Genre Bazinda Oyun Sayisi",
            xaxis_title="Oyun Sayisi",
            height=500,
            yaxis=dict(autorange="reversed")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Pazar Payi Dagilimi")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=genre_profil['primary_genre'],
            x=genre_profil['pazar_pay'],
            name='Pazar Payi (%)',
            orientation='h',
            marker=dict(color='#e74c3c'),
            text=genre_profil['pazar_pay'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Genre Bazinda Pazar Payi",
            xaxis_title="Pazar Payi (%)",
            height=500,
            yaxis=dict(autorange="reversed")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ── ACTION PARADOKSU VURGUSU ──
    with st.container(border=True):
        st.markdown("### 🎯 Action Paradoksu")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Action Oyun Sayisi", "8.995", "%7.9 pay", delta_color="off")
        with col_b:
            st.metric("Action Pazar Payi", "%57.9", "Pazarin yarisindan fazla", delta_color="normal")
        with col_c:
            st.metric("Pay/Sayi Orani", "7.3x", "Hipertrofik pazar payi", delta_color="off")
        
        st.markdown("""
        > **Action segmenti**, oyun sayisi olarak Indie'nin 1/9'u kadar olmasina ragmen 
        > pazarin **yarisindan fazlasini** uretiyor. CS2 ($10.7B), PUBG ($4.9B), 
        > Apex ($1.5B), Cyberpunk ($761M) gibi mega oyunlar bu durumu yaratiyor.
        """)
    
    # ── PROFIL TABLOSU ──
    st.markdown("#### Genre Finansal Profilleri")
    
    tablo = genre_profil[['primary_genre', 'oyun_sayisi', 'ort_revenue', 
                          'median_revenue', 'toplam_revenue', 'ort_review_score', 
                          'ort_price', 'pazar_pay']].copy()
    
    tablo.columns = ['Genre', 'Oyun', 'Ort. Revenue', 'Median Revenue', 
                     'Toplam Revenue', 'Review Skoru', 'Ort. Fiyat', 'Pazar %']
    
    tablo['Ort. Revenue'] = tablo['Ort. Revenue'].apply(lambda x: f"${x/1000:,.0f}K")
    tablo['Median Revenue'] = tablo['Median Revenue'].apply(lambda x: f"${x:,.0f}")
    tablo['Toplam Revenue'] = tablo['Toplam Revenue'].apply(lambda x: f"${x/1e9:,.2f}B")
    tablo['Ort. Fiyat'] = tablo['Ort. Fiyat'].apply(lambda x: f"${x:,.2f}")
    tablo['Pazar %'] = tablo['Pazar %'].apply(lambda x: f"{x:.1f}%")
    tablo['Oyun'] = tablo['Oyun'].apply(lambda x: f"{x:,.0f}")
    tablo['Review Skoru'] = tablo['Review Skoru'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(tablo, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════
# TAB 2: GENRE x FIYAT
# ═══════════════════════════════════════════════════════
def _genre_fiyat_sekmesi():
    st.markdown("### Genre x Fiyat Segmentasyonu")
    st.caption("Iki boyutlu cesit - 70 olasi kombinasyon, 37 anlamli (>=100 oyun)")
    
    matrix_oyun = segment_genre_fiyat_oyun_yukle()
    matrix_rev = segment_genre_fiyat_revenue_yukle()
    
    # Fiyat sirasi
    price_sirasi = ['Free', 'Cheap', 'Low', 'Mid', 'Premium', 'Luxury']
    matrix_oyun = matrix_oyun.reindex(columns=price_sirasi, fill_value=0)
    matrix_rev = matrix_rev.reindex(columns=price_sirasi, fill_value=0)
    
    # Revenue'yu milyar dolara cevir
    matrix_rev_b = matrix_rev / 1e9
    
    # ── 2 HEATMAP YAN YANA ──
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Heatmap 1: Oyun Sayisi")
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix_oyun.values,
            x=matrix_oyun.columns,
            y=matrix_oyun.index,
            colorscale='YlGnBu',
            text=matrix_oyun.values,
            texttemplate='%{text:,}',
            textfont=dict(size=10),
            colorbar=dict(title="Oyun")
        ))
        
        fig.update_layout(
            title="Genre x Fiyat - Oyun Sayisi",
            xaxis_title="Fiyat Segmenti",
            yaxis_title="Primary Genre",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Heatmap 2: Toplam Revenue ($B)")
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix_rev_b.values,
            x=matrix_rev_b.columns,
            y=matrix_rev_b.index,
            colorscale='YlOrRd',
            text=matrix_rev_b.values,
            texttemplate='$%{text:.2f}B',
            textfont=dict(size=10),
            colorbar=dict(title="Revenue ($B)")
        ))
        
        fig.update_layout(
            title="Genre x Fiyat - Toplam Revenue",
            xaxis_title="Fiyat Segmenti",
            yaxis_title="Primary Genre",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 **Karsilastirma:** Sol heatmap (oyun yogunlugu) ve sag heatmap (revenue) arasindaki **kontrast**, 'cok oyun var ama az kazaniyor' vs 'az oyun var ama cok kazaniyor' hikayesini gosterir.")
    
    # ── STRATEJIK ONERILER ──
    st.markdown("### 🎯 Stratejik Konumlanma Onerileri")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.markdown("#### ✅ Hedeflenebilir Segmentler")
            st.markdown("""
            | Segment | Oyun | Strateji |
            |---------|------|----------|
            | **Simulation_Premium** | 170 | Dusuk rekabet, yuksek fiyat |
            | **Action_Luxury** | 215 | AAA hedefi, az ama buyuk rekabet |
            | **RPG_Mid** | 190 | Nis kalite |
            | **Strategy_Mid** | 285 | Kontrollu rekabet |
            | **Indie_Mid** | 6.027 | Orta hacim, orta rekabet |
            """)
    
    with col_b:
        with st.container(border=True):
            st.markdown("#### ❌ Kacinilmasi Gereken Segmentler")
            st.markdown("""
            | Segment | Oyun | Risk |
            |---------|------|------|
            | **Indie_Cheap** | 37.976 | Asiri rekabet (%33.5 pazar) |
            | **Indie_Low** | 25.240 | Yoğun rekabet (%22.2 pazar) |
            | **Indie_Free** | 11.449 | Goruunmek zor |
            | **Casual_Cheap** | 4.707 | Kapsama az |
            """)
    
    # ── INDIE HEGEMONYASI VURGUSU ──
    with st.container(border=True):
        st.markdown("### ⚠️ Indie Hegemonyasi")
        st.markdown("""
        > **Indie + (Free/Cheap/Low/Mid) toplami: %71.1 oyun** (80.692 oyun)
        > 
        > Steam pazarinin **3'te 2'si** Indie + dusuk fiyat segmentinde yogunlasiyor. 
        > Yeni geliştirici icin **gorunurluk** en buyuk zorluk.
        """)


# ═══════════════════════════════════════════════════════
# TAB 3: KMEANS CLUSTER
# ═══════════════════════════════════════════════════════
def _kmeans_sekmesi():
    st.markdown("### KMeans Cluster Segmentasyonu")
    st.caption("10 cluster - cok boyutlu otomatik kumeleme, finansal davranisa gore gruplama")
    
    cluster_profil = segment_kmeans_yukle()
    
    # Sutun isim duzenlemesi
    if 'kmeans_cluster' in cluster_profil.columns:
        cluster_profil = cluster_profil.rename(columns={'kmeans_cluster': 'cluster_id'})
    
    # Anlamli isim ekle
    cluster_profil['isim'] = cluster_profil['cluster_id'].apply(cluster_id_to_isim)
    
    # Renkler
    cluster_profil['renk'] = cluster_profil['cluster_id'].map(CLUSTER_RENKLERI)
    
    # Sirala
    cluster_profil = cluster_profil.sort_values('pazar_payi', ascending=False)
    
    # ── ÜST: PIE CHART + PARETO BILGISI ──
    col1, col2 = st.columns([2, 1])
   # ── ÜST: 2 GRAFIK + PARETO BILGISI ──
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Pazar Payi Dagilimi")
        
        # 2 alt grafik: donut + log bar
        graf_sec = st.radio(
            "Gorunum:",
            ["🍩 Donut (Pareto)", "📊 Bar Chart (Log Scale)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if graf_sec == "🍩 Donut (Pareto)":
            # Sadece ilk 4 cluster, kalanlari "Diger" olarak grupla
            top4 = cluster_profil.head(4).copy()
            diger_pay = cluster_profil.iloc[4:]['pazar_payi'].sum()
            
            labels = top4['isim'].tolist() + [f'Diger 6 Cluster']
            values = top4['pazar_payi'].tolist() + [diger_pay]
            colors = top4['renk'].tolist() + ['#bdc3c7']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                textinfo='label+percent',
                textfont=dict(size=12),
                hole=0.5,
                pull=[0.1, 0, 0, 0, 0]  # Cluster_6'yi disari pop yap
            )])
            
            fig.update_layout(
                title="Cluster_6 Hegemonyasi (Top 4 + Diger)",
                height=500,
                showlegend=True,
                annotations=[dict(
                    text='%93.3<br><span style="font-size:14px">Cluster_6</span>',
                    x=0.5, y=0.5,
                    font_size=24,
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # Bar chart (log scale)
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=cluster_profil['isim'],
                x=cluster_profil['pazar_payi'].clip(lower=0.001),  # Log icin sifir koruma
                orientation='h',
                marker=dict(color=cluster_profil['renk'].tolist()),
                text=cluster_profil['pazar_payi'].apply(
                    lambda x: f"%{x:.3f}" if x < 0.1 else f"%{x:.1f}"
                ),
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Tum 10 Cluster - Log Scale (Aksi takdirde Cluster_6 digerlerini ezer)",
                xaxis_title="Pazar Payi (%, log scale)",
                xaxis_type='log',
                height=500,
                yaxis=dict(autorange="reversed"),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Pareto Sertligi")
        
        with st.container(border=True):
            st.metric("Cluster_6 Pazar Payi", "%93.3", 
                     delta="4.580 oyun (%4)", delta_color="off")
            st.metric("Pareto Carpani", "19.9x",
                     help="Pazar % / Oyun %")
            st.metric("Klasik 80/20'den", "4 kat sert",
                     help="Klasik Pareto: %20 oyun = %80 pazar")
        
        st.markdown("---")
        st.markdown("**Algoritma:** KMeans (k=10)")
        st.markdown("**Optimal k Analizi:**")
        st.markdown("- Elbow Method: k=4")
        st.markdown("- Silhouette: k=3")
        st.markdown("- **Secilen: k=10** (is degeri)")
        
        st.caption("📌 k=10 secimi gerekçesi: Detay icin Metodoloji sekmesi")
    
    # ── CLUSTER KARAKTERIZASYON KARTLARI ──
    st.markdown("### Cluster Karakterizasyonu")
    st.caption("Her cluster, Steam pazarindaki gercek bir oyun profilini temsil ediyor")
    
    # 5'er ikili gruplar
    for i in range(0, len(cluster_profil), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(cluster_profil):
                row = cluster_profil.iloc[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"### {row['isim']}")
                        
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Oyun", f"{int(row['oyun_sayisi']):,}")
                        with m2:
                            st.metric("Pazar %", f"%{row['pazar_payi']:.1f}")
                        with m3:
                            st.metric("Ort. Revenue", f"${row['ort_revenue']/1000:.0f}K")
                        
                        m4, m5, m6 = st.columns(3)
                        with m4:
                            st.metric("Median", f"${row['median_revenue']:,.0f}")
                        with m5:
                            st.metric("Review", f"{row['ort_review_score']:.1f}")
                        with m6:
                            st.metric("Fiyat", f"${row['ort_price']:.2f}")
