import requests
import json
from config import config
from db import DatabaseService
db_service=DatabaseService()

ATTENDEE_KEY = 'Token ' + config.ATTENDEE_API_KEY

def createbot(user_id:str, meeting_url: str = "", meeting_id:str = ""):
    url = config.ATTENDEE_APP_URL + '/api/v1/bots'
    headers = {'Authorization': ATTENDEE_KEY, 'Content-Type': "application/json"}
    payload = {'meeting_url': meeting_url, 'bot_name': 'Luca Bot'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    print(r.json())
    result = db_service.create_bot_record(user_id, r.json(), meeting_id)
    print(result)
    return result

def getrecording(bot_id: str = ""):
    url = config.ATTENDEE_APP_URL + '/api/v1/bots/' + bot_id + '/recording'
    headers = {'Authorization': ATTENDEE_KEY, 'Content-Type': "application/json"}
    r = requests.get(url, headers=headers)

    return r.json()

def botstatus(bot_id: str = ""):
    url = config.ATTENDEE_APP_URL + '/api/v1/bots/' + bot_id
    headers = {'Authorization': ATTENDEE_KEY, 'Content-Type': "application/json"}
    r = requests.get(url, headers=headers)

    return r.json()


def transcript(bot_id: str = ""):
    url = config.ATTENDEE_APP_URL + '/api/v1/bots/' + bot_id + '/transcript'
    headers = {'Authorization': ATTENDEE_KEY, 'Content-Type': "application/json"}
    r = requests.get(url, headers=headers)

    return r.json()


def audio(bot_id: str = ""):
    url = config.ATTENDEE_APP_URL + '/api/v1/bots/' + bot_id + '/output_audio'
    headers = {'Authorization': ATTENDEE_KEY, 'Content-Type': "application/json"}
    payload = {"type": "audio/mp3","data": ""}
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    return r.json()



