"""
Steam Dashboard - Filtre Modulu
"""

import streamlit as st

# NSFW icerik anahtar kelimeleri
NSFW_ANAHTAR = [
    'Hentai', 'Lust', 'Milf', 'Ecchi', 'Sex', 'Porn',
    'Gyno', 'Adult', 'XXX', 'Naked', 'Erotic', 'Nudity',
    'Bimbo', 'Futanari', 'NSFW'
]


def nsfw_filtre_uygula(df, isim_kolonu='Name'):
    """NSFW icerikli oyunlari filtrele."""
    pattern = '|'.join(NSFW_ANAHTAR)
    nsfw_mask = df[isim_kolonu].str.contains(pattern, case=False, na=False)
    return df[~nsfw_mask].copy()


def sidebar_olustur(df):
    """Tum sayfalarda kullanilan ortak sidebar."""
    with st.sidebar:
        st.title("Steam Pazar Analizi")
        st.caption("Bitirme Projesi - DEU Endustri Muh.")
        
        st.divider()
        
        # NSFW Filtre
        nsfw_acik = st.toggle(
            "Aile Dostu Mod",
            value=True,
            help="NSFW icerikli oyunlar filtrelenir."
        )
        
        st.divider()
        
        # Mini Istatistik
        st.markdown("### Hizli Bakis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Toplam Oyun", f"{len(df):,}")
        with col2:
            st.metric("2025 Pazar", "$16.25B")
        
        st.metric("Pareto Sertligi", "%93.3", help="Cluster_6 pazar payi")
        st.metric("Model Dogrulugu", "R² = 0.84", help="Hybrid Stacking")
        
        st.divider()
        
        # Hakkinda
        st.markdown("### Hakkinda")
        st.markdown("""
        **Veri:** 113.456 oyun  
        **Algoritma:** Hybrid Stacking  
        **Tahmin:** ARIMA, HoltWinters, Prophet  
        **Akademik:** 6 ampirik bulgu
        """)
        
    return {"nsfw_acik": nsfw_acik}
