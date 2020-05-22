import os
from datetime import datetime

open('intercept', 'a').close()
try:
    while True:
        if "intercept_req" in os.listdir():
            os.system("clear")
            print("Message intercepted at " + str(datetime.now()))
            print("-------------------------------------------")
            with open('intercept_req') as req_file:
                for line in req_file.readlines():
                    print(line)
            req_file.close()
            os.remove('intercept_req')
            reply = input("> ")
            with open('intercept_resp_writing', 'w') as resp_file:
                resp_file.write(reply)
                resp_file.close()
            os.rename('intercept_resp_writing', 'intercept_resp')
            print("Response sent.")
except KeyboardInterrupt:
    print("Cleanly shutting down.")
    os.remove('intercept')