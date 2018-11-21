from flask import Flask,request,jsonify

import mongo_connection as mc



app = Flask(__name__)


def data_extraction(data):
    extracted_data = str(data).replace("b","",1).replace("'","").strip()
    login_credentials = {
         "username": "",
         "password": ""
     }

    if (extracted_data.split(",")[0].split(":")[0] == "user_name"):
         login_credentials["username"] = extracted_data.split(",")[0].split(":")[1]
    if (extracted_data.split(",")[1].split(":")[0] == "password"):
         login_credentials["password"] = extracted_data.split(",")[1].split(":")[1]
    return login_credentials
         



@app.route('/signup',methods=['POST'])
def insert():
     received_data = str(request.data).replace("b","",1).replace("'","").strip()

     login_credentials = {
         "username": "",
         "password": ""
     }

     if (received_data.split(",")[0].split(":")[0] == "user_name"):
         login_credentials["username"] = received_data.split(",")[0].split(":")[1]
     if (received_data.split(",")[1].split(":")[0] == "password"):
         login_credentials["password"] = received_data.split(",")[1].split(":")[1]

     result = mc.insert(login_credentials)

     if (result) != "":
         print("The User data is inserted successfully.......")
         return  jsonify({"status":True})
     else:
         print("The data insertion resulted in failure.......")
         return jsonify({"status":False})

   
@app.route('/signin', methods=['POST'])
def find_one():
    login_credentials = data_extraction(request.data)
    result = mc.find_one(login_credentials)
    if (result) != "":
         print("The User data is exists .......")
         return  jsonify({"status":True})
    else:
         print("The data doesn't exists.......")
         return jsonify({"status":False})
    


if __name__ == '__main__':
    app.run()
