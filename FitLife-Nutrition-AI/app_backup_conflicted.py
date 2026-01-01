"""
<<<<<<< HEAD
FitLife Nutrition AI - Application Utilisateur Finale
Version Épurée Sans Détails Techniques
=======
FitLife Nutrition AI - Application Utilisateur Finale (Version Corrigée)
Assistant Nutritionnel IA 
Auteurs: Asma Bélkahla & Monia Selleoui
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Import RAG pipeline
import sys
try:
    from modules.rag.rag_pipeline import NutritionRAGPipeline
except ImportError:
    NutritionRAGPipeline = None
import os

# Ajouter le dossier modules au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import des modules locaux
from modules.nutrition_calculator import NutritionalCalculator, UserProfile
from modules.food_recommender import FoodRecommendationEngine, NutritionalTarget
from modules.meal_plan_generator import MealPlanGenerator, MealPlanPreferences
from modules.nutrition_assistant import NutritionAssistant

# Configuration de la page
st.set_page_config(
    page_title="FitLife - Assistant Nutritionnel IA",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transition: transform 0.3s;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.3);
    }
<<<<<<< HEAD
=======
    .metric-card h2 {
        font-size: 3rem;
        margin: 0.5rem 0;
    }
    .metric-card h3 {
        margin: 0.5rem 0;
        font-size: 1.3rem;
    }
    .metric-card p {
        font-size: 0.95rem;
        opacity: 0.9;
    }
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    .food-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #f0f2f6;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .food-card:hover {
        border-color: #FF6B35;
        box-shadow: 0 4px 8px rgba(255,107,53,0.2);
    }
    .recommendation-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%);
        color: white;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255,107,53,0.3);
    }
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid #FF6B35;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
<<<<<<< HEAD
=======
    .chat-user {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 10%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-assistant {
        background: linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 10%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
</style>
""", unsafe_allow_html=True)

# Initialisation de la session
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'nutritional_needs' not in st.session_state:
    st.session_state.nutritional_needs = None
if 'weight_history' not in st.session_state:
    st.session_state.weight_history = []
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'favorite_foods' not in st.session_state:
    st.session_state.favorite_foods = []
if 'recommender' not in st.session_state:
    st.session_state.recommender = None
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'meal_generator' not in st.session_state:
    st.session_state.meal_generator = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Accueil"

# Chargement des données
@st.cache_data
def load_food_data():
    """Charge le dataset alimentaire"""
    try:
        dfs = []
        data_path = "data/nutrition"
        
        if os.path.exists(data_path):
            for i in range(1, 6):
                file_path = os.path.join(data_path, f"FOOD-DATA-GROUP{i}.csv")
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    dfs.append(df)
        
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            combined_df = combined_df.dropna(subset=['food'])
            combined_df = combined_df.fillna(0)
            return combined_df
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement des données: {str(e)}")
    
    # Dataset de fallback
    return pd.DataFrame({
        'food': [
            'Poulet grillé', 'Riz complet', 'Brocoli', 'Saumon', 'Œufs',
            'Quinoa', 'Avocat', 'Amandes', 'Yaourt grec', 'Banane',
            'Épinards', 'Patate douce', 'Tofu', 'Lentilles', 'Pomme',
            'Thon', 'Flocons avoine', 'Fromage blanc', 'Pain complet', 'Tomate',
            'Pâtes complètes', 'Blanc de dinde', 'Concombre', 'Haricots verts', 'Kiwi'
        ],
        'Caloric Value': [165, 370, 34, 208, 155, 368, 160, 579, 59, 89, 23, 86, 76, 116, 52, 144, 389, 73, 247, 18, 348, 135, 15, 31, 61],
        'Protein': [31, 7.9, 2.8, 20, 13, 14, 2, 21, 10, 1.1, 2.9, 1.6, 8, 9, 0.3, 30, 13.2, 12.5, 13, 0.9, 12, 30, 0.7, 1.8, 1.1],
        'Carbohydrates': [0, 77, 6.6, 0, 1.1, 64, 9, 22, 3.6, 23, 3.6, 20, 1.9, 20, 14, 0, 66, 4, 49, 3.9, 75, 0, 3.6, 7, 15],
        'Fat': [3.6, 2.9, 0.4, 13, 11, 6, 15, 49, 0.4, 0.3, 0.4, 0.1, 5, 0.4, 0.2, 5, 7, 0.2, 3.3, 0.2, 1.5, 1, 0.1, 0.2, 0.5],
        'Dietary Fiber': [0, 3.5, 2.6, 0, 0, 7, 7, 12, 0, 2.6, 2.2, 3, 0.3, 7.9, 2.4, 0, 10.6, 0, 7, 1.2, 3.2, 0, 0.5, 2.7, 3],
        'Saturated Fats': [1, 0.6, 0.1, 3, 3.5, 0.7, 2.1, 3.8, 0.1, 0.1, 0.1, 0, 0.7, 0.1, 0, 1.3, 1.2, 0.1, 0.7, 0, 0.3, 0.3, 0, 0, 0.1],
        'Sugars': [0, 0.8, 1.7, 0, 0.6, 0, 0.7, 4.4, 3.6, 12, 0.4, 4.2, 0.6, 1.8, 10, 0, 0.8, 4, 5, 2.6, 2.7, 0, 1.7, 3.3, 9],
        'Sodium': [74, 7, 33, 59, 124, 7, 7, 1, 36, 1, 79, 55, 7, 2, 1, 354, 2, 50, 550, 5, 6, 60, 2, 1, 3],
        'Water': [65, 12, 89, 69, 76, 13, 73, 5, 81, 75, 92, 77, 85, 70, 86, 70, 8, 82, 35, 95, 11, 68, 96, 90, 83],
        'Vitamin A': [21, 0, 623, 40, 520, 0, 146, 1, 243, 64, 9376, 961, 85, 8, 54, 50, 0, 28, 0, 833, 0, 0, 105, 380, 87],
        'Vitamin B12': [0.3, 0, 0, 3.2, 0.9, 0, 0, 0, 1.3, 0, 0, 0, 0, 0.1, 0, 4.3, 0, 0.2, 0, 0, 0, 0.4, 0, 0, 0],
        'Vitamin C': [0, 0, 89, 0, 0, 0, 10, 0, 0, 8.7, 28, 2.4, 0.1, 1.5, 4.6, 0, 0, 0, 0, 14, 0, 0, 2.8, 12, 93],
        'Vitamin D': [0, 0, 0, 11, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Calcium': [15, 23, 47, 12, 50, 47, 12, 264, 110, 5, 99, 30, 350, 19, 6, 10, 54, 103, 175, 10, 21, 11, 16, 37, 34],
        'Iron': [1.0, 1.5, 0.7, 0.8, 1.2, 4.6, 0.6, 3.7, 0.1, 0.3, 2.7, 0.6, 5.4, 3.3, 0.1, 1.3, 4.7, 0.1, 3.6, 0.3, 1.5, 0.7, 0.3, 1.0, 0.3],
        'Magnesium': [29, 143, 21, 29, 10, 197, 29, 268, 11, 27, 79, 25, 53, 36, 5, 29, 177, 11, 90, 11, 53, 30, 13, 25, 17],
        'Potassium': [256, 268, 316, 363, 126, 563, 485, 705, 141, 358, 558, 337, 121, 369, 107, 252, 429, 220, 240, 237, 169, 302, 147, 209, 312],
        'Nutrition Density': [8.5, 7.2, 9.1, 8.8, 7.9, 8.3, 7.5, 7.8, 8.0, 6.5, 9.5, 7.8, 7.6, 8.4, 7.1, 8.6, 7.9, 8.2, 6.8, 8.9, 7.0, 8.7, 9.2, 8.8, 8.1]
    })

# Charger les données
food_data = load_food_data()

# Initialiser les modules
@st.cache_resource
def initialize_ai_modules(_food_data):
    """Initialise tous les modules"""
    try:
        recommender = FoodRecommendationEngine(_food_data)
        meal_generator = MealPlanGenerator(_food_data, recommender)
        assistant = NutritionAssistant(_food_data, recommender)
        return recommender, meal_generator, assistant
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation: {str(e)}")
        return None, None, None

<<<<<<< HEAD
@st.cache_resource(show_spinner="Chargement du pipeline IA...")
def load_rag_pipeline():
    """Charge le pipeline RAG"""
    try:
        if NutritionRAGPipeline:
            return NutritionRAGPipeline()
        return None
    except Exception as e:
        print(f"RAG Error: {e}")
        return None


=======
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
# Initialiser
if st.session_state.recommender is None:
    recommender, meal_generator, assistant = initialize_ai_modules(food_data)
    st.session_state.recommender = recommender
    st.session_state.meal_generator = meal_generator
    st.session_state.assistant = assistant
else:
    recommender = st.session_state.recommender
    meal_generator = st.session_state.meal_generator
    assistant = st.session_state.assistant

# Fonction pour changer de page
def change_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# Sidebar - Navigation
st.sidebar.markdown("# 🥗 FitLife AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "👤 Profil", "📊 Dashboard", 
     "🎯 Recommandations", "🍽️ Plan Alimentaire",
<<<<<<< HEAD
     "💬 Assistant", "🧠 Assistant IA (RAG)", "📈 Suivi", "📚 Base Aliments"]
=======
     "💬 Assistant", "📈 Suivi", "📚 Base Aliments"],
    index=["🏠 Accueil", "👤 Profil", "📊 Dashboard", 
           "🎯 Recommandations", "🍽️ Plan Alimentaire",
           "💬 Assistant", "📈 Suivi", "📚 Base Aliments"].index(st.session_state.current_page)
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
)

