from flask import Flask, request, jsonify

import amazon_s3_connection as s3
import mongo_connection as mc

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024


def data_extraction(data):

    extracted_data = str(data).replace("b","",1).replace("'","").strip()
    # print(extracted_data)
    login_credentials = {}
    if (extracted_data.split(",")[0].split(":")[0] == "user_name"):
         login_credentials["username"] = extracted_data.split(",")[0].split(":")[1]
    if (extracted_data.split(",")[1].split(":")[0] == "password"):
         login_credentials["password"] = extracted_data.split(",")[1].split(":")[1]
    if (extracted_data.split(",")[1].split(":")[0] == "sessionId"):
         login_credentials["authentication_server_sessionId"] = extracted_data.split(",")[1].split(":")[1]
    if (extracted_data.split(",")[0].split(":")[0] == "file"):
        login_credentials["file"] = extracted_data.split(",")[0].split(":")[1]
    # if (extracted_data.split(",")[1].split(":")[0] == "name"):
    #     login_credentials["file_name"] = extracted_data.split(",")[0].split(":")[1]
    print(login_credentials)

    return login_credentials
         

@app.route('/register',methods=['POST'])
def update():
    login_credentials = data_extraction(request.data)
    filter = {"username": login_credentials["username"]}
    result = mc.update(filter,login_credentials)
    if (result.raw_result["updatedExisting"]):
        print("The User data is updated successfully.......")
        return jsonify({"status": True})
    else:
        print("The data updation resulted in failure.......")
        return jsonify({"status": False})


@app.route('/signup',methods=['POST'])
def insert():
     login_credentials =  data_extraction(request.data)
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

@app.route('/validate', methods=['POST'])
def validate_user():
    credentials = data_extraction(request.data)
    result = mc.find_one(credentials)
    print(credentials)
    if (result) != "":
         print("The User data is exists .......")
         return  jsonify({"status":True})
    else:
         print("The data doesn't exists.......")
         return jsonify({"status":False})


@app.route('/getObjects', methods=['GET'])
def send_objects():
    return jsonify(s3.list_objects("file.server.1"))


@app.route('/getObject', methods=['GET'])
def get_object():
    return s3.get_object("file.server.1",request.args.get('key'))

@app.route('/uploadObject', methods=['POST'])
def upload_object():
    import json
    files = json.loads(str(request.data).replace("b","",1).replace("'",""))
    results = []
    for file in files:
        results.append(s3.upload_object(file))

    for result in results:
        if  (result):
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})


@app.route('/deleteObjects', methods=['POST'])
def delete_objects():
    import json
    objects = json.loads(str(request.data).replace("b", "", 1).replace("'", ""))
    print(objects)
    results = []

    results.append(s3.delete_objects(objects))
    print(results)

    if (False in results):
        return jsonify({"status": False})
    else:
        return jsonify({"status": True})
















if __name__ == '__main__':
    app.run()

