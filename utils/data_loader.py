"""
Steam Dashboard - Veri Yukleme Modulu
"""

import pandas as pd
import streamlit as st
from pathlib import Path

# Veri klasoru
DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data(show_spinner="Steam veri seti yukleniyor (113.456 oyun)...")
def df_dashboard_yukle():
    """Ana oyun veri seti."""
    df = pd.read_csv(DATA_DIR / "df_dashboard.csv")
    return df


@st.cache_data
def time_series_en_iyi_yukle():
    """Best-of-Best segment sonuclari."""
    return pd.read_csv(DATA_DIR / "time_series_en_iyi_segmentler.csv")


@st.cache_data
def time_series_genre_yukle():
    """Genre x Yil revenue tablosu."""
    df = pd.read_csv(DATA_DIR / "time_series_genre_revenue.csv")
    df = df.set_index("Yil")
    return df


@st.cache_data
def time_series_cluster_yukle():
    """Cluster x Yil revenue tablosu."""
    df = pd.read_csv(DATA_DIR / "time_series_cluster_revenue.csv")
    df = df.set_index("Yil")
    return df


@st.cache_data
def segment_kmeans_yukle():
    """KMeans cluster profilleri."""
    return pd.read_csv(DATA_DIR / "segment_kmeans_profilleri.csv")


@st.cache_data
def segment_genre_yukle():
    """Genre profilleri."""
    return pd.read_csv(DATA_DIR / "segment_genre_profilleri.csv")


@st.cache_data
def segment_genre_fiyat_oyun_yukle():
    """Genre x Fiyat matrisi - oyun sayisi."""
    df = pd.read_csv(DATA_DIR / "segment_genre_fiyat_oyun_sayisi.csv")
    df = df.set_index("primary_genre")
    return df


@st.cache_data
def segment_genre_fiyat_revenue_yukle():
    """Genre x Fiyat matrisi - toplam revenue."""
    df = pd.read_csv(DATA_DIR / "segment_genre_fiyat_revenue.csv")
    df = df.set_index("primary_genre")
    return df


@st.cache_data
def oneri_modelleri_yukle():
    """3 oneri modeli karsilastirmasi."""
    return pd.read_csv(DATA_DIR / "oneri_modelleri_final_karsilastirma.csv")


@st.cache_data
def knn_karsilastirma_yukle():
    """8 K-NN model karsilastirmasi."""
    return pd.read_csv(DATA_DIR / "knn_model_karsilastirma.csv")


# ════════════════════════════════════════════════════════════════
# CLUSTER ISIMLENDIRME
# ════════════════════════════════════════════════════════════════

CLUSTER_ISIMLERI = {
    6: "AAA Hit Lokomotif",
    0: "Mid-tier Basarili",
    5: "Indie Standart",
    9: "Premium Nis",
    8: "Kaliteli Kucuk",
    7: "Dusuk Kalite",
    2: "Mukemmel Nis",
    1: "Nis Yuksek Kalite",
    3: "Basarisiz",
    4: "Kucuk F2P",
}


def cluster_id_to_isim(cluster_id):
    """Cluster ID'sini anlamli isme cevir."""
    return CLUSTER_ISIMLERI.get(cluster_id, f"Cluster_{cluster_id}")
# ════════════════════════════════════════════════════════════════
# K-NN MODELI VE FEATURE MATRISI (SAYFA 3 ICIN)
# ════════════════════════════════════════════════════════════════

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor

# Meta-learner katsayilari (Bolum 6.8'den)
META_W_KNN = 1.1648
META_W_CB = -0.1511
META_B = -0.0938

# Notebook'taki ozellik listesi
SAYISAL_OZELLIKLER = [
    'log_wishlists', 'log_copies', 'log_followers', 'log_review_count',
    'Review Score', 'price_usd_clipped', 'log_playtime'
]


@st.cache_resource(show_spinner="K-NN modeli egitiliyor (ilk acilis ~30 sn)...")
def knn_model_egit():
    """
    Hybrid Stacking icin K-NN base model.
    
    Notebook Bolum 6.5'te en iyi cikan: ZScore + Manhattan + K=5
    
    Returns:
        knn_model, scaler, df_dashboard_indexli
    """
    df = df_dashboard_yukle()
    
    # Eksik degerleri 0 ile doldur
    X_numeric = df[SAYISAL_OZELLIKLER].fillna(0).copy()
    
    # Z-Score normalizasyon (Bolum 6'da en iyi cikan)
    scaler = StandardScaler()
    X_zscore = scaler.fit_transform(X_numeric)
    
    # K-NN modeli (Manhattan, K=5)
    knn = KNeighborsRegressor(
        n_neighbors=5,
        metric='manhattan',
        n_jobs=-1
    )
    knn.fit(X_zscore, df['log_revenue'].fillna(0).values)
    
    return knn, scaler, X_zscore


