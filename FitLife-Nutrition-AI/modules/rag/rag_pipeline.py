
import os
import sys
from pathlib import Path
import yaml
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

class NutritionRAGPipeline:
    """Pipeline RAG complet pour la nutrition - Version Windows"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Configuration pour éviter les erreurs de bibliothèque sur Windows
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        
        # Définir le chemin racine du projet (FitLife-Nutrition-AI)
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        print(f"DEBUG: Root dir resolved to: {self.root_dir}")
        
        self.config = self._load_config(config_path)
        self._init_components()
    
    def _load_config(self, config_path: Optional[str] = None):
        """Charge la configuration depuis YAML"""
        default_config = {
            "data": {
                "csv_path": str(self.root_dir / "data" / "cleaned_nutrition_data.csv"),
                "sample_size": None
            },
            "embedding": {
                "model_name": "all-MiniLM-L6-v2",
                "batch_size": 32,
                "save_embeddings": True
            },
            "indexing": {
                "index_type": "IndexFlatL2",
                "save_index": True
            },
            "llm": {
                "enabled": True,
                "backend": "ollama",
                "model_name": "llama3.2:1b",
                "ollama_base_url": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 300
            },
            "retrieval": {
                "default_k": 10,
                "use_cache": True
            },
            "paths": {
                "embeddings": str(self.root_dir / "models" / "embeddings.npy"),
                "index": str(self.root_dir / "models" / "faiss_index.index")
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Fusionner récursivement
                for key in default_config:
                    if key in user_config:
                        if isinstance(default_config[key], dict) and isinstance(user_config[key], dict):
                            default_config[key].update(user_config[key])
                        else:
                            default_config[key] = user_config[key]
        
        return default_config
    
    def _init_components(self):
        """Initialise tous les composants du pipeline"""
        print("=" * 60)
        print("🧠 INITIALISATION DU PIPELINE NUTRITION RAG - Windows")
        print("=" * 60)
        
        # Créer les répertoires nécessaires
        models_dir = self.root_dir / "models"
        os.makedirs(models_dir, exist_ok=True)
        
        # 1. Préprocessing
        print("\n📥 ÉTAPE 1: PRÉPROCESSING")
        from modules.rag.data_processor import NutritionDataProcessor
        
        csv_path = self.config["data"]["csv_path"]
        if not os.path.exists(csv_path):
            print(f"   ⚠️ Fichier de données non trouvé: {csv_path}")
            print(f"   📌 Création de données d'exemple...")
            self._create_sample_data()
        
        self.preprocessor = NutritionDataProcessor(csv_path)
        self.df = self.preprocessor.run_pipeline()
        
        # Échantillonner si nécessaire
        sample_size = self.config["data"]["sample_size"]
        if sample_size and sample_size < len(self.df):
            print(f"   📊 Échantillonnage: {sample_size} aliments")
            self.df = self.df.sample(sample_size, random_state=42).reset_index(drop=True)
        
        print(f"   ✓ Données chargées: {len(self.df)} aliments")
        
        # 2. Embedding
        print("\n🔤 ÉTAPE 2: EMBEDDING")
        from modules.rag.embeddings import NutritionEmbedder
        
        self.embedder = NutritionEmbedder(
            model_name=self.config["embedding"]["model_name"]
        )
        
        # Charger ou créer les embeddings
        embeddings_path = self.config["paths"]["embeddings"]
        if os.path.exists(embeddings_path):
            print("   ✓ Chargement des embeddings sauvegardés")
            self.embeddings = np.load(embeddings_path)
        else:
            print("   📝 Création des embeddings...")
            texts = self.df['food_description'].tolist()
            self.embeddings = self.embedder.create_embeddings(
                texts, 
                batch_size=self.config["embedding"]["batch_size"]
            )
            if self.config["embedding"]["save_embeddings"]:
                np.save(embeddings_path, self.embeddings)
                print(f"   💾 Embeddings sauvegardés: {embeddings_path}")
        
        # 3. Indexation
        print("\n📊 ÉTAPE 3: INDEXATION")
        from modules.rag.indexer import FaissIndexer
        
        dimension = self.embeddings.shape[1]
        self.indexer = FaissIndexer(dimension)
        
        # Charger ou créer l'index
        index_path = self.config["paths"]["index"]
        if os.path.exists(index_path):
            print("   ✓ Chargement de l'index FAISS sauvegardé")
            self.indexer.load_index(index_path)
        else:
            self.indexer.add_embeddings(self.embeddings)
            if self.config["indexing"]["save_index"]:
                self.indexer.save_index(index_path)
                print(f"   💾 Index sauvegardé: {index_path}")
        
        # 4. Retriever
        print("\n🔍 ÉTAPE 4: RETRIEVER")
        from modules.rag.retriever import NutritionRetriever
        
        self.retriever = NutritionRetriever(
            self.df, 
            self.embedder, 
            self.indexer
        )
        
        # 5. Augmenter de contexte
        print("\n🎭 ÉTAPE 5: AUGMENTATION DE CONTEXTE")
        from modules.rag.context_augmenter import ContextAugmenter
        self.augmenter = ContextAugmenter()
        
        # 6. LLM (optionnel)
        if self.config["llm"]["enabled"]:
            print("\n🤖 ÉTAPE 6: INITIALISATION LLM")
            from modules.rag.llm_generator import LocalLLMGenerator
            
            try:
                self.generator = LocalLLMGenerator(
                    model_name=self.config["llm"]["model_name"],
                    base_url=self.config["llm"]["ollama_base_url"],
                    backend=self.config["llm"]["backend"]
                )
                self.use_llm = True
                print(f"   ✓ LLM prêt (backend: {self.generator.backend})")
            except Exception as e:
                print(f"   ⚠️ LLM non disponible: {e}")
                print("   ⚠️ Utilisation du mode simple")
                self.use_llm = False
        else:
            self.use_llm = False
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE PRÊT À L'EMPLOI")
        print("=" * 60)
    
    def _create_sample_data(self):
        """Crée des données d'exemple si le fichier CSV n'existe pas"""
        sample_data = {
            'food_name': [
                'Pomme', 'Banane', 'Poulet grillé', 'Saumon', 'Brocoli',
                'Riz brun', 'Œuf', 'Yaourt grec', 'Amandes', 'Avocat'
            ],
            'calories_kcal': [52, 89, 165, 208, 34, 111, 155, 59, 579, 160],
            'protein_g': [0.3, 1.1, 31.0, 20.0, 2.8, 2.6, 13.0, 10.0, 21.2, 2.0],
            'carbs_g': [13.8, 22.8, 0.0, 0.0, 6.6, 23.0, 1.1, 3.6, 21.6, 8.5],
            'fat_g': [0.2, 0.3, 3.6, 13.0, 0.4, 0.9, 11.0, 0.4, 49.9, 14.7],
            'fiber_g': [2.4, 2.6, 0.0, 0.0, 2.6, 1.8, 0.0, 0.0, 12.5, 6.7],
            'sugars_g': [10.4, 12.2, 0.0, 0.0, 1.7, 0.4, 1.1, 3.6, 4.4, 0.7],
            'food_category': [
                'Fruit', 'Fruit', 'Viande', 'Poisson', 'Légume',
                'Céréale', 'Produit animal', 'Laitier', 'Noix', 'Légume'
            ],
            'health_score': [85.0, 82.0, 75.0, 88.0, 92.0, 72.0, 70.0, 68.0, 76.0, 80.0]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(self.config["data"]["csv_path"], index=False)
        print(f"   ✓ Données d'exemple créées: {self.config['data']['csv_path']}")
    
    def query(self, user_query: str, k: int = None, filters: Dict = None):
        """Exécute une requête complète"""
        if k is None:
            k = self.config["retrieval"]["default_k"]
        
        print(f"\n🎯 REQUÊTE: '{user_query}'")
        
        # Récupération
        retrieved_foods = self.retriever.retrieve(
            query=user_query,
            k=k,
            filters=filters,
            use_cache=self.config["retrieval"]["use_cache"]
        )
        
        if retrieved_foods.empty:
            return {
                "response": "❌ Aucun aliment correspondant trouvé.",
                "foods": [],
                "used_llm": False,
                "query": user_query,
                "foods_count": 0,
                "top_categories": [],
                "similarity_scores": []
            }
        
        # Augmentation du contexte
        context = self.augmenter.augment_context(user_query, retrieved_foods)
        
        # Génération de la réponse
        if self.use_llm:
            query_type = self.augmenter.detect_query_type(user_query)
            style_map = {
                'comparison': 'comparison_specialist',
                'recommendation': 'nutrition_expert',
                'analysis': 'nutrition_expert',
                'simple': 'simple_assistant'
            }
            style = style_map.get(query_type, 'simple_assistant')
            
            try:
                response = self.generator.generate_response(
                    query=user_query,
                    context=context,
                    style=style,
                    temperature=self.config["llm"]["temperature"],
                    max_tokens=self.config["llm"]["max_tokens"]
                )
                used_llm = True
            except Exception as e:
                print(f"   ⚠️ Erreur génération LLM: {e}")
                response = self._generate_simple_response(user_query, retrieved_foods)
                used_llm = False
        else:
            response = self._generate_simple_response(user_query, retrieved_foods)
            used_llm = False
        
        # Préparation des résultats
        result = {
            "response": response,
            "foods": retrieved_foods.head(5).to_dict('records'),
            "used_llm": used_llm,
            "query": user_query,
            "foods_count": len(retrieved_foods),
            "top_categories": self.retriever.get_top_categories(retrieved_foods, 3),
            "similarity_scores": retrieved_foods['similarity_score'].head(5).tolist()
        }
        
        print(f"   ✓ {result['foods_count']} aliments trouvés")
        if result['top_categories']:
            print(f"   📁 Catégories: {', '.join(result['top_categories'])}")
        
        return result
    
    def _generate_simple_response(self, query, foods):
        """Génère une réponse simple sans LLM"""
        if foods.empty:
            return f"❌ Aucun aliment trouvé pour la requête : '{query}'"
        
        top_foods = foods.head(3)
        response_lines = [f"✅ **Résultats pour '{query}'**", ""]
        
        for i, (_, food) in enumerate(top_foods.iterrows(), 1):
            response_lines.append(f"**{i}. {food['food_name']}**")
            response_lines.append(f"   • Catégorie: {food.get('food_category', 'N/A')}")
            response_lines.append(f"   • Calories: {food.get('calories_kcal', 0)} kcal")
            response_lines.append(f"   • Protéines: {food.get('protein_g', 0)}g")
            response_lines.append(f"   • Score santé: {food.get('health_score', 'N/A')}")
            response_lines.append(f"   • Similarité: {food.get('similarity_score', 0)*100:.1f}%")
            response_lines.append("")
        
        response_lines.append("💡 *Pour une analyse plus détaillée, activez le mode IA dans les paramètres.*")
        
        return "\\n".join(response_lines)
    
    def get_statistics(self):
        """Retourne des statistiques sur les données"""
        stats = {
            "total_foods": len(self.df),
            "categories": self.df['food_category'].nunique() if 'food_category' in self.df.columns else 0,
            "columns": list(self.df.columns),
            "memory_usage": round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)  # MB
        }
        
        if 'health_score' in self.df.columns:
            stats.update({
                "avg_health_score": round(self.df['health_score'].mean(), 1),
                "min_health_score": round(self.df['health_score'].min(), 1),
                "max_health_score": round(self.df['health_score'].max(), 1)
            })
        
        # Statistiques nutritionnelles
        if 'calories_kcal' in self.df.columns:
            stats['avg_calories'] = round(self.df['calories_kcal'].mean(), 1)
        
        if 'protein_g' in self.df.columns:
            stats['avg_protein'] = round(self.df['protein_g'].mean(), 1)
        
        return stats
    
    def save_pipeline(self):
        """Sauvegarde l'état du pipeline"""
        state = {
            'config': self.config,
            'df_shape': self.df.shape,
            'embeddings_shape': self.embeddings.shape,
            'index_size': self.indexer.index.ntotal
        }
        
        with open('models/pipeline_state.json', 'w') as f:
            import json
            json.dump(state, f, indent=2)
        
        print("💾 État du pipeline sauvegardé")
    
    def test_query(self, test_query="Quels aliments sont riches en protéines ?"):
        """Test rapide du pipeline"""
        print("\n🧪 Test du pipeline...")
        results = self.query(test_query, k=3)
        print("\n📝 Résultats du test:")
        print(f"• Requête: {results['query']}")
        print(f"• Aliments trouvés: {results['foods_count']}")
        print(f"• LLM utilisé: {results['used_llm']}")
        print(f"\n📄 Réponse (extrait):")
        print(results['response'][:200] + "...")
        return results

if __name__ == "__main__":
    # Test rapide si exécuté directement
    pipeline = NutritionRAGPipeline()
    stats = pipeline.get_statistics()
    print(f"\n📊 Statistiques des données:")
    print(f"• Total aliments: {stats['total_foods']}")
    print(f"• Catégories: {stats['categories']}")
    if 'avg_health_score' in stats:
        print(f"• Score santé moyen: {stats['avg_health_score']}")
    
    # Exécuter un test
    test_results = pipeline.test_query()
