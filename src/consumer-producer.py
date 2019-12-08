from flask import jsonify
from kafka import KafkaConsumer
from json import loads
from dotenv import load_dotenv
import os
from kafka import KafkaProducer
from json import dumps
from pymongo import MongoClient

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
  raw_topic = os.getenv('raw_topic')
  processed_topic=os.getenv('processed_topic')
  mongodb_uri = os.getenv('mongodb_uri')

  client = MongoClient(mongodb_uri)
  collection = client.kafka.processed

  # Read data from the raw data topic
  consumer = KafkaConsumer(
    raw_topic,
    bootstrap_servers=[servers],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

  producer = connect_kafka_producer()
  for message in consumer:
    data = message.value

    # Process raw data below. Check for violations, per hour rate based on location and time, criminal offenses etc against a public database and update the object. For example
    data['is_wanted'] = False
    data['rate_per_hour'] = 2
    data['accumulated_penalty'] = 100

    # if data['is_wanted']:
    #   Call law enforcement API

    # Insert record to mongodb
    collection.insert_one(data)

    # Write the data to a proceesed data topic, if required by other consumers.
    # publish_message(producer, processed_topic, data)
    
    print(data)
      
