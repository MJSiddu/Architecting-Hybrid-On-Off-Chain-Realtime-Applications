from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from kafka import KafkaProducer
from json import dumps
import os
import hashlib
import random

app = Flask(__name__)

load_dotenv()

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/upload_processor', methods = ['POST'])
def upload_processor():
  code_file = request.files['code']
  code = code_file.read()
  dirname = os.path.dirname(__file__)
  processors = os.path.join(dirname, '../processors')
  filename = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[:12]
  with open(processors + '/'+ filename + '.py', 'wb') as f:
    f.write(code)
    f.close()
  return filename
 
@app.route('/entry', methods = ['POST'])
def process_entry():
  data = request.get_json()
  kafka_producer = get_producer()
  entry = os.getenv('entry_topic')
  publish_message(kafka_producer, entry, data)
  return jsonify(data)

@app.route('/exit', methods = ['POST'])
def process_exit():
  data = request.get_json()
  kafka_producer = get_producer()
  exit = os.getenv('exit_topic')
  publish_message(kafka_producer, exit, data)
  return jsonify(data)

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