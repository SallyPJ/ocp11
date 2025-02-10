from locust import HttpUser, task, between

class ProjectPerfTest(HttpUser):
    host = "http://localhost:5000"

    @task()
    def index(self):
        self.client.get('/')

    @task()
    def show_summary(self):
        # Simuler l'envoi d'un email pour accéder à la page de résumé
        # Remplacez "test@example.com" par un email valide présent dans votre JSON
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task()
    def points_overview(self):
        self.client.get("/points-overview")
