
from typing import Dict, List

class ContextAugmenter:
    """Classe pour enrichir et structurer le contexte pour le LLM"""
    
    def __init__(self):
        self.templates = {
            'comparison': self._comparison_template,
            'recommendation': self._recommendation_template,
            'analysis': self._analysis_template,
            'simple': self._simple_template
        }
    
    def detect_query_type(self, query):
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['comparer', 'différence', 'vs', 'versus']):
            return 'comparison'
        elif any(word in query_lower for word in ['recommand', 'suggère', 'conseil', 'meilleur']):
            return 'recommendation'
        elif any(word in query_lower for word in ['analyse', 'détaillé', 'complet', 'expert']):
            return 'analysis'
        else:
            return 'simple'
    
    def augment_context(self, query, retrieved_foods, query_type=None):
        print("🎭 Étape 5: Augmentation du contexte...")
        
        if query_type is None:
            query_type = self.detect_query_type(query)
        print(f"   ✓ Type de requête détecté: {query_type}")
        
        template_func = self.templates.get(query_type, self._simple_template)
        context = template_func(query, retrieved_foods)
        
        print(f"   ✓ Contexte généré ({len(context.split())} mots)")
        return context
    
    def _simple_template(self, query, foods):
        context_lines = [
            f"QUESTION: {query}",
            "",
            "INFORMATIONS NUTRITIONNELLES DISPONIBLES:",
            ""
        ]
        
        for i, (_, food) in enumerate(foods.iterrows()):
            context_lines.append(f"{i+1}. {food['food_name']}")
            context_lines.append(f"   Catégorie: {food.get('food_category', 'N/A')}")
            context_lines.append(f"   Calories: {food.get('calories_kcal', 0)} kcal")
            context_lines.append(f"   Protéines: {food.get('protein_g', 0)}g")
            context_lines.append(f"   Glucides: {food.get('carbs_g', 0)}g")
            context_lines.append(f"   Lipides: {food.get('fat_g', 0)}g")
            if 'health_score' in food:
                context_lines.append(f"   Score santé: {food['health_score']:.1f}")
            context_lines.append("")
        
        return "\\n".join(context_lines)
    
    def _comparison_template(self, query, foods):
        context_lines = [
            f"QUESTION DE COMPARAISON: {query}",
            "",
            "ALIMENTS À COMPARER:",
            ""
        ]
        
        headers = ["Aliment", "Calories", "Protéines", "Glucides", "Lipides", "Score Santé"]
        context_lines.append(" | ".join(headers))
        context_lines.append("-" * 60)
        
        for _, food in foods.iterrows():
            row = [
                food['food_name'][:20],
                f"{food.get('calories_kcal', 0)}",
                f"{food.get('protein_g', 0)}g",
                f"{food.get('carbs_g', 0)}g",
                f"{food.get('fat_g', 0)}g",
                f"{food.get('health_score', 0):.1f}" if 'health_score' in food else "N/A"
            ]
            context_lines.append(" | ".join(row))
        
        context_lines.append("")
        context_lines.append("CONTEXTE SUPPLÉMENTAIRE:")
        
        if len(foods) >= 2:
            max_protein = foods.loc[foods['protein_g'].idxmax()]
            min_calories = foods.loc[foods['calories_kcal'].idxmin()]
            
            context_lines.append(f"- Le plus protéiné: {max_protein['food_name']} ({max_protein['protein_g']}g)")
            context_lines.append(f"- Le moins calorique: {min_calories['food_name']} ({min_calories['calories_kcal']} kcal)")
        
        return "\\n".join(context_lines)
    
    def _recommendation_template(self, query, foods):
        context_lines = [
            f"DEMANDE DE RECOMMANDATION: {query}",
            "",
            "OPTIONS DISPONIBLES (triées par pertinence):",
            ""
        ]
        
        foods_with_rec = foods.copy()
        
        if 'health_score' in foods.columns and 'calories_kcal' in foods.columns:
            foods_with_rec['recommendation_score'] = (
                0.4 * (foods['health_score'] / 100) +
                0.3 * (1 / (foods['calories_kcal'].clip(lower=1) ** 0.3)) +
                0.3 * foods['similarity_score']
            )
            foods_with_rec = foods_with_rec.sort_values('recommendation_score', ascending=False)
        
        for i, (_, food) in enumerate(foods_with_rec.iterrows()):
            stars = "⭐" * min(5, int((i / len(foods_with_rec)) * 5) + 1)
            
            context_lines.append(f"{stars} {food['food_name']}")
            context_lines.append(f"   ✓ Calories: {food.get('calories_kcal', 0)} kcal")
            context_lines.append(f"   ✓ Bilan nutritionnel: {self._get_nutrition_summary(food)}")
            
            if 'health_score' in food:
                if food['health_score'] > 70:
                    context_lines.append(f"   ✓ Excellent choix santé")
                elif food['health_score'] > 50:
                    context_lines.append(f"   ✓ Bon choix modéré")
            
            context_lines.append("")
        
        return "\\n".join(context_lines)
    
    def _analysis_template(self, query, foods):
        context_lines = [
            f"DEMANDE D'ANALYSE DÉTAILLÉE: {query}",
            "",
            "INFORMATIONS NUTRITIONNELLES POUR ANALYSE:",
            ""
        ]
        
        for i, (_, food) in enumerate(foods.iterrows()):
            context_lines.append(f"--- Aliment {i+1}: {food['food_name']} ---")
            context_lines.append(f"  • Catégorie: {food.get('food_category', 'N/A')}")
            context_lines.append(f"  • Description complète: {food['food_description']}")
            if 'health_score' in food:
                context_lines.append(f"  • Score santé: {food['health_score']:.1f}/100")
            if 'nutrient_density_score' in food:
                context_lines.append(f"  • Densité nutritionnelle: {food['nutrient_density_score']:.2f}")
            context_lines.append("")
        
        context_lines.append("INSTRUCTIONS POUR L'ANALYSE:")
        context_lines.append("Veuillez analyser les aliments ci-dessus en profondeur, en mettant en évidence les aspects nutritionnels clés, les avantages ou inconvénients, et en les reliant à la requête de l'utilisateur.")
        
        return "\\n".join(context_lines)
    
    def _get_nutrition_summary(self, food):
        protein = food.get('protein_g', 0)
        carbs = food.get('carbs_g', 0)
        fat = food.get('fat_g', 0)
        
        if protein > 20:
            protein_desc = "riche en protéines"
        elif protein > 10:
            protein_desc = "bonne source de protéines"
        else:
            protein_desc = "faible en protéines"
        
        if carbs < 5:
            carbs_desc = "faible en glucides"
        elif carbs > 30:
            carbs_desc = "riche en glucides"
        else:
            carbs_desc = "glucides modérés"
        
        return f"{protein_desc}, {carbs_desc}"
