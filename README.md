# 📚 Scan Trad - Traducteur de Manga IA

Application de développement pour traduire automatiquement les pages de manga grâce à l'IA.

## 🏗️ Structure du projet

```
Scan-Trad-project/
├── backend/               # API FastAPI
│   └── main.py
├── frontend/              # Interface Streamlit
│   └── app.py
├── docker-compose.yml     # Configuration Docker
├── Dockerfile.backend     # Image backend
├── Dockerfile.frontend    # Image frontend
├── requirements.txt       # Dépendances Python
├── dev-start.bat         # 🚀 Script de démarrage rapide
└── docker-run.bat        # Scripts de gestion Docker
```

## 🚀 Démarrage ultra-rapide

### 1️⃣ Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installé

### 2️⃣ Lancement en 1 clic
```bash
# Démarrage complet avec construction automatique
.\dev-start.bat
```

### 3️⃣ Accès immédiat
- **🖥️ Interface utilisateur** : http://localhost:8501
- **🔗 API Backend** : http://localhost:8000
- **📚 Documentation API** : http://localhost:8000/docs

## 🛠️ Commandes de développement

```bash
# Démarrage rapide
.\dev-start.bat

# Voir les logs en temps réel
.\docker-run.bat logs

# Arrêter l'environnement
.\docker-run.bat stop

# Redémarrer après modifications
.\docker-run.bat restart

# Nettoyage complet
.\docker-run.bat clean
```

## 🔧 Fonctionnalités

### 🎯 **Mode Démonstration**
- Simulation complète du pipeline de traduction
- Détection de bulles simulée (YOLO)
- OCR simulé avec textes d'exemple
- Traduction multilingue simulée
- Rendu fonctionnel sur l'image

### 🌐 **Langues supportées**
- Français, Espagnol, Allemand, Italien

### ⚡ **Développement optimisé**
- **Hot reload** : Modifications instantanées
- **Isolation Docker** : Aucun conflit de dépendances
- **API REST** : Backend/Frontend séparés
- **Logs en temps réel** : Debug facilité

## 🐳 Architecture Docker

```
┌─────────────────────────────────────────────┐
│                Docker Host                 │
├─────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐        │
│  │  Frontend   │◄──►│   Backend   │        │
│  │ (Streamlit) │    │  (FastAPI)  │        │
│  │ Port: 8501  │    │ Port: 8000  │        │
│  └─────────────┘    └─────────────┘        │
│         │                    │             │
│  ┌─────────────┐    ┌─────────────┐        │
│  │ Hot Reload  │    │ Hot Reload  │        │
│  │ ./frontend/ │    │ ./backend/  │        │
│  └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────┘
```

## 📊 Pipeline de traitement

1. **Upload** → Image envoyée via Streamlit
2. **API** → Transmission vers FastAPI
3. **Détection** → Simulation YOLO (bulles de texte)
4. **OCR** → Extraction de texte simulée
5. **Traduction** → Conversion multilingue
6. **Rendu** → Application du texte traduit
7. **Download** → Récupération de l'image finale

## 🔮 Technologies

- **Backend** : FastAPI + Uvicorn + OpenCV + PIL
- **Frontend** : Streamlit + Requests + Pandas
- **DevOps** : Docker + Docker Compose
- **Images** : NumPy + OpenCV + Pillow

## 🚀 Développement

### Structure optimisée pour le dev
- ✅ **Hot reload** automatique
- ✅ **Health checks** intégrés
- ✅ **Logs structurés**
- ✅ **Variables d'environnement** configurées
- ✅ **Réseau Docker** dédié

### Workflow de développement
1. Modifier le code (backend ou frontend)
2. Les changements sont automatiquement détectés
3. Les services se rechargent instantanément
4. Tester sur http://localhost:8501

## 🐛 Dépannage

### Services ne démarrent pas
```bash
.\docker-run.bat logs  # Voir les erreurs
.\docker-run.bat clean # Nettoyage complet
.\dev-start.bat        # Redémarrage
```

### Ports occupés
```bash
netstat -ano | findstr :8501
taskkill /PID [PID] /F
```

---

**💻 Environnement de développement optimisé avec Docker** 

**🔄 Hot reload activé - Codez et voyez les changements instantanément !**