
import requests
import json
from typing import Optional
import sys

class LocalLLMGenerator:
    """Classe adaptative pour générer des réponses avec LLM (Windows et VSCode)"""
    
    def __init__(self, model_name=None, base_url="http://localhost:11434", backend="ollama"):
        print("🤖 Étape 6.1: Initialisation du LLM adaptatif...")
        
        self.model_name = model_name
        self.base_url = base_url
        self.backend = backend
        self.is_windows = sys.platform.startswith('win')
        
        print(f"   💻 Environnement détecté: {'Windows' if self.is_windows else 'Linux/Mac'}")
        
        # Initialiser selon le backend spécifié
        if backend == "ollama":
            if self._try_ollama():
                self.backend = "ollama"
            else:
                print("   ⚠️ Ollama non disponible, passage en mode simple")
                self.backend = "simple"
        elif backend == "huggingface":
            if self._try_huggingface():
                self.backend = "huggingface"
            else:
                print("   ⚠️ HuggingFace non disponible, passage en mode simple")
                self.backend = "simple"
        else:
            print("   ⚠️ Mode simple activé")
            self.backend = "simple"
        
        # Templates de prompt
        self.prompt_templates = self._load_prompt_templates()
        
        print(f"   ✅ LLM prêt (backend: {self.backend})")
    
    def _try_ollama(self):
        """Essaie de se connecter à Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name and self.model_name in model_names:
                    self.ollama_model = self.model_name
                elif model_names:
                    self.ollama_model = model_names[0]
                else:
                    print("   ⚠️ Ollama installé mais pas de modèles")
                    return False
                
                print(f"   ✅ Ollama connecté avec modèle: {self.ollama_model}")
                return True
            
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Ollama non détecté - Assurez-vous qu'Ollama est démarré")
            print("   📌 Commandes pour Windows:")
            print("       1. Ouvrir un terminal séparé")
            print("       2. Exécuter: ollama serve")
            print("       3. Revenir ici")
        except Exception as e:
            print(f"   ⚠️ Erreur Ollama: {e}")
        
        return False
    
    def _try_huggingface(self):
        """Essaie de charger un modèle HuggingFace"""
        try:
            from transformers import pipeline
            import torch
            
            hf_model = self.model_name or "google/flan-t5-small"
            print(f"   📦 Chargement du modèle HuggingFace: {hf_model}")
            
            if "t5" in hf_model.lower():
                self.hf_generator = pipeline(
                    "text2text-generation",
                    model=hf_model,
                    device=-1,
                    torch_dtype=torch.float32
                )
            else:
                self.hf_generator = pipeline(
                    "text-generation",
                    model=hf_model,
                    device=-1,
                    torch_dtype=torch.float32
                )
            
            print(f"   ✅ Modèle HuggingFace chargé")
            return True
            
        except Exception as e:
            print(f"   ❌ Échec chargement HuggingFace: {str(e)[:80]}")
            return False
    
    def _load_prompt_templates(self):
        return {
            'nutrition_expert': """Tu es un nutritionniste expert avec 10 ans d'expérience.

CONTEXTE NUTRITIONNEL:
{context}

QUESTION DU PATIENT:
{query}

INSTRUCTIONS POUR TA RÉPONSE:
1. Sois précis et scientifique
2. Utilise les données fournies
3. Donne des conseils pratiques
4. Mentionne les limites des données
5. Structure ta réponse clairement

RÉPONSE DU NUTRITIONNISTE:""",

            'simple_assistant': """Tu es un assistant nutritionnel.

INFORMATIONS:
{context}

QUESTION:
{query}

Réponds de manière utile et concise:""",

            'comparison_specialist': """Tu es un expert en comparaison nutritionnelle.

DONNÉES À COMPARER:
{context}

DEMANDE DE COMPARAISON:
{query}

Fournis une analyse comparative détaillée:"""
        }
    
    def generate_response(self, query: str, context: str,
                         style: str = "nutrition_expert",
                         max_tokens: int = 500,
                         temperature: float = 0.7) -> str:
        print(f"🎨 Étape 6.2: Génération de la réponse (style: {style}, backend: {self.backend})...")
        
        template = self.prompt_templates.get(style, self.prompt_templates['simple_assistant'])
        prompt = template.format(context=context, query=query)
        
        if self.backend == "ollama":
            return self._generate_with_ollama(prompt, max_tokens, temperature)
        elif self.backend == "huggingface":
            return self._generate_with_huggingface(prompt, max_tokens, temperature)
        else:
            return self._fallback_response(query, context)
    
    def _generate_with_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                full_response = result['response']
                cleaned_response = self._clean_response(full_response, prompt)
                
                print(f"   ✓ Réponse générée ({len(cleaned_response.split())} mots)")
                return cleaned_response
            else:
                error_msg = f"Erreur Ollama: {response.status_code}"
                print(f"   ❌ {error_msg}")
                return self._fallback_response_from_prompt(prompt)
                
        except Exception as e:
            print(f"   ❌ Erreur Ollama: {e}")
            return self._fallback_response_from_prompt(prompt)
    
    def _generate_with_huggingface(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            generation_params = {
                "max_length": len(prompt.split()) + max_tokens,
                "temperature": temperature,
                "do_sample": True,
                "num_return_sequences": 1,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
            
            result = self.hf_generator(prompt, **generation_params)
            
            if isinstance(result, list) and len(result) > 0:
                if 'generated_text' in result[0]:
                    full_response = result[0]['generated_text']
                else:
                    full_response = str(result[0])
            else:
                full_response = str(result)
            
            cleaned_response = self._clean_response(full_response, prompt)
            
            print(f"   ✓ Réponse générée ({len(cleaned_response.split())} mots)")
            return cleaned_response
            
        except Exception as e:
            print(f"   ❌ Erreur HuggingFace: {e}")
            return self._fallback_response_from_prompt(prompt)
    
    def _clean_response(self, response: str, prompt: str) -> str:
        if prompt in response:
            response = response.split(prompt)[-1]
        
        stop_sequences = ["###", "Human:", "Assistant:", "\\n\\n\\n", "[INST]", "[/INST]"]
        for stop in stop_sequences:
            if stop in response:
                response = response.split(stop)[0]
        
        response = response.strip()
        
        if len(response.split()) > 400:
            sentences = response.split('. ')
            response = '. '.join(sentences[:8]) + '.'
        
        return response
    
    def _fallback_response_from_prompt(self, prompt: str) -> str:
        print("   ⚠️ Utilisation du mode fallback")
        
        lines = prompt.split('\\n')
        query = ""
        for line in lines:
            if "QUESTION:" in line or "Question:" in line:
                query = line.replace("QUESTION:", "").replace("Question:", "").strip()
                break
        
        return f"""Basé sur votre question "{query}", voici une analyse nutritionnelle:

Pour une réponse plus détaillée, consultez les données nutritionnelles complètes.

Note: Le système d'IA avancé est temporairement indisponible."""
    
    def _fallback_response(self, query: str, context: str) -> str:
        print("   ⚠️ Utilisation du mode fallback simple")
        
        lines = context.split('\\n')
        foods = []
        
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')) or 'Calories:' in line:
                foods.append(line)
        
        if foods:
            summary = "\\n".join(foods[:5])
            return f"""Basé sur votre question "{query}", voici ce que j'ai trouvé:

{summary}

Pour une analyse plus détaillée, veuillez reformuler votre question."""
        else:
            return f"Je n'ai pas pu générer une réponse détaillée pour votre question sur '{query}'. Voici les informations disponibles:\\n\\n{context[:500]}..."
