# auth.py
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from auth.jwt_utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def token_required(token: str = Depends(oauth2_scheme)):
    return decode_token(token)
