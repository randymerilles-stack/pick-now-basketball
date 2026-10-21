"""Single-owner login. Secret hash lives only in service environment."""
from collections import deque
import hashlib
import hmac
from http.cookies import SimpleCookie
import os
import secrets
import threading
import time

COOKIE='__Host-picknow_session'
TTL=30*24*60*60
LOCK=threading.Lock()
SESSIONS={}
ATTEMPTS=deque()

LOGIN='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pick Now — Private access</title><style>body{font:16px system-ui;background:#0b1220;color:#e7eefb;display:grid;place-items:center;min-height:95vh;margin:0;padding:20px;box-sizing:border-box}main{background:#17243a;padding:32px;border-radius:18px;max-width:370px;width:100%;box-sizing:border-box}input,button{box-sizing:border-box;width:100%;padding:14px;border-radius:9px;border:0;font:inherit;margin:10px 0}button{background:#3d82ff;color:white;font-weight:700;cursor:pointer}p{color:#a5b7d3}label{display:block}</style></head><body><main><h1>🏀 Pick Now</h1><p>Private access · Owner only</p><form method="post" action="/login"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required maxlength="256"><button type="submit">SIGN IN</button></form><p>MESSAGE</p></main></body></html>'''

def configured():
    try:
        salt,digest=os.environ.get('PICKNOW_PASSWORD_HASH','').split('$')
        return len(bytes.fromhex(salt))>=16 and len(bytes.fromhex(digest))==32
    except ValueError:return False

def verify_password(password):
    if not configured() or not isinstance(password,str) or len(password)>256:return False
    salt,expected=os.environ['PICKNOW_PASSWORD_HASH'].split('$')
    actual=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),200_000).hex()
    return hmac.compare_digest(actual,expected)

def allow_attempt():
    now=time.time()
    with LOCK:
        while ATTEMPTS and ATTEMPTS[0]<now-60:ATTEMPTS.popleft()
        if len(ATTEMPTS)>=20:return False
        ATTEMPTS.append(now)
        return True

def new_session():
    token=secrets.token_urlsafe(32)
    with LOCK:
        now=time.time()
        for key,expiry in list(SESSIONS.items()):
            if expiry<=now:SESSIONS.pop(key,None)
        if len(SESSIONS)>=128:SESSIONS.pop(next(iter(SESSIONS)))
        SESSIONS[hashlib.sha256(token.encode()).digest()]=now+TTL
    return token

def cookie_token(header):
    try:
        cookies=SimpleCookie();cookies.load(header or '')
        return cookies[COOKIE].value if COOKIE in cookies else None
    except Exception:return None

def authenticated(header):
    if not configured():return False
    token=cookie_token(header)
    if not token or len(token)>100:return False
    key=hashlib.sha256(token.encode()).digest()
    with LOCK:
        expiry=SESSIONS.get(key,0)
        if expiry<=time.time():SESSIONS.pop(key,None);return False
        return True

def logout(header):
    token=cookie_token(header)
    if token:
        with LOCK:SESSIONS.pop(hashlib.sha256(token.encode()).digest(),None)

def session_cookie(token):
    return f'{COOKIE}={token}; Path=/; Max-Age={TTL}; Secure; HttpOnly; SameSite=Strict'

def clear_cookie():
    return f'{COOKIE}=; Path=/; Max-Age=0; Secure; HttpOnly; SameSite=Strict'
