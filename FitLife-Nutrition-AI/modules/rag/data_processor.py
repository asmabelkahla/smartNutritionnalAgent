# data_processor.py
import pandas as pd
import numpy as np

class NutritionDataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
    
    def load_data(self):
        """Charge les données nutritionnelles"""
        self.df = pd.read_csv(self.data_path)
        print(f"✓ Données chargées: {len(self.df)} lignes")
        return self.df
    
    def clean_data(self):
        """Nettoie les données"""
        if self.df is None:
            raise ValueError("Chargez d'abord les données avec load_data()")
        
        # Supprime les doublons
        self.df = self.df.drop_duplicates()
        
        # Remplace les valeurs manquantes
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = self.df[numeric_cols].fillna(0)
        
        print(f"✓ Données nettoyées: {len(self.df)} lignes restantes")
        return self.df
    
    def create_text_representations(self):
        """Crée des descriptions textuelles pour chaque aliment"""
        if self.df is None:
            raise ValueError("Chargez et nettoyez d'abord les données")
        
        def generate_food_description(row):
            description = f"{row.get('food_name', 'Aliment')}"
            
            # Ajoute les nutriments principaux
            if 'calories' in row:
                description += f" avec {row['calories']} calories"
            if 'protein' in row:
                description += f", {row['protein']}g de protéines"
            if 'carbs' in row:
                description += f", {row['carbs']}g de glucides"
            if 'fat' in row:
                description += f", {row['fat']}g de lipides"
            
            return description
        
        self.df['food_description'] = self.df.apply(generate_food_description, axis=1)
        print(f"   ✓ Descriptions créées pour {len(self.df)} aliments")
        return self.df
    
    def run_pipeline(self):
        """Exécute tout le pipeline de traitement"""
        self.load_data()
        self.clean_data()
        self.create_text_representations()
        return self.df

# Utilisation
if __name__ == "__main__":
    # Testez la classe
    processor = NutritionDataProcessor("votre_fichier_nutrition.csv")
    processed_data = processor.run_pipeline()
    
    # Affiche un échantillon
    print("\nÉchantillon des données traitées:")
    print(processed_data[['food_name', 'food_description']].head())