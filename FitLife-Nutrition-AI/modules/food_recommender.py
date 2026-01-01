"""
Module 2: Moteur de Recommandation d'Aliments
Système ML basé sur la similarité cosine et l'optimisation
Auteurs: Asma Bélkahla & Monia Selleoui
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class NutritionalTarget:
    """Représente un objectif nutritionnel cible"""
    calories: float
    proteins: float
    carbs: float
    fats: float
    goal: str  # 'Perte de poids', 'Maintien', 'Prise de masse'

class FoodRecommendationEngine:
    """
    Moteur de recommandation ML 
    Utilise: cosine similarity, feature engineering, scoring personnalisé
    
    Architecture:
    1. Préparation features: normalisation StandardScaler
    2. Création profil-cible: adapté aux besoins utilisateur
    3. Calcul similarités: cosine similarity
    4. Pondération: ajustements selon objectif
    5. Ranking: tri par score final
    """
    
    def __init__(self, food_df: pd.DataFrame):
        self.food_df = food_df.copy()
        self.scaler = StandardScaler()
        self.nutrition_cols = [
            'Caloric Value', 'Fat', 'Saturated Fats', 
            'Carbohydrates', 'Sugars', 'Protein', 
            'Dietary Fiber', 'Sodium'
        ]
        self._prepare_features()
    
    def _prepare_features(self):
        """Prépare et normalise les features nutritionnelles"""
        # Remplir les valeurs manquantes
        for col in self.nutrition_cols:
            if col in self.food_df.columns:
                self.food_df[col] = self.food_df[col].fillna(0)
        
        # Créer matrice de features
        self.nutrition_matrix = self.food_df[self.nutrition_cols].values
        
        # Normalisation (crucial pour cosine similarity)
        self.features_scaled = self.scaler.fit_transform(self.nutrition_matrix)
        
        # Calculer scores de densité nutritionnelle si absent
        if 'Nutrition Density' not in self.food_df.columns or self.food_df['Nutrition Density'].isna().all():
            self.food_df['Nutrition Density'] = self._calculate_nutrition_density()
    
    def _calculate_nutrition_density(self) -> np.ndarray:
        """
        Calcul du score de densité nutritionnelle
        Basé sur: protéines, fibres, vitamines vs calories, gras saturés
        
        Formule heuristique:
        Score = (protéines/cal)*100 + (fibres/cal)*50 - (sat_fat/cal)*30 - (sucres/cal)*20
        Normalisé entre 0-10
        """
        scores = np.zeros(len(self.food_df))
        
        for i, row in self.food_df.iterrows():
            score = 0
            
            # Points positifs (nutriments bénéfiques par calorie)
            if row['Caloric Value'] > 0:
                score += (row['Protein'] / row['Caloric Value']) * 100
                score += (row['Dietary Fiber'] / row['Caloric Value']) * 50
            
            # Pénalités (nutriments à limiter)
            if row['Caloric Value'] > 0:
                score -= (row['Saturated Fats'] / row['Caloric Value']) * 30
                score -= (row['Sugars'] / row['Caloric Value']) * 20
            
            # Normaliser entre 0-10
            scores[i] = max(0, min(10, score * 2))
        
        return scores
    
    def _create_target_profile(self, target: NutritionalTarget) -> np.ndarray:
        """
        Crée un profil nutritionnel cible pour la comparaison
        Normalisé par 100g pour cohérence avec dataset
        
        Args:
            target: Objectifs nutritionnels
            
        Returns:
            Profil normalisé (1, n_features)
        """
        profile = np.array([
            target.calories / 100,
            target.fats / 100,
            target.fats * 0.3 / 100,  # ~30% gras saturés
            target.carbs / 100,
            target.carbs * 0.15 / 100,  # ~15% sucres
            target.proteins / 100,
            25 / 100,  # Objectif fibres standard
            2000 / 100  # Limite sodium recommandée
        ]).reshape(1, -1)
        
        return self.scaler.transform(profile)
    
    def _apply_goal_weights(self, similarities: np.ndarray, goal: str) -> np.ndarray:
        """
        Applique des pondérations selon l'objectif
        Booste les aliments alignés avec l'objectif
        
        Args:
            similarities: Scores de similarité de base
            goal: Objectif utilisateur
            
        Returns:
            Similarités pondérées
        """
        weighted_sims = similarities.copy()
        
        if goal == 'Prise de masse':
            # Favoriser: haute calorie, haute protéine
            protein_boost = self.food_df['Protein'].fillna(0) / (self.food_df['Protein'].max() + 1e-6)
            calorie_boost = self.food_df['Caloric Value'].fillna(0) / (self.food_df['Caloric Value'].max() + 1e-6)
            weighted_sims *= (1 + protein_boost * 0.5 + calorie_boost * 0.3)
        
        elif goal == 'Perte de poids':
            # Favoriser: basse calorie, haute fibre, haute protéine
            calorie_penalty = 1 - (self.food_df['Caloric Value'].fillna(0) / (self.food_df['Caloric Value'].max() + 1e-6))
            fiber_boost = self.food_df['Dietary Fiber'].fillna(0) / (self.food_df['Dietary Fiber'].max() + 1e-6)
            protein_boost = self.food_df['Protein'].fillna(0) / (self.food_df['Protein'].max() + 1e-6)
            weighted_sims *= (1 + calorie_penalty * 0.4 + fiber_boost * 0.3 + protein_boost * 0.2)
        
        else:  # Maintien
            # Favoriser équilibre nutritionnel
            density_boost = self.food_df['Nutrition Density'].fillna(5) / 10
            weighted_sims *= (1 + density_boost * 0.3)
        
        return weighted_sims
    
    def recommend_foods(
        self, 
        target: NutritionalTarget,
        n_recommendations: int = 10,
        exclude_foods: Optional[List[str]] = None,
        min_protein: float = 0,
        max_calories: float = 1000
    ) -> pd.DataFrame:
        """
        Recommande des aliments basés sur le profil cible
        Pipeline ML complet
        
        Args:
            target: Objectifs nutritionnels
            n_recommendations: Nombre de recommandations
            exclude_foods: Aliments à exclure
            min_protein: Protéines minimum (g/100g)
            max_calories: Calories maximum (kcal/100g)
            
        Returns:
            DataFrame avec aliments recommandés et scores
        """
        # Créer profil cible
        target_profile = self._create_target_profile(target)
        
        # Calculer similarités cosine
        similarities = cosine_similarity(target_profile, self.features_scaled)[0]
        
        # Appliquer pondérations selon objectif
        weighted_similarities = self._apply_goal_weights(similarities, target.goal)
        
        # Filtrer selon critères
        mask = np.ones(len(self.food_df), dtype=bool)
        
        if exclude_foods:
            mask &= ~self.food_df['food'].isin(exclude_foods)
        
        mask &= self.food_df['Protein'] >= min_protein
        mask &= self.food_df['Caloric Value'] <= max_calories
        
        # Sélectionner top N
        filtered_indices = np.where(mask)[0]
        filtered_sims = weighted_similarities[filtered_indices]
        
        top_indices = filtered_indices[np.argsort(filtered_sims)[-n_recommendations:][::-1]]
        
        # Préparer résultats
        results = self.food_df.iloc[top_indices].copy()
        results['similarity_score'] = weighted_similarities[top_indices]
        results['match_percentage'] = (results['similarity_score'] / results['similarity_score'].max() * 100).round(1)
        
        return results.reset_index(drop=True)
    
    def find_alternatives(
        self,
        food_name: str,
        n_alternatives: int = 5,
        goal: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Trouve des alternatives à un aliment donné
        Basé sur similarité nutritionnelle
        
        Args:
            food_name: Nom de l'aliment
            n_alternatives: Nombre d'alternatives
            goal: Objectif (optionnel pour pondération)
            
        Returns:
            DataFrame avec alternatives similaires
        """
        # Trouver l'aliment
        food_match = self.food_df[self.food_df['food'].str.contains(food_name, case=False, na=False)]
        
        if food_match.empty:
            return pd.DataFrame()
        
        food_idx = food_match.index[0]
        food_features = self.features_scaled[food_idx].reshape(1, -1)
        
        # Calculer similarités
        similarities = cosine_similarity(food_features, self.features_scaled)[0]
        
        # Appliquer pondérations si objectif spécifié
        if goal:
            similarities = self._apply_goal_weights(similarities, goal)
        
        # Exclure l'aliment lui-même
        similarities[food_idx] = -1
        
        # Top alternatives
        top_indices = np.argsort(similarities)[-(n_alternatives+1):][::-1]
        top_indices = top_indices[top_indices != food_idx][:n_alternatives]
        
        results = self.food_df.iloc[top_indices].copy()
        results['similarity_score'] = similarities[top_indices]
        
        return results.reset_index(drop=True)


