from send_push_notification import send_message

def send_test_notification(user_id, body=None, data={}):
    data = {"name": "John Doe"}
    title = 'This is test'
    body = 'This is body for test notification'
    # fetch token from user
    token = 'crPak-I_TIevWd9vDkU1o3:APA91bG-FQm5_pA_MRdNkA68n7lmGvlPAMGM4XQnR-4oDg1gpWYbHgEWCdRDFWTs3RweGolaZ1BWhd2ofuZDZM4bJNTJuDCI-gL7xJxJFRaJW2Y0ePcGjLA'
    send_message(token, title, body, data)
