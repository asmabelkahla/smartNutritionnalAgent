# src/faiss_indexer.py
import faiss
import numpy as np
import pickle
import os

class FaissIndexer:
    """Classe pour créer et gérer un index FAISS"""
    
    def __init__(self, dimension=384):  # all-MiniLM-L6-v2 = 384 dimensions
        print("📊 Étape 3.1: Initialisation de l'index FAISS...")
        self.dimension = dimension
        
        # Index avec similarité cosinus (normalisation interne)
        self.index = faiss.IndexFlatIP(dimension)  # Produit scalaire interne
        self.normalize_index = faiss.IndexFlatIP(dimension)
        
        print(f"   ✓ Index créé avec dimension {dimension}")
        print(f"   ✓ Métrique: similarité cosinus (IndexFlatIP)")
    
    def add_embeddings(self, embeddings, normalize=True):
        print("➕ Étape 3.2: Ajout des embeddings à l'index...")
        embeddings_array = np.array(embeddings).astype('float32')
        
        if embeddings_array.shape[1] != self.dimension:
            raise ValueError(f"Dimension mismatch: expected {self.dimension}, got {embeddings_array.shape[1]}")
        
        # Normaliser pour la similarité cosinus
        if normalize:
            faiss.normalize_L2(embeddings_array)
        
        self.index.add(embeddings_array)
        print(f"   ✓ {len(embeddings_array)} embeddings ajoutés")
        print(f"   ✓ Taille totale de l'index: {self.index.ntotal}")
        return self.index
    
    def save_index(self, filepath='data/processed/faiss_index.bin'):
        """Sauvegarde l'index FAISS"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        faiss.write_index(self.index, filepath)
        print(f"💾 Index FAISS sauvegardé: {filepath}")
    
    def load_index(self, filepath='data/processed/faiss_index.bin'):
        """Charge un index FAISS sauvegardé"""
        if os.path.exists(filepath):
            self.index = faiss.read_index(filepath)
            self.dimension = self.index.d
            print(f"📂 Index FAISS chargé: {filepath}")
            print(f"   ✓ Dimension: {self.dimension}")
            print(f"   ✓ Nombre de vecteurs: {self.index.ntotal}")
        else:
            print(f"⚠️  Fichier non trouvé: {filepath}")
    
    def search(self, query_embedding, k=10, normalize_query=True):
        """
        Recherche les k plus proches voisins
        
        Args:
            query_embedding: Embedding de la requête
            k: Nombre de résultats à retourner
            normalize_query: Normaliser la requête pour similarité cosinus
            
        Returns:
            indices: Indices des résultats
            similarities: Scores de similarité (0 à 1)
        """
        # Préparer la requête
        query = query_embedding.reshape(1, -1).astype('float32')
        
        # Normaliser pour similarité cosinus
        if normalize_query:
            faiss.normalize_L2(query)
        
        # Rechercher
        distances, indices = self.index.search(query, k)
        
        # Convertir distances en similarités (pour IndexFlatIP, distances = 1 - similarité)
        similarities = 1.0 - distances[0]  # Pour IndexFlatIP
        
        # Filtrer les résultats invalides
        valid_mask = indices[0] != -1
        valid_indices = indices[0][valid_mask]
        valid_similarities = similarities[valid_mask]
        
        return valid_indices, valid_similarities
    
    def search_with_threshold(self, query_embedding, k=10, similarity_threshold=0.5):
        """Recherche avec seuil de similarité minimum"""
        indices, similarities = self.search(query_embedding, k)
        
        # Filtrer par seuil
        mask = similarities >= similarity_threshold
        filtered_indices = indices[mask]
        filtered_similarities = similarities[mask]
        
        return filtered_indices, filtered_similarities