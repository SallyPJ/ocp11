import pytest
import shutil
import os
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Define the JSON files
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

    yield

    # Restore the original JSON files
    shutil.copy(BACKUP_CLUBS_FILE, CLUBS_FILE)
    shutil.copy(BACKUP_COMPETITIONS_FILE, COMPETITIONS_FILE)

    # Delete backup files
    os.remove(BACKUP_CLUBS_FILE)
    os.remove(BACKUP_COMPETITIONS_FILE)
