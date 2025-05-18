# app/services/sms.py
def send_sms_notification(user_id, message):
    if message == "force_fail":
        raise Exception("Simulated SMS failure for testing retries")
    print(f"Sending SMS to user {user_id}: {message}")
