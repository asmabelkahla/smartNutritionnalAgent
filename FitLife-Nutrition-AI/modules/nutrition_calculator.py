"""
Module 1: Calculateur Nutritionnel
Calculs des besoins caloriques et macronutriments
Auteurs: Asma Bélkahla & Monia Selleoui
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class UserProfile:
    """Profil utilisateur pour calculs nutritionnels"""
    weight: float  # kg
    height: float  # cm
    age: int
    sex: str  # 'Homme' ou 'Femme'
    activity_level: str
    goal: str  # 'Perte de poids', 'Maintien', 'Prise de masse'
    target_weight: float

class NutritionalCalculator:
    """
    Calculateur basé sur des formules scientifiques validées
    - Formule Mifflin-St Jeor pour BMR
    - Facteurs d'activité Harris-Benedict
    - Recommandations macronutriments basées sur recherche scientifique
    """
    
    ACTIVITY_FACTORS = {
        'Sédentaire': 1.2,
        'Légèrement actif': 1.375,
        'Modérément actif': 1.55,
        'Très actif': 1.725,
        'Extrêmement actif': 1.9
    }
    
    GOAL_ADJUSTMENTS = {
        'Perte de poids': 0.85,  # -15% pour perte contrôlée
        'Maintien': 1.0,
        'Prise de masse': 1.15   # +15% pour gain musculaire
    }
    
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, sex: str) -> float:
        """
        Calcul du métabolisme de base (formule Mifflin-St Jeor)
        Plus précise que Harris-Benedict pour populations modernes
        
        Args:
            weight: Poids en kg
            height: Taille en cm
            age: Âge en années
            sex: 'Homme' ou 'Femme'
            
        Returns:
            BMR en kcal/jour
        """
        if sex == 'Homme':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calcul de la dépense énergétique totale quotidienne
        
        Args:
            bmr: Métabolisme de base
            activity_level: Niveau d'activité
            
        Returns:
            TDEE en kcal/jour
        """
        factor = NutritionalCalculator.ACTIVITY_FACTORS.get(activity_level, 1.2)
        return round(bmr * factor, 2)
    
    @staticmethod
    def calculate_target_calories(tdee: float, goal: str) -> float:
        """
        Ajustement des calories selon l'objectif
        
        Args:
            tdee: Dépense énergétique totale
            goal: Objectif ('Perte de poids', 'Maintien', 'Prise de masse')
            
        Returns:
            Calories cibles en kcal/jour
        """
        adjustment = NutritionalCalculator.GOAL_ADJUSTMENTS.get(goal, 1.0)
        return round(tdee * adjustment, 2)
    
    @staticmethod
    def calculate_macros(calories: float, weight: float, goal: str) -> Dict[str, float]:
        """
        Calcul de la répartition des macronutriments
        Basé sur les recommandations scientifiques actuelles
        
        Stratégie:
        - Protéines: priorité selon objectif (préservation/construction musculaire)
        - Lipides: 25-30% des calories (fonctions hormonales)
        - Glucides: reste des calories (énergie)
        
        Args:
            calories: Calories cibles
            weight: Poids en kg
            goal: Objectif
            
        Returns:
            Dict avec grammes et pourcentages de chaque macro
        """
        # Protéines: priorité selon objectif
        if goal == 'Prise de masse':
            proteins_g = weight * 2.0  # 2g/kg pour hypertrophie
        elif goal == 'Perte de poids':
            proteins_g = weight * 2.0  # Maintenir masse musculaire
        else:
            proteins_g = weight * 1.8
        
        proteins_cal = proteins_g * 4  # 4 kcal/g
        
        # Lipides: 27% des calories (optimal pour hormones)
        fats_cal = calories * 0.27
        fats_g = fats_cal / 9  # 9 kcal/g
        
        # Glucides: reste des calories
        carbs_cal = calories - proteins_cal - fats_cal
        carbs_g = carbs_cal / 4  # 4 kcal/g
        
        return {
            'proteins': round(proteins_g, 1),
            'carbs': round(max(0, carbs_g), 1),  # Éviter valeurs négatives
            'fats': round(fats_g, 1),
            'proteins_cal': round(proteins_cal, 1),
            'carbs_cal': round(max(0, carbs_cal), 1),
            'fats_cal': round(fats_cal, 1),
            'proteins_pct': round((proteins_cal / calories) * 100, 1),
            'carbs_pct': round((max(0, carbs_cal) / calories) * 100, 1),
            'fats_pct': round((fats_cal / calories) * 100, 1)
        }
    
    @staticmethod
    def estimate_duration(current_weight: float, target_weight: float, goal: str) -> Tuple[float, str]:
        """
        Estimation de la durée pour atteindre l'objectif
        Basé sur taux de changement sains recommandés
        
        Args:
            current_weight: Poids actuel
            target_weight: Poids cible
            goal: Objectif
            
        Returns:
            Tuple (nombre_semaines, message_explicatif)
        """
        weight_diff = abs(current_weight - target_weight)
        
        if weight_diff < 0.5:
            return 0, "Vous êtes déjà à votre poids cible!"
        
        if goal == 'Perte de poids':
            # Perte recommandée: 0.5-1kg/semaine (0.75kg moyenne)
            # Taux sain et durable
            weeks = weight_diff / 0.75
            message = f"Perte recommandée: 0.75kg/semaine (sain et durable)"
        elif goal == 'Prise de masse':
            # Gain recommandé: 0.25-0.5kg/semaine (0.375kg moyenne)
            # Minimise gain de graisse
            weeks = weight_diff / 0.375
            message = f"Gain recommandé: 0.375kg/semaine (muscle > graisse)"
        else:
            return 0, "Objectif de maintien - pas de durée estimée"
        
        return round(weeks, 1), message
    
    @staticmethod
    def calculate_water_needs(weight: float, activity_level: str) -> float:
        """
        Calcul des besoins en eau (litres/jour)
        Formule: 33ml/kg ajusté selon activité
        
        Args:
            weight: Poids en kg
            activity_level: Niveau d'activité
            
        Returns:
            Litres d'eau recommandés par jour
        """
        base_water = weight * 0.033  # 33ml/kg
        
        # Ajustement selon activité
        if 'actif' in activity_level.lower():
            base_water *= 1.2
        if 'très' in activity_level.lower() or 'extrêmement' in activity_level.lower():
            base_water *= 1.3
            
        return round(base_water, 1)
    
    @staticmethod
    def calculate_complete_needs(profile: UserProfile) -> Dict:
        """
        Calcul complet de tous les besoins nutritionnels
        Point d'entrée principal du module
        
        Args:
            profile: Profil utilisateur complet
            
        Returns:
            Dict avec tous les besoins calculés
        """
        # 1. Métabolisme de base
        bmr = NutritionalCalculator.calculate_bmr(
            profile.weight, profile.height, profile.age, profile.sex
        )
        
        # 2. Dépense énergétique totale
        tdee = NutritionalCalculator.calculate_tdee(bmr, profile.activity_level)
        
        # 3. Calories cibles ajustées
        target_calories = NutritionalCalculator.calculate_target_calories(
            tdee, profile.goal
        )
        
        # 4. Répartition macronutriments
        macros = NutritionalCalculator.calculate_macros(
            target_calories, profile.weight, profile.goal
        )
        
        # 5. Estimation durée
        duration, duration_msg = NutritionalCalculator.estimate_duration(
            profile.weight, profile.target_weight, profile.goal
        )
        
        # 6. Besoins en eau
        water = NutritionalCalculator.calculate_water_needs(
            profile.weight, profile.activity_level
        )
        
        return {
            'bmr': bmr,
            'tdee': tdee,
            'target_calories': target_calories,
            'macros': macros,
            'duration_weeks': duration,
            'duration_message': duration_msg,
            'water_liters': water,
            'deficit_surplus': target_calories - tdee
        }


