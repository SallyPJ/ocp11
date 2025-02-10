from locust import HttpUser, task


class ProjectPerfTest(HttpUser):
    host = "http://localhost:5000"

    @task()
    def index(self):
        self.client.get('/')

    @task()
    def show_summary(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task()
    def points_overview(self):
        self.client.get("/points-overview")
