import sys
import os


# Add the project root (P11) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

import pytest
import shutil
import os

# Définition des fichiers JSON
CLUBS_FILE = "clubs.json"
COMPETITIONS_FILE = "competitions.json"
BACKUP_CLUBS_FILE = "clubs_backup.json"
BACKUP_COMPETITIONS_FILE = "competitions_backup.json"

@pytest.fixture(scope="function", autouse=True)
def restore_json_files():
    """
    Fixture to backup the original JSON files before running a test and restore them after.
    """

    # Sauvegarde des fichiers JSON avant d'exécuter un test
    shutil.copy(CLUBS_FILE, BACKUP_CLUBS_FILE)
    shutil.copy(COMPETITIONS_FILE, BACKUP_COMPETITIONS_FILE)

    yield  # Exécute le test ici

    # Restauration des fichiers après le test
    shutil.copy(BACKUP_CLUBS_FILE, CLUBS_FILE)
    shutil.copy(BACKUP_COMPETITIONS_FILE, COMPETITIONS_FILE)

    # Suppression des fichiers temporaires
    os.remove(BACKUP_CLUBS_FILE)
    os.remove(BACKUP_COMPETITIONS_FILE)