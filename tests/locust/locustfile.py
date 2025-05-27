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

def check_response(response, expect_approval=True):
    """ Checks if the response is as expected. """
    if expect_approval:
        if "Order Approved" not in response.text:
            if "Not enough stock" in response.text or "Payment rejected" in response.text:
                response.success() # Order rejected because out of stock or random in transaction declined order
            else:
                response.failure("Legitimate order was rejected: " + response.text)
        else:
            response.success()
    else:
        if "Order not approved" not in response.text:
            response.failure("Fraudulent order was incorrectly accepted: " + response.text)
        else:
            response.success()

def build_payload(user_name, book_items, cc_number, cc_exp, cc_cvv):
    """ Builds the JSON for the purchase info"""
    return {
        "user": {
            "name": user_name,
            "contact": "loadtest@example.com"
        },
        "creditCard": {
            "number": cc_number,
            "expirationDate": cc_exp,
            "cvv": cc_cvv
        },
        "userComment": "Stress test",
        "items": book_items,
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

class NonFraudulent(HttpUser):
    """ Non-fraudulent users buying books"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        payload = build_payload("John Stone", items, "4111111111111111", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
                check_response(response, expect_approval=True)

    @task
    def order_2(self):
        """ Regular order, buying 2 different books"""
        book1 = BOOKS[1]
        book2 = BOOKS[2]
        items = [{"name": book1["name"], "author": book1["author"], "quantity": 1},
                {"name": book2["name"], "author": book2["author"], "quantity": 1}]
        payload = build_payload("Lisa Stone", items, "4111111111111111", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=True)

class Fraudulent(HttpUser):
    """Fraudulent users buying books"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Fraud, credit card number wrong"""
        book = BOOKS[0]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        # One number missing in cc_number
        payload = build_payload("John Stone", items, "411111111111111", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=False)

    @task
    def order_2(self):
        """ Fraud, credit card expiration date wrong"""
        book = BOOKS[1]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        # Old date in cc_exp
        payload = build_payload("John Stone", items, "4111111111111111", "12/20", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=False)


    @task
    def order_3(self):
        """ Fraud, credit card cvv too short"""
        book = BOOKS[2]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        # Too short cc_cvv
        payload = build_payload("John Stone", items, "4111111111111111", "12/25", "1")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=False)

    @task
    def order_4(self):
        """ Fraud, credit card number banned"""
        book = BOOKS[3]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        # Card in banned numbers
        payload = build_payload("John Stone", items, "0000000000000000", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=False)


class Mixed(HttpUser):
    """ Non-fraudulent and fraudulent users buying books"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        payload = build_payload("John Stone", items, "4111111111111111", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=True)

    @task
    def order_2(self):
        """ Fraud, credit card expired"""
        book = BOOKS[1]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        payload = build_payload("John Stone", items, "4111111111111111", "12/20", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=False)

class Conflicting(HttpUser):
    """ Non-fraudulent users buying the same book"""
    wait_time = between(3, 5)

    @task
    def order_1(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        payload = build_payload("John Stone", items, "4111111111111111", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=True)

    @task
    def order_2(self):
        """ Regular order, buying 1 book"""
        book = BOOKS[0]
        items = [{"name": book["name"], "author": book["author"], "quantity": 1}]
        payload = build_payload("Lisa Stone", items, "4111111111111111", "12/25", "123")

        with self.client.post("/checkout", json=payload, catch_response=True) as response:
            check_response(response, expect_approval=True)