st.session_state.current_page = page

st.sidebar.markdown("---")

if st.session_state.profile:
    st.sidebar.success("✅ Profil configuré")
    st.sidebar.info(f"**Objectif:** {st.session_state.profile['goal']}")
    if st.session_state.nutritional_needs:
        st.sidebar.metric("Calories/jour", 
                         f"{st.session_state.nutritional_needs['target_calories']:.0f}")
else:
    st.sidebar.warning("⚠️ Configurez votre profil")

# ==================== PAGES ====================

# PAGE: ACCUEIL
if page == "🏠 Accueil":
    st.markdown('<h1 class="main-header">🥗 Bienvenue sur FitLife</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Votre assistant nutritionnel intelligent pour atteindre vos objectifs</p>', unsafe_allow_html=True)
    
<<<<<<< HEAD
    # Fonctionnalités principales
=======
    # Fonctionnalités principales AVEC BOUTONS FONCTIONNELS
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>📊</h2>
            <h3>Analyse Personnalisée</h3>
            <p>Calculez vos besoins nutritionnels adaptés à votre profil</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 Voir Dashboard", key="card_dash", use_container_width=True):
            change_page("📊 Dashboard")
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>🎯</h2>
            <h3>Recommandations</h3>
            <p>Découvrez les aliments parfaits pour votre objectif</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎯 Découvrir", key="card_reco", use_container_width=True):
            change_page("🎯 Recommandations")
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>📈</h2>
            <h3>Suivi Progrès</h3>
            <p>Suivez votre évolution et restez motivé(e)</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📈 Suivre", key="card_suivi", use_container_width=True):
            change_page("📈 Suivi")
    
    st.markdown("---")
    
    # Guide d'utilisation
    st.markdown("### 📖 Comment utiliser FitLife")
