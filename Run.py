#!/usr/bin/env python3

from CarService import CarService

driver = CarService()

driver.clean()

# Get logged in users
driver.mechanic_count_logged_in()

# Create a new mechanic
driver.mechanic_create("Johnny", "secret")
driver.mechanic_create("Mike", "secret")
driver.mechanic_create("ToBeDeleted", "secret")

# Create a new mechanic - failure (duplicate name)
driver.mechanic_create("Johnny", "secret")

# Delete mechanic
driver.mechanic_delete("ToBeDeleted")

# Login as mechanic
mechanic_token = driver.mechanic_login("Johnny", "secret")
if mechanic_token:
    print("Logged in with token " + mechanic_token)

# Get logged in users
driver.mechanic_count_logged_in()

mechanic2_token = driver.mechanic_login("Mike", "secret")
if mechanic_token:
    print("Logged in with token " + mechanic2_token)


# Login as mechanic -- failure
mechanic_token_failure = driver.mechanic_login("asd", "asdQWE123")

# Describe account
driver.mechanic_describe(mechanic_token)

# Get parts replaced in total
driver.mechanic_get_parts_replaced(mechanic_token)
driver.mechanic_get_parts_replaced(mechanic2_token)

# Reset password
driver.mechanic_reset_password("Johnny", "secret2")

# Record order
order1_id = driver.order_record(
    "WOB123",
    "Volkswagen Arteon Shooting Brake 2.0 BiTDI SCR 4motion",
    2020,
    "Does not start.",
)

# Add note to order
driver.order_add_note(mechanic_token, order1_id, "Starter Motor", 140000)
driver.order_add_note(
    mechanic_token, order1_id, "Diesel Particulate Filter", 420000
)
driver.order_add_note(mechanic2_token, order1_id, "Battery", 40000)

# Add note to order - failure - invalid mechanic token
driver.order_add_note("invalid", order1_id, "Starter Motor", 140000)

# Add note to order - failure - invalid order id
driver.order_add_note(mechanic_token, "", "Starter Motor", 140000)

# Order status
driver.order_status(order1_id)

# Order status - failure - invalid id
driver.order_status("")

# Order list
driver.order_list(mechanic_token)

# Order complete
driver.order_complete(mechanic_token, order1_id)

# Best mechanic
driver.mechanic_top()

# Get parts replaced in total
driver.mechanic_get_parts_replaced(mechanic_token)
driver.mechanic_get_parts_replaced(mechanic2_token)

# Get logged in users
driver.mechanic_count_logged_in()

# Invalidate all sessions
driver.mechanic_invalidate_tokens()

# Get logged in users
driver.mechanic_count_logged_in()
