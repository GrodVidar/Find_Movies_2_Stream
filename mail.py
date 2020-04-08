import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
# requires an keys.py script with host, sender_mail and passwd variable declarations
from keys import *


def send_mail(mail, msg, name="Unknown"):
    port = 465
    message = MIMEMultipart("alternative")
    message['Subject'] = "Movie Search Form"
    message['From'] = formataddr((str(Header('Movie Search', 'utf-8')), sender_mail))
    message['To'] = receiver_mail

    text = f"""\
        Hello Vidar! ☺
        {name} sent this message:
        \"{msg}\""""
    html = f"""\
        <html>
          <body>
            <p>Hello Vidar! ☺<br>
               <a href="mailto:{mail}">{name}</a> sent this message:<br>
               \"{msg}\"
            </p>
          </body>
        </html>
        """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(sender_mail, passwd)
        server.sendmail(sender_mail, receiver_mail, message.as_string())
        server.close()


if __name__ == '__main__':
    send_to = input("enter your mail")
    send_name = input("enter message")
    send_mail(send_to.rstrip(), send_name.rstrip())
