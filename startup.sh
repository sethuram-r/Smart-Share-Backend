#!/bin/bash

echo  Started Running the startup Script.......

nohup python -m AuthenticationService.RequestHandler --port 5001 >> log_file &

nohup python  -m CoreService/Reads.RequestHandler --port 5002  >> log_file &

nohup python  -m CoreService.Lock.LockServer --port 5003  >> log_file&

nohup python  CoreService/Writes/RequestHandler.py --port 5004  >> log_file &

nohup python  AccessManagementService/RequestHandler.py  >> log_file &

nohup python  AuthenticationConsumer.py  >> log_file&

nohup python  CacheConsumer.py  >> log_file&

nohup python  PostgresConsumer.py   >> log_file&
















