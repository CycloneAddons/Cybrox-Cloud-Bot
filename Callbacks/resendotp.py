import re
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.email_util import check_mail

callback_data = "resendotp"

def handle_callback(bot, call):
 email = extract_emails(call.message.text)
 if call.message.chat.id not in bot.user_otps:
    bot.delete_message(call.message.chat.id, call.message.message_id)
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(InlineKeyboardButton("Send OTP", callback_data='sendotp'),
                    InlineKeyboardButton("Change Email", callback_data='changeEmail'))

    bot.send_message(call.message.chat.id, f"Opps! It's Look like Old Session Restarted Please Send OTP Again To:\n\nEmail: {email}\n", reply_markup=markup)  
 else:       
    otp = bot.user_otps[call.message.chat.id]
    check_mail(bot)
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }}
            .header {{ background-color: #4CAF50; padding: 10px 0; text-align: center; color: white; }}
            .header h1 {{ margin: 0; }}
            .content {{ padding: 20px; background-color: white; }}
            .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #777; }}
            .button {{ display: inline-block; padding: 10px 20px; color: white; background-color: #4CAF50; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Cybrox Cloud!</h1>
            </div>
            <div class="content">
                <p>Dear User,</p>
                <p>Thank you for signing up for our Cybrox Cloud. We're excited to have you on board!</p>
                <p>Below Is Your OTP Copy and Send It To Bot.</p>
                <p><a class="button">{otp}</a></p>
                <p>If you have any questions, feel free to reach out to us at <a href="mailto:clutchcloudpro@gmail.com">clutchcloudpro@gmail.com</a>.</p>
                <p>Best regards,<br>Cybrox Cloud</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Cybrox Cloud. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


    otpmail = MIMEMultipart()
    otpmail['From'] = "clutchcloudpro@gmail.com"
    otpmail['To'] = email
    otpmail['Subject'] = "Here IS Your OTP !!!"


    otpmail.attach(MIMEText(html_message, "html"))
    bot.mail.sendmail(email, email, otpmail.as_string())

    if call.message.chat.id not in bot.otp_success_id:
     bot.otp_success_id[call.message.chat.id] = None

    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(InlineKeyboardButton("Resend OTP Again", callback_data='resendotp'),
               InlineKeyboardButton("Change Email", callback_data='changeEmail'))
    
    frst = bot.send_message(call.message.chat.id, f"OTP successfully Resend to\n EMAIL: {email}", reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    bot.otp_success_id[call.message.chat.id] = frst.message_id



def extract_emails(msg):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_regex, msg)  # Use search instead of findall
    return match.group(0) if match else None
