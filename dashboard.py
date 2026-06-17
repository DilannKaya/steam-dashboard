"""
Steam Pazar Analizi Dashboard
DEU Endustri Muhendisligi Bitirme Projesi - Dilan Kaya
"""

import streamlit as st
from utils.data_loader import df_dashboard_yukle
from utils.filters import sidebar_olustur, nsfw_filtre_uygula
from utils.styles import CUSTOM_CSS

# ════════════════════════════════════════════════════════════════
# SAYFA KONFIGURASYONU
# ════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Steam Pazar Analizi",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# VERI YUKLEME
# ════════════════════════════════════════════════════════════════

df_ham = df_dashboard_yukle()

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

filtreler = sidebar_olustur(df_ham)

# NSFW filtre uygula
if filtreler["nsfw_acik"]:
    df = nsfw_filtre_uygula(df_ham)
else:
    df = df_ham

# ════════════════════════════════════════════════════════════════
# ANA BASLIK
# ════════════════════════════════════════════════════════════════

st.markdown("# Steam Pazar Analizi Dashboard")
st.markdown("##### *Veri-odakli karar destek sistemi - 113.456 oyun, 5 algoritma, 2027 projeksiyonu*")

st.divider()

# Sayfa secimi (tab'lar)
sayfa = st.tabs([
    "Pazar Panoramasi",
    "Segmentasyon",
    "Karar Destek",
    "Metodoloji"
])

# ════════════════════════════════════════════════════════════════
# SAYFALAR (Su an placeholder)
# ════════════════════════════════════════════════════════════════

with sayfa[0]:
    from pages import page_1_panorama
    page_1_panorama.goster(df)

with sayfa[1]:
    from pages import page_2_segmentasyon
    page_2_segmentasyon.goster(df)

with sayfa[2]:
    from pages import page_3_karar
    page_3_karar.goster(df)

with sayfa[3]:
    from pages import page_4_metodoloji
    page_4_metodoloji.goster(df)
    
# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("**Veri:** Steam Marketplace (DataHumble)")
with col2:
    st.caption("**Akademik:** Wolpert 1992 - Lewis 1982 - Box-Jenkins 1970")
with col3:
    st.caption("**Gelistirici:** Dilan Kaya - DEU EM - Mayis 2026")
