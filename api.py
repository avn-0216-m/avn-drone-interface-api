from __future__ import print_function
import flask
from flask import request
import random
import os
import sys
import base64

healthcheck_messages = ["hiya!", "hey there!", "beep boop!", "i'm alive. <3"]

app = flask.Flask("avn-0216")

@app.route('/', methods=['GET'])
def healthcheck():

    return random.choice(healthcheck_messages)

@app.route('/', methods=['POST'])
def interface():

    reply = "beep boop!"

    if "intercept" in os.listdir():
        print("Intercepting transmission.")
        with open("intercept_req_writing", "w") as req_file:
            for header_key, header_value in request.headers:
                req_file.write(header_key + ": " + header_value + "\n")
            req_file.write(str(request.data))
            req_file.close()
        os.rename("intercept_req_writing", "intercept_req")

        while "intercept_resp" not in os.listdir():
            pass
        with open("intercept_resp") as resp_file:
            reply = resp_file.readline()
            resp_file.close()
            os.remove('intercept_resp')

    else:
        print("No interception.")

        post_body = str(request.data).lower()

        if "beep" in post_body:
            reply = "boop!"
        elif "boop" in post_body:
            reply = "beep!"
        elif any(lovely_word in post_body for lovely_word in ["ily", "i love you"]):
            reply = "i love you too!! <3"
        elif "<3" in post_body:
            reply = "<3 <3 <3"
        elif "ping" in post_body:
            reply = "pong~!"

    return reply

app.run(host='0.0.0.0', port=216)
