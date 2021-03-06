import uuid
from redis import Redis


class CarService:
    def __init__(self):
        self.r = Redis(decode_responses=True)
        self.MAX_COMPLETED_ORDERS_IN_MEMORY = (
            0  # should be 200 according to spec
        )

    def clean(self):
        """
        Clean the database and start fresh.
        """

        self.r.flushdb()

    def mechanic_create(self, name, password):
        """
        Create a new mechanic.
        """

        if name == "tokens" or name == "names" or name == "login":
            return print("[Mechanic] Create: Invalid name")

        if self.r.sismember("mechanic:names", name):
            return print(
                "[Mechanic] A mechanic with the name '"
                + name
                + "' already exists!"
            )

        self.r.hmset(
            "mechanic:" + name,
            {"name": name, "password": password},
        )
        self.r.sadd("mechanic:names", name)
        print(
            "[Mechanic] Create: Mechanic with the name '"
            + name
            + "' created successfully!"
        )

    def mechanic_delete(self, mechanic_name):
        """
        Delete a mechanic and their tokens.
        :param mechanic_name: The name of the mechanic
        """
        if not self.r.sismember("mechanic:names", mechanic_name):
            return print(
                "[Mechanic] No mechanic with the name '"
                + mechanic_name
                + "' exists!"
            )

        self.r.delete("mechanic:" + mechanic_name)
        self.r.zrem("parts_replaced", mechanic_name)
        for mechanic_token, mechanic_name in self.r.hscan_iter(
            "mechanic:tokens", mechanic_name
        ):
            self.r.hdel("mechanic:tokens", mechanic_token)

        print(
            "[Mechanic] Delete: Successfully deleted '{}'!".format(
                mechanic_name
            )
        )

    def mechanic_login(self, name, password):
        """
        Log in as a mechanic.
        :param name: The name of the mechanic.
        :param password: The password of the mechanic.
        """
        if not self.r.sismember("mechanic:names", name):
            print(
                "[Mechanic] Login: A mechanic with the name '"
                + name
                + "' does not exist!"
            )
            return None

        if not password == self.r.hget("mechanic:" + name, "password"):
            print("[Mechanic] Login: Invalid password")
            return None

        token = uuid.uuid4().__str__()
        self.r.hset("mechanic:tokens", token, name)
        self.r.pfadd("mechanic:login", name)
        return token

    def mechanic_count_logged_in(self):
        """
        Count logged in users.
        :return:
        """
        logged_in_n = self.r.pfcount("mechanic:login")
        if logged_in_n == 0 or logged_in_n > 1:
            print(
                "[Mechanic] There are {} logged in users at the moment.".format(
                    logged_in_n
                )
            )
        else:
            print(
                "[Mechanic] There is {} logged in user at the moment.".format(
                    logged_in_n
                )
            )

    def mechanic_invalidate_tokens(self):
        """
        Invalidate all current tokens.
        """
        self.r.delete("mechanic:tokens")
        self.r.delete("mechanic:login")
        print("[Mechanic] Invalidated all tokens!")

    def mechanic_describe(self, mechanic_token):
        """
        Describe current mechanic.
        """
        if not self.r.hexists("mechanic:tokens", mechanic_token):
            return print("[Mechanic] Describe: This token does not exist!")

        mechanic_name = self.r.hget("mechanic:tokens", mechanic_token)

        print(
            "[Mechanic] Describe: Currently logged in with account "
            + mechanic_name
        )

    def mechanic_reset_password(self, mechanic_name, new_password):
        """
        Reset password for mechanic.
        """
        if not self.r.sismember("mechanic:names", mechanic_name):
            return print(
                "[Mechanic] No mechanic with the name '"
                + mechanic_name
                + "' exists!"
            )

        self.r.hset(
            "mechanic:" + mechanic_name, mapping={"password": new_password}
        )
        print(
            "[Mechanic] Password reset: New password '{}' set for mechanic '{}'".format(
                new_password, mechanic_name
            )
        )

    def mechanic_get_parts_replaced(self, mechanic_token):
        """
        Get the cost of the parts replaced by mechanic in total.
        """
        if not self.r.hexists("mechanic:tokens", mechanic_token):
            return print("[Order] Add Note: This token does not exist!")

        mechanic_name = self.r.hget("mechanic:tokens", mechanic_token)

        found = False

        for mechanic, cost in self.r.zscan_iter(
            "parts_replaced", mechanic_name
        ):
            found = True
            print(
                "[Mechanic] {} has replaced parts for {} HUF in total.".format(
                    mechanic, cost
                )
            )

        if not found:
            print(
                "[Mechanic] {} has not replaced any parts yet.".format(
                    mechanic_name
                )
            )

    def mechanic_top(self):
        """
        List the best working mechanics in the shop!
        """
        if not self.r.exists("parts_replaced"):
            return print("[Mechanic] Top: No parts have been replaced yet.")

        print("[Mechanic] Top 5 mechanics:")
        i = 1
        for mechanic, earning in self.r.zrevrange(
            "parts_replaced", 0, 4, withscores=True
        ):
            print(
                "{}. {} has replaced parts for {} HUF".format(
                    i, mechanic, earning
                )
            )
            i = i + 1

    def order_record(
        self, license_plate_number, car_name, car_year_of_production, symptoms
    ):
        """
        Record a new order.
        :param license_plate_number: The license plate number of the car.
        :param car_name: The name of the car.
        :param car_year_of_production: The year of production of the car.
        :param symptoms:  The symptoms of the car.
        """

        order_id = uuid.uuid4().__str__()
        self.r.hmset(
            "order:" + order_id,
            {
                "license_plate_number": license_plate_number,
                "car_name": car_name,
                "car_year_of_production": car_year_of_production,
                "symptoms": symptoms,
                "is_complete": 0,
            },
        )
        self.r.sadd("order:ids", order_id)
        print("[Order] Create: Order created successfully!")
        return order_id

    def order_add_note(self, mechanic_token, order_id, part_name, cost):
        """
        Add a note to an existing order (replace a part and log it).

        :param mechanic_token: The token of the logged-in mechanic.
        :param order_id: The id of the order.
        :param part_name: Part being replaced.
        :param cost: Cost of the replacement and the part.
        """
        if not self.r.hexists("mechanic:tokens", mechanic_token):
            return print("[Order] Add Note: This token does not exist!")

        if not self.r.sismember("order:ids", order_id):
            return print("[Order] Add Note: This order does not exist!")

        self.r.zadd(
            "order:notes:" + order_id,
            {part_name: cost},
        )

        mechanic_name = self.r.hget("mechanic:tokens", mechanic_token)

        if self.r.zscore("parts_replaced", mechanic_name):
            self.r.zincrby("parts_replaced", cost, mechanic_name)
        else:
            self.r.zadd("parts_replaced", {mechanic_name: cost})

    def order_complete(self, mechanic_token, order_id):
        """
        Complete an order (set its status to true, calculate the costs) of the
        repair.
        :param mechanic_token: the token of the logged-in mechanic
        :param order_id: the id of the order
        """
        if not self.r.sismember("order:ids", order_id):
            return print(
                "[Order] Complete: Order with the id '"
                + order_id
                + "' does not exist!"
            )

        if not self.r.hexists("mechanic:tokens", mechanic_token):
            return print(
                "[Order] Complete: The token '"
                + mechanic_token
                + "' does not exist!"
            )

        self.r.hset("order:" + order_id, mapping={"is_complete": 1})
        self.r.lpush("order:completed", order_id)
        print(
            "[Order] Complete: Order '" + order_id + "' completed successfully!"
        )
        self.order_invoice(order_id, expected_or_total="total")

    def order_delete_completed(self):
        """
        Delete completed orders and create a file to store the data in a
        persistent database (MySQL).
        :return:
        """
        if self.r.llen("order:completed") > self.MAX_COMPLETED_ORDERS_IN_MEMORY:
            for order_id in self.r.lrange("order:completed", 0, -1):
                order: dict = self.r.hgetall("order:" + order_id)
                order_notes = self.r.zrange(
                    "order:notes:" + order_id, 0, -1, withscores=True
                )
                # TODO: generate query and save to file `queries_to_run`
                query = """
                INSERT INTO orders(
                    order_id, car_name, car_year_of_production, symptoms
                ) VALUES('{}', '{}', {}, '{}');
                """.format(
                    order_id,
                    order.get("car_name"),
                    order.get("car_year_of_production"),
                    order.get("symptoms"),
                )

                if order_notes:
                    for part_replaced, cost in order_notes:
                        query_order_notes = """
                        INSERT INTO order_notes(order_id, part_replaced, cost)
                        VALUES ('{}', '{}', {});
                        """.format(
                            order_id, part_replaced, cost
                        )
                        query = query + query_order_notes

                with open("queries_to_run", "a") as file:
                    file.write(query)

                self.r.delete("order:" + order_id)
                self.r.delete("order:notes:" + order_id)
                self.r.lrem("order:completed", 0, order_id)

    def order_status(self, order_id):
        """
        Query order status.
        """
        if not self.r.sismember("order:ids", order_id):
            return print(
                "[Order] Status: Order with the id '"
                + order_id
                + "' does not exist!"
            )

        order_data: dict = self.r.hgetall("order:" + order_id)

        order_status = (
            "completed" if order_data.get("is_complete") else "work in progress"
        )
        print("[Order {}]".format(order_id))
        print(
            "Car: {} {}".format(
                order_data.get("car_year_of_production"),
                order_data.get("car_name"),
            )
        )
        print("Symptom(s): {}".format(order_data.get("symptoms")))
        print("Status: {}".format(order_status))

        self.order_invoice(order_id)

    def order_invoice(self, order_id, expected_or_total="expected"):
        """
        Generate the invoice for an order.
        """
        order_notes: tuple = self.r.zrange(
            "order:notes:" + order_id, 0, -1, withscores=True
        )
        order_sum = 0
        if order_notes:
            print("Notes:")
            for part, cost in order_notes:
                print("  - Replaced '{}' for {} HUF ".format(part, cost))
                order_sum = order_sum + cost
            if expected_or_total == "expected":
                print("Expected cost: {} HUF".format(order_sum))
            elif expected_or_total == "total":
                print("Total cost: {} HUF".format(order_sum))

    def order_list(self, mechanic_token):
        """
        List all orders.
        """
        if not self.r.hexists("mechanic:tokens", mechanic_token):
            return print("[Order] List: This token does not exist!")

        for order_id in self.r.smembers("order:ids"):
            print(order_id)
            if order_id:
                self.order_status(order_id)
