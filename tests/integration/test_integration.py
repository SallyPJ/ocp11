from datetime import datetime
from app import clubs, competitions
from flask import url_for
import html


def test_index_route(client):
    """Integration test: Verify that the homepage loads correctly."""

    response = client.get("/")

    # Ensure the request was successful
    assert response.status_code == 200

    # Check if the page title is correct
    assert b"<title>GUDLFT Registration</title>" in response.data

    # Verify the presence of the login form
    assert b'<form action="/showSummary" method="post">' in response.data

    # Verify the presence of the "Points Overview" link
    assert b'<a href="/points-overview">Points Overview</a>' in response.data


def test_show_summary_valid(client):
    clubs.append({"name": "Test Club", "email": "test@club.com", "points": 50})
    competitions.append({
        "name": "Test Competition",
        "date": datetime(2099, 1, 1, 12, 0, 0),
        "numberOfPlaces": "10"
    })
    response = client.post('/showSummary', data={"email": "test@club.com"})
    assert response.status_code == 200
    # On s'attend à ce que le template welcome.html soit affiché et contienne le nom du club
    assert b"Welcome, test@club.com" in response.data
    assert b"Points available: 50" in response.data
    assert b"Test Competition" in response.data
    assert b"Number of Places: 10" in response.data
    assert b"Book Places" in response.data


# Test de la route showSummary pour un email invalide (POST /showSummary)
def test_show_summary_invalid_with_redirect(client):
    clubs.append({"name": "Test Club", "email": "test@club.com", "points": 50})
    response = client.post('/showSummary', data={"email": "nonexistent@club.com"}, follow_redirects=True)

    # Verify the response
    assert response.status_code == 200  # Redirect to index
    # Decode response to text and normalize HTML entities
    response_text = html.unescape(response.data.decode())
    assert "Sorry, that email wasn't found." in response_text


def test_show_summary_invalid_without_redirect(client):
    """Integration test: Invalid email without redirection."""

    # Add a valid club
    clubs.append({"name": "Test Club", "email": "test@club.com", "points": 50})

    # Simulate login with an incorrect email (no redirect)
    response = client.post('/showSummary', data={"email": "nonexistent@club.com"}, follow_redirects=False)

    # Verify response is a redirect (302)
    assert response.status_code == 302

    # Check if the response redirects to the index page
    assert response.headers["Location"] == url_for("index", _external=False)


def test_book_valid(client):
    """Integration test: Booking page should display correctly when both club and competition exist."""

    # Add a test club
    clubs.append({"name": "Test Club", "email": "test@club.com", "points": 50})

    # Add a test competition
    competitions.append({
        "name": "Test Competition",
        "date": "2099-12-31 12:00:00",  # Future date
        "numberOfPlaces": "10"
    })

    # Request the booking page
    response = client.get('/book/Test%20Competition/Test%20Club')

    # Verify response
    assert response.status_code == 200

    # Decode response
    response_text = html.unescape(response.data.decode())

    # Check that the competition and club are correctly displayed
    assert "Test Competition" in response_text
    assert "Test Club" in response_text
    assert "Places available: 10" in response_text
    assert "How many places?" in response_text  # Ensure booking form is shown


def test_cannot_book_past_competition(client):
    """Test that a club cannot book places in a past competition."""

    # Add a test club with enough points
    club_name = "Test Club"
    club_email = "test@club.com"
    clubs.append({"name": club_name, "email": club_email, "points": "10"})

    # Convert string to datetime object before adding the competition
    past_competition_name = "Past Competition"
    past_date = "2020-01-01 12:00:00"

    competitions.append({"name": past_competition_name, "date": past_date, "numberOfPlaces": "5"})

    # Simulate a login with the test club
    response = client.post("/showSummary", data={"email": club_email}, follow_redirects=True)

    # Ensure the page loads correctly
    assert response.status_code == 200
    response_text = html.unescape(response.data.decode())

    # Verify that the message indicating the competition has ended is displayed
    assert "This competition has already ended." in response_text

    # Ensure the "Book Places" button is not present for this competition
    assert f'<a href="/book/{past_competition_name}/{club_name}">Book Places</a>' not in response_text


