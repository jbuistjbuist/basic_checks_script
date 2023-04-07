from zenpy import Zenpy
from zenpy.lib.api_objects import Comment

import os

from dotenv import load_dotenv

load_dotenv()

email = os.getenv("agent_email")
token = os.getenv("zendesk_api_token")

def initialize_zendesk():
    zd_token = {
    'email': email,
    'token': token,
    'subdomain': 'ssensesupport'
    }

    global zenpy_client
    zenpy_client = Zenpy(**zd_token)


def update_ticket(ticket_number, check_info):

    ticket = zenpy_client.tickets(id=ticket_number)
    ticket.comment = Comment(body=check_info, public=False)
    zenpy_client.tickets.update(ticket)