<<<<<<< HEAD
    
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Premiers Pas</h4>
        <ol style="margin: 0.5rem 0;">
            <li><strong>Configurez votre profil</strong> - Rendez-vous dans l'onglet <strong>👤 Profil</strong> pour renseigner vos informations personnelles (poids, taille, âge, objectif...)</li>
            <li><strong>Consultez votre dashboard</strong> - Visualisez vos besoins nutritionnels quotidiens calculés automatiquement</li>
            <li><strong>Découvrez les recommandations</strong> - Obtenez une liste d'aliments adaptés à vos besoins</li>
            <li><strong>Générez votre plan alimentaire</strong> - Créez un plan de repas personnalisé pour la semaine</li>
            <li><strong>Posez vos questions</strong> - Utilisez l'assistant pour obtenir des conseils nutritionnels</li>
            <li><strong>Suivez votre progression</strong> - Enregistrez votre poids régulièrement et visualisez votre évolution</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Objectifs disponibles
    st.markdown("### 🎯 Objectifs Disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🔥 Perte de poids
        - Déficit calorique calculé
        - Aliments faibles en calories
        - Riches en protéines et fibres
        - Maintien de la masse musculaire
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 Maintien
        - Équilibre nutritionnel
        - Maintien du poids actuel
        - Alimentation variée
        - Bien-être général
        """)
    
    with col3:
        st.markdown("""
        #### 💪 Prise de masse
        - Surplus calorique optimal
        - Aliments riches en protéines
        - Développement musculaire
        - Nutrition sportive
        """)
    
    st.markdown("---")
    
    # Avantages
    st.markdown("### ✨ Pourquoi choisir FitLife ?")
=======
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Premiers Pas</h4>
        <ol style="margin: 0.5rem 0;">
            <li><strong>Configurez votre profil</strong> - Renseignez vos informations (poids, taille, âge, objectif)</li>
            <li><strong>Consultez votre dashboard</strong> - Visualisez vos besoins nutritionnels</li>
            <li><strong>Découvrez les recommandations</strong> - Aliments adaptés à vos besoins</li>
            <li><strong>Générez votre plan alimentaire</strong> - Créez un menu personnalisé</li>
            <li><strong>Posez vos questions</strong> - L'assistant vous répond</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Objectifs disponibles
    st.markdown("### 🎯 Objectifs Disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
<<<<<<< HEAD
        ✅ **Personnalisation complète**  
        Tous les conseils sont adaptés à votre profil unique
        
        ✅ **Base de données complète**  
        Des milliers d'aliments avec informations nutritionnelles détaillées
        
        ✅ **Plans alimentaires intelligents**  
        Génération automatique de menus équilibrés et variés
=======
        #### 🔥 Perte de poids
        - Déficit calorique calculé
        - Aliments faibles en calories
        - Riches en protéines et fibres
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        """)
    
    with col2:
        st.markdown("""
<<<<<<< HEAD
        ✅ **Assistant nutritionnel**  
        Réponses instantanées à vos questions
        
        ✅ **Suivi de progression**  
        Graphiques et statistiques pour visualiser vos résultats
        
        ✅ **Facile à utiliser**  
        Interface intuitive et conviviale
        """)
    
    # Call to action
    if not st.session_state.profile:
        st.markdown("---")
        st.markdown("### 🚀 Prêt(e) à commencer ?")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📝 Créer mon profil maintenant", use_container_width=True, type="primary"):
                st.rerun()
    else:
        st.markdown("---")
