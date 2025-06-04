from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import os
import uuid
from typing import List, Dict, Any
import tempfile

app = FastAPI(
    title="Scan Trad API",
    description="API pour la traduction automatique de pages de manga",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dossier pour stocker temporairement les images
TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)

class MangaProcessor:
    """Classe pour traiter les pages de manga"""
    
    def __init__(self):
        self.demo_mode = True  # Mode démo pour l'instant
    
    def detect_text_bubbles(self, image: np.ndarray) -> List[Dict]:
        """Simule la détection des bulles de texte avec YOLO"""
        h, w = image.shape[:2]
        
        # Générer des détections réalistes basées sur la taille de l'image
        detections = [
            {
                "id": 1,
                "x": w//6, 
                "y": h//8, 
                "width": w//4, 
                "height": h//12, 
                "confidence": 0.95
            },
            {
                "id": 2,
                "x": w//2, 
                "y": h//4, 
                "width": w//5, 
                "height": h//15, 
                "confidence": 0.88
            },
            {
                "id": 3,
                "x": w//8, 
                "y": h//2, 
                "width": w//3, 
                "height": h//10, 
                "confidence": 0.92
            },
            {
                "id": 4,
                "x": 3*w//5, 
                "y": 2*h//3, 
                "width": w//4, 
                "height": h//12, 
                "confidence": 0.87
            }
        ]
        
        return detections
    
    def extract_text_ocr(self, image: np.ndarray, bbox: Dict) -> str:
        """Simule l'extraction de texte avec OCR"""
        demo_texts = [
            "What are you doing?",
            "I won't give up!",
            "This is impossible...",
            "Let's fight together!",
            "Amazing power!",
            "No way!"
        ]
        
        # Simuler l'extraction en fonction de l'ID de la détection
        text_index = bbox.get("id", 1) % len(demo_texts)
        return demo_texts[text_index - 1]
    
    def translate_text(self, text: str, target_language: str = "fr") -> str:
        """Simule la traduction du texte"""
        translations = {
            "What are you doing?": {
                "fr": "Que fais-tu ?",
                "es": "¿Qué estás haciendo?",
                "de": "Was machst du?",
                "it": "Cosa stai facendo?"
            },
            "I won't give up!": {
                "fr": "Je n'abandonnerai pas !",
                "es": "¡No me rendiré!",
                "de": "Ich gebe nicht auf!",
                "it": "Non mi arrenderò!"
            },
            "This is impossible...": {
                "fr": "C'est impossible...",
                "es": "Esto es imposible...",
                "de": "Das ist unmöglich...",
                "it": "È impossibile..."
            },
            "Let's fight together!": {
                "fr": "Combattons ensemble !",
                "es": "¡Luchemos juntos!",
                "de": "Lass uns zusammen kämpfen!",
                "it": "Combattiamo insieme!"
            },
            "Amazing power!": {
                "fr": "Pouvoir incroyable !",
                "es": "¡Poder increíble!",
                "de": "Erstaunliche Kraft!",
                "it": "Potere incredibile!"
            },
            "No way!": {
                "fr": "Impossible !",
                "es": "¡De ninguna manera!",
                "de": "Niemals!",
                "it": "Non è possibile!"
            }
        }
        
        return translations.get(text, {}).get(target_language, f"[{target_language}] {text}")
    
    def clean_and_replace_text(self, image: np.ndarray, detection: Dict, translation: str) -> np.ndarray:
        """Nettoie la zone de texte original et place le texte traduit"""
        try:
            x, y, w, h = detection["x"], detection["y"], detection["width"], detection["height"]
            
            # Étendre légèrement la zone pour bien nettoyer
            padding = 3
            clean_x = max(0, x - padding)
            clean_y = max(0, y - padding) 
            clean_w = min(image.shape[1] - clean_x, w + 2*padding)
            clean_h = min(image.shape[0] - clean_y, h + 2*padding)
            
            # Méthode 1: Essayer de deviner la couleur de fond
            # Échantillonner les pixels autour de la zone de texte
            border_pixels = []
            border_size = 8
            
            # Haut et bas de la zone
            for i in range(max(0, x - border_size), min(image.shape[1], x + w + border_size)):
                if clean_y - border_size >= 0:
                    border_pixels.append(image[clean_y - border_size, i])
                if clean_y + clean_h + border_size < image.shape[0]:
                    border_pixels.append(image[clean_y + clean_h + border_size, i])
            
            # Gauche et droite de la zone
            for j in range(max(0, y - border_size), min(image.shape[0], y + h + border_size)):
                if clean_x - border_size >= 0:
                    border_pixels.append(image[j, clean_x - border_size])
                if clean_x + clean_w + border_size < image.shape[1]:
                    border_pixels.append(image[j, clean_x + clean_w + border_size])
            
            # Calculer la couleur moyenne du fond
            if border_pixels:
                avg_color = np.mean(border_pixels, axis=0).astype(np.uint8)
            else:
                # Fallback: utiliser blanc
                avg_color = np.array([255, 255, 255], dtype=np.uint8)
            
            # Nettoyer la zone en la remplissant avec la couleur de fond
            image[clean_y:clean_y+clean_h, clean_x:clean_x+clean_w] = avg_color
            
            return image
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
            return image
    
    def place_translated_text(self, image: np.ndarray, detection: Dict, translation: str) -> np.ndarray:
        """Place le texte traduit dans la zone nettoyée"""
        try:
            x, y, w, h = detection["x"], detection["y"], detection["width"], detection["height"]
            
            # Convertir en PIL pour le traitement de texte
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            
            # Calculer la taille de police optimale
            max_font_size = min(h - 4, 40)  # Limiter la taille max
            min_font_size = 8
            optimal_font = None
            optimal_size = min_font_size
            
            # Essayer différentes tailles de police
            for font_size in range(max_font_size, min_font_size - 1, -2):
                try:
                    # Essayer d'abord avec une police système
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.load_default()
                    except:
                        continue
                
                # Mesurer le texte
                bbox = font.getbbox(translation)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Vérifier si le texte rentre dans la zone avec une marge
                if text_width <= w * 0.95 and text_height <= h * 0.9:
                    optimal_font = font
                    optimal_size = font_size
                    break
            
            # Si aucune police n'a fonctionné, utiliser la police par défaut
            if optimal_font is None:
                optimal_font = ImageFont.load_default()
            
            # Gérer le texte trop long en le découpant
            words = translation.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = optimal_font.getbbox(test_line)
                test_width = bbox[2] - bbox[0]
                
                if test_width <= w * 0.95:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Mot trop long, le garder quand même
                        lines.append(word)
                        current_line = ""
            
            if current_line:
                lines.append(current_line)
            
            # Si pas de lignes, utiliser le texte original
            if not lines:
                lines = [translation]
            
            # Calculer la position pour centrer le texte
            line_height = optimal_size + 2
            total_text_height = len(lines) * line_height
            start_y = y + (h - total_text_height) // 2
            
            # Dessiner chaque ligne
            for i, line in enumerate(lines):
                bbox = optimal_font.getbbox(line)
                line_width = bbox[2] - bbox[0]
                
                # Centrer horizontalement
                text_x = x + (w - line_width) // 2
                text_y = start_y + i * line_height
                
                # S'assurer que le texte reste dans les limites
                text_x = max(x, min(text_x, x + w - line_width))
                text_y = max(y, min(text_y, y + h - line_height))
                
                # Dessiner le texte en noir
                draw.text((text_x, text_y), line, fill="black", font=optimal_font)
            
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        except Exception as e:
            print(f"Erreur lors du placement du texte: {e}")
            return image
    
    def draw_translated_text(self, image: np.ndarray, detections: List[Dict], translations: List[str]) -> np.ndarray:
        """Remplace le texte original par le texte traduit"""
        try:
            result_image = image.copy()
            
            # Traiter chaque détection une par une
            for detection, translation in zip(detections, translations):
                # Étape 1: Nettoyer la zone de texte original
                result_image = self.clean_and_replace_text(result_image, detection, translation)
                
                # Étape 2: Placer le texte traduit
                result_image = self.place_translated_text(result_image, detection, translation)
            
            return result_image
        
        except Exception as e:
            print(f"Erreur lors du remplacement du texte: {e}")
            return image