# ===== TESTS =====
def test_calculator():
    """Tests unitaires du calculateur"""
    print("=== TESTS DU CALCULATEUR NUTRITIONNEL ===\n")
    
    # Test 1: Homme, perte de poids
    profile1 = UserProfile(
        weight=85,
        height=175,
        age=30,
        sex='Homme',
        activity_level='Modérément actif',
        goal='Perte de poids',
        target_weight=75
    )
    
    results1 = NutritionalCalculator.calculate_complete_needs(profile1)
    
    print("Test 1 - Homme, 85kg, Perte de poids:")
    print(f"BMR: {results1['bmr']} kcal")
    print(f"TDEE: {results1['tdee']} kcal")
    print(f"Calories cible: {results1['target_calories']} kcal")
    print(f"Protéines: {results1['macros']['proteins']}g ({results1['macros']['proteins_pct']}%)")
    print(f"Glucides: {results1['macros']['carbs']}g ({results1['macros']['carbs_pct']}%)")
    print(f"Lipides: {results1['macros']['fats']}g ({results1['macros']['fats_pct']}%)")
    print(f"Durée estimée: {results1['duration_weeks']} semaines")
    print(f"Eau: {results1['water_liters']} litres/jour")
    print(f"Déficit: {results1['deficit_surplus']} kcal\n")
    
    # Test 2: Femme, prise de masse
    profile2 = UserProfile(
        weight=58,
        height=165,
        age=25,
        sex='Femme',
        activity_level='Très actif',
        goal='Prise de masse',
        target_weight=62
    )
    
    results2 = NutritionalCalculator.calculate_complete_needs(profile2)
    
    print("Test 2 - Femme, 58kg, Prise de masse:")
    print(f"BMR: {results2['bmr']} kcal")
    print(f"TDEE: {results2['tdee']} kcal")
    print(f"Calories cible: {results2['target_calories']} kcal")
    print(f"Protéines: {results2['macros']['proteins']}g")
    print(f"Durée estimée: {results2['duration_weeks']} semaines")
    print(f"Surplus: {results2['deficit_surplus']} kcal\n")
    
    # Validation
    assert results1['bmr'] > 0, "BMR doit être positif"
    assert results1['target_calories'] < results1['tdee'], "Déficit pour perte"
    assert results2['target_calories'] > results2['tdee'], "Surplus pour prise"
    assert results1['macros']['proteins'] > 0, "Protéines doivent être positives"
    
    print("✅ Tous les tests passés!\n")


if __name__ == "__main__":
    test_calculator()