=======
        #### 🎯 Maintien
        - Équilibre nutritionnel
        - Maintien du poids actuel
        - Alimentation variée
        """)
    
    with col3:
        st.markdown("""
        #### 💪 Prise de masse
        - Surplus calorique optimal
        - Aliments riches en protéines
        - Développement musculaire
        """)
    
    st.markdown("---")
    
    # Call to action
    if not st.session_state.profile:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Créer mon profil maintenant", use_container_width=True, type="primary"):
                change_page("👤 Profil")
    else:
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        st.success(f"""
        ✅ **Profil configuré avec succès!**
        
        Votre objectif: **{st.session_state.profile['goal']}**  
        Calories quotidiennes: **{st.session_state.nutritional_needs['target_calories']:.0f} kcal**
        
        👉 Explorez maintenant les autres fonctionnalités!
        """)

# PAGE: PROFIL
elif page == "👤 Profil":
    st.markdown('<h1 class="main-header">👤 Configuration du Profil</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
<<<<<<< HEAD
        📝 <strong>Renseignez vos informations personnelles</strong> pour obtenir des recommandations nutritionnelles adaptées à vos besoins et objectifs.
=======
        📝 <strong>Renseignez vos informations personnelles</strong> pour obtenir des recommandations adaptées.
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("profile_form"):
        st.markdown("### 📏 Informations Physiques")
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Poids actuel (kg)", 30.0, 200.0, 70.0, 0.1)
            height = st.number_input("Taille (cm)", 120, 220, 170, 1)
            age = st.number_input("Âge", 15, 100, 25, 1)
        
        with col2:
            sex = st.selectbox("Sexe", ["Homme", "Femme"])
            target_weight = st.number_input("Poids cible (kg)", 30.0, 200.0, 65.0, 0.1)
            goal = st.selectbox("Objectif", ["Perte de poids", "Maintien", "Prise de masse"])
        
        st.markdown("### 🏃 Activité Physique")
        activity_level = st.select_slider(
            "Niveau d'activité quotidienne",
            options=['Sédentaire', 'Légèrement actif', 'Modérément actif', 'Très actif', 'Extrêmement actif'],
            value='Modérément actif',
            help="Sédentaire: Peu ou pas d'exercice | Légèrement actif: Exercice 1-3 jours/semaine | Modérément actif: 3-5 jours/semaine | Très actif: 6-7 jours/semaine | Extrêmement actif: Sport intense quotidien"
        )
        
<<<<<<< HEAD
        st.markdown("### 🍽️ Préférences Alimentaires")
        col1, col2 = st.columns(2)
        with col1:
            diet_type = st.multiselect(
                "Régime alimentaire",
                ["Omnivore", "Végétarien", "Végétalien", "Sans gluten", "Sans lactose"],
                default=["Omnivore"]
            )
        with col2:
            allergies = st.text_area("Allergies ou intolérances alimentaires", 
                                     placeholder="Ex: Arachides, fruits de mer, lactose...")
        
        st.markdown("---")
        submitted = st.form_submit_button("💾 Enregistrer mon profil", use_container_width=True, type="primary")
        
=======
        st.markdown("---")
        submitted = st.form_submit_button("💾 Enregistrer mon profil", use_container_width=True, type="primary")
        
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        if submitted:
            # Créer profil utilisateur
            profile_data = UserProfile(
                weight=weight,
                height=height,
                age=age,
                sex=sex,
                activity_level=activity_level,
                goal=goal,
                target_weight=target_weight
            )
            
            # Calculer besoins nutritionnels
            needs = NutritionalCalculator.calculate_complete_needs(profile_data)
            
            # Sauvegarder
            st.session_state.profile = {
                'weight': weight,
                'height': height,
                'age': age,
                'sex': sex,
                'target_weight': target_weight,
                'goal': goal,
                'activity_level': activity_level,
                'created_at': datetime.now()
            }
            
            st.session_state.nutritional_needs = needs
            
            # Mettre à jour le contexte de l'assistant
            if assistant:
                assistant.set_context(st.session_state.profile, needs)
            
            st.success("✅ Profil enregistré avec succès!")
            st.balloons()
            
            # Afficher les résultats
            st.markdown("---")
            st.markdown("### 📊 Vos Besoins Nutritionnels")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
<<<<<<< HEAD
                st.metric("🔥 Métabolisme de base", f"{needs['bmr']:.0f} kcal", 
                         help="Calories brûlées au repos")
            with col2:
                st.metric("⚡ Dépense quotidienne", f"{needs['tdee']:.0f} kcal", 
                         help="Calories totales brûlées par jour")
            with col3:
                st.metric("🎯 Calories recommandées", f"{needs['target_calories']:.0f} kcal", 
                         delta=f"{needs['deficit_surplus']:+.0f} kcal")
            with col4:
                if needs['duration_weeks'] > 0:
                    st.metric("⏱️ Durée estimée", f"{needs['duration_weeks']:.0f} semaines",
                             help=needs['duration_message'])
                else:
                    st.metric("⏱️ Objectif", "Maintien")
            
            st.markdown("### 🥗 Répartition Quotidienne des Macronutriments")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g",
                         help=f"{needs['macros']['proteins_pct']:.1f}% de vos calories")
            with col2:
                st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g",
                         help=f"{needs['macros']['carbs_pct']:.1f}% de vos calories")
            with col3:
                st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g",
                         help=f"{needs['macros']['fats_pct']:.1f}% de vos calories")
            
            st.markdown("### 💧 Hydratation")
            st.metric("💧 Eau recommandée par jour", f"{needs['water_liters']} litres")
            
            st.info(f"""
            ✅ **Récapitulatif de votre profil:**
            - **Objectif:** {goal}
            - **Évolution souhaitée:** de {weight}kg à {target_weight}kg
            - **Niveau d'activité:** {activity_level}
            - **Régime alimentaire:** {', '.join(diet_type)}
            """)
=======
                st.metric("🔥 Métabolisme de base", f"{needs['bmr']:.0f} kcal")
            with col2:
                st.metric("⚡ Dépense quotidienne", f"{needs['tdee']:.0f} kcal")
            with col3:
                st.metric("🎯 Calories recommandées", f"{needs['target_calories']:.0f} kcal")
            with col4:
                if needs['duration_weeks'] > 0:
                    st.metric("⏱️ Durée estimée", f"{needs['duration_weeks']:.0f} sem")
            
            st.markdown("### 🥗 Répartition Quotidienne")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g")
            with col2:
                st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g")
            with col3:
                st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a

# PAGE: DASHBOARD
elif page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">📊 Tableau de Bord</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
<<<<<<< HEAD
        st.warning("⚠️ Veuillez d'abord configurer votre profil dans l'onglet **👤 Profil**")
=======
        st.warning("⚠️ Veuillez d'abord configurer votre profil")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    else:
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
        # Métriques principales
        st.markdown("### 📊 Vos Objectifs Nutritionnels Quotidiens")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Calories", f"{needs['target_calories']:.0f} kcal")
        with col2:
            st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g")
        with col3:
            st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g")
        with col4:
            st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Répartition des Macronutriments")
            fig = go.Figure(data=[go.Pie(
                labels=['Protéines', 'Glucides', 'Lipides'],
                values=[
                    needs['macros']['proteins_cal'],
                    needs['macros']['carbs_cal'],
                    needs['macros']['fats_cal']
                ],
                hole=0.4,
                marker_colors=['#FF6B6B', '#4ECDC4', '#FFE66D']
            )])
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Progression vers l'Objectif")
            current = profile['weight']
            target = profile['target_weight']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=current,
                title={'text': "Poids Actuel (kg)"},
                delta={'reference': target},
                gauge={
                    'axis': {'range': [None, max(current, target) + 10]},
                    'bar': {'color': "#FF6B35"},
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'value': target
                    }
                }
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
<<<<<<< HEAD
        
        # Recommandations du jour
        st.markdown("---")
        st.markdown("### 🎯 Aliments Recommandés pour Vous")
        
        if recommender:
            target = NutritionalTarget(
                calories=needs['target_calories'],
                proteins=needs['macros']['proteins'],
                carbs=needs['macros']['carbs'],
                fats=needs['macros']['fats'],
                goal=profile['goal']
            )
            
            recommendations = recommender.recommend_foods(target, n_recommendations=6)
            
            cols = st.columns(3)
            for idx, (_, food) in enumerate(recommendations.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="food-card">
                        <h4>🍽️ {food['food']}</h4>
                        <span class="recommendation-badge">Compatibilité: {food['match_percentage']:.0f}%</span>
                        <p><strong>Pour 100g:</strong></p>
                        <ul style="font-size: 0.9rem;">
                            <li>🔥 {food['Caloric Value']:.0f} kcal</li>
                            <li>🥩 {food['Protein']:.1f}g protéines</li>
                            <li>🌾 {food['Carbohydrates']:.1f}g glucides</li>
                            <li>🥑 {food['Fat']:.1f}g lipides</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"⭐ Favoris", key=f"fav_dash_{idx}"):
                        if food['food'] not in st.session_state.favorite_foods:
                            st.session_state.favorite_foods.append(food['food'])
                            st.success(f"✅ {food['food']} ajouté aux favoris!")
=======
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a

# PAGE: RECOMMANDATIONS
elif page == "🎯 Recommandations":
    st.markdown('<h1 class="main-header">🎯 Recommandations Personnalisées</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des recommandations personnalisées")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
<<<<<<< HEAD
        st.markdown("""
        <div class="info-box">
            💡 Découvrez les aliments les plus adaptés à votre objectif et vos besoins nutritionnels
        </div>
        """, unsafe_allow_html=True)
        
=======
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        st.markdown("### 🔍 Recherche d'Aliments")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔎 Rechercher un aliment", placeholder="Nom d'aliment...")
        with col2:
<<<<<<< HEAD
            n_results = st.number_input("Nombre de résultats", 5, 20, 10)
        with col3:
            sort_by = st.selectbox("Trier par", ["Compatibilité", "Protéines", "Calories"])
        
        # Filtres avancés
        with st.expander("🔧 Filtres avancés"):
            col1, col2 = st.columns(2)
            with col1:
                min_protein = st.slider("Protéines minimum (g/100g)", 0, 50, 0)
                max_calories = st.slider("Calories maximum (kcal/100g)", 0, 1000, 1000)
            with col2:
                exclude_foods = st.multiselect(
                    "Exclure des aliments",
                    st.session_state.favorite_foods if st.session_state.favorite_foods else ["Aucun"]
                )
        
        if st.button("🎯 Voir les recommandations", use_container_width=True, type="primary"):
            with st.spinner("🔍 Recherche des meilleurs aliments pour vous..."):
                # Calculer les besoins pour un repas
=======
            n_results = st.number_input("Résultats", 5, 20, 10)
        
        if st.button("🎯 Obtenir recommandations", use_container_width=True, type="primary"):
            with st.spinner("🔍 Recherche en cours..."):
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                meal_ratio = 0.30
                
                target = NutritionalTarget(
                    calories=needs['target_calories'] * meal_ratio,
                    proteins=needs['macros']['proteins'] * meal_ratio,
                    carbs=needs['macros']['carbs'] * meal_ratio,
                    fats=needs['macros']['fats'] * meal_ratio,
                    goal=profile['goal']
                )
                
                recommendations = recommender.recommend_foods(target, n_recommendations=n_results)
                
                if search:
                    recommendations = recommendations[
                        recommendations['food'].str.contains(search, case=False, na=False)
                    ]
                
<<<<<<< HEAD
                st.success(f"✅ {len(recommendations)} aliments recommandés pour votre objectif: **{profile['goal']}**")
=======
                st.success(f"✅ {len(recommendations)} aliments recommandés")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                
                for idx, (_, food) in enumerate(recommendations.iterrows()):
<<<<<<< HEAD
                    with st.expander(f"#{idx+1} - {food['food']} (Compatibilité: {food['match_percentage']:.0f}%)", expanded=(idx < 3)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📊 Valeurs nutritionnelles /100g:**")
                            st.text(f"🔥 Calories: {food['Caloric Value']:.0f} kcal")
                            st.text(f"🥩 Protéines: {food['Protein']:.1f}g")
                            st.text(f"🌾 Glucides: {food['Carbohydrates']:.1f}g")
                            st.text(f"🥑 Lipides: {food['Fat']:.1f}g")
                            st.text(f"🌿 Fibres: {food['Dietary Fiber']:.1f}g")
                        
                        with col2:
                            st.markdown("**🍽️ Portion suggérée:**")
=======
                    with st.expander(f"#{idx+1} - {food['food']} ({food['match_percentage']:.0f}%)", expanded=(idx < 3)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📊 Valeurs /100g:**")
                            st.text(f"🔥 {food['Caloric Value']:.0f} kcal")
                            st.text(f"🥩 {food['Protein']:.1f}g protéines")
                            st.text(f"🌾 {food['Carbohydrates']:.1f}g glucides")
                            st.text(f"🥑 {food['Fat']:.1f}g lipides")
                        
                        with col2:
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                            if food['Caloric Value'] > 0:
                                portion = min(200, target.calories * 0.4 / food['Caloric Value'] * 100)
                            else:
<<<<<<< HEAD
                                suggested_portion = 100
                            st.text(f"📏 {suggested_portion:.0f}g recommandés")
                            
                            portion_cal = food['Caloric Value'] * suggested_portion / 100
                            portion_prot = food['Protein'] * suggested_portion / 100
                            st.text(f"🔥 {portion_cal:.0f} kcal")
                            st.text(f"🥩 {portion_prot:.1f}g protéines")
                            
                            # Indicateurs
                            if food['Protein'] > 15:
                                st.success("💪 Riche en protéines")
                            if food['Dietary Fiber'] > 5:
                                st.success("🌿 Riche en fibres")
                            if food['Caloric Value'] < 100:
                                st.info("🔥 Faible en calories")
                        
                        with col3:
                            st.markdown("**⭐ Évaluation:**")
                            score = food.get('Nutrition Density', 5)
                            st.progress(min(score / 10, 1.0))
                            st.caption(f"Score nutritionnel: {score:.1f}/10")
                            
                            st.markdown("**🎯 Pour votre objectif:**")
                            if profile['goal'] == 'Perte de poids':
                                if food['Caloric Value'] < 150 and food['Protein'] > 10:
                                    st.success("✅ EXCELLENT CHOIX")
                                elif food['Caloric Value'] < 300:
                                    st.warning("⚠️ BON AVEC MODÉRATION")
                                else:
                                    st.error("❌ À LIMITER")
                            elif profile['goal'] == 'Prise de masse':
                                if food['Caloric Value'] > 200 and food['Protein'] > 15:
                                    st.success("✅ EXCELLENT CHOIX")
                                else:
                                    st.info("ℹ️ BON ALIMENT")
                            else:
                                st.success("✅ COMPATIBLE")
                        
                        # Actions
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"⭐ Ajouter aux favoris", key=f"fav_rec_{idx}"):
                                if food['food'] not in st.session_state.favorite_foods:
                                    st.session_state.favorite_foods.append(food['food'])
                                    st.success(f"✅ {food['food']} ajouté!")
                        with col_b:
                            if st.button(f"🔄 Voir alternatives", key=f"alt_rec_{idx}"):
                                alternatives = recommender.find_alternatives(food['food'], n_alternatives=3)
                                if not alternatives.empty:
                                    st.write("**Alternatives similaires:**")
                                    for _, alt in alternatives.iterrows():
                                        st.text(f"• {alt['food']}")
        
        # Favoris
        if st.session_state.favorite_foods:
            st.markdown("---")
            st.markdown("### ⭐ Mes Aliments Favoris")
            
            cols = st.columns(4)
            for idx, food_name in enumerate(st.session_state.favorite_foods):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class="food-card">
                        <p><strong>{food_name}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🗑️ Retirer", key=f"remove_fav_{idx}"):
                        st.session_state.favorite_foods.remove(food_name)
                        st.rerun()

# PAGE: PLAN ALIMENTAIRE
elif page == "🍽️ Plan Alimentaire":
    st.markdown('<h1 class="main-header">🍽️ Votre Plan Alimentaire Personnalisé</h1>', unsafe_allow_html=True)
=======
                                portion = 100
                            st.markdown(f"**Portion suggérée: {portion:.0f}g**")
                            st.text(f"🔥 {food['Caloric Value'] * portion / 100:.0f} kcal")
                        
                        with col3:
                            if st.button("⭐ Favoris", key=f"fav_{idx}"):
                                if food['food'] not in st.session_state.favorite_foods:
                                    st.session_state.favorite_foods.append(food['food'])
                                    st.success("✅ Ajouté!")

# PAGE: PLAN ALIMENTAIRE
elif page == "🍽️ Plan Alimentaire":
    st.markdown('<h1 class="main-header">🍽️ Plan Alimentaire Personnalisé</h1>', unsafe_allow_html=True)
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
<<<<<<< HEAD
        st.markdown("""
        <div class="info-box">
            📅 Générez un plan alimentaire hebdomadaire adapté à vos besoins et préférences
        </div>
        """, unsafe_allow_html=True)
        
=======
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        with st.form("meal_plan_form"):
            st.markdown("### ⚙️ Personnalisez votre plan")
            
            col1, col2 = st.columns(2)
            
            with col1:
<<<<<<< HEAD
                meals_per_day = st.slider("Nombre de repas par jour", 3, 6, 4,
                                         help="3 repas = Petit-déj, Déjeuner, Dîner | 4+ = Ajout de collations")
                variety_days = st.slider("Variété des repas (jours)", 1, 7, 7,
                                        help="Nombre de jours avant de répéter les mêmes repas")
            
            with col2:
                budget = st.selectbox("Budget alimentaire", ["Économique", "Moyen", "Élevé"])
                prep_time = st.selectbox("Temps de préparation", 
                                        ["Rapide (<30min)", "Moyen (30-60min)", "Élaboré (>60min)"])
            
            st.markdown("---")
            generate = st.form_submit_button("🎨 Générer mon plan alimentaire", use_container_width=True, type="primary")
            
            if generate and meal_generator:
                with st.spinner("🍳 Création de votre plan personnalisé..."):
                    # Préparer les préférences
=======
                meals_per_day = st.slider("Repas par jour", 3, 6, 4)
                variety_days = st.slider("Variété (jours)", 1, 7, 7)
            
            with col2:
                budget = st.selectbox("Budget", ["Économique", "Moyen", "Élevé"])
                prep_time = st.selectbox("Temps", ["Rapide (<30min)", "Moyen", "Élaboré"])
            
            generate = st.form_submit_button("🎨 Générer", use_container_width=True, type="primary")
            
            if generate and meal_generator:
                with st.spinner("🳳 Création en cours..."):
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                    preferences = MealPlanPreferences(
                        meals_per_day=meals_per_day,
                        variety_days=variety_days,
                        budget=budget,
                        prep_time=prep_time
                    )
                    
                    week_plan = meal_generator.generate_week_plan(
                        st.session_state.nutritional_needs,
                        preferences
                    )
                    
<<<<<<< HEAD
                    # Formater
                    formatted_plan = meal_generator.format_plan_for_display(week_plan)
                    st.session_state.meal_plan = formatted_plan
                    
                    # Stats
                    stats = meal_generator.calculate_plan_stats(week_plan)
                    
                    st.success("✅ Votre plan alimentaire est prêt!")
                    st.balloons()
                    
                    # Statistiques
=======
                    formatted_plan = meal_generator.format_plan_for_display(week_plan)
                    st.session_state.meal_plan = formatted_plan
                    
                    stats = meal_generator.calculate_plan_stats(week_plan)
                    
                    st.success("✅ Plan prêt!")
                    st.balloons()
                    
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Calories moy", f"{stats['avg_daily_calories']:.0f}")
                    with col2:
                        st.metric("Protéines moy", f"{stats['avg_daily_proteins']:.0f}g")
                    with col3:
                        st.metric("Aliments différents", stats['unique_foods_count'])
                    with col4:
                        st.metric("Score de variété", f"{stats['variety_score']:.0f}%")
        
        if st.session_state.meal_plan:
            st.markdown("---")
<<<<<<< HEAD
            st.markdown("### 📅 Votre Plan de la Semaine")
=======
            st.markdown("### 📅 Votre Plan")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
            
            days = list(st.session_state.meal_plan.keys())
<<<<<<< HEAD
            selected_day = st.selectbox("📆 Choisissez un jour", days)
=======
            selected_day = st.selectbox("📆 Jour", days)
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
            
            if selected_day in st.session_state.meal_plan:
                day_meals = st.session_state.meal_plan[selected_day]
                
                total_cal = sum([meal.get('calories', 0) for meal in day_meals.values()])
                
<<<<<<< HEAD
                st.markdown(f"### 📊 Bilan nutritionnel - {selected_day}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Calories", f"{total_cal:.0f} kcal")
                with col2:
                    st.metric("Total Protéines", f"{total_prot:.0f}g")
                with col3:
                    st.metric("Total Glucides", f"{total_carbs:.0f}g")
                with col4:
                    st.metric("Total Lipides", f"{total_fats:.0f}g")
                
                # Comparaison
                target = st.session_state.nutritional_needs['target_calories']
                diff = total_cal - target
                if abs(diff) < 100:
                    st.success(f"✅ Parfait! Vous êtes à {diff:+.0f} kcal de votre objectif")
                elif abs(diff) < 200:
                    st.warning(f"⚠️ Proche de l'objectif ({diff:+.0f} kcal de différence)")
                else:
                    st.error(f"❌ Écart important: {diff:+.0f} kcal")
                
                st.markdown("---")
                
                # Repas du jour
=======
                st.metric("Total jour", f"{total_cal:.0f} kcal")
                
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                for meal_name, meal_data in day_meals.items():
                    with st.expander(f"🍽️ {meal_name}", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
<<<<<<< HEAD
                            st.markdown("**🥘 Composition du repas:**")
=======
                            st.markdown("**Aliments:**")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                            for aliment in meal_data.get('aliments', []):
                                st.markdown(f"• {aliment}")
                        
                        with col2:
<<<<<<< HEAD
                            st.markdown("**📊 Valeurs nutritionnelles:**")
                            st.markdown(f"- 🔥 {meal_data.get('calories', 0):.0f} kcal")
                            st.markdown(f"- 🥩 {meal_data.get('proteines', 0):.0f}g protéines")
                            st.markdown(f"- 🌾 {meal_data.get('glucides', 0):.0f}g glucides")
                            st.markdown(f"- 🥑 {meal_data.get('lipides', 0):.0f}g lipides")
            
            # Actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Générer un nouveau plan", use_container_width=True):
                    st.session_state.meal_plan = None
                    st.rerun()
            with col2:
                if st.button("📥 Exporter en PDF", use_container_width=True):
                    st.info("🚧 Fonctionnalité d'export bientôt disponible")
            with col3:
                if st.button("💾 Sauvegarder", use_container_width=True):
                    st.success("✅ Plan sauvegardé!")
=======
                            st.markdown("**Nutrition:**")
                            st.markdown(f"🔥 {meal_data.get('calories', 0):.0f} kcal")
                            st.markdown(f"🥩 {meal_data.get('proteines', 0):.0f}g")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a

# PAGE: ASSISTANT (CORRIGÉ - Réponses diversifiées)
elif page == "💬 Assistant":
    st.markdown('<h1 class="main-header">💬 Assistant Nutritionnel</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
<<<<<<< HEAD
        💡 Posez toutes vos questions sur la nutrition, les aliments, et recevez des conseils personnalisés
=======
        💡 Posez vos questions sur la nutrition et recevez des conseils personnalisés
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des réponses personnalisées")
<<<<<<< HEAD
    
    st.markdown("### 💡 Questions Fréquentes (Cliquez pour poser)")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍳 Petit-déjeuner protéiné", use_container_width=True):
            question = "Suggère-moi un petit-déjeuner protéiné adapté à mon objectif"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col2:
        if st.button("🏋️ Post-entraînement", use_container_width=True):
            question = "Que dois-je manger après mon entraînement?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col3:
        if st.button("💧 Hydratation", use_container_width=True):
            question = "Combien d'eau dois-je boire par jour?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐟 Bienfaits du saumon", use_container_width=True):
            question = "Quels sont les bienfaits du saumon pour moi?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col2:
        if st.button("🔄 Alternatives poulet", use_container_width=True):
            question = "Quelles sont les alternatives au poulet?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col3:
        if st.button("⏰ Timing des repas", use_container_width=True):
            question = "À quelle heure dois-je prendre mes repas?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    
    st.markdown("---")
    
    # Historique du chat
    chat_container = st.container()
    with chat_container:
=======
        if st.button("Configurer mon profil"):
            change_page("👤 Profil")
    else:
        # Questions rapides
        st.markdown("### 💡 Questions Fréquentes")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🳳 Petit-déjeuner", use_container_width=True):
                question = "Suggère-moi un petit-déjeuner protéiné"
                st.session_state.chat_history.append({"role": "user", "content": question})
                if assistant:
                    response = assistant.answer_query(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("🏋️ Post-entraînement", use_container_width=True):
                question = "Que manger après l'entraînement?"
                st.session_state.chat_history.append({"role": "user", "content": question})
                if assistant:
                    response = assistant.answer_query(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("💧 Hydratation", use_container_width=True):
                question = "Combien d'eau dois-je boire?"
                st.session_state.chat_history.append({"role": "user", "content": question})
                if assistant:
                    response = assistant.answer_query(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        st.markdown("---")
        
        # Historique du chat
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        for msg in st.session_state.chat_history[-10:]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong>👤 Vous:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>🤖 Assistant:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
<<<<<<< HEAD
    
    # Zone de saisie
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("💬 Votre question...", 
                                   key="chat_input", 
                                   label_visibility="collapsed",
                                   placeholder="Ex: Suggère-moi un repas, Quels aliments pour mon objectif?")
    with col2:
        send = st.button("📤 Envoyer", use_container_width=True)
    
    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤖 Réflexion en cours..."):
            if assistant and st.session_state.profile:
                response = assistant.answer_query(user_input)
            else:
                response = """
