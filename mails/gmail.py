from __future__ import print_function

import base64
import mimetypes
import os
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send(subject, message, attachment_filename, src, dst):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)
        mime_message = EmailMessage()

        # headers
        mime_message['To'] = dst
        mime_message['From'] = src
        mime_message['Subject'] = subject

        # text
        mime_message.set_content(message, 'html')

        with open(attachment_filename, 'rb') as fp:
            mime_message.add_attachment(fp.read(), maintype='application/pdf', subtype= "pdf", filename=attachment_filename)        
        
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())

        print(F'Message Id: {send_message["id"]}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        draft = None
    return send_message
