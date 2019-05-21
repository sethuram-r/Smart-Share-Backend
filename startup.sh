#!/bin/bash

echo  Started Running the startup Script.......


echo  "running AuthenticationService.RequestHandler" >log_file
nohup python3 -m AuthenticationService.RequestHandler 5001 >> log_file &

echo  "running CoreService.Reads.RequestHandler" >>log_file
nohup python3  -m CoreService.Reads.RequestHandler 5002  >> log_file &


echo  "running CoreService.Lock.LockServer " >>log_file
nohup python3  -m CoreService.Lock.LockServer 5003  >> log_file &

echo  "running C CoreService.Writes.RequestHandler " >>log_file
nohup python3 -m  CoreService.Writes.RequestHandler 5004  >> log_file &


echo  "running AccessManagementService.RequestHandler " >>log_file
nohup python3 -m   AccessManagementService.RequestHandler 5005 >> log_file &

sleep 8

echo  "running AuthenticationConsumer " >>log_file
nohup python3   AuthenticationConsumer.py  >> log_file &

echo  "running CacheConsumer " >>log_file
nohup python3  CacheConsumer.py  >> log_file &


echo  "running PostgresConsumer " >>log_file
python3  PostgresConsumer.py














