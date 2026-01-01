# src/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os

class NutritionEmbedder:
    """Classe pour créer des embeddings nutritionnels"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print("🔤 Étape 2.1: Chargement du modèle d'embedding...")
        self.model = SentenceTransformer(model_name)
        print(f"   ✓ Modèle chargé: {model_name}")
        print(f"   ✓ Dimension des embeddings: {self.model.get_sentence_embedding_dimension()}")
    
    def create_embeddings(self, texts, batch_size=32):
        print(f"🎯 Étape 2.2: Création des embeddings...")
        print(f"   ✓ Nombre de textes: {len(texts)}")
        print(f"   ✓ Taille des lots: {batch_size}")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        print(f"   ✓ Embeddings créés: {embeddings.shape}")
        return embeddings
    
    def create_query_embedding(self, query):
        return self.model.encode([query], normalize_embeddings=True)[0]
    
    def save_embeddings(self, embeddings, filepath='data/processed/embeddings.pkl'):
        """Sauvegarde les embeddings sur disque"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(embeddings, f)
        print(f"💾 Embeddings sauvegardés: {filepath}")
    
    def load_embeddings(self, filepath='data/processed/embeddings.pkl'):
        """Charge les embeddings depuis le disque"""
        with open(filepath, 'rb') as f:
            embeddings = pickle.load(f)
        print(f"📂 Embeddings chargés: {embeddings.shape}")
        return embeddings