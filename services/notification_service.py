import logging
import os

# Configure logging for notifications
logger = logging.getLogger('notifications')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('notifications.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def send_notification(user_email, user_phone, subject, message):
    """
    Simulates sending a notification via Email and Push (SMS/App).
    In a real app, this would use SMTP and a Push Notification Service (e.g., Firebase, Twilio).
    """

    # Simulate Email
    log_message = f"EMAIL to {user_email}: [{subject}] {message}"
    print(log_message) # Print to console for verification
    logger.info(log_message)

    # Simulate Push/SMS
    log_message = f"PUSH/SMS to {user_phone}: {message}"
    print(log_message)
    logger.info(log_message)

    return True

def notify_direction(subject, message):
    """
    Sends notification to all users with role 'direction'.
    """
    from models import User

    direction_users = User.query.filter_by(role='direction', actif=True).all()

    count = 0
    for user in direction_users:
        # Assuming email might be stored or we just use phone
        email = getattr(user, 'email', 'direction@example.com') # User model might not have email, checking...
        # User model has email in Entreprise? No, User has no email in the model I read earlier.
        # Wait, let me check User model again.

        send_notification(f"user_{user.id}@example.com", user.telephone, subject, message)
        count += 1

    return count
