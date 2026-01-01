from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class UserProfile:
    id: Optional[int]
    name: str
    age: Optional[int]
    sex: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    goals: Optional[str]
    dietary_preferences: Optional[str]
    activity_level: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "UserProfile":
        return UserProfile(
            id=d.get("id"),
            name=d.get("name", ""),
            age=d.get("age"),
            sex=d.get("sex"),
            height_cm=d.get("height_cm"),
            weight_kg=d.get("weight_kg"),
            goals=d.get("goals"),
            dietary_preferences=d.get("dietary_preferences"),
            activity_level=d.get("activity_level"),
        )
# src/user_profile.py
import sqlite3
import json
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional, Dict, List
import hashlib
import bcrypt

@dataclass
class UserProfile:
    """Classe pour gérer le profil utilisateur"""
    user_id: str
    username: str
    email: str
    age: int
    gender: str  # 'male', 'female', 'other'
    height_cm: float
    weight_kg: float
    activity_level: str  # 'sedentary', 'light', 'moderate', 'active', 'very_active'
    goal: str  # 'weight_loss', 'maintenance', 'muscle_gain', 'endurance'
    dietary_preferences: List[str]  # ['vegetarian', 'vegan', 'gluten_free', etc.]
    allergies: List[str]
    created_at: datetime
    last_updated: datetime
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crée un profil à partir d'un dictionnaire"""
        return cls(
            user_id=data.get('user_id', hashlib.md5(data.get('email', '').encode()).hexdigest()),
            username=data.get('username', ''),
            email=data.get('email', ''),
            age=data.get('age', 30),
            gender=data.get('gender', 'other'),
            height_cm=data.get('height_cm', 170),
            weight_kg=data.get('weight_kg', 70),
            activity_level=data.get('activity_level', 'moderate'),
            goal=data.get('goal', 'maintenance'),
            dietary_preferences=data.get('dietary_preferences', []),
            allergies=data.get('allergies', []),
            created_at=data.get('created_at', datetime.now()),
            last_updated=data.get('last_updated', datetime.now())
        )
    
    def to_dict(self) -> Dict:
        """Convertit le profil en dictionnaire"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'activity_level': self.activity_level,
            'goal': self.goal,
            'dietary_preferences': self.dietary_preferences,
            'allergies': self.allergies,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    def calculate_bmr(self) -> float:
        """Calcule le métabolisme basal (Harris-Benedict)"""
        if self.gender == 'male':
            bmr = 88.362 + (13.397 * self.weight_kg) + (4.799 * self.height_cm) - (5.677 * self.age)
        elif self.gender == 'female':
            bmr = 447.593 + (9.247 * self.weight_kg) + (3.098 * self.height_cm) - (4.330 * self.age)
        else:
            # Moyenne homme/femme
            bmr = 500 + (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age)
        return round(bmr, 2)
    
    def calculate_tdee(self) -> float:
        """Calcule les besoins caloriques journaliers"""
        bmr = self.calculate_bmr()
        
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(self.activity_level, 1.55)
        
        # Ajustement selon l'objectif
        goal_adjustments = {
            'weight_loss': 0.85,  # Déficit de 15%
            'maintenance': 1.0,
            'muscle_gain': 1.15,  # Surplus de 15%
            'endurance': 1.1
        }
        
        tdee *= goal_adjustments.get(self.goal, 1.0)
        return round(tdee, 2)
    
    def calculate_macros(self) -> Dict[str, float]:
        """Calcule les besoins en macronutriments"""
        tdee = self.calculate_tdee()
        
        # Protéines (g)
        if self.goal == 'muscle_gain':
            protein_g_per_kg = 2.0
        elif self.goal == 'weight_loss':
            protein_g_per_kg = 2.2
        else:
            protein_g_per_kg = 1.8
        
        protein_g = round(self.weight_kg * protein_g_per_kg, 1)
        protein_cal = protein_g * 4
        
        # Lipides (% des calories)
        fat_percentage = 0.25  # 25% des calories
        fat_cal = tdee * fat_percentage
        fat_g = round(fat_cal / 9, 1)
        
        # Glucides (le reste)
        carbs_cal = tdee - protein_cal - fat_cal
        carbs_g = round(carbs_cal / 4, 1)
        
        # Fibres
        fiber_g = round(14 * (tdee / 1000), 1)  # 14g pour 1000 kcal
        
        # Eau (ml)
        water_ml = round(self.weight_kg * 30, 0)  # 30ml par kg
        
        return {
            'calories': round(tdee, 0),
            'protein_g': protein_g,
            'carbs_g': carbs_g,
            'fat_g': fat_g,
            'fiber_g': fiber_g,
            'water_ml': water_ml,
            'protein_percentage': round((protein_cal / tdee) * 100, 1),
            'carbs_percentage': round((carbs_cal / tdee) * 100, 1),
            'fat_percentage': round((fat_cal / tdee) * 100, 1)
        }
    
    def calculate_bmi(self) -> Dict[str, float]:
        """Calcule l'IMC et l'interprétation"""
        height_m = self.height_cm / 100
        bmi = self.weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Insuffisance pondérale"
            recommendation = "Consultez un nutritionniste"
        elif 18.5 <= bmi < 25:
            category = "Poids normal"
            recommendation = "Maintenez vos bonnes habitudes"
        elif 25 <= bmi < 30:
            category = "Surpoids"
            recommendation = "Augmentez l'activité physique"
        else:
            category = "Obésité"
            recommendation = "Consultez un professionnel de santé"
        
        return {
            'bmi': round(bmi, 1),
            'category': category,
            'recommendation': recommendation,
            'healthy_weight_min': round(18.5 * (height_m ** 2), 1),
            'healthy_weight_max': round(25 * (height_m ** 2), 1)
        }
    
    def get_recommendations(self) -> List[str]:
        """Génère des recommandations personnalisées"""
        recommendations = []
        
        # Basé sur l'objectif
        if self.goal == 'weight_loss':
            recommendations.append("🍎 Privilégiez les aliments riches en fibres")
            recommendations.append("💧 Buvez au moins 2L d'eau par jour")
            recommendations.append("⏱️ Mangez lentement et écoutez votre satiété")
        
        elif self.goal == 'muscle_gain':
            recommendations.append("💪 Consommez 1.5-2g de protéines par kg de poids")
            recommendations.append("🥦 Incluez des glucides complexes dans chaque repas")
            recommendations.append("🕒 Mangez toutes les 3-4 heures")
        
        elif self.goal == 'endurance':
            recommendations.append("⚡ Augmentez votre apport en glucides")
            recommendations.append("🧂 Attention à l'hydratation et aux électrolytes")
            recommendations.append("🥑 Consommez des graisses saines")
        
        # Basé sur l'âge
        if self.age > 50:
            recommendations.append("🦴 Augmentez votre apport en calcium")
            recommendations.append("☀️ Pensez à la vitamine D")
            recommendations.append("💪 Maintenez votre masse musculaire")
        
        # Basé sur les préférences
        if 'vegetarian' in self.dietary_preferences:
            recommendations.append("🌱 Combinez céréales et légumineuses pour des protéines complètes")
        
        if 'vegan' in self.dietary_preferences:
            recommendations.append("🥬 Complémentez en vitamine B12")
            recommendations.append("🌰 Varier les sources de protéines végétales")
        
        return recommendations


class UserProfileManager:
    """Gestionnaire de profils utilisateurs avec base de données"""
    
    def __init__(self, db_path: str = "data/user_profiles.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                age INTEGER,
                gender TEXT,
                height_cm REAL,
                weight_kg REAL,
                activity_level TEXT,
                goal TEXT,
                dietary_preferences TEXT,
                allergies TEXT,
                created_at TIMESTAMP,
                last_updated TIMESTAMP
            )
        ''')
        
        # Table poids (suivi)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                weight_kg REAL,
                date DATE,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Table repas (historique)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date DATE,
                meal_type TEXT,
                food_name TEXT,
                calories REAL,
                protein_g REAL,
                carbs_g REAL,
                fat_g REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, profile_data: Dict, password: str = None) -> str:
        """Crée un nouvel utilisateur"""
        profile = UserProfile.from_dict(profile_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hacher le mot de passe si fourni
        password_hash = None
        if password:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, email, password_hash, age, gender, height_cm, weight_kg, 
             activity_level, goal, dietary_preferences, allergies, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.user_id,
            profile.username,
            profile.email,
            password_hash,
            profile.age,
            profile.gender,
            profile.height_cm,
            profile.weight_kg,
            profile.activity_level,
            profile.goal,
            json.dumps(profile.dietary_preferences),
            json.dumps(profile.allergies),
            profile.created_at.isoformat(),
            profile.last_updated.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return profile.user_id
    
    def get_user(self, user_id: str = None, email: str = None) -> Optional[UserProfile]:
        """Récupère un utilisateur par ID ou email"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        elif email:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        else:
            return None
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_profile(dict(row))
        
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserProfile]:
        """Authentifie un utilisateur"""
        user = self.get_user(email=email)
        
        if not user:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            if bcrypt.checkpw(password.encode(), result[0].encode()):
                return user
        
        return None
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Met à jour le profil utilisateur"""
        user = self.get_user(user_id=user_id)
        
        if not user:
            return False
        
        # Mettre à jour les attributs
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.last_updated = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET
                username = ?, age = ?, gender = ?, height_cm = ?, weight_kg = ?,
                activity_level = ?, goal = ?, dietary_preferences = ?, allergies = ?,
                last_updated = ?
            WHERE user_id = ?
        ''', (
            user.username,
            user.age,
            user.gender,
            user.height_cm,
            user.weight_kg,
            user.activity_level,
            user.goal,
            json.dumps(user.dietary_preferences),
            json.dumps(user.allergies),
            user.last_updated.isoformat(),
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        return True
    
    def add_weight_entry(self, user_id: str, weight_kg: float, date: date = None, notes: str = ""):
        """Ajoute une entrée de poids"""
        if date is None:
            date = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weight_tracking (user_id, weight_kg, date, notes)
            VALUES (?, ?, ?, ?)
        ''', (user_id, weight_kg, date.isoformat(), notes))
        
        conn.commit()
        conn.close()
    
    def get_weight_history(self, user_id: str, days: int = 30) -> List[Dict]:
        """Récupère l'historique des poids"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        cursor.execute('''
            SELECT * FROM weight_tracking 
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        ''', (user_id, start_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_meal(self, user_id: str, meal_data: Dict):
        """Ajoute un repas à l'historique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO meals 
            (user_id, date, meal_type, food_name, calories, protein_g, carbs_g, fat_g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            meal_data.get('date', datetime.now().date().isoformat()),
            meal_data.get('meal_type', 'meal'),
            meal_data.get('food_name', ''),
            meal_data.get('calories', 0),
            meal_data.get('protein_g', 0),
            meal_data.get('carbs_g', 0),
            meal_data.get('fat_g', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_daily_summary(self, user_id: str, target_date: date = None) -> Dict:
        """Récupère le résumé nutritionnel de la journée"""
        if target_date is None:
            target_date = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(calories) as total_calories,
                SUM(protein_g) as total_protein,
                SUM(carbs_g) as total_carbs,
                SUM(fat_g) as total_fat,
                COUNT(*) as meal_count
            FROM meals 
            WHERE user_id = ? AND date = ?
        ''', (user_id, target_date.isoformat()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return {
                'date': target_date.isoformat(),
                'total_calories': result[0] or 0,
                'total_protein': result[1] or 0,
                'total_carbs': result[2] or 0,
                'total_fat': result[3] or 0,
                'meal_count': result[4] or 0
            }
        
        return {
            'date': target_date.isoformat(),
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'meal_count': 0
        }
    
    def _row_to_profile(self, row: Dict) -> UserProfile:
        """Convertit une ligne de base de données en UserProfile"""
        return UserProfile(
            user_id=row['user_id'],
            username=row['username'],
            email=row['email'],
            age=row['age'],
            gender=row['gender'],
            height_cm=row['height_cm'],
            weight_kg=row['weight_kg'],
            activity_level=row['activity_level'],
            goal=row['goal'],
            dietary_preferences=json.loads(row['dietary_preferences'] or '[]'),
            allergies=json.loads(row['allergies'] or '[]'),
            created_at=datetime.fromisoformat(row['created_at']),
            last_updated=datetime.fromisoformat(row['last_updated'])
        )