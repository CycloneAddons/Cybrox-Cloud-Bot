import smtplib
from utils.email_setup import setup_mail

def check_mail(bot):
    """
    Ensures that the mail server is functional. Reinitializes if disconnected.
    """
    if bot.mail is None:
        bot.mail = setup_mail()
    else:
        try:
            bot.mail.noop()  # Check if the connection is active
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPException):
            print("Reinitializing mail server...")
            bot.mail = setup_mail()
