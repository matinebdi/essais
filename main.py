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

# --- Main Page ---
def main_page():
    # Header with Address and Delivery Type
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.text_input("📍 Adresse de livraison", value=st.session_state.delivery_address, 
                      key="delivery_address_input", placeholder="Entrez votre adresse")
    with col2:
        st.selectbox("Type de commande", ["Livraison", "À emporter"], key="delivery_type")
    with col3:
        if st.button("🚪 Déconnexion"):
            st.session_state.clear()
            st.session_state.update(SESSION_DEFAULTS)
            rerun()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Catégorie", ["Tous", "Burgers", "Pizza", "Sushi", "Healthy", "Desserts"], 
                    key="selected_category")
    with col2:
        st.selectbox("Trier par", ["Recommandés", "Temps de livraison", "Notes", "Frais de livraison"], 
                    key="sort_by")
    with col3:
        st.selectbox("Prix", ["Tous les prix", "€", "€€", "€€€", "€€€€"], key="price_range")

    # Search
    search_query = st.text_input("🔍 Rechercher un restaurant, un plat...", key="search_query")
    
    # Restaurants Display
    df_restaurants = load_restaurants()
    filtered_restaurants = filter_restaurants(df_restaurants, search_query)
    
    st.markdown("### 🍽️ Restaurants disponibles")
    
    for _, restaurant in filtered_restaurants.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(restaurant.get('image_url', 'https://via.placeholder.com/300x200'), 
                        use_container_width=True)
            
            with col2:
                st.markdown(f"### {restaurant['name']}")
                st.markdown(f"⭐ {restaurant['rating']:.1f} • {restaurant['delivery_time']} min • "
                          f"{restaurant['delivery_fee']}€ livraison")
                st.markdown(f"Minimum: {restaurant['min_order']}€ • {restaurant.get('categories_list', '')}")
                
                if st.button("Voir le menu", key=f"menu_{restaurant['id']}", type="primary"):
                    st.session_state.current_restaurant = restaurant['id']
                    st.session_state.estimated_time = calculate_delivery_time()
                    rerun()

def filter_restaurants(df, search_query):
    if search_query:
        df = df[df['name'].str.contains(search_query, case=False, na=False)]
    
    if st.session_state.selected_category != "Tous":
        df = df[df['categories_list'].str.contains(st.session_state.selected_category, case=False, na=False)]
    
    if st.session_state.price_range != "Tous les prix":
        df = df[df['price'].str.len() == len(st.session_state.price_range)]
    
    if st.session_state.sort_by == "Temps de livraison":
        df = df.sort_values('delivery_time')
    elif st.session_state.sort_by == "Notes":
        df = df.sort_values('rating', ascending=False)
    elif st.session_state.sort_by == "Frais de livraison":
        df = df.sort_values('delivery_fee')
    
    return df

# --- Menu Page ---
def menu_page():
    df_restaurants = load_restaurants()
    restaurant = df_restaurants[df_restaurants['id'] == st.session_state.current_restaurant].iloc[0]
    
    # Header
    st.button("← Retour", key="back_button", 
             on_click=lambda: setattr(st.session_state, 'current_restaurant', -1))
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.image(restaurant.get('image_url', 'https://via.placeholder.com/300x200'), 
                use_container_width=True)
    
    with col2:
        st.title(restaurant['name'])
        st.markdown(f"⭐ {restaurant['rating']:.1f} • {restaurant['delivery_time']} min • "
                   f"{restaurant['delivery_fee']}€ livraison")
        st.markdown(f"Minimum: {restaurant['min_order']}€ • {restaurant.get('categories_list', '')}")
    
    # Menu Categories
    st.markdown("## 🍽️ Menu")
    
    categories = {
        "Populaires": [
            {"name": "Bestseller #1", "price": 15.90, "description": "Notre plat le plus vendu", 
             "image": "https://via.placeholder.com/150"},
            {"name": "Bestseller #2", "price": 13.90, "description": "Un favori des clients", 
             "image": "https://via.placeholder.com/150"}
        ],
        "Entrées": [
            {"name": "Entrée Signature", "price": 8.50, "description": "Entrée fraîche du jour", 
             "image": "https://via.placeholder.com/150"},
            {"name": "Salade Maison", "price": 7.90, "description": "Légumes de saison", 
             "image": "https://via.placeholder.com/150"}
        ],
        "Plats": [
            {"name": "Plat Principal", "price": 18.90, "description": "Spécialité du chef", 
             "image": "https://via.placeholder.com/150"},
            {"name": "Plat Végétarien", "price": 16.90, "description": "100% végétal", 
             "image": "https://via.placeholder.com/150"}
        ],
        "Desserts": [
            {"name": "Dessert du Jour", "price": 6.50, "description": "Fait maison", 
             "image": "https://via.placeholder.com/150"},
            {"name": "Café Gourmand", "price": 8.90, "description": "Assortiment de mignardises", 
             "image": "https://via.placeholder.com/150"}
        ]
    }
    
    for category, items in categories.items():
        st.markdown(f"### {category}")
        for item in items:
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.image(item['image'], use_container_width=True)
                
                with col2:
                    st.markdown(f"**{item['name']}**")
                    st.markdown(item['description'])
                    st.markdown(f"**{item['price']:.2f} €**")
                
                with col3:
                    if st.button("Ajouter", key=f"add_{category}_{item['name']}", type="primary"):
                        st.session_state.cart.append(item)
                        st.toast(f"{item['name']} ajouté au panier !")
                        time.sleep(0.3)
                        rerun()
            
            st.markdown("---")

# --- Shopping Cart ---
def shopping_cart():
    with st.sidebar:
        st.markdown("### 🛒 Votre panier")
        
        if not st.session_state.cart:
            st.info("Votre panier est vide")
            return
        
        total = sum(item['price'] for item in st.session_state.cart)
        delivery_fee = 2.99 if total < 20 else 0
        
        for index, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"{item['name']}")
            col2.markdown(f"{item['price']:.2f} €")
            if col3.button("❌", key=f"remove_{index}"):
                st.session_state.cart.pop(index)
                rerun()
        
        st.markdown("---")
        st.markdown(f"Sous-total: **{total:.2f} €**")
        st.markdown(f"Frais de livraison: **{delivery_fee:.2f} €**")
        st.markdown(f"**Total: {(total + delivery_fee):.2f} €**")
        
        if st.session_state.delivery_address:
            if st.button("Commander", type="primary"):
                order = {
                    'id': generate_order_id(),
                    'items': st.session_state.cart.copy(),
                    'total': total + delivery_fee,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'status': 'En préparation',
                    'address': st.session_state.delivery_address,
                    'estimated_time': st.session_state.estimated_time
                }
                st.session_state.orders.append(order)
                st.session_state.cart = []
                st.success(f"Commande {order['id']} confirmée !")
                time.sleep(1)
                rerun()
        else:
            st.warning("Veuillez entrer une adresse de livraison")

# --- Main Routing ---
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.current_restaurant == -1:
        main_page()
    else:
        menu_page()
    shopping_cart()

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