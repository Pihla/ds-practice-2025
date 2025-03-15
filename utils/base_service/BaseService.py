class BaseService:
    def __init__(self, service_name="BaseService"):
        self.service_name = service_name
        print(f"{self.service_name} initialized.")