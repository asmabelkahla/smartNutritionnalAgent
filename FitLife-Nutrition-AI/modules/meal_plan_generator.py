"""
Module 3: Générateur de Plans Alimentaires
Système basé sur des règles et optimisation
Auteurs: Asma Bélkahla & Monia Selleoui
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random

@dataclass
class MealPlanPreferences:
    """Préférences utilisateur pour la génération de plan"""
    meals_per_day: int = 4
    variety_days: int = 7
    budget: str = 'Moyen'  # 'Économique', 'Moyen', 'Élevé'
    prep_time: str = 'Moyen'  # 'Rapide', 'Moyen', 'Élaboré'
    diet_type: List[str] = field(default_factory=lambda: ['Omnivore'])
    exclude_foods: List[str] = field(default_factory=list)

class MealPlanGenerator:
    """
    Générateur de plans alimentaires sans API externe
    Utilise: règles nutritionnelles, templates, randomisation intelligente
    
    Architecture:
    1. Catégorisation aliments: par macros et type
    2. Templates repas: structures prédéfinies
    3. Sélection intelligente: via moteur de reco
    4. Calcul portions: ajustement pour cibles
    5. Optimisation variété: évite répétitions
    """
    
    MEAL_NAMES = [
        'Petit-déjeuner', 'Collation matinale', 'Déjeuner', 
        'Collation', 'Dîner', 'Collation du soir'
    ]
    
    MEAL_CALORIE_RATIOS = {
        'Petit-déjeuner': 0.25,
        'Collation matinale': 0.10,
        'Déjeuner': 0.30,
        'Collation': 0.10,
        'Dîner': 0.25,
        'Collation du soir': 0.10
    }
    
    MEAL_TEMPLATES = {
        'Petit-déjeuner': {
            'structure': ['protéine', 'glucide', 'fruit', 'boisson'],
            'portions': [0.4, 0.4, 0.15, 0.05]
        },
        'Déjeuner': {
            'structure': ['protéine', 'féculent', 'légume', 'matière grasse'],
            'portions': [0.40, 0.30, 0.25, 0.05]
        },
        'Collation': {
            'structure': ['protéine', 'fruit/oléagineux'],
            'portions': [0.6, 0.4]
        },
        'Dîner': {
            'structure': ['protéine', 'légume', 'féculent', 'matière grasse'],
            'portions': [0.35, 0.35, 0.25, 0.05]
        }
    }
    
    def __init__(self, food_df: pd.DataFrame, recommender):
        self.food_df = food_df
        self.recommender = recommender
        self._categorize_foods()
    
    def _categorize_foods(self):
        """Catégorise les aliments par type nutritionnel"""
        self.categories = {
            'protéine': [],
            'glucide': [],
            'légume': [],
            'fruit': [],
            'féculent': [],
            'matière grasse': [],
            'boisson': [],
            'fruit/oléagineux': []
        }
        
        # Catégorisation basée sur les macros
        for idx, row in self.food_df.iterrows():
            food_name = row['food']
            
            # Protéines (>15g/100g)
            if row['Protein'] > 15:
                self.categories['protéine'].append(food_name)
            
            # Féculents (>50g glucides ET >2g fibres)
            if row['Carbohydrates'] > 50 and row['Dietary Fiber'] > 2:
                self.categories['féculent'].append(food_name)
                self.categories['glucide'].append(food_name)
            
            # Légumes (<50 kcal ET <10g glucides)
            if row['Caloric Value'] < 50 and row['Carbohydrates'] < 10:
                self.categories['légume'].append(food_name)
            
            # Fruits (>8g sucres ET >1.5g fibres)
            if row['Sugars'] > 8 and row['Dietary Fiber'] > 1.5:
                self.categories['fruit'].append(food_name)
                self.categories['fruit/oléagineux'].append(food_name)
            
            # Matières grasses (>40g lipides/100g)
            if row['Fat'] > 40:
                self.categories['matière grasse'].append(food_name)
                self.categories['fruit/oléagineux'].append(food_name)
            
            # Glucides généraux (>20g glucides)
            if row['Carbohydrates'] > 20:
                self.categories['glucide'].append(food_name)
    
    def _select_food_for_slot(
        self,
        category: str,
        calorie_target: float,
        macro_target: Dict[str, float],
        used_foods: List[str],
        goal: str
    ) -> Tuple[str, float]:
        """
        Sélectionne un aliment pour un slot du repas
        Utilise le moteur de recommandation
        
        Args:
            category: Catégorie d'aliment recherchée
            calorie_target: Calories cibles pour ce slot
            macro_target: Macros cibles
            used_foods: Aliments déjà utilisés (pour variété)
            goal: Objectif utilisateur
            
        Returns:
            Tuple (nom_aliment, portion_grammes)
        """
        # Import du NutritionalTarget
        try:
            from food_recommender import NutritionalTarget
        except:
            from dataclasses import dataclass
            @dataclass
            class NutritionalTarget:
                calories: float
                proteins: float
                carbs: float
                fats: float
                goal: str
        
        target = NutritionalTarget(
            calories=calorie_target,
            proteins=macro_target.get('proteins', 20),
            carbs=macro_target.get('carbs', 50),
            fats=macro_target.get('fats', 15),
            goal=goal
        )
        
        # Obtenir recommandations
        recommendations = self.recommender.recommend_foods(
            target, 
            n_recommendations=20,
            exclude_foods=used_foods
        )
        
        # Filtrer par catégorie si disponible
        if self.categories.get(category) and self.categories[category]:
            cat_foods = recommendations[
                recommendations['food'].isin(self.categories[category])
            ]
            if not cat_foods.empty:
                recommendations = cat_foods
        
        if recommendations.empty:
            return None, 0
        
        # Sélectionner aléatoirement parmi les top 5 (variété)
        top_foods = recommendations.head(5)
        selected = top_foods.sample(n=1).iloc[0]
        
        # Calculer portion appropriée
        if selected['Caloric Value'] > 0:
            portion = min(250, (calorie_target / selected['Caloric Value']) * 100)
        else:
            portion = 100
        
        return selected['food'], portion
    
    def _generate_meal(
        self,
        meal_name: str,
        calorie_target: float,
        macro_targets: Dict[str, float],
        goal: str,
        used_foods_today: List[str]
    ) -> Dict:
        """
        Génère un repas complet selon template
        
        Args:
            meal_name: Nom du repas
            calorie_target: Calories cibles
            macro_targets: Macros cibles
            goal: Objectif
            used_foods_today: Aliments déjà utilisés aujourd'hui
            
        Returns:
            Dict avec composition complète du repas
        """
        # Obtenir le template approprié
        if meal_name in ['Collation matinale', 'Collation', 'Collation du soir']:
            template = self.MEAL_TEMPLATES['Collation']
        else:
            template = self.MEAL_TEMPLATES.get(meal_name, self.MEAL_TEMPLATES['Déjeuner'])
        
        meal = {
            'nom': meal_name,
            'aliments': [],
            'portions': [],
            'calories': 0,
            'proteines': 0,
            'glucides': 0,
            'lipides': 0,
            'description': []
        }
        
        structure = template['structure']
        portions_ratio = template['portions']
        
        # Pour chaque élément de la structure
        for i, category in enumerate(structure):
            slot_calories = calorie_target * portions_ratio[i]
            
            slot_macros = {
                'proteins': macro_targets['proteins'] * portions_ratio[i],
                'carbs': macro_targets['carbs'] * portions_ratio[i],
                'fats': macro_targets['fats'] * portions_ratio[i]
            }
            
            food, portion = self._select_food_for_slot(
                category,
                slot_calories,
                slot_macros,
                used_foods_today,
                goal
            )
            
            if food:
                # Récupérer les données nutritionnelles
                food_data = self.food_df[self.food_df['food'] == food].iloc[0]
                
                # Calculer apport
                factor = portion / 100
                meal['aliments'].append(food)
                meal['portions'].append(portion)
                meal['calories'] += food_data['Caloric Value'] * factor
                meal['proteines'] += food_data['Protein'] * factor
                meal['glucides'] += food_data['Carbohydrates'] * factor
                meal['lipides'] += food_data['Fat'] * factor
                
                meal['description'].append(f"{food} ({portion:.0f}g)")
                used_foods_today.append(food)
        
        return meal
    
    def generate_day_plan(
        self,
        day_name: str,
        nutritional_needs: Dict,
        preferences: MealPlanPreferences,
        used_foods_week: List[str] = None
    ) -> Dict[str, Dict]:
        """
        Génère un plan pour une journée complète
        
        Args:
            day_name: Nom du jour
            nutritional_needs: Besoins nutritionnels
            preferences: Préférences utilisateur
            used_foods_week: Aliments utilisés cette semaine
            
        Returns:
            Dict avec tous les repas du jour
        """
        if used_foods_week is None:
            used_foods_week = []
        
        day_plan = {}
        used_foods_today = []
        
        # Sélectionner les repas selon préférence
        meal_names = self.MEAL_NAMES[:preferences.meals_per_day]
        
        # Calculer les cibles par repas
        total_calories = nutritional_needs['target_calories']
        total_proteins = nutritional_needs['macros']['proteins']
        total_carbs = nutritional_needs['macros']['carbs']
        total_fats = nutritional_needs['macros']['fats']
        goal = nutritional_needs.get('goal', 'Maintien')
        
        for meal_name in meal_names:
            ratio = self.MEAL_CALORIE_RATIOS.get(meal_name, 0.25)
            
            meal_targets = {
                'calories': total_calories * ratio,
                'proteins': total_proteins * ratio,
                'carbs': total_carbs * ratio,
                'fats': total_fats * ratio
            }
            
            meal = self._generate_meal(
                meal_name,
                meal_targets['calories'],
                meal_targets,
                goal,
                used_foods_today
            )
            
            day_plan[meal_name] = meal
        
        return day_plan
    
    def generate_week_plan(
        self,
        nutritional_needs: Dict,
        preferences: MealPlanPreferences
    ) -> Dict[str, Dict]:
        """
        Génère un plan complet pour la semaine
        
        Args:
            nutritional_needs: Besoins nutritionnels
            preferences: Préférences utilisateur
            
        Returns:
            Dict avec plan complet de la semaine
        """
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        week_plan = {}
        used_foods_week = []
        
        for i in range(preferences.variety_days):
            day_name = days[i]
            day_plan = self.generate_day_plan(
                day_name,
                nutritional_needs,
                preferences,
                used_foods_week
            )
            week_plan[day_name] = day_plan
            
            # Ajouter les aliments utilisés
            for meal in day_plan.values():
                used_foods_week.extend(meal['aliments'])
        
        return week_plan
    
    def format_plan_for_display(self, week_plan: Dict) -> Dict:
        """
        Formate le plan pour l'affichage (compatible Streamlit)
        
        Args:
            week_plan: Plan brut généré
            
        Returns:
            Plan formaté pour affichage
        """
        formatted = {}
        
        for day, meals in week_plan.items():
            formatted[day] = {}
            for meal_name, meal_data in meals.items():
                formatted[day][meal_name] = {
                    'aliments': meal_data['description'],
                    'calories': int(meal_data['calories']),
                    'proteines': int(meal_data['proteines']),
                    'glucides': int(meal_data['glucides']),
                    'lipides': int(meal_data['lipides'])
                }
        
        return formatted
    
    def calculate_plan_stats(self, week_plan: Dict) -> Dict:
        """
        Calcule les statistiques du plan hebdomadaire
        
        Args:
            week_plan: Plan de la semaine
            
        Returns:
            Dict avec statistiques agrégées
        """
        total_calories = 0
        total_proteins = 0
        total_carbs = 0
        total_fats = 0
        unique_foods = set()
        
        for day_meals in week_plan.values():
            for meal in day_meals.values():
                total_calories += meal['calories']
                total_proteins += meal['proteines']
                total_carbs += meal['glucides']
                total_fats += meal['lipides']
                unique_foods.update(meal['aliments'])
        
        num_days = len(week_plan)
        
        return {
            'avg_daily_calories': total_calories / num_days,
            'avg_daily_proteins': total_proteins / num_days,
            'avg_daily_carbs': total_carbs / num_days,
            'avg_daily_fats': total_fats / num_days,
            'unique_foods_count': len(unique_foods),
            'variety_score': len(unique_foods) / (num_days * 4) * 100  # % de variété
        }


# ===== TESTS =====
def test_meal_plan_generator():
    """Tests du générateur de plans"""
    print("=== TESTS DU GÉNÉRATEUR DE PLANS ALIMENTAIRES ===\n")
    
    # Créer dataset test
    test_data = pd.DataFrame({
        'food': [
            'Poulet grillé', 'Riz complet', 'Brocoli', 'Saumon', 'Œufs',
            'Quinoa', 'Avocat', 'Amandes', 'Yaourt grec', 'Banane',
            'Épinards', 'Patate douce', 'Tofu', 'Lentilles', 'Pomme'
        ],
        'Caloric Value': [165, 370, 34, 208, 155, 368, 160, 579, 59, 89, 23, 86, 76, 116, 52],
        'Protein': [31, 7.9, 2.8, 20, 13, 14, 2, 21, 10, 1.1, 2.9, 1.6, 8, 9, 0.3],
        'Carbohydrates': [0, 77, 6.6, 0, 1.1, 64, 9, 22, 3.6, 23, 3.6, 20, 1.9, 20, 14],
        'Fat': [3.6, 2.9, 0.4, 13, 11, 6, 15, 49, 0.4, 0.3, 0.4, 0.1, 5, 0.4, 0.2],
        'Dietary Fiber': [0, 3.5, 2.6, 0, 0, 7, 7, 12, 0, 2.6, 2.2, 3, 0.3, 7.9, 2.4],
        'Saturated Fats': [1, 0.6, 0.1, 3, 3.5, 0.7, 2.1, 3.8, 0.1, 0.1, 0.1, 0, 0.7, 0.1, 0],
        'Sugars': [0, 0.8, 1.7, 0, 0.6, 0, 0.7, 4.4, 3.6, 12, 0.4, 4.2, 0.6, 1.8, 10],
        'Sodium': [74, 7, 33, 59, 124, 7, 7, 1, 36, 1, 79, 55, 7, 2, 1]
    })
    
    # Initialiser
    try:
        from food_recommender import FoodRecommendationEngine
    except:
        print("⚠️ Module food_recommender non trouvé")
        return
    
    recommender = FoodRecommendationEngine(test_data)
    generator = MealPlanGenerator(test_data, recommender)
    
    # Test 1: Générer une journée
    print("Test 1: Génération d'une journée complète")
    nutritional_needs = {
        'target_calories': 2000,
        'macros': {'proteins': 150, 'carbs': 200, 'fats': 65},
        'goal': 'Maintien'
    }
    
    preferences = MealPlanPreferences(meals_per_day=4, variety_days=3)
    
    day_plan = generator.generate_day_plan(
        'Lundi',
        nutritional_needs,
        preferences
    )
    
    total_cal = sum(m['calories'] for m in day_plan.values())
    
    print(f"Journée générée avec {len(day_plan)} repas")
    print(f"Total calories: {total_cal:.0f} kcal")
    print()
    
    # Test 2: Générer semaine
    print("Test 2: Génération d'un plan de 3 jours")
    week_plan = generator.generate_week_plan(nutritional_needs, preferences)
    
    stats = generator.calculate_plan_stats(week_plan)
    
    print(f"Plan généré pour {len(week_plan)} jours")
    print(f"Calories moyennes: {stats['avg_daily_calories']:.0f} kcal")
    print(f"Aliments uniques: {stats['unique_foods_count']}")
    print(f"Variété: {stats['variety_score']:.1f}%")
    print()
    
    # Validation
    assert len(day_plan) == preferences.meals_per_day
    assert 1800 <= total_cal <= 2200
    
    print("✅ Tous les tests passés!\n")


if __name__ == "__main__":
    test_meal_plan_generator()