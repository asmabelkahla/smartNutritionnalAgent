## 🥗 FitLife - Assistant Nutritionnel IA (100% Local)

Application Streamlit d’aide nutritionnelle qui calcule vos besoins, recommande des aliments, génère des plans alimentaires et répond aux questions de base sur la nutrition. Le tout fonctionne en local.

---

### 🚀 Fonctionnalités
- **Analyse personnalisée**: calcul du BMR, TDEE, calories cibles, macros quotidiennes.
- **Recommandations intelligentes**: propositions d’aliments alignées sur votre objectif (perte, maintien, prise de masse).
- **Génération de plans alimentaires**: menus journaliers/hebdomadaires équilibrés selon vos préférences.
- **Assistant conversationnel**: réponses guidées par règles et contexte utilisateur (profil, besoins).
- **Dashboard et suivi**: métriques clefs, graphiques, favoris, base aliments consultable.

---

### 🧱 Architecture du projet
```
FitLife-Nutrition-AI/
├─ app.py                          # Application Streamlit (UI)
├─ requirements.txt                # Dépendances Python
├─ modules/
│  ├─ nutrition_calculator.py      # Module 1: Calculs BMR/TDEE/macros/eau
│  ├─ food_recommender.py          # Module 2: Recommandations (cosine similarity + scoring)
│  ├─ meal_plan_generator.py       # Module 3: Générateur de plans (règles + optimisation simple)
│  └─ nutrition_assistant.py       # Module 4: Assistant NLP à base de règles/templates
└─ data/
   └─ nutrition/
      ├─ FOOD-DATA-GROUP1.csv      # Jeux de données 
      ├─ FOOD-DATA-GROUP2.csv
      ├─ FOOD-DATA-GROUP3.csv
      ├─ FOOD-DATA-GROUP4.csv
      └─ FOOD-DATA-GROUP5.csv
```

---

Prérequis: Python 3.9+ recommandé.

1) Cloner le dépôt et se placer à la racine:
```bash
git clone <url_du_repo>
cd FitLife-Nutrition-AI
```

2) Créer un environnement virtuel (recommandé):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

3) Installer les dépendances:
```bash
pip install -r requirements.txt
```

---



### 📂 Données
- Par défaut, l’application tentera de charger les CSV présents dans `data/nutrition/`.
- Si aucun fichier n’est trouvé, un petit dataset de secours en mémoire est utilisé.
- Colonnes attendues (exemples): `food`, `Caloric Value`, `Protein`, `Carbohydrates`, `Fat`, `Dietary Fiber`, `Saturated Fats`, `Sugars`, `Sodium`, etc.

---

### 🧠 Modèles IA et approche
Le projet est 100% local et n’appelle aucune API. Les “modèles”/méthodes utilisées:
- Module 1 – `NutritionalCalculator`:
  - Formule Mifflin-St Jeor pour BMR, facteurs d’activité pour TDEE.
  - Heuristiques scientifiques pour la répartition des macronutriments et l’hydratation.
- Module 2 – `FoodRecommendationEngine`:
  - Standardisation des features (scikit-learn `StandardScaler`).
  - Similarité cosinus (`sklearn.metrics.pairwise.cosine_similarity`) entre un profil-cible et les aliments.
  - Pondérations spécifiques à l’objectif (perte/maintien/prise de masse).
  - Score “Nutrition Density” calculé de manière heuristique.
- Module 3 – `MealPlanGenerator`:
  - Génération par règles/structures de repas, utilisation du moteur de reco pour remplir chaque “slot”.
  - Répartition calorique par repas, contraintes simples (variété, catégories d’aliments).
- Module 4 – `NutritionAssistant`:
  - Assistant à base de règles et de templates, reconnaissance de motifs (regex).
  - Utilise le contexte utilisateur (profil, besoins) pour personnaliser les réponses.

Aucun modèle LLM externe ni de deep learning n’est nécessaire. Voir `MODELES.md` pour plus de détails.

---

### 🧩 Principales dépendances
Contenues dans `requirements.txt`:
- `streamlit`: interface et interactions
- `plotly`: visualisations
- `scikit-learn`: standardisation et similarité cosinus
- `pandas`, `numpy`: manipulation de données et calculs

---

### 🔎 Points d’entrée et modules
- `app.py`: UI, navigation, intégration des 4 modules, gestion de session, affichages.
- `modules/nutrition_calculator.py`: BMR/TDEE/calories cibles/macros/eau, durée vers l’objectif.
- `modules/food_recommender.py`: préparation des features, profil-cible, similarités, ranking.
- `modules/meal_plan_generator.py`: génération jour/semaine, formatage affichage, statistiques.
- `modules/nutrition_assistant.py`: intents par regex, réponses guidées par templates, analyse d’aliments.


---

### ⚠️ Avertissement
Cette application fournit des informations à titre indicatif et éducatif. Pour un suivi personnalisé, consultez un professionnel de santé.

---

### 📜 Licence
Open Source. Voir entête des fichiers pour crédits: Asma Bélkahla .

