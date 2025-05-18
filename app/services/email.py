# app/services/email.py
def send_email_notification(user_id, message):
    if message == "force_fail":
        raise Exception("Simulated email failure for testing retries")
    print(f"Sending Email to user {user_id}: {message}")
