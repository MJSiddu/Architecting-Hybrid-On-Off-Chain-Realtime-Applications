from flask import Flask, request, jsonify
from dotenv import load_dotenv
from kafka import KafkaProducer
from json import dumps
import os
from pymongo import MongoClient

app = Flask(__name__)

load_dotenv()
mongodb_uri = os.getenv('mongodb_uri')
client = MongoClient(mongodb_uri)
processed = client.kafka.processed

@app.route('/')
def home():
  return 'App running on port: 3500'

@app.route('/entry', methods = ['POST'])
def process_entry():
  data = request.get_json()
  kafka_producer = get_producer()
  raw = os.getenv('raw_topic')
  publish_message(kafka_producer, raw, data)
  return jsonify(data)

@app.route('/exit', methods = ['POST'])
def process_exit():
  new_data = request.get_json()
  data = processed.find_one({"_id": new_data['_id']})
  exit_time = new_data['exit_timestamp']
  entry_time = data['entry_timestamp']
  tot_amount = ((exit_time-entry_time)/60)*data['rate_per_hour']+data['accumulated_penalty']

  #Call BigchainDB trnasaction function here. If the transaction suceeds, update fines and etc. If the transaction fails update accordingly

  return {'tot_amount': tot_amount}

def publish_message(producer_instance, topic_name, data):
  try:
    producer_instance.send(topic_name, value=data)
    producer_instance.flush()
    print('Message published successfully.')
  except Exception as ex:
    print('Exception in publishing message')
    print(str(ex))

def get_producer():
  producer = None
  try:
    servers = os.getenv('kafka-servers')
    producer = KafkaProducer(bootstrap_servers=[servers], value_serializer=lambda x: dumps(x).encode('utf-8'))
  except Exception as ex:
    print('Exception while connecting Kafka')
    print(str(ex))
  finally:
    return producer

if __name__ == '__main__':
  app.run(host="localhost", port=3500)