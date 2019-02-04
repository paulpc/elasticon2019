import requests
import logging
import smtplib
from email.mime.text import MIMEText


def alert(message, system, recipients, conf):
    """ sends an alert email based on the message and the recipient list"""
    msg = MIMEText(str(message))

    msg['Subject'] = 'The health status of %s is concerning' % system
    msg['From'] = conf['alerts']['sender']
    msg['To'] = ';'.join(recipients)

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(conf['alerts']['host'])
    s.sendmail(conf['alerts']['sender'], recipients, msg.as_string())
    s.quit()

def internal_teams_message(message, system, teams, colour):
    """sends a card on teams"""
    card={
    "@context": "http://schema.org/extensions",
    "@type": "MessageCard",
    "themeColor": colour,
    "title": system,
    "text": message
    }
    for webhook in teams:        
        wh_resp=requests.post(url=webhook, json=card)
        if wh_resp.status_code != 200:
            logging.info(wh_resp.text)
