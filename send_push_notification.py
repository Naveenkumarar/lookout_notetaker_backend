import firebase_admin
from firebase_admin import credentials, messaging

# Replace 'path/to/your/serviceAccountKey.json' with the actual path
cred = credentials.Certificate('service_acc.json')
firebase_admin.initialize_app(cred)

def send_message(device_token, title, body, data):
    # Example for sending to a specific device token
    registration_token = device_token

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data,
        token=registration_token,
    )

    try:
        response = messaging.send(message)
        print(f'Successfully sent message: {response}')
    except Exception as e:
        print(f'Error sending message: {e}')

    # Example for sending to a topic
    # topic = 'news'
    # message = messaging.Message(
    #     notification=messaging.Notification(
    #         title='Breaking News!',
    #         body='Check out the latest updates.',
    #     ),
    #     topic=topic,
    # )
    # try:
    #     response = messaging.send(message)
    #     print(f'Successfully sent message to topic: {response}')
    # except Exception as e:
    #     print(f'Error sending message to topic: {e}')