# Instance du processeur
processor = MangaProcessor()

@app.get("/")
async def root():
    """Endpoint de test"""
    return {"message": "Scan Trad API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {"status": "healthy", "demo_mode": processor.demo_mode}

@app.post("/process-manga")
async def process_manga(
    file: UploadFile = File(...),
    target_language: str = "fr"
):
    """
    Traite une page de manga et retourne l'image traduite
    
    Args:
        file: Image de manga uploadée
        target_language: Langue cible (fr, es, de, it)
    
    Returns:
        JSON avec l'URL de l'image traduite et les détails du traitement
    """
    
    # Vérifier le format du fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    try:
        # Lire l'image uploadée
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Impossible de décoder l'image")
        
        # Étape 1: Détection des bulles
        detections = processor.detect_text_bubbles(image)
        
        # Étape 2: Extraction du texte
        extracted_texts = []
        for detection in detections:
            text = processor.extract_text_ocr(image, detection)
            extracted_texts.append(text)
        
        # Étape 3: Traduction
        translations = []
        for text in extracted_texts:
            translation = processor.translate_text(text, target_language)
            translations.append(translation)
        
        # Étape 4: Remplacement du texte original par le texte traduit
        result_image = processor.draw_translated_text(image, detections, translations)
        
        # Sauvegarder l'image résultat
        result_filename = f"result_{uuid.uuid4().hex}.png"
        result_path = os.path.join(TEMP_DIR, result_filename)
        cv2.imwrite(result_path, result_image)
        
        # Préparer la réponse
        response_data = {
            "success": True,
            "result_image_url": f"/download/{result_filename}",
            "statistics": {
                "bubbles_detected": len(detections),
                "texts_extracted": len(extracted_texts),
                "texts_translated": len(translations)
            },
            "detections": [
                {
                    "id": det["id"],
                    "position": {"x": det["x"], "y": det["y"], "width": det["width"], "height": det["height"]},
                    "confidence": det["confidence"],
                    "original_text": orig_text,
                    "translated_text": trans_text
                }
                for det, orig_text, trans_text in zip(detections, extracted_texts, translations)
            ],
            "target_language": target_language
        }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Télécharge une image traitée"""
    file_path = os.path.join(TEMP_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=filename
    )

@app.get("/languages")
async def get_supported_languages():
    """Retourne la liste des langues supportées"""
    return {
        "languages": [
            {"code": "fr", "name": "Français"},
            {"code": "es", "name": "Espagnol"},
            {"code": "de", "name": "Allemand"},
            {"code": "it", "name": "Italien"}
        ]
    }

@app.delete("/cleanup")
async def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    try:
        files_deleted = 0
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_deleted += 1
        
        return {"message": f"{files_deleted} fichiers supprimés", "success": True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du nettoyage: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 