import jwt
from datetime import datetime, timedelta
import sys

sys.path.append("..")
from FuntooNote.settings import SECRET_KEY


class JWTAuth:
    @staticmethod
    def getToken(username, password, secretKey=SECRET_KEY):
        pay_load = {
            'username': username,
            'password': password,
            'exp': datetime.utcnow() + timedelta(minutes=5)
        }
        jwtToken = jwt.encode(pay_load, key=secretKey)
        return jwtToken

    @staticmethod
    def verifyToken(jwtToken, secretKey=SECRET_KEY):
        try:
            verificationStatus = jwt.decode(jwtToken, key=secretKey, algorithms='HS256')
            return verificationStatus
        except jwt.ExpiredSignatureError:
            return False
