import time
from locust import HttpUser, task, between

class MlaosInfraUser(HttpUser):
    # Simulates a user waiting 1–5 seconds between requests
    wait_time = between(1, 5)

    @task(1)
    def get_root(self):
        """Tests the basic heartbeat of the API."""
        self.client.get("/")  # matches @app.get("/")



