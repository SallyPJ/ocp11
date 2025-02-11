import pytest
import json
from app import (loadClubs, loadCompetitions, saveClubs, saveCompetitions,
                 showSummary, app, index, book, purchasePlaces, logout, points_overview)
from flask import url_for
from datetime import datetime


def test_loadClubs(mocker):
    """
    Tests the `loadClubs` function to ensure it correctly loads clubs from a JSON file.

    - Mocks a file containing a list of clubs.
    - Ensures that the function returns a list.
    - Verifies that the club information is correctly extracted.
    """

    # Mock JSON file content
    mock_clubs_data = {"clubs": [{"name": "Simply Lift", "email": "admin@simplylift.co", "points": 10}]}

    # Mock open() to return the mock JSON data
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_clubs_data)))

    # Run the function
    clubs = loadClubs()

    # Assertions
    assert isinstance(clubs, list)  # Should return a list
    assert len(clubs) == 1  # One club in mock data
    assert clubs[0]["name"] == "Simply Lift"
    assert clubs[0]["email"] == "admin@simplylift.co"
    assert clubs[0]["points"] == 10


def test_loadCompetitions(mocker):
    """
    Tests the `loadCompetitions` function to ensure it correctly loads competitions from a JSON file.

    - Mocks a file containing a list of competitions.
    - Ensures the function returns a list.
    - Checks that the competition's date is converted to a datetime object.
    - Verifies that the number of available places is correctly parsed.
    """
    # Mock JSON file content
    mock_competitions_data = {
        "competitions": [
            {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "10"}
        ]
    }

    # Mock open() to return the mock JSON data
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_competitions_data)))

    # Run the function
    competitions = loadCompetitions()

    # Assertions
    assert isinstance(competitions, list)
    assert len(competitions) == 1
    assert competitions[0]["name"] == "Fall Classic"
    assert isinstance(competitions[0]["date"], datetime)  # Ensure date is converted
    assert competitions[0]["date"].year == 2025
    assert int(competitions[0]["numberOfPlaces"]) == 10


def test_saveClubs(mocker):
    """
    Tests the `saveClubs` function to ensure it correctly writes club data to a JSON file.

    - Mocks file opening to prevent actual writing.
    - Checks that the file is opened in write mode.
    - Verifies that `json.dump()` (or equivalent) is called to write data.
    """
    # Mock open() to prevent file writing
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # Run function
    saveClubs()

    # Check if the file was written
    mock_open.assert_called_once_with("clubs.json", "w")

    # Check if json.dump() was called
    mock_open().write.assert_called()


def test_saveCompetitions(mocker):
    """
    Tests the `saveCompetitions` function to ensure it correctly writes competition data to a JSON file.

    - Mocks file opening to prevent actual writing.
    - Ensures that the file is opened in write mode.
    - Verifies that `json.dump()` (or equivalent) is called to write data.
    """
    # Mock open() to prevent file writing
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # Run function
    saveCompetitions()

    # Check if the file was written
    mock_open.assert_called_once_with("competitions.json", "w")

    # Check if json.dump() was called
    mock_open().write.assert_called()


def test_index_route(mocker):
    """
    Unit test for the `index` route.
    - Ensures the function calls `render_template('index.html')`.
    - Verifies that the response is valid.
    """
    # Mock render_template to prevent actual template rendering
    mock_render_template = mocker.patch('app.render_template', return_value="Mocked Index Page")

    # Create an application context to allow Flask functions to work
    with app.app_context():
        response = index()

    # Ensure render_template is called with the correct template
    mock_render_template.assert_called_once_with('index.html')
    # Ensure the function returns the mocked response correctly
    assert response == "Mocked Index Page"


