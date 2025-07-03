from fastapi import FastAPI, HTTPException, Depends
import firebase_admin
from firebase_admin import auth, credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate("lookoutai-firebase-adminsdk-po5xv-48c9278aaa.json")
firebase_admin.initialize_app(cred)


def verify_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        return {"status":True,"message": "Token is valid", "decoded_token": decoded_token}
    except Exception as e:
        return {"status":False,"message": e, "decoded_token": None}
