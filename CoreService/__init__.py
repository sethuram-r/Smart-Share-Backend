import logging
import os

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
ip = os.environ["KAFKA_IP"]
port = os.environ["KAFKA_PORT"]
