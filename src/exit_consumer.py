from flask import jsonify
from kafka import KafkaConsumer
from json import loads
from dotenv import load_dotenv
import os
from kafka import KafkaProducer
from json import dumps
from pymongo import MongoClient
import importlib
import sys

def publish_message(producer_instance, topic_name, data):
  try:
    producer_instance.send(topic_name, value=data)
    producer_instance.flush()
    print('Message published successfully.')
  except Exception as ex:
    print('Exception in publishing message')
    print(str(ex))

def connect_kafka_producer():
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
  load_dotenv()
  servers = os.getenv('kafka-servers')
  exit_topic = os.getenv('exit_topic')
  tx_topic = os.getenv('tx_topic')
  mongodb_uri = os.getenv('mongodb_uri')

  client = MongoClient(mongodb_uri)
  collection = client.kafka.raw

  # Read data from the exit data topic
  consumer = KafkaConsumer(
    exit_topic,
    bootstrap_servers=[servers],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

  producer = connect_kafka_producer()

  dirname = os.path.dirname(__file__)
  processors = os.path.join(dirname, '../processors')
  sys.path.insert(1, processors)

  for message in consumer:
    exit_data = message.value
    entry_data = collection.find({"_id":exit_data['_id']})
    module_name = exit_data['processor']
    proc = importlib.import_module(module_name)
    processed_data = proc.process(entry_data, exit_data)
    publish_message(producer, tx_topic, processed_data)
    print(exit_data)
      