def test_points_are_deducted_after_booking(client):
    """Test that points are correctly deducted from the club after booking places in a competition."""

    # Add a test club with sufficient points
    club_name = "Test Club 11"
    club_email = "test@club.com"
    initial_points = 15  # Points before booking
    clubs.append({"name": club_name, "email": club_email, "points": str(initial_points)})

    # Add a future competition with available places
    competition_name = "Test Competition"
    competitions.append({"name": competition_name, "date": "2099-12-31 12:00:00", "numberOfPlaces": "10"})

    # Simulate the club logging in
    response = client.post("/showSummary", data={"email": club_email}, follow_redirects=True)
    assert response.status_code == 200

    # Book places
    places_to_book = 5  # Number of places to book
    response = client.post("/purchasePlaces", data={
        "competition": competition_name,
        "club": club_name,
        "places": str(places_to_book)
    }, follow_redirects=True)

    assert response.status_code == 200
    response_text = html.unescape(response.data.decode())

    # Ensure the booking confirmation message appears
    assert "Great-booking complete!" in response_text

    # Calculate the expected remaining points
    expected_remaining_points = initial_points - places_to_book

    # Verify that the club's points have been updated correctly
    assert f"Points available: {expected_remaining_points}" in response_text, "Club points were not updated correctly!"


def test_purchase_places(client):
    """Test a successful booking when conditions are met."""

    clubs.append({"name": "Test Club 12", "email": "test@club.com", "points": "10"})
    competitions.append({
        "name": "Test Competition 2",
        "date": "2099-12-31 12:00:00",
        "numberOfPlaces": "10"
    })

    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition 2",
        "club": "Test Club 12",
        "places": "3"
    }, follow_redirects=True)

    assert response.status_code == 200
    response_text = html.unescape(response.data.decode())
    print(response_text)
    assert "Great-booking complete!" in response_text
    assert "Number of Places: 7" in response_text  # 10 - 3 = 7
    assert "Points available: 7" in response_text  # 10 - 3 = 7


def test_purchase_places_exceed_limit(client):
    """Test booking fails when trying to reserve more than 12 places."""

    clubs.append({"name": "Test Club 3", "email": "test@club.com", "points": "20"})
    competitions.append({
        "name": "Test Competition",
        "date": "2099-12-31 12:00:00",
        "numberOfPlaces": "20"
    })

    # ✅ Envoi direct au backend (bypass du formulaire HTML)
    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition",
        "club": "Test Club 3",
        "places": "13"  # 🚨 Plus que la limite autorisée (12)
    }, follow_redirects=True)

    assert response.status_code == 200  # La requête aboutit

    response_text = html.unescape(response.data.decode())

    # ✅ Vérifier que le message d'erreur s'affiche bien
    assert "You cannot book more than 12 places at once." in response_text

    # ✅ Vérifier que les places **n'ont pas été modifiées**
    assert "Number of Places: 20" in response_text


def test_purchase_places_exceed_club_points(client):
    """Test booking fails when trying to reserve more than club points."""

    clubs.append({"name": "Test Club 4", "email": "test@club.com", "points": "5"})
    competitions.append({
        "name": "Test Competition",
        "date": "2099-12-31 12:00:00",
        "numberOfPlaces": "20"
    })

    # ✅ Envoi direct au backend (bypass du formulaire HTML)
    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition",
        "club": "Test Club 4",
        "places": "6"  # 🚨 Plus que la limite autorisée (12)
    }, follow_redirects=True)

    assert response.status_code == 200  # La requête aboutit

    response_text = html.unescape(response.data.decode())

    # ✅ Vérifier que le message d'erreur s'affiche bien
    assert "You do not have enough points to book this many places." in response_text

    # ✅ Vérifier que les places **n'ont pas été modifiées**
    assert "Number of Places: 20" in response_text


def test_points_overview(client):
    """Integration test: Verify that the points overview page loads correctly."""

    clubs.append({"name": "Club A", "email": "clubA@email.com", "points": "10"})
    clubs.append({"name": "Club B", "email": "clubB@email.com", "points": "20"})

    response = client.get("/points-overview")

    assert response.status_code == 200

    response_text = html.unescape(response.data.decode())

    assert "Public Clubs and Points Overview" in response_text
    assert "<td>Club A</td>" in response_text
    assert "<td>10</td>" in response_text
    assert "<td>Club B</td>" in response_text
    assert "<td>20</td>" in response_text
    assert 'Back to Home' in response_text


def test_logout(client):
    """Integration test: Verify that the user logout."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # On s'attend à retrouver le contenu de la page index après redirection
    assert b"GUDLFT Registration" in response.data
