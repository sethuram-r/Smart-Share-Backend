# from flask import Flask, request
# import argparse
# from flask import Flask,json,request,jsonify
# import os
# from git import Repo
# import json
#
# app = Flask(__name__)
#
# @app.route('/', methods=['GET'])
# def get():
#
#     if len(cc_manager.commits) == 0:
#         commit_number = 'Done'
#     else:
#         commit = cc_manager.commits.pop(0)
#         commit_number = commit.hexsha
#         print("new length of commit_numbers = ", len(cc_manager.commits))
#
#     data = {'commit_number': commit_number,}
#
#     response = jsonify(data)
#     response.status_code = 200
#     return response
#
#
# @app.route('/', methods=['POST'])
# def post():
#
#     if request.headers['CONTENT_TYPE'] == 'application/json':
#
#         data = request.json
#
#         print("worker id: ", data['worker_id'])
#         print("worker cc: ", data['cc'])
#
#         # add cc result to manager
#         cc_manager.add_cc(data['commit_number'], int(data['cc']))
#
#         return "JSON Message: " + json.dumps(request.json)
#     else:
#         raise NotImplementedError
#
# class CodeComplexityMaster:
#
#     def __init__(self ,slave_ip, slave_port):
#
#         if  slave_ip and  slave_port:
#             self.slave_address = "http://{0}:{1}".format(slave_ip, slave_port)
#             print self.slave_address
#
#         print("Initialising Master...")
#
#         # GIT repository settings
#         self.git_repository = "https://github.com/DLTK/DLTK"
#         self.root_repo_dir = "./repo"
#         self.commits = []
#         self.cc_per_commit = {}
#         self.repo = None
#
#     def setup_gitrepo(self):
#
#         repo_dir = self.root_repo_dir
#         if not os.path.exists(repo_dir):
#             os.makedirs(repo_dir)
#
#         if not os.listdir(repo_dir):
#             print('cloning repository into directory: {0}'.format(repo_dir))
#             Repo.clone_from(self.git_repository, repo_dir)
#             print('cloning finished')
#
#         self.repo = Repo(repo_dir)
#         assert not self.repo.bare
#
#         self.commits = list(self.repo.iter_commits('master'))
#         # self.cc_per_commit = {commit: None for commit in self.commits}
#         self.cc_per_commit = {}
#
#         print("Repository setup complete")
#
#     def add_cc(self, commit_number, cc):
#
#         cc_manager.cc_per_commit[commit_number] = cc
#
#         if len(cc_manager.commits) == 0:
#             print("COMPLETE, total CC = ", sum(self.cc_per_commit.values()))
#
#     @app.route('/register', methods=['POST'])
#     def update():
#
#     @app.route('/signup', methods=['POST'])
#     def insert():
#
#
#     @app.route('/signin', methods=['POST'])
#     def find_one():
#
#
#     @app.route('/validateSession', methods=['GET'])
#     def validate_user():
#
#
#     @app.route('/getObjects', methods=['GET'])
#     def send_objects():
#
#
#     @app.route('/logout', methods=['GET'])
#     def sign_out():
#
#
#     @app.route('/getObject', methods=['GET'])
#     def get_object(object=""):
#
#
#     @app.route('/uploadObject', methods=['POST'])
#     def upload_object():
#
#
#     @app.route('/deleteObjects', methods=['POST'])
#     def delete_objects():
#
#
#     @app.route('/lockObjects', methods=['POST'])
#     def lock_objects():
#
#
#     @app.route('/lockStatus', methods=['POST'])
#     def lock_status():
#
#
#     @app.route('/accessRequest', methods=['Get'])
#     def access_request():
#
#
#     @app.route('/getAccessRequests', methods=['Get'])
#     def requested_access():
#
#
#     @app.route('/requestStatus', methods=['POST'])
#     def request_status():
#
#
#     @app.route('/deleteRecord', methods=['POST'])
#     def delete_record():
#
#
#     @app.route('/getAccessedRecords', methods=['Get'])
#     def accessed_records():
#
#
#
#
# if __name__ == '__main__':
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--host',type=str,default='127.0.0.1',help='host ip of server.')
#     parser.add_argument('--port',type=int,default=8000,help='port of server.')
#     parser.add_argument('--workerID', type=int, default=3, help='ID to identify worker')
#
#
#     FLAGS, unparsed = parser.parse_known_args()
#
#     # global cc_manager
#     cc_manager = CodeComplexityMaster(FLAGS.host,FLAGS.port)
#     cc_manager.setup_gitrepo()
#
#
#     # run application with set flags
