import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


@pytest.fixture(scope="function")
def driver():
    """Initialize and close the WebDriver."""
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def test_points_overview_display(driver):
    """Functional test: Check if the points overview page displays correctly."""

    driver.get("http://127.0.0.1:5000/points-overview")
    time.sleep(2)

    assert "Public Clubs and Points Overview" in driver.page_source

    clubs_data = {
        "Simply Lift": "0",
        "Iron Temple": "1",
        "She Lifts": "12"
    }

    for club, points in clubs_data.items():
        assert club in driver.page_source  # Vérifier que le club est affiché
        assert points in driver.page_source  # Vérifier que le bon nombre de points est affiché


def test_user_login_and_book_places(driver):
    """Functional test: User logs in, books places for a competition, and logs out."""

    driver.get("http://127.0.0.1:5000/")
    time.sleep(2)

    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys("kate@shelifts.co.uk")  # Email du club "She Lifts"
    email_input.send_keys(Keys.RETURN)  # Appuyer sur "Entrée"
    time.sleep(2)

    assert "Welcome, kate@shelifts.co.uk" in driver.page_source

    book_link = driver.find_element(By.LINK_TEXT, "Book Places")
    book_link.click()
    time.sleep(2)

    assert "How many places?" in driver.page_source

    places_input = driver.find_element(By.NAME, "places")
    places_input.send_keys("3")  # Réserver 3 places
    places_input.send_keys(Keys.RETURN)
    time.sleep(2)

    assert "Great-booking complete!" in driver.page_source

    logout_link = driver.find_element(By.LINK_TEXT, "Logout")
    logout_link.click()
    time.sleep(2)

    assert "GUDLFT Registration" in driver.page_source


def test_invalid_email_login(driver):
    """Functional test: Attempt to login with an invalid email."""

    driver.get("http://127.0.0.1:5000")

    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys("wrong@email.com")

    email_input.send_keys(Keys.RETURN)

    time.sleep(2)

    flash_messages = driver.find_elements(By.TAG_NAME, "li")  # Flask affiche souvent les messages dans des <li>
    error_found = any("Sorry, that email wasn't found." in msg.text for msg in flash_messages)

    assert error_found, "Expected error message was not displayed!"