def test_show_summary_valid_email(mocker):
    """
    Unit test for `showSummary` when a valid email is provided.
    - Ensures the correct club is retrieved.
    - Competitions should be marked as past/future correctly.
    - The function should return the correct template.
    """
    # Mock clubs and competitions
    mock_clubs = [{'name': 'ClubTest', 'email': 'test@email.com', 'points': 10}]
    mock_competitions = [
        {'name': 'Future Comp', 'date': datetime(2025, 1, 1, 12, 0, 0)},
        {'name': 'Past Comp', 'date': datetime(2020, 1, 1, 12, 0, 0)}
    ]
    mocker.patch('app.clubs', mock_clubs)
    mocker.patch('app.competitions', mock_competitions)

    # Mock datetime.now()
    mocker.patch('app.datetime', autospec=True)
    mocker.patch('app.datetime.now', return_value=datetime(2023, 1, 1, 12, 0, 0))

    # Mock render_template
    mock_render_template = mocker.patch('app.render_template')

    # Create Flask request context
    with app.test_request_context(method='POST', data={'email': 'test@email.com'}):
        response = showSummary()

    assert response is not None

    # Ensure competitions are marked correctly
    assert mock_competitions[0]['is_past'] is False  # Future competition
    assert mock_competitions[1]['is_past'] is True   # Past competition

    # Ensure render_template is called with correct arguments
    mock_render_template.assert_called_once_with(
        'welcome.html', club=mock_clubs[0], competitions=mock_competitions
    )


def test_show_summary_invalid_email(mocker):
    """
    Unit test for `showSummary` when an invalid email is provided.
    - Ensures a flash message is displayed.
    - The function should redirect to the index page.
    """
    # Mock clubs (does not contain the invalid email)
    mock_clubs = [{'name': 'ClubTest', 'email': 'test@email.com', 'points': 10}]
    mocker.patch('app.clubs', mock_clubs)

    # Mock flash and redirect
    mock_flash = mocker.patch('app.flash')

    # Configurer redirect pour qu'il renvoie un objet avec status_code=302
    mock_redirect_response = mocker.MagicMock()
    mock_redirect_response.status_code = 302
    mock_redirect = mocker.patch('app.redirect', return_value=mock_redirect_response)

    # Create Flask application context
    with app.app_context():
        with app.test_request_context(method='POST', data={'email': 'wrong@email.com'}):
            response = showSummary()

            # Vérifier que response est bien la redirection mockée
            assert response == mock_redirect.return_value
            assert response.status_code == 302  # 🔥 Test fixé ici

            # Get the expected redirect URL inside the request context
            expected_redirect_url = url_for('index')

            # Ensure flash is called with the correct message
            mock_flash.assert_called_once_with("Sorry, that email wasn't found.")

            # Ensure redirect is called with the correct URL
            mock_redirect.assert_called_once_with(expected_redirect_url)


def test_book_valid_club_competition(mocker):
    """
    Unit test for `book()` when both club and competition exist.
    - Ensures the function retrieves the correct data.
    - Checks if `booking.html` is rendered with the right parameters.
    """
    # Mock club and competition data
    mock_clubs = [{'name': 'Test Club', 'email': 'test@email.com', 'points': 10}]
    mock_competitions = [{'name': 'Test Competition', 'date': '2025-10-22 13:30:00', 'numberOfPlaces': '10'}]

    # Patch global variables
    mocker.patch('app.clubs', mock_clubs)
    mocker.patch('app.competitions', mock_competitions)

    # Mock render_template
    mock_render_template = mocker.patch('app.render_template')

    # Create Flask application context
    with app.app_context():
        response = book('Test Competition', 'Test Club')

    assert response is not None

    # Ensure render_template is called with booking.html and correct parameters
    mock_render_template.assert_called_once_with('booking.html', club=mock_clubs[0], competition=mock_competitions[0])


@pytest.fixture
def mock_data():
    """Fixture providing test data for clubs and competitions."""
    return {
        "club": {"name": "Test Club", "email": "test@email.com", "points": "10"},
        "competition": {"name": "Test Competition", "numberOfPlaces": "5"},
    }


def test_purchase_places_success(mocker, mock_data):
    """Test successful booking when the club has enough points and the competition has enough places."""
    mocker.patch("app.clubs", [mock_data["club"]])
    mocker.patch("app.competitions", [mock_data["competition"]])
    mock_flash = mocker.patch("app.flash")
    mock_render = mocker.patch("app.render_template", return_value="Success")

    with app.test_request_context(method="POST", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "3"
    }):
        response = purchasePlaces()
    assert response is not None
    assert response == "Success"
    assert int(mock_data["competition"]["numberOfPlaces"]) == 2  # Convert to int
    assert int(mock_data["club"]["points"]) == 7  # Convert to int
    mock_flash.assert_called_once_with("Great-booking complete!")
    mock_render.assert_called_once()


