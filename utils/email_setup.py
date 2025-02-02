import os
from dotenv import load_dotenv
import smtplib
load_dotenv()

def setup_mail():
    """
    Sets up and returns an SMTP mail server instance.
    """
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.getenv("GMAIL"), os.getenv("APP_PASS"))
    return server