# ===== TESTS =====
def test_recommender():
    """Tests du moteur de recommandation"""
    print("=== TESTS DU MOTEUR DE RECOMMANDATION ===\n")
    
    # Créer dataset test
    test_data = pd.DataFrame({
        'food': ['Poulet grillé', 'Riz complet', 'Brocoli', 'Saumon', 'Œufs', 
                 'Quinoa', 'Avocat', 'Amandes', 'Yaourt grec', 'Banane'],
        'Caloric Value': [165, 370, 34, 208, 155, 368, 160, 579, 59, 89],
        'Protein': [31, 7.9, 2.8, 20, 13, 14, 2, 21, 10, 1.1],
        'Carbohydrates': [0, 77, 6.6, 0, 1.1, 64, 9, 22, 3.6, 23],
        'Fat': [3.6, 2.9, 0.4, 13, 11, 6, 15, 49, 0.4, 0.3],
        'Dietary Fiber': [0, 3.5, 2.6, 0, 0, 7, 7, 12, 0, 2.6],
        'Saturated Fats': [1.0, 0.6, 0.1, 3.0, 3.5, 0.7, 2.1, 3.8, 0.1, 0.1],
        'Sugars': [0, 0.8, 1.7, 0, 0.6, 0, 0.7, 4.4, 3.6, 12],
        'Sodium': [74, 7, 33, 59, 124, 7, 7, 1, 36, 1]
    })
    
    # Initialiser
    recommender = FoodRecommendationEngine(test_data)
    
    # Test 1: Recommandations perte de poids
    print("Test 1: Recommandations pour perte de poids")
    target_loss = NutritionalTarget(
        calories=500,
        proteins=40,
        carbs=50,
        fats=15,
        goal='Perte de poids'
    )
    
    recs_loss = recommender.recommend_foods(target_loss, n_recommendations=5)
    print(f"Top 5 aliments recommandés:")
    for idx, row in recs_loss.iterrows():
        print(f"  {idx+1}. {row['food']} - Match: {row['match_percentage']:.1f}%")
    print()
    
    # Test 2: Alternatives
    print("Test 2: Trouver alternatives au poulet")
    alternatives = recommender.find_alternatives('poulet', n_alternatives=3)
    print(f"Alternatives:")
    for idx, row in alternatives.iterrows():
        print(f"  {idx+1}. {row['food']}")
    print()
    
    # Validation
    assert len(recs_loss) <= 5, "Doit retourner max 5 recommandations"
    assert all(recs_loss['match_percentage'] <= 100), "Pourcentage <= 100"
    
    print("✅ Tous les tests passés!\n")


if __name__ == "__main__":
    test_recommender()