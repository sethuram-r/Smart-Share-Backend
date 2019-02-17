import argparse
import os
from os import walk

import radon
import requests
from flask import Flask
from git import Repo
from radon.complexity import cc_rank

app = Flask(__name__)


class CodeComplexityWorker:

    def __init__(self, worker_id, worker_name, master_ip, master_port):
        # GIT repository settings
        self.worker_id = worker_id
        self.worker_name = worker_name
        self.git_repository = "https://github.com/DLTK/DLTK"
        self.root_repo_dir = "./repo_worker_" + str(worker_id)
        self.master_address = "http://{0}:{1}".format(master_ip, master_port)

        self.repo = None
        self.files = []
        # { 'file': cc }
        self.cc_files = {}

        self.setup_gitrepo()

    def setup_gitrepo(self):

        repo_dir = self.root_repo_dir
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)

        if not os.listdir(repo_dir):
            print('cloning repository into directory: {0}'.format(repo_dir))
            Repo.clone_from(self.git_repository, repo_dir)
            print('cloning finished')

        self.repo = Repo(repo_dir)
        assert not self.repo.bare

        # setup list of all .py files from most recent commit
        self.update_files()

    def set_commit_state(self, commit_number):
        """ sets repository state to the provided commit"""

        print("setting repository state to: {0}".format(commit_number))

        # use checkout from git
        git = self.repo.git
        git.checkout(commit_number)

        # refresh list of all .py files
        self.update_files()

    def update_files(self):
        """ get all files from current commit"""

        self.files = []
        for (dirpath, dirnames, filenames) in walk(self.root_repo_dir):
            for filename in filenames:
                if '.py' in filename:
                    dirpath = dirpath.replace("\\", "/")
                    self.files.append(dirpath + '/' + filename)

        # reset code complexity results for each file
        self.cc_files = {file: None for file in self.files}

    def calculate_cyclomatic_complexity(self, commit_number):
        """ calculate cc for all files in current commit """

        for file in self.files:
            with open(file) as f:
                data = f.read()
                try:
                    cc = radon.complexity.cc_visit(data)
                    cc_tot = 0
                    for cc_item in cc:
                        cc_tot += cc_item.complexity
                        # print("complexity = ", cc_item.complexity)
                except Exception as err:
                    print("ERROR: could not calculate cc for file {0} in commit {1}".format(file, commit_number))
                    print(err)
                    cc_tot = 0

                self.cc_files[file] = cc_tot

        # return total complexity of all files
        return sum(self.cc_files.values())

    def respond_to_request(self, key):

        # checkout to commit number:
        self.set_commit_state(key)

        # calculate cyclomatic complexity
        print('worker {0} - calculating commit {1}'.format(self.worker_name, key))
        cc = self.calculate_cyclomatic_complexity(key)

        stat_msg = '{} completed by worker {}'.format(key, self.worker_name)
        cc_msg = str(cc)

        post_msg = {'worker_id': self.worker_id, 'commit_number': str(key), 'cc': cc_msg}

        # post result to the server
        response = requests.post(self.master_address, json=post_msg)

    def listen_requests(self):
        """ send requests to master for tasks """

        while True:
            # ask the server for a task
            response = requests.get(self.master_address)
            task = response.text
            data = response.json()
            commit_number = data['commit_number']

            # if no task stop worker
            if commit_number == 'Done':
                break

            self.respond_to_request(commit_number)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host ip of master.')
    parser.add_argument('--port', type=int, default=8000, help='port of master.')
    parser.add_argument('--workerID', type=int, default=3, help='ID to identify worker')

    FLAGS, unparsed = parser.parse_known_args()

    worker_name = 'worker_{0}'.format(FLAGS.workerID)
    worker = CodeComplexityWorker(FLAGS.workerID, worker_name, FLAGS.host, FLAGS.port)
    worker.listen_requests()
