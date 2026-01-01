"""
Package modules pour FitLife Nutrition AI
Tous les modules IA développés localement
Auteurs: Asma Bélkahla & Monia Selleoui
"""

from .nutrition_calculator import NutritionalCalculator, UserProfile
from .food_recommender import FoodRecommendationEngine, NutritionalTarget
from .meal_plan_generator import MealPlanGenerator, MealPlanPreferences
from .nutrition_assistant import NutritionAssistant, ConversationContext

__version__ = '1.0.0'
__author__ = 'Asma Bélkahla & Monia Selleoui'

__all__ = [
    'NutritionalCalculator',
    'UserProfile',
    'FoodRecommendationEngine',
    'NutritionalTarget',
    'MealPlanGenerator',
    'MealPlanPreferences',
    'NutritionAssistant',
    'ConversationContext'
]