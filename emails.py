from send_email import send_email
from jinja2 import Environment, FileSystemLoader

def send_email_invite(recipients_addr, user_id):
    data = {"name": "John Doe"}
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('invite.html')
    html_content = template.render(data)
    send_email(None, recipients_addr, "Lookout Notetaker Invite", html_content)
