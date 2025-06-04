@echo off
cls
echo.
echo ===============================================
echo       🚀 Scan Trad - Dev Environment
echo ===============================================
echo.

REM Vérification Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé !
    echo Installez Docker Desktop : https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo 🐳 Docker détecté - Démarrage de l'environnement de développement...
echo.

REM Arrêter les conteneurs existants s'ils existent
docker-compose down >nul 2>&1

echo 📦 Construction et démarrage des services...
docker-compose up --build -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ Environnement de développement démarré !
    echo.
    echo 🌐 Interfaces disponibles :
    echo   👤 Frontend   : http://localhost:8501
    echo   🔗 Backend    : http://localhost:8000
    echo   📚 API Docs   : http://localhost:8000/docs
    echo.
    echo 📊 Commandes utiles :
    echo   .\docker-run.bat logs     - Voir les logs
    echo   .\docker-run.bat stop     - Arrêter les services
    echo   .\docker-run.bat restart  - Redémarrer
    echo.
    echo 🔄 Hot reload activé - Les modifications de code sont automatiques !
    echo.
    echo Appuyez sur une touche pour voir les logs en temps réel...
    pause >nul
    echo.
    echo 📊 Logs en temps réel (Ctrl+C pour arrêter) :
    docker-compose logs -f
) else (
    echo ❌ Erreur lors du démarrage
    echo Vérifiez les logs avec : .\docker-run.bat logs
    pause
) 