# gudlift-registration

1. Why


    This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

# Project 11 - gudlift-registration

## Description
**gudlift-registration** is a web application designed for managing sports competitions. It allows clubs to register, book spots for competitions, and track their status in real-time.

## Main Features
- **Authentication**: Secure login for clubs.
- **Competition Management**: Display available competitions and their status.
- **Spot Reservation**: Clubs can reserve a certain number of spots for a given competition.
- **Data Management**: Storage and retrieval of club and competition information via JSON files.
- **Automated Testing**: Test suite to ensure the proper functioning of the application.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: JSON (files `clubs.json` and `competitions.json`)
- **Testing**: Pytest & Coverage
- **Virtual Environment**: Virtualenv

## Installation and Execution
### Prerequisites
- Python 3.x
- Virtualenv

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/SallyPJ/P11.git
   cd P11
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   flask run
   ```
   The application will be accessible at `http://127.0.0.1:5000/`.

## Project Structure
```
P11/
│── app.py                 # Main application file
│── clubs.json             # Club data
│── competitions.json      # Competition data
│── requirements.txt       # Dependencies
│── templates/             # HTML Templates
│── tests/                 # Test files
│── README.md              # Project documentation
```

## Running Tests

### Tests report
The application includes a test suite to ensure proper functionality. To run tests, use:
```sh
pytest
```
### Coverage report
To generate a test coverage report:
```sh
coverage run -m pytest
coverage report -m
```
### Load Testing

To execute a load test, navigate to the project directory and run:
```sh
locust -f tests/locustfile.py
```

Then, open a browser and visit http://localhost:8089/ to configure and start the load test.