@st.cache_data(show_spinner="Content-Based matrisi hazirlaniyor...")
def content_based_matris_hazirla():
    """
    Content-Based filtering icin binary feature matrisi.
    
    Genre + Tag + Feature listelerinden one-hot encoded matris uretir.
    
    Returns:
        X_content (numpy array), feature_isimleri (list)
    """
    df = df_dashboard_yukle()
    
    # genre_list, tag_list, feature_list string olarak gelir, parse et
    import ast
    
    def parse_liste(s):
        if pd.isna(s) or s == '' or s == '[]':
            return []
        try:
            return ast.literal_eval(s) if isinstance(s, str) else s
        except (ValueError, SyntaxError):
            return []
    
    df['_genre_list'] = df['genre_list'].apply(parse_liste)
    df['_tag_list'] = df['tag_list'].apply(parse_liste)
    df['_feature_list'] = df['feature_list'].apply(parse_liste)
    
    # 12 anlamli genre (notebook'tan)
    anlamli_genres = [
        'Indie', 'Casual', 'Action', 'Adventure', 'Simulation', 'Strategy',
        'RPG', 'Free To Play', 'Early Access', 'Sports', 'Racing',
        'Massively Multiplayer'
    ]
    
    # En yaygin 30 tag ve 30 feature
    tum_tagler = [t for tags in df['_tag_list'] for t in tags]
    tum_features = [f for feats in df['_feature_list'] for f in feats]
    
    top_30_tag = [t for t, _ in pd.Series(tum_tagler).value_counts().head(30).items()]
    top_30_feature = [f for f, _ in pd.Series(tum_features).value_counts().head(30).items()]
    
    # Binary feature matrisi olustur
    matrisler = []
    feature_isimleri = []
    
    for genre in anlamli_genres:
        col = df['_genre_list'].apply(lambda lst: 1 if genre in lst else 0).values
        matrisler.append(col)
        feature_isimleri.append(f'genre_{genre}')
    
    for tag in top_30_tag:
        col = df['_tag_list'].apply(lambda lst: 1 if tag in lst else 0).values
        matrisler.append(col)
        feature_isimleri.append(f'tag_{tag}')
    
    for feat in top_30_feature:
        col = df['_feature_list'].apply(lambda lst: 1 if feat in lst else 0).values
        matrisler.append(col)
        feature_isimleri.append(f'feature_{feat}')
    
    X_content = np.column_stack(matrisler).astype(np.float32)
    
    return X_content, feature_isimleri, anlamli_genres, top_30_tag, top_30_feature


def lewis_kategorisi(mape):
    """Lewis (1982) MAPE esik tablosu."""
    if mape < 10:
        return 'Yuksek', '🟢', 'Guvenle yatirim karari'
    elif mape < 20:
        return 'Orta', '🟡', 'Yatirim + risk uyarisi'
    elif mape < 50:
        return 'Dusuk', '🟠', 'Alternatif degerlendirme onerilir'
    else:
        return 'Cok dusuk', '🔴', 'Karar destek icin kullanilamaz'


def cagr_sozlukleri_hazirla():
    """
    Bolum 7'den CAGR sozlukleri olustur (Cluster + Genre).
    
    Returns:
        cluster_cagr_dict, genre_cagr_dict, FALLBACK_CAGR
    """
    df = time_series_en_iyi_yukle()
    
    cluster_cagr = {}
    genre_cagr = {}
    
    for _, row in df.iterrows():
        if row['Gercek_2025'] > 0:
            buyume = row['Forecast_2027'] / row['Gercek_2025']
            cagr = buyume ** 0.5 - 1
        else:
            cagr = 0.0
        
        bilgi = {
            'cagr': float(cagr),
            'mape': float(row['MAPE']),
            'algo': row['Algoritma'],
            'forecast_2027': float(row['Forecast_2027']),
            'gercek_2025': float(row['Gercek_2025']),
        }
        
        if row['Tip'] == 'Cluster':
            c_id = int(row['Segment'].split('_')[1])
            cluster_cagr[c_id] = bilgi
        elif row['Tip'] == 'Genre':
            genre_cagr[row['Segment']] = bilgi
    
    return cluster_cagr, genre_cagr, 0.027  # %2.7 fallback
