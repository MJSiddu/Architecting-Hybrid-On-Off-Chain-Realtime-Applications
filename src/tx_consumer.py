from flask import jsonify
from kafka import KafkaConsumer
from json import loads
from dotenv import load_dotenv
import os
from kafka import KafkaProducer
from json import dumps
from pymongo import MongoClient
import bigchain_currency as bc

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
  tx_topic = os.getenv('tx_topic')

  # Read data from the transaction data topic
  consumer = KafkaConsumer(
    tx_topic,
    bootstrap_servers=[servers],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

  producer = connect_kafka_producer()
  cur = bc.Currency(["Vehicle1", "Sensor1"])
  
  for message in consumer:
    tx_data = message.value
    print(tx_data)
    res = cur.transfer(tx_data['from_id'],tx_data['to_id'],tx_data['tot_amount'])
    print(res)
