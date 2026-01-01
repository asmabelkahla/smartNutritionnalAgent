## 📘 Modèles et Approches IA Utilisés

Ce document détaille les méthodes “IA/ML” et les choix algorithmiques faits dans FitLife. 

---

### 1) Calculateur Nutritionnel (`modules/nutrition_calculator.py`)
- **Type**: Formules scientifiques + heuristiques
- **Entrées**: profil utilisateur (`poids`, `taille`, `âge`, `sexe`, `niveau d’activité`, `objectif`, `poids cible`)
- **Sorties**:
  - `bmr` (Mifflin-St Jeor)
  - `tdee` (BMR × facteur d’activité)
  - `target_calories` (ajustement selon l’objectif)
  - `macros` (protéines/glucides/lipides avec calories et pourcentages)
  - `water_liters`
  - `duration_weeks` + message
- **Hypothèses**:
  - Protéines élevées en perte/prise (≈2 g/kg) pour préserver/développer la masse musculaire.
  - Lipides ~27% des calories, glucides = calories restantes.
  - Eau ≈ 33 ml/kg ajustée selon activité.

---

### 2) Moteur de Recommandation (`modules/food_recommender.py`)
- **Type**: Recommandation basée contenu (Content-Based) + similarité cosinus
- **Outils**: `StandardScaler` et `cosine_similarity` (scikit-learn)
- **Features** (par aliment):
  - `Caloric Value`, `Fat`, `Saturated Fats`, `Carbohydrates`, `Sugars`, `Protein`, `Dietary Fiber`, `Sodium`
- **Pipeline**:
  1. Remplissage NaN → Matrice features → Standardisation
  2. Construction d’un “profil-cible” (objectif calories/macros ramenés à 100 g)
  3. Similarité cosinus entre profil-cible et chaque aliment
  4. Pondérations spécifiques à l’objectif:
     - Perte de poids: bonus fibres/protéines, pénalité calories
     - Prise de masse: bonus protéines et calories
     - Maintien: bonus “Nutrition Density”
  5. Filtrage (min protéines, max calories, exclusions), tri par score
- **Scores dérivés**:
  - `Nutrition Density` (heuristique): récompense protéines/fibres par kcal, pénalise sucres/gras saturés.

---

### 3) Générateur de Plans (`modules/meal_plan_generator.py`)
- **Type**: Règles + optimisation simple par slots + randomisation contrôlée
- **Idée**:
  - Définir une structure par type de repas (ex: Déjeuner = protéine + féculent + légume + MG)
  - Allouer une part des calories et des macros par slot
  - Demander au moteur de reco l’aliment “le plus adapté” pour chaque slot en tenant compte:
    - de la catégorie attendue
    - des aliments déjà utilisés (variété)
  - Calculer les portions en g pour respecter les cibles/slots
- **Sorties**:
  - Jour(s) et Semaine formatés (calories, protéines, glucides, lipides, liste d’aliments)
  - Statistiques globales (moyennes/jour, variété, etc.)

---

### 4) Assistant Nutritionnel (`modules/nutrition_assistant.py`)
- **Type**: Système de règles/regex + templates contextuels
- **Fonctionnement**:
  - Détection d’intentions via motifs (ex: “petit-déjeuner”, “post-entraînement”, “hydratation”, “analyse aliment”, etc.)
  - Utilisation du contexte (profil, besoins calculés) pour personnaliser les réponses
  - Mode “analyse aliment”: récupération des valeurs alimentaires, évaluation vs objectif, alternatives via le moteur de reco



---