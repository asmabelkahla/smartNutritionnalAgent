
import pandas as pd
import numpy as np
from typing import Dict, Optional

class NutritionRetriever:
    """Classe intelligente pour récupérer les aliments pertinents"""
    
    def __init__(self, df, embedder, indexer):
        self.df = df
        self.embedder = embedder
        self.indexer = indexer
        self.query_cache = {}
    
    def retrieve(self, query, k=10, filters=None, use_cache=True):
        print(f"🔍 Étape 4: Recherche pour '{query}'...")
        
        cache_key = f"{query}_{k}_{str(filters)}"
        if use_cache and cache_key in self.query_cache:
            print("   ✓ Résultats récupérés depuis le cache")
            return self.query_cache[cache_key]
        
        query_embedding = self.embedder.create_query_embedding(query)
        indices, similarities = self.indexer.search(query_embedding, k * 3)
        
        results = self.df.iloc[indices].copy()
        results['similarity_score'] = similarities
        
        if filters:
            results = self._apply_filters(results, filters)
        
        results = results.sort_values('similarity_score', ascending=False).head(k)
        results = self._calculate_additional_scores(results, query)
        
        if use_cache:
            self.query_cache[cache_key] = results
        
        print(f"   ✓ {len(results)} aliments trouvés")
        print(f"   ✓ Score de similarité: {results['similarity_score'].iloc[0]:.3f}")
        return results
    
    def _apply_filters(self, results, filters):
        filtered = results.copy()
        for key, value in filters.items():
            if key in filtered.columns:
                if isinstance(value, list):
                    filtered = filtered[filtered[key].isin(value)]
                elif callable(value):
                    filtered = filtered[filtered[key].apply(value)]
                else:
                    filtered = filtered[filtered[key] == value]
        return filtered
    
    def _calculate_additional_scores(self, results, query):
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['protéine', 'protein', 'muscle']):
            results['protein_score'] = results['protein_g'] / results['calories_kcal'].clip(lower=1)
            results['final_score'] = 0.7 * results['similarity_score'] + 0.3 * results['protein_score']
        
        elif any(word in query_lower for word in ['calorie', 'léger', 'light', 'faible']):
            results['calorie_score'] = 1 / (results['calories_kcal'].clip(lower=1) ** 0.5)
            results['final_score'] = 0.6 * results['similarity_score'] + 0.4 * results['calorie_score']
        
        elif any(word in query_lower for word in ['santé', 'health', 'nutritif']):
            if 'health_score' in results.columns:
                results['health_score_norm'] = results['health_score'] / 100
                results['final_score'] = 0.5 * results['similarity_score'] + 0.5 * results['health_score_norm']
            else:
                results['final_score'] = results['similarity_score']
        
        else:
            results['final_score'] = results['similarity_score']
        
        results = results.sort_values('final_score', ascending=False)
        return results
    
    def get_top_categories(self, results, n=3):
        if 'food_category' in results.columns:
            return results['food_category'].value_counts().head(n).index.tolist()
        return []