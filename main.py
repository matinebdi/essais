import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="UberEats-style Admin",
    layout="wide",
    page_icon="🚀"
)

# --- Session State Initialization ---
SESSION_DEFAULTS = {
    'logged_in': False,
    'username': "",
    'cart': [],
    'current_restaurant': -1,
    'delivery_address': "",
    'estimated_time': "",
    'selected_category': "Tous",
    'sort_by': "Recommandés",
    'price_range': "Tous les prix",
    'delivery_type': "Livraison",
    'orders': []  # Pour suivre l'historique des commandes
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Utility Functions ---
def rerun():
    st.rerun()

@st.cache_data
def load_restaurants():
    try:
        df = pd.read_csv("DATA/df_restaurants_local (1).csv")
        df['delivery_time'] = np.random.randint(15, 45, size=len(df))  # Temps de livraison estimé
        df['delivery_fee'] = np.random.randint(1, 5, size=len(df))  # Frais de livraison
        df['min_order'] = np.random.randint(10, 25, size=len(df))  # Commande minimum
        return df
    except FileNotFoundError:
        st.error("Fichier de données introuvable !")
        return pd.DataFrame()

def calculate_delivery_time():
    return f"{np.random.randint(20, 50)} min"

def generate_order_id():
    return f"ORDER-{datetime.now().strftime('%Y%m%d')}-{np.random.randint(1000, 9999)}"

# --- Custom CSS ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #000000;
        color: white;
    }
    .stButton > button:hover {
        background-color: #333333;
        color: white;
    }
    .css-1d391kg {
        padding: 1rem;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .stAlert {
        border-radius: 10px;
    }
    .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Login Page ---
def login_page():
    st.title("🚀 UberEats Admin")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn.pixabay.com/photo/2017/08/31/10/44/restaurant-2700325_1280.png", use_container_width=True)
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Se connecter", type="primary"):
                if username == "admin" and password == st.secrets.get("ADMIN_PASSWORD", "adminpassword"):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    rerun()
                else:
                    st.error("Identifiants incorrects !")

# --- Main Routing ---
if not st.session_state.logged_in:
    login_page()
else:
    st.success("Bienvenue dans l'application UberEats-style Admin !")
