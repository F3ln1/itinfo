from locust import HttpUser, task, between


class ITINFOUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(3)
    def view_home(self):
        self.client.get("/")

    @task(5)
    def view_news_list(self):
        self.client.get("/news/")

    @task(4)
    def view_news_list_it(self):
        self.client.get("/news/?category=it")

    @task(4)
    def view_news_list_science(self):
        self.client.get("/news/?category=science")

    @task(3)
    def view_news_list_tech(self):
        self.client.get("/news/?category=tech")

    @task(2)
    def view_register(self):
        self.client.get("/register/")

    @task(2)
    def view_login(self):
        self.client.get("/login/")
