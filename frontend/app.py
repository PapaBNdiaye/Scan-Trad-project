import streamlit as st
import requests
import pandas as pd
from PIL import Image
import io
import time
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Scan Trad - Interface",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration de l'API Backend
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86C1;
        margin-bottom: 30px;
    }
    .upload-section {
        border: 2px dashed #3498DB;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .result-section {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .success-box {
        background-color: #D5F4E6;
        border: 1px solid #27AE60;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #FADBD8;
        border: 1px solid #E74C3C;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .stats-container {
        background-color: #EBF5FB;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Vérifie si l'API backend est accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_supported_languages():
    """Récupère la liste des langues supportées depuis l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/languages")
        if response.status_code == 200:
            data = response.json()
            return {lang["name"]: lang["code"] for lang in data["languages"]}
        else:
            return {"Français": "fr", "Espagnol": "es", "Allemand": "de", "Italien": "it"}
    except:
        return {"Français": "fr", "Espagnol": "es", "Allemand": "de", "Italien": "it"}

def process_manga_image(uploaded_file, target_language):
    """Envoie l'image à l'API pour traitement"""
    try:
        # Préparer les données pour l'API
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {
            "target_language": target_language
        }
        
        # Envoyer la requête à l'API
        response = requests.post(
            f"{API_BASE_URL}/process-manga",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_detail = response.json().get("detail", "Erreur inconnue")
            return None, f"Erreur API: {error_detail}"
    
    except requests.exceptions.Timeout:
        return None, "Timeout: Le traitement a pris trop de temps"
    except requests.exceptions.ConnectionError:
        return None, "Erreur de connexion: Vérifiez que l'API backend est lancée"
    except Exception as e:
        return None, f"Erreur inattendue: {str(e)}"

def download_result_image(image_url):
    """Télécharge l'image résultat depuis l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}{image_url}")
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None
    except Exception as e:
        st.error(f"Erreur lors du téléchargement de l'image: {e}")
        return None

def main():
    # En-tête principal
    st.markdown('<h1 class="main-header">📚 Scan Trad - Traducteur de Manga IA</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <p style="font-size: 18px; color: #5D6D7E;">
        Interface frontend pour la traduction automatique de pages de manga
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Vérification de l'état de l'API
    api_status = check_api_health()
    
    if not api_status:
        st.error("""
        🚨 **API Backend non accessible**
        
        Assurez-vous que l'API backend est lancée :
        ```
        cd backend
        python main.py
        ```
        Ou avec uvicorn :
        ```
        uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
        ```
        """)
        st.stop()
    
    # Sidebar avec configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Vérification du statut API
        st.success("✅ API Backend connectée")
        
        # Sélection de la langue
        languages = get_supported_languages()
        selected_language_name = st.selectbox(
            "Langue cible :",
            list(languages.keys()),
            index=0
        )
        target_language = languages[selected_language_name]
        
        st.markdown("---")
        
        # Informations sur l'API
        st.header("🔗 API Info")
        st.info(f"""
        **URL API :** {API_BASE_URL}
        
        **Endpoints disponibles :**
        - POST `/process-manga` - Traitement
        - GET `/languages` - Langues supportées
        - GET `/health` - État de l'API
        """)
        
        st.markdown("---")
        
        # Statistiques de session
        if 'session_stats' in st.session_state:
            st.header("📊 Statistiques")
            stats = st.session_state.session_stats
            st.metric("Images traitées", stats.get('processed', 0))
            st.metric("Total bulles détectées", stats.get('total_bubbles', 0))
            st.metric("Total textes traduits", stats.get('total_translations', 0))
        
        st.markdown("---")
        
        # Actions de maintenance
        st.header("🧹 Maintenance")
        if st.button("Nettoyer les fichiers temporaires"):
            try:
                response = requests.delete(f"{API_BASE_URL}/cleanup")
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ {data['message']}")
                else:
                    st.error("❌ Erreur lors du nettoyage")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    # Interface principale
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📤 Upload de l'image de manga")
        
        uploaded_file = st.file_uploader(
            "Choisissez une page de manga :",
            type=["jpg", "jpeg", "png"],
            help="Formats supportés: JPG, JPEG, PNG (max 10MB)"
        )
        
        if uploaded_file is not None:
            # Afficher l'image originale
            image = Image.open(uploaded_file)
            st.image(image, caption="Image originale", use_container_width=True)
            
            # Informations sur l'image
            st.write(f"**Nom :** {uploaded_file.name}")
            st.write(f"**Taille :** {len(uploaded_file.getvalue())} bytes")
            st.write(f"**Dimensions :** {image.size[0]}x{image.size[1]} pixels")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Bouton de traitement
            if st.button("🚀 Lancer la traduction", type="primary", use_container_width=True):
                
                # Barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("Traitement en cours..."):
                    status_text.text("📤 Upload vers l'API...")
                    progress_bar.progress(25)
                    
                    # Appel à l'API
                    result_data, error = process_manga_image(uploaded_file, target_language)
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        progress_bar.progress(100)
                        status_text.text("✅ Traitement terminé!")
                        
                        # Stocker les résultats dans la session
                        st.session_state.last_result = result_data
                        
                        # Mise à jour des statistiques
                        if 'session_stats' not in st.session_state:
                            st.session_state.session_stats = {
                                'processed': 0, 
                                'total_bubbles': 0, 
                                'total_translations': 0
                            }
                        
                        stats = result_data.get('statistics', {})
                        st.session_state.session_stats['processed'] += 1
                        st.session_state.session_stats['total_bubbles'] += stats.get('bubbles_detected', 0)
                        st.session_state.session_stats['total_translations'] += stats.get('texts_translated', 0)
                        
                        st.rerun()
        else:
            st.markdown('</div>', unsafe_allow_html=True)
            st.info("👆 Uploadez une image de manga pour commencer")
    
    with col2:
        st.subheader("📋 Résultats de la traduction")
        
        if 'last_result' in st.session_state:
            result_data = st.session_state.last_result
            
            # Télécharger et afficher l'image traduite
            image_url = result_data.get('result_image_url')
            if image_url:
                translated_image = download_result_image(image_url)
                
                if translated_image:
                    st.image(translated_image, caption="Image traduite", use_container_width=True)
                    
                    # Bouton de téléchargement
                    buf = io.BytesIO()
                    translated_image.save(buf, format="PNG")
                    
                    st.download_button(
                        label="📥 Télécharger l'image traduite",
                        data=buf.getvalue(),
                        file_name=f"manga_traduit_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Impossible de charger l'image traduite")
            
            # Afficher les statistiques du traitement
            st.markdown('<div class="stats-container">', unsafe_allow_html=True)
            st.subheader("📊 Statistiques du traitement")
            
            stats = result_data.get('statistics', {})
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Bulles détectées", stats.get('bubbles_detected', 0))
            with col_b:
                st.metric("Textes extraits", stats.get('texts_extracted', 0))
            with col_c:
                st.metric("Textes traduits", stats.get('texts_translated', 0))
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Détails des détections
            st.subheader("🔍 Détails des détections")
            
            detections = result_data.get('detections', [])
            
            if detections:
                # Créer un DataFrame pour afficher les résultats
                detection_data = []
                for detection in detections:
                    detection_data.append({
                        "ID": detection['id'],
                        "Confiance": f"{detection['confidence']:.2f}",
                        "Texte original": detection['original_text'],
                        "Traduction": detection['translated_text'],
                        "Position X": detection['position']['x'],
                        "Position Y": detection['position']['y']
                    })
                
                df = pd.DataFrame(detection_data)
                st.dataframe(df, use_container_width=True)
                
                # Affichage détaillé avec expandeurs
                for i, detection in enumerate(detections):
                    with st.expander(f"Bulle {detection['id']} - Confiance: {detection['confidence']:.2f}"):
                        col_x, col_y = st.columns(2)
                        
                        with col_x:
                            st.write("**Texte original :**")
                            st.write(f"_{detection['original_text']}_")
                        
                        with col_y:
                            st.write(f"**Traduction ({selected_language_name}) :**")
                            st.write(f"**{detection['translated_text']}**")
                        
                        pos = detection['position']
                        st.write(f"**Position :** x={pos['x']}, y={pos['y']}, largeur={pos['width']}, hauteur={pos['height']}")
            else:
                st.info("Aucune détection trouvée dans cette image")
        
        else:
            st.info("👈 Uploadez et traitez une image pour voir les résultats ici")
    
    # Section d'informations
    st.markdown("---")
    
    with st.expander("ℹ️ À propos de Scan Trad"):
        st.markdown("""
        ### 🎯 Architecture du projet
        
        **Frontend (Streamlit)** ↔️ **Backend (FastAPI)** ↔️ **Modèles IA**
        
        ### 🔧 Technologies utilisées
        - **FastAPI** : API backend pour le traitement
        - **Streamlit** : Interface utilisateur moderne
        - **OpenCV** : Traitement d'image
        - **PIL** : Manipulation d'images
        
        ### 📊 Pipeline de traitement
        1. **Upload** : Envoi de l'image vers l'API
        2. **Détection** : Identification des bulles de texte
        3. **OCR** : Extraction du texte
        4. **Traduction** : Conversion vers la langue cible
        5. **Rendu** : Application du texte traduit
        6. **Téléchargement** : Récupération du résultat
        
        ### 🚀 Version actuelle
        - Mode démonstration avec données simulées
        - Architecture backend/frontend séparée
        - Communication via API REST
        
        ### 🔮 Améliorations futures
        - Intégration de YOLO pour la détection réelle
        - Ajout de Tesseract OCR
        - Modèles de traduction Transformers
        - Support de plus de langues
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7F8C8D;">
        <p>🚀 Scan Trad - Architecture Backend/Frontend</p>
        <p>Backend: FastAPI | Frontend: Streamlit</p>
        <p>🎭 Mode Démonstration</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 