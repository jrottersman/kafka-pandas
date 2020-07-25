import json
from kafka import KafkaProducer

topic = "foo"

def producer():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8'))
    
    for i in range(1000):
        num = {"number": i}
        producer.send(topic, num)

if __name__ == '__main__':
    producer()