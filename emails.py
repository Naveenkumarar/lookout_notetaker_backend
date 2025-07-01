from send_email import send_email
from jinja2 import Environment, FileSystemLoader

def send_email_invite(recipients_addr, user_id):
    data = {"name": "John Doe"}
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('invite.html')
    html_content = template.render(data)
    send_email(None, recipients_addr, "Lookout Notetaker Invite", html_content)


def share_email_invite(recipients_addr, user_id, meeting_id):
    username = user_id.replace("@gmail.com", "")
    
    data = {
        "name": username,
        "meeting_id": meeting_id
    }
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('share.html')
    html_content = template.render(data)
    send_email(None, recipients_addr, "Lookout Notetaker Meeting Invite", html_content)
