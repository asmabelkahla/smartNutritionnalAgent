from typing import Dict, Any, List
import pandas as pd
import random
from .user_profile import UserProfile


def generate_meal_plan(profile: UserProfile, nutrition_csv: str = "data/cleaned_nutrition_data.csv", days: int = 7) -> List[Dict[str, Any]]:
    """
    Generate a simple meal plan based on the user's dietary preferences.
    This is a lightweight heuristic planner: it samples foods from the nutrition CSV
    and groups them into breakfasts/lunches/dinners for the requested number of days.
    """
    try:
        df = pd.read_csv(nutrition_csv)
    except Exception:
        return []

    # Try to infer a sensible column for food name
    name_col = None
    for c in ("food", "name", "item", "description"):
        if c in df.columns:
            name_col = c
            break
    if name_col is None:
        name_col = df.columns[0]

    # Filter by dietary preferences if available
    prefs = (profile.dietary_preferences or "").lower()
    if prefs:
        mask = df.apply(lambda row: prefs in (str(row).lower()), axis=1)
        filtered = df[mask]
        if len(filtered) >= 3:
            df = filtered

    foods = df[name_col].astype(str).dropna().unique().tolist()
    random.shuffle(foods)

    plan: List[Dict[str, Any]] = []
    for day in range(days):
        day_meals = {
            "day": day + 1,
            "breakfast": foods[(day * 3) % max(1, len(foods))] if foods else "",
            "lunch": foods[(day * 3 + 1) % max(1, len(foods))] if foods else "",
            "dinner": foods[(day * 3 + 2) % max(1, len(foods))] if foods else "",
        }
        plan.append(day_meals)

    return plan
