from flask import Flask,request

import mongo_connection as mc
import json


app = Flask(__name__)


@app.route('/login',methods=['POST'])
def insert():
     received_data = str(request.data).replace("b","",1).replace("'","").strip()

     print("received_data",received_data)
     print("received_data", received_data.split(","))

     login_credentials = {
         "username": "",
         "password": ""
     }

     if (received_data.split(",")[0].split(":")[0] == "user_name"):
         login_credentials["username"] = received_data.split(",")[0].split(":")[1]
     if (received_data.split(",")[1].split(":")[0] == "password"):
         login_credentials["password"] = received_data.split(",")[1].split(":")[1]

     print(login_credentials)
     print(json.dumps(login_credentials))
     return mc.insert(json.dumps(login_credentials))


if __name__ == '__main__':
    app.run()