def test_purchase_places_not_enough_places(mocker, mock_data):
    """Test booking fails if requested places exceed available places."""
    mocker.patch("app.clubs", [mock_data["club"]])
    mocker.patch("app.competitions", [mock_data["competition"]])
    mock_flash = mocker.patch("app.flash")
    mock_render = mocker.patch("app.render_template", return_value="Fail")

    with app.test_request_context(method="POST", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "6"
    }):
        response = purchasePlaces()
    assert response is not None
    assert response == "Fail"
    assert int(mock_data["competition"]["numberOfPlaces"]) == 5  # Convert to int
    assert int(mock_data["club"]["points"]) == 10  # Convert to int
    mock_flash.assert_called_once_with("Not enough places available in this competition.")
    mock_render.assert_called_once()


def test_purchase_places_not_enough_points(mocker, mock_data):
    """Test booking fails if requested places exceed the club's available points."""
    mocker.patch("app.clubs", [mock_data["club"]])
    mocker.patch("app.competitions", [mock_data["competition"]])
    mock_flash = mocker.patch("app.flash")
    mock_render = mocker.patch("app.render_template", return_value="Fail")

    with app.test_request_context(method="POST", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "11"
    }):
        response = purchasePlaces()
    assert response is not None
    assert response == "Fail"
    assert int(mock_data["competition"]["numberOfPlaces"]) == 5  # Convert to int
    assert int(mock_data["club"]["points"]) == 10  # Convert to int
    mock_flash.assert_called_once_with("You do not have enough points to book this many places.")
    mock_render.assert_called_once()


def test_purchase_places_over_limit(mocker, mock_data):
    """Test booking fails if a club tries to book more than 12 places in one transaction."""
    mocker.patch("app.clubs", [mock_data["club"]])
    mocker.patch("app.competitions", [mock_data["competition"]])
    mock_flash = mocker.patch("app.flash")
    mock_render = mocker.patch("app.render_template", return_value="Fail")

    with app.test_request_context(method="POST", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "13"
    }):
        response = purchasePlaces()
    assert response is not None
    assert response == "Fail"
    assert int(mock_data["competition"]["numberOfPlaces"]) == 5  # Convert to int
    assert int(mock_data["club"]["points"]) == 10  # Convert to int
    mock_flash.assert_called_once_with("You cannot book more than 12 places at once.")
    mock_render.assert_called_once()


def test_purchase_places_invalid_number(mocker, mock_data):
    """Test booking fails when a club tries to book 0 or negative places."""
    mocker.patch("app.clubs", [mock_data["club"]])
    mocker.patch("app.competitions", [mock_data["competition"]])
    mock_flash = mocker.patch("app.flash")
    mock_render = mocker.patch("app.render_template", return_value="Fail")

    with app.test_request_context(method="POST", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "0"
    }):
        response = purchasePlaces()
    assert response is not None
    assert response == "Fail"
    assert int(mock_data["competition"]["numberOfPlaces"]) == 5  # Convert to int
    assert int(mock_data["club"]["points"]) == 10  # Convert to int
    mock_flash.assert_called_once_with("Invalid number of places.")
    mock_render.assert_called_once()


def test_points_overview(mocker):
    """Test GET /points-overview to ensure it renders the correct template with club data."""

    # Mock clubs
    mock_clubs = [
        {"name": "Club One", "points": 10},
        {"name": "Club Two", "points": 15}
    ]

    # Mock global variable clubs
    mocker.patch("app.clubs", mock_clubs)

    # Mock render_template
    mock_render = mocker.patch("app.render_template", return_value="Rendered Page")

    # Simulate a GET request
    response = points_overview()

    # Assertions
    mock_render.assert_called_once_with("points_overview.html", clubs=mock_clubs)
    assert response == "Rendered Page"


def test_logout(mocker):
    """Test GET /logout to ensure it redirects to index."""

    # Mock redirect and url_for
    mock_redirect = mocker.patch("app.redirect")
    mock_url_for = mocker.patch("app.url_for", return_value="/")

    # Simulate a GET request to /logout
    response = logout()

    # Assertions
    mock_url_for.assert_called_once_with("index")
    mock_redirect.assert_called_once_with("/")
    assert response == mock_redirect.return_value
