@echo off
REM Script lanceur pour le Planificateur de tâches Windows
REM Il active l'environnement WSL et lance le script Python

cd %~dp0
wsl -d Ubuntu -u tahar -e bash -l -c "cd /home/tahar/project/AMP && python3 school_assistant/daily_check.py >> daily_log.txt 2>&1"