⚠️ **Configuration nécessaire**

Pour recevoir des conseils personnalisés, veuillez:
1. Configurer votre profil dans l'onglet **👤 Profil**
2. Renseigner vos informations personnelles
3. Enregistrer votre profil

Je pourrai ensuite vous fournir des recommandations adaptées à votre objectif! 💪
"""
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Effacer historique
    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.chat_history = []
=======
        
        # Zone de saisie
        st.markdown("---")
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("💬 Votre question...", 
                                       key="chat_input", 
                                       placeholder="Ex: Analyse le saumon pour mon objectif")
        with col2:
            send = st.button("📤", use_container_width=True)
        
        if send and user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 Réflexion..."):
                if assistant:
                    response = assistant.answer_query(user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
            
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
            st.rerun()
        
        # Effacer historique
        if st.session_state.chat_history:
            st.markdown("---")
            if st.button("🗑️ Effacer l'historique"):
                st.session_state.chat_history = []
                st.rerun()

# PAGE: SUIVI
elif page == "📈 Suivi":
    st.markdown('<h1 class="main-header">📈 Suivi de Votre Progression</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
        st.markdown("""
        <div class="info-box">
            📊 Suivez votre évolution en enregistrant régulièrement votre poids et visualisez vos progrès
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Nouvel Enregistrement")
            with st.form("weight_form"):
