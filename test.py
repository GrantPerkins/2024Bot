import smtplib
import ssl

gmail_user = "gcperk20@gmail.com"
gmail_password = None
with open("pass.txt", 'r') as f:
    gmail_password = f.readline().rstrip('\n')
sent_from = gmail_user
to = "gcperkins@wpi.edu"


email_text = """\
From: gcperk20@gmail.com
To: {to}
Subject: [Dine On Campus] Reservation Confirmation

Dear {name},

Thank you for making a reservation through Dine On Campus. 

You are confirmed at:

Location: {hall}
Date: {date}
Time: {time}

You can cancel your reservation any time by logging into your account using the Dine On Campus mobile app or website. 

You can login at https://dineoncampus.com/wpi/login

Thank you!

------------------------------------ 

This email is sent from an automated inbox and is not checked for replies.

""".format(to=to, name="Grant", hall="morgan", date="today", time="now")

port = 465  # For SSL

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)


print("email sent")
