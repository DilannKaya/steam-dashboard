"""
Steam Dashboard - Stil Modulu
"""

# Renk paleti
RENKLER = {
    "ana_mavi": "#2E86AB",
    "mor": "#9b59b6",
    "yesil": "#27ae60",
    "sari": "#f39c12",
    "kirmizi": "#e74c3c",
    "altin": "#FFD700",
    "teal": "#1abc9c",
    "gri": "#95a5a6",
    "lacivert": "#34495e",
}

# Cluster renkleri (Pareto'ya gore)
CLUSTER_RENKLERI = {
    6: "#FFD700",
    0: "#3498db",
    5: "#27ae60",
    9: "#9b59b6",
    8: "#16a085",
    7: "#e74c3c",
    2: "#1abc9c",
    1: "#5dade2",
    3: "#7f8c8d",
    4: "#bdc3c7",
}


CUSTOM_CSS = """
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
"""
