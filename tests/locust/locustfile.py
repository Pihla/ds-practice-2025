from locust import HttpUser, task, between

BOOKS = [
    {"name": "The Lord of the Rings", "author": "J.R.R. Tolkien"},
    {"name": "The Twilight", "author": "Stephenie Meyer"},
    {"name": "The Book Thief", "author": "Markus Zusak"},
    {"name": "Pride and Prejudice", "author": "Jane Austin"},
]

# Use pip install locust
# run locust command when in the folder where locustfile.py is while docker container of the system is running
# add host to be http://localhost:8081 and specify nr of users

class NonFraudulent(HttpUser):
    """ Non-fraudulent users buying books"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        payload = {
            "user": {
                "name": f"John Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
                if "Order Approved" not in response.text:
                    response.failure("Legitimate order was rejected")
                else:
                    response.success()

    @task
    def order_2(self):
        """ Regular order, buying larger amount of books (10)"""
        book = BOOKS[1]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 10}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order Approved" not in response.text:
                response.failure("Legitimate order was rejected")
            else:
                response.success()

    @task
    def order_3(self):
        """ Regular order, buying 2 different books"""
        book1 = BOOKS[2]
        book2 = BOOKS[3]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [
                {"name": book1["name"], "author": book1["author"], "quantity": 1},
                {"name": book2["name"], "author": book2["author"], "quantity": 1},
            ],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order Approved" not in response.text:
                response.failure("Legitimate order was rejected")
            else:
                response.success()

class Fraudulent(HttpUser):
    """Fraudulent users buying books"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Fraud, credit card number wrong"""
        book = BOOKS[0]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "411111111111111", # One number missing
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order not approved" not in response.text:
                response.failure("Fraudulent order was incorrectly accepted" + response.text)
            else:
                response.success()

    @task
    def order_2(self):
        """ Fraud, credit card expiration date wrong"""
        book = BOOKS[1]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/20", # Old date
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order not approved" not in response.text:
                response.failure("Fraudulent order was incorrectly accepted" + response.text)
            else:
                response.success()

    @task
    def order_3(self):
        """ Fraud, credit card cvv too short"""
        book = BOOKS[2]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "12" # Too short cvv
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order not approved" not in response.text:
                response.failure("Fraudulent order was incorrectly accepted" + response.text)
            else:
                response.success()

    @task
    def order_4(self):
        """ Fraud, credit card number banned"""
        book = BOOKS[3]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "0000000000000000", # Banned credit card umber
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order not approved" not in response.text:
                response.failure("Fraudulent order was incorrectly accepted" + response.text)
            else:
                response.success()

class Mixed(HttpUser):
    """ Non-fraudulent and  fraudulent users buying books"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        payload = {
            "user": {
                "name": f"John Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order Approved" not in response.text:
                response.failure("Legitimate order was rejected")
            else:
                response.success()

    @task
    def order_2(self):
        """ Fraud, credit card number wrong"""
        book = BOOKS[1]
        payload = {
            "user": {
                "name": f"Lisa Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "411111111111111",  # One number missing
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order not approved" not in response.text:
                response.failure("Fraudulent order was incorrectly accepted" + response.text)
            else:
                response.success()

class Conflicting(HttpUser):
    """ Non-fraudulent users buying the same book"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        payload = {
            "user": {
                "name": f"John Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order Approved" not in response.text:
                response.failure("Legitimate order was rejected")
            else:
                response.success()

    @task
    def order_2(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        payload = {
            "user": {
                "name": f"John Stone",
                "contact": "loadtest@example.com"
            },
            "creditCard": {
                "number": "4111111111111111",
                "expirationDate": "12/25",
                "cvv": "123"
            },
            "userComment": "Stress test order",
            "items": [{"name": book["name"], "author": book["author"], "quantity": 1}],
            "billingAddress": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701",
                "country": "USA"
            },
            "shippingMethod": "Standard",
            "giftWrapping": True,
            "termsAccepted": True
        }

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            if "Order Approved" not in response.text:
                response.failure("Legitimate order was rejected")
            else:
                response.success()
