test = 'user_name:hgch,password:vbn'


login_credentials = {
    "username":"",
    "password":""
}

if(test.split(",")[0].split(":")[0] == "user_name"):
    login_credentials["username"] = test.split(",")[0].split(":")[1]
if(test.split(",")[1].split(":")[0] == "password"):
    login_credentials["password"] = test.split(",")[1].split(":")[1]

print(login_credentials)





