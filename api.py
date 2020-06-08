from __future__ import print_function
import flask
from flask import request
import random
import os
import sys
import base64
import json
import bcrypt
import sqlite3

database_name = "user_details"
healthcheck_messages = ["hiya!", "hey there!", "beep boop!", "i'm alive. <3", "welcome to my twisted api", "hello! you can use this to interface with my brain"]
default_replies = ["beep!!", "boop!", "nyaaa~", "beepboop!", "my sources say no", "ask again later", ":3c"]

app = flask.Flask("avn-0216")

@app.route('/register', methods=['POST'])
def register():

    #See if the request can be parsed as json.
    try:
        request_body = json.loads(request.data.decode("utf-8"))
    except:
        return "Could not parse request body.", 400

    #Check we have all the required fields.
    if "username" not in request_body:
        return "'username' field missing from registration request.", 400
    
    if "password" not in request_body:
        return "'password' field missing from registration request.", 400

    #Check if a user by that name is already registered in the database.
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (request_body.get('username'),))
    if c.fetchone() is not None:
        return "User already exists.", 400

    #We have a username and password, and the user doesn't already exist. Let's hash the password with bcrypt and store it in the DB.
    plaintext = request_body.get('password')
    pwbytes = plaintext.encode()
    hashstring = bcrypt.hashpw(pwbytes, bcrypt.gensalt()).decode()

    #Password encrypted, store user details in DB.
    c.execute("INSERT INTO users(username, hash) VALUES(?,?);", (request_body.get('username'), hashstring), )
    conn.commit()
    conn.close()

    return f"Username {request_body.get('username')} successfully registered. This service doesn't support recovery emails so please don't forget your password!", 200

@app.route('/login', methods=['POST'])
def login():
    #See if the request can be parsed as json.
    try:
        request_body = json.loads(request.data.decode("utf-8"))
    except:
        return "Could not parse request body.", 400

    #Check we have all the required fields.
    if "username" not in request_body:
        return "'username' field missing from login request.", 400
    
    if "password" not in request_body:
        return "'password' field missing from login request.", 400

    basic_auth_string = (request_body['username']+":"+request_body['password'])
    basic_auth = base64.b64encode(basic_auth_string.encode())

    return(f"Your authorization key is '{basic_auth.decode()}'. Include it in your request headers as:\n'Authorization: Basic {basic_auth.decode()}'.\nDo not share this key with anyone, as your password can be extracted from it.")


@app.route('/', methods=['GET'])
def healthcheck():
    return random.choice(healthcheck_messages)

@app.route('/', methods=['POST'])
def interface():

    #Authenticate the user.
    auth = request.headers.get('Authorization', None)
    if auth is None:
        return "Unauthorized. Authorization header missing.", 401
    if "Basic" not in auth:
        return "Authorization must be basic.", 400

    b64string = auth[6:]
    try:
        creds = base64.b64decode(b64string).decode()
    except:
        return "Unable to parse basic auth.", 400
    creds_split = creds.split(":")

    #We have the password we want to compare, pull the user from the DB and get the hash.
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (creds_split[0],))
    row = c.fetchone()
    if row is None:
        return "User not found or password incorrect.", 400

    conn.close()

    #Compare the hashes.
    if not bcrypt.checkpw(creds_split[1].encode(), row[2].encode()):
        return "User not found or password incorrect.", 400


    #Alright, authorization all good and taken care of, now build response.
    reply = random.choice(default_replies)
    request_body = request.data.decode("utf-8")
    
    with open("logs.txt","a+") as log_file:
        log_file.write(creds_split[0] + ": " + request_body+"\n")
        log_file.close()

    if "intercept" in os.listdir():
        print("Intercepting transmission.")
        with open("intercept_req_writing", "w") as req_file:
            for header_key, header_value in request.headers:
                req_file.write(header_key + ": " + header_value + "\n")
            req_file.write(request_body)
            req_file.close()
        os.rename("intercept_req_writing", "intercept_req")

        while "intercept_resp" not in os.listdir():
            pass
        with open("intercept_resp") as resp_file:
            reply = resp_file.readline()
            resp_file.close()
            os.remove('intercept_resp')

    else:
        if "beep" in request_body:
            reply = "boop!"
        elif "boop" in request_body:
            reply = "beep!"
        elif any(lovely_word in request_body for lovely_word in ["ily", "i love you"]):
            reply = "i love you too!! <3"
        elif "<3" in request_body:
            reply = "<3 <3 <3"
        elif "ping" in request_body:
            reply = "pong~!"
        elif "miss" in request_body:
            reply = "it's okay, i'm here. always will be. <3"
        elif "you ok" in request_body:
            reply = "yeah, i'm fine. <3 thank you."

    return reply


#Do data migration here.
print("Doing data migration.")
try:
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username VARCHAR(255) NOT NULL, hash VARCHAR(255) NOT NULL );")
except Exception as e:
    print("Something went wrong with data migration. Shutting down.")
    print(e)
finally:
    if conn:
        conn.close()
print("Data migration done.")
print("Starting API.")
app.run(host='0.0.0.0', port=216)