<<<<<<< HEAD
                col_a, col_b = st.columns(2)
                with col_a:
                    weight_date = st.date_input("Date de la mesure", datetime.now())
                    weight_val = st.number_input("Poids (kg)", 30.0, 200.0, 
                                                 st.session_state.profile['weight'], 0.1)
                with col_b:
                    notes = st.text_area("Notes (optionnel)", 
                                        placeholder="Comment vous sentez-vous? Observations...")
=======
                weight_date = st.date_input("Date", datetime.now())
                weight_val = st.number_input("Poids (kg)", 30.0, 200.0, 
                                             st.session_state.profile['weight'], 0.1)
                notes = st.text_area("Notes", placeholder="Comment vous sentez-vous?")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                
                if st.form_submit_button("💾 Enregistrer", use_container_width=True, type="primary"):
                    st.session_state.weight_history.append({
                        'date': weight_date,
                        'weight': weight_val,
                        'notes': notes
                    })
<<<<<<< HEAD
                    st.success(f"✅ Poids de {weight_val} kg enregistré pour le {weight_date}")
=======
                    st.success(f"✅ Poids enregistré: {weight_val} kg")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                    st.balloons()
        
        with col2:
            if st.session_state.weight_history:
                st.markdown("### 📊 Vos Statistiques")
                latest = st.session_state.weight_history[-1]['weight']
                initial = st.session_state.profile['weight']
                target = st.session_state.profile['target_weight']
                
                st.metric("Dernier poids", f"{latest:.1f} kg", 
                         f"{latest - initial:+.1f} kg")
                
                progress = abs(initial - latest)
                total = abs(initial - target)
                pct = (progress / total * 100) if total > 0 else 0
                
                st.progress(min(pct / 100, 1.0))
