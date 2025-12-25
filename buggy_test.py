import os

def get_user_data(user_id):
    # SECURITY RISK: Hardcoded API Key
    api_key = "12345-secret-key"

    # LOGIC BUG: This string formatting is vulnerable to SQL Injection
    # if this were a real SQL query
    query = "SELECT * FROM users WHERE id = " + user_id

    print(f"Executing: {query}")
    return {"id": user_id, "name": "John Doe"}

def calculate_total(items):
    total = 0
    # PERFORMANCE ISSUE: Iterating nicely, but let's add a useless sleep
    for item in items:
        import time
        time.sleep(0.1) 
        total += item['price']
    return total