# src/meal_planner.py
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class MealPlanner:
    """Générateur de plans alimentaires personnalisés"""
    
    def __init__(self, nutrition_data: List[Dict], user_profile):
        self.nutrition_data = nutrition_data
        self.user_profile = user_profile
        
        # Catégoriser les aliments
        self.categorized_foods = self._categorize_foods()
        
        # Objectifs nutritionnels
        self.nutrition_goals = user_profile.calculate_macros()
    
    def _categorize_foods(self) -> Dict[str, List[Dict]]:
        """Catégorise les aliments par type"""
        categories = {
            'breakfast': [],
            'lunch_dinner': [],
            'snack': [],
            'protein': [],
            'vegetable': [],
            'fruit': [],
            'grain': [],
            'dairy': []
        }
        
        for food in self.nutrition_data:
            # Catégorie principale
            food_category = food.get('food_category', '').lower()
            food_name = food.get('food_name', '').lower()
            
            # Petit-déjeuner
            if any(word in food_name for word in ['oat', 'cereal', 'yogurt', 'milk', 'bread', 'egg']):
                categories['breakfast'].append(food)
            
            # Repas principaux
            if any(word in food_name for word in ['chicken', 'fish', 'meat', 'tofu', 'bean', 'lentil', 'rice', 'pasta']):
                categories['lunch_dinner'].append(food)
            
            # Snacks
            if any(word in food_name for word in ['nut', 'seed', 'fruit', 'bar', 'cracker']):
                categories['snack'].append(food)
            
            # Protéines
            protein = food.get('protein_g', 0)
            if protein > 10:
                categories['protein'].append(food)
            
            # Légumes
            if 'vegetable' in food_category or any(word in food_name for word in ['broccoli', 'spinach', 'carrot', 'salad']):
                categories['vegetable'].append(food)
            
            # Fruits
            if 'fruit' in food_category:
                categories['fruit'].append(food)
            
            # Céréales
            if any(word in food_category for word in ['grain', 'cereal']):
                categories['grain'].append(food)
            
            # Produits laitiers
            if any(word in food_category for word in ['dairy', 'cheese']):
                categories['dairy'].append(food)
        
        return categories
    
    def generate_weekly_plan(self) -> Dict:
        """Génère un plan alimentaire pour la semaine"""
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        weekly_plan = {}
        
        for day in days:
            daily_plan = self._generate_daily_plan()
            weekly_plan[day] = daily_plan
        
        return weekly_plan
    
    def _generate_daily_plan(self) -> Dict:
        """Génère un plan alimentaire pour une journée"""
        # Répartition des calories
        meal_distribution = {
            'breakfast': 0.25,  # 25% des calories
            'lunch': 0.35,      # 35% des calories
            'dinner': 0.30,     # 30% des calories
            'snacks': 0.10      # 10% des calories
        }
        
        daily_calories = self.nutrition_goals['calories']
        
        plan = {
            'breakfast': self._generate_meal('breakfast', daily_calories * meal_distribution['breakfast']),
            'lunch': self._generate_meal('lunch_dinner', daily_calories * meal_distribution['lunch']),
            'dinner': self._generate_meal('lunch_dinner', daily_calories * meal_distribution['dinner']),
            'snacks': self._generate_snacks(daily_calories * meal_distribution['snacks'])
        }
        
        # Calcul du total
        total = self._calculate_meal_totals(plan)
        plan['total'] = total
        plan['goals'] = self.nutrition_goals
        
        return plan
    
    def _generate_meal(self, meal_type: str, target_calories: float) -> Dict:
        """Génère un repas"""
        meal = {
            'name': f"{meal_type.capitalize()} équilibré",
            'foods': [],
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0
        }
        
        # Structure du repas
        meal_structure = {
            'breakfast': ['protein', 'grain', 'fruit', 'dairy'],
            'lunch_dinner': ['protein', 'vegetable', 'grain', 'vegetable']
        }
        
        structure = meal_structure.get(meal_type, ['protein', 'vegetable', 'grain'])
        
        for food_type in structure:
            available_foods = self.categorized_foods.get(food_type, [])
            
            if available_foods:
                # Filtrer selon les préférences alimentaires
                filtered_foods = self._filter_by_preferences(available_foods)
                
                if filtered_foods:
                    # Choisir un aliment aléatoire
                    selected_food = random.choice(filtered_foods)
                    
                    # Déterminer la portion
                    portion = self._calculate_portion(selected_food, food_type, target_calories)
                    
                    meal['foods'].append({
                        'name': selected_food['food_name'],
                        'category': food_type,
                        'portion_g': portion,
                        'calories': selected_food.get('calories_kcal', 0) * (portion / 100),
                        'protein_g': selected_food.get('protein_g', 0) * (portion / 100),
                        'carbs_g': selected_food.get('carbs_g', 0) * (portion / 100),
                        'fat_g': selected_food.get('fat_g', 0) * (portion / 100)
                    })
        
        # Mettre à jour les totaux
        meal.update(self._calculate_meal_totals({'temp': meal}))
        
        return meal
    
    def _generate_snacks(self, target_calories: float) -> List[Dict]:
        """Génère des collations"""
        snacks = []
        available_snacks = self.categorized_foods.get('snack', [])
        
        if not available_snacks:
            return snacks
        
        # 2-3 collations par jour
        num_snacks = random.randint(2, 3)
        calories_per_snack = target_calories / num_snacks
        
        for _ in range(num_snacks):
            filtered_snacks = self._filter_by_preferences(available_snacks)
            
            if filtered_snacks:
                selected_snack = random.choice(filtered_snacks)
                portion = self._calculate_portion(selected_snack, 'snack', calories_per_snack)
                
                snacks.append({
                    'name': selected_snack['food_name'],
                    'portion_g': portion,
                    'calories': selected_snack.get('calories_kcal', 0) * (portion / 100),
                    'protein_g': selected_snack.get('protein_g', 0) * (portion / 100)
                })
        
        return snacks
    
    def _filter_by_preferences(self, foods: List[Dict]) -> List[Dict]:
        """Filtre les aliments selon les préférences et allergies"""
        filtered = []
        
        for food in foods:
            food_name = food.get('food_name', '').lower()
            food_category = food.get('food_category', '').lower()
            
            # Vérifier les allergies
            skip = False
            for allergy in self.user_profile.allergies:
                if allergy.lower() in food_name or allergy.lower() in food_category:
                    skip = True
                    break
            
            if skip:
                continue
            
            # Vérifier les préférences alimentaires
            if 'vegetarian' in self.user_profile.dietary_preferences:
                if any(word in food_name for word in ['meat', 'chicken', 'fish', 'pork', 'beef']):
                    continue
            
            if 'vegan' in self.user_profile.dietary_preferences:
                if any(word in food_name for word in ['meat', 'dairy', 'cheese', 'milk', 'egg', 'honey']):
                    continue
            
            if 'gluten_free' in self.user_profile.dietary_preferences:
                if any(word in food_name for word in ['wheat', 'barley', 'rye', 'bread', 'pasta']):
                    continue
            
            filtered.append(food)
        
        return filtered
    
    def _calculate_portion(self, food: Dict, food_type: str, target_calories: float) -> float:
        """Calcule une portion appropriée"""
        calories_per_100g = food.get('calories_kcal', 100)
        
        # Portions types par catégorie
        base_portions = {
            'protein': 150,  # 150g pour les protéines
            'vegetable': 200,  # 200g pour les légumes
            'grain': 100,  # 100g pour les céréales
            'fruit': 150,  # 150g pour les fruits
            'dairy': 150,  # 150g pour les produits laitiers
            'snack': 50   # 50g pour les snacks
        }
        
        base_portion = base_portions.get(food_type, 100)
        
        # Ajuster selon les calories cibles
        max_calories_from_food = target_calories * 0.5  # Max 50% des calories cibles
        calculated_portion = (max_calories_from_food / calories_per_100g) * 100
        
        # Prendre le minimum entre portion type et calculée
        portion = min(base_portion, calculated_portion)
        
        return round(portion, 0)
    
    def _calculate_meal_totals(self, meal_data: Dict) -> Dict:
        """Calcule les totaux nutritionnels d'un repas"""
        totals = {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0
        }
        
        if 'foods' in meal_data:
            for food in meal_data['foods']:
                totals['total_calories'] += food.get('calories', 0)
                totals['total_protein'] += food.get('protein_g', 0)
                totals['total_carbs'] += food.get('carbs_g', 0)
                totals['total_fat'] += food.get('fat_g', 0)
        
        # Arrondir
        for key in totals:
            totals[key] = round(totals[key], 1)
        
        return totals
    
    def generate_shopping_list(self, weekly_plan: Dict) -> Dict:
        """Génère une liste de courses basée sur le plan hebdomadaire"""
        shopping_list = {}
        
        for day, daily_plan in weekly_plan.items():
            for meal_type, meal in daily_plan.items():
                if meal_type in ['breakfast', 'lunch', 'dinner'] and 'foods' in meal:
                    for food in meal['foods']:
                        food_name = food['name']
                        portion = food['portion_g']
                        
                        if food_name not in shopping_list:
                            shopping_list[food_name] = {
                                'category': food.get('category', 'other'),
                                'total_grams': 0,
                                'unit': 'g',
                                'days_used': []
                            }
                        
                        shopping_list[food_name]['total_grams'] += portion
                        shopping_list[food_name]['days_used'].append(day)
        
        # Convertir les grammes en unités plus pratiques
        for food_name, details in shopping_list.items():
            total_grams = details['total_grams']
            
            # Pour les fruits/légumes, convertir en pièces
            if details['category'] in ['fruit', 'vegetable']:
                avg_weight = 150  # Poids moyen d'un fruit/légume
                pieces = total_grams / avg_weight
                details['quantity'] = round(pieces, 1)
                details['unit'] = 'pièces'
            
            # Pour les céréales, convertir en tasses
            elif details['category'] == 'grain':
                cups = total_grams / 200  # ~200g par tasse
                details['quantity'] = round(cups, 1)
                details['unit'] = 'tasses'
            
            # Pour les protéines, convertir en portions
            elif details['category'] == 'protein':
                portions = total_grams / 150  # 150g par portion
                details['quantity'] = round(portions, 1)
                details['unit'] = 'portions'
            
            else:
                details['quantity'] = round(total_grams / 100, 1)
                details['unit'] = 'x100g'
            
            # Supprimer les grammes totaux
            del details['total_grams']
        
        # Trier par catégorie
        sorted_list = {}
        categories = ['fruit', 'vegetable', 'protein', 'grain', 'dairy', 'snack', 'other']
        
        for category in categories:
            category_items = {k: v for k, v in shopping_list.items() if v['category'] == category}
            if category_items:
                sorted_list[category] = category_items
        
        return sorted_list