<<<<<<< HEAD
                st.caption(f"**{pct:.1f}%** de votre objectif atteint")
                
                remaining = abs(target - latest)
                st.metric("Reste à atteindre", f"{remaining:.1f} kg")
            else:
                st.info("📊 Aucun enregistrement.\nCommencez à suivre votre progression!")
=======
                st.caption(f"{pct:.1f}% atteint")
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
        
        # Graphique
        if st.session_state.weight_history:
            st.markdown("---")
            st.markdown("### 📈 Courbe d'Évolution")
            
            dates = [e['date'] for e in st.session_state.weight_history]
            weights = [e['weight'] for e in st.session_state.weight_history]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=weights,
                mode='lines+markers',
<<<<<<< HEAD
                name='Votre poids',
                line=dict(color='#FF6B35', width=3),
                marker=dict(size=10, color='#FF6B35')
=======
                name='Poids',
                line=dict(color='#FF6B35', width=3)
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
            ))
            
            target = st.session_state.profile['target_weight']
            fig.add_trace(go.Scatter(
                x=[dates[0], dates[-1]],
                y=[target, target],
                mode='lines',
                name='Objectif',
                line=dict(color='green', dash='dash')
            ))
            
            fig.update_layout(
<<<<<<< HEAD
                title="Évolution de Votre Poids",
=======
                title="Évolution du Poids",
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
                xaxis_title="Date",
                yaxis_title="Poids (kg)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

# PAGE: BASE ALIMENTS
elif page == "📚 Base Aliments":
    st.markdown('<h1 class="main-header">📚 Base de Données</h1>', unsafe_allow_html=True)
    
    st.markdown(f"### 🔍 {len(food_data)} aliments disponibles")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("🔎 Rechercher", placeholder="Nom d'aliment...")
    with col2:
        min_protein = st.slider("Protéines min (g)", 0, 50, 0)
    with col3:
        max_calories = st.slider("Calories max", 0, 1000, 1000)
    
    # Filtrage
    filtered = food_data.copy()
    
    if search:
        filtered = filtered[filtered['food'].str.contains(search, case=False, na=False)]
    
    filtered = filtered[
        (filtered['Protein'] >= min_protein) &
        (filtered['Caloric Value'] <= max_calories)
    ]
    
    st.markdown(f"### 📊 {len(filtered)} résultats")
    
    # Affichage paginé
    items_per_page = 10
    total_pages = max(1, (len(filtered) - 1) // items_per_page + 1)
    
    if total_pages > 0:
        page_num = st.number_input("Page", 1, total_pages, 1)
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered))
        
        page_data = filtered.iloc[start_idx:end_idx]
        
        for idx, (_, row) in enumerate(page_data.iterrows()):
            with st.expander(f"🍽️ {row['food']} - {row['Caloric Value']:.0f} kcal", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Macronutriments")
                    st.markdown(f"""
                    - 🔥 Calories: {row['Caloric Value']:.0f} kcal
                    - 🥩 Protéines: {row['Protein']:.1f}g
                    - 🌾 Glucides: {row['Carbohydrates']:.1f}g
                    - 🥑 Lipides: {row['Fat']:.1f}g
                    - 🌿 Fibres: {row['Dietary Fiber']:.1f}g
                    """)
                
                with col2:
                    st.markdown("#### 💊 Vitamines & Minéraux")
                    st.markdown(f"""
                    - 🅰️ Vitamine A: {row['Vitamin A']:.1f}µg
                    - 🅱️ Vitamine B12: {row['Vitamin B12']:.2f}µg
                    - 🍊 Vitamine C: {row['Vitamin C']:.1f}mg
                    - 🦴 Calcium: {row['Calcium']:.0f}mg
                    """)

<<<<<<< HEAD
# PAGE: Assistant IA (RAG)
elif page == "🧠 Assistant IA (RAG)":
    st.markdown('<h1 class="main-header">🧠 Assistant Intelligence Artificielle</h1>', unsafe_allow_html=True)
    
    # Charger pipeline
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = load_rag_pipeline()
    
    if not st.session_state.rag_pipeline:
        st.warning("⚠️ Le module IA n'est pas disponible (vérifiez les logs console et que RAG est bien installé)")
    else:
        st.markdown("""
        <div class="info-box">
            🤖 Posez des questions complexes sur la nutrition. L'IA utilise une base de connaissances avancée pour vous répondre.
        </div>
        """, unsafe_allow_html=True)
        
        # Zone de query
        col1, col2 = st.columns([3, 1])
        with col1:
             user_query = st.text_input("💬 Votre question", placeholder="Ex: Quels aliments pour améliorer la mémoire ?", key="rag_query_input")
        with col2:
             use_llm = st.checkbox("Utiliser LLM", value=True, help="Activer la génération de réponse par IA")
             # Retrieve stats for valid slider range
             total_docs = 10
             try:
                if st.session_state.rag_pipeline and hasattr(st.session_state.rag_pipeline, 'df'):
                    total_docs = len(st.session_state.rag_pipeline.df)
             except:
                pass
             k = st.slider("Sources", 1, min(20, total_docs), 5)

        if st.button("🚀 Analyser", type="primary"):
            if user_query:
                with st.spinner("🤖 L'IA analyse votre demande..."):
                    try:
                        # Contexte utilisateur
                        context_query = user_query
                        if 'profile' in st.session_state and st.session_state.profile:
                             profile = st.session_state.profile
                             context_query = f"Contexte: {profile.get('age')} ans, Objectif {profile.get('goal')}. Question: {user_query}"
                             
                        # Pipeline execution
                        if hasattr(st.session_state.rag_pipeline, 'use_llm'):
                             st.session_state.rag_pipeline.use_llm = use_llm

                        results = st.session_state.rag_pipeline.query(context_query, k=k)
                        
                        # Affichage
                        st.markdown("### 🤖 Réponse de l'Assistant")
                        st.success(results['response'])
                        
                        st.markdown("### 📚 Sources utilisées")
                        for food in results['foods']:
                             with st.expander(f"{food['food_name']} ({food.get('similarity_score', 0)*100:.1f}%)"):
                                  st.write(f"- Calories: {food.get('calories_kcal')} kcal")
                                  st.write(f"- Protéines: {food.get('protein_g')} g")
                                  st.write(f"- Catégorie: {food.get('food_category')}")
                                  
                    except Exception as e:
                        st.error(f"Erreur IA: {str(e)}")
            else:
                st.warning("Veuillez poser une question")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>🥗 FitLife - Assistant Nutritionnel IA 100% Local</strong></p>
    <p>Développé avec ❤️ par Asma Bélkahla & Monia Selleoui</p>
    <p style='font-size: 0.9rem;'>
        🤖 Powered by: Scikit-learn, Streamlit, Pandas, NumPy, Plotly<br>
        ✅ Sans API externe | ✅ 100% Local | ✅ Open Source
    </p>
    <p style='font-size: 0.8rem; margin-top: 1rem;'>
        ⚠️ Les conseils fournis sont à titre informatif uniquement.<br>
        Consultez toujours un professionnel de santé avant de modifier votre régime.
    </p>
    <hr style='margin: 1rem auto; width: 50%; border: 1px solid #ddd;'>
    <p style='font-size: 0.8rem;'>
        <strong>Modules IA utilisés:</strong><br>
        📊 Calculateur Nutritionnel | 🎯 Recommandeur ML | 🍽️ Planificateur | 💬 Assistant NLP
=======
# Footer simplifié
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1.5rem;'>
    <p><strong>🥗 FitLife - Assistant Nutritionnel IA</strong></p>
    <p>Développé par Asma Bélkahla & Monia Selleoui</p>
    <p style='font-size: 0.9rem; margin-top: 1rem;'>
        🤖 IA 100% Locale | 📊 Scikit-learn | 🎨 Streamlit | 📈 Plotly
>>>>>>> 6660fe86de3a80c1cfe400a7d0c97cbe914de13a
    </p>
</div>
""", unsafe_allow_html=True)

