import jwt
from datetime import datetime, timedelta
from django.conf import settings

def get_access_token(payload, days):
    """Define get access token"""
    token = jwt.encode(
        {"exp": datatime.now() + timedelta((days=days), **payload)},
        settings.SECRET_KEY,
        algorithm="HS256"
    )