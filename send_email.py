import os
import smtplib
from config import config
import mimetypes
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

def mime_init(from_addr, recipients_addr, subject, body):
    """
    :param str from_addr:           The email address you want to send mail from
    :param list recipients_addr:    The list of email addresses of recipients
    :param str subject:             Mail subject
    :param str body:                Mail body
    :return:                        MIMEMultipart object
    """

    msg = MIMEMultipart()

    msg['From'] = from_addr
    msg['To'] = ','.join(recipients_addr)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    return msg


def send_email(from_addr, recipients_addr, subject, body, files_path=None):
    """
    :param str user:                Sender's email userID
    :param str password:            sender's email password
    :param str from_addr:           The email address you want to send mail from
    :param list recipients_addr:    List of (or space separated string) email addresses of recipients
    :param str subject:             Mail subject
    :param str body:                Mail body
    :param list files_path:         List of paths of files you want to attach
    :param str server:              SMTP server (port is choosen 587)
    :return:                        None
    """

    #   assert isinstance(recipents_addr, list)
    FROM = config.EMAIL_FROM if from_addr is None else from_addr
    TO = recipients_addr if isinstance(recipients_addr, list) else recipients_addr.split(' ')
    PASS = config.EMAIL_PASS
    SERVER = config.EMAIL_SERVER
    EMAIL_PORT = config.EMAIL_PORT
    SUBJECT = subject
    BODY = body
    msg = mime_init(FROM, TO, SUBJECT, BODY)

    for file_path in files_path or []:
        with open(file_path, "rb") as fp:
            part = MIMEBase('application', "octet-stream")
            part.set_payload((fp).read())
            # Encoding payload is necessary if encoded (compressed) file has to be attached.
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(file_path))
            msg.attach(part)

    if SERVER == 'localhost':   # send mail from local server
        # Start local SMTP server
        server = smtplib.SMTP(SERVER)
        text = msg.as_string()
        server.send_message(msg)
    else:
        # Start SMTP server at port 587
        server = smtplib.SMTP(SERVER, EMAIL_PORT)
        server.starttls()
        # Enter login credentials for the email you want to sent mail from
        server.login(config.EMAIL_USER, PASS)
        text = msg.as_string()
        # Send mail
        server.sendmail(FROM, TO, text)

    server.quit()



