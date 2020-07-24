import json
from pprint import pprint

from kafka import KafkaProducer, KafkaConsumer
from kafka.structs import TopicPartition
import pandas as pd

topic = "foo"

def producer():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8'))
    
    for i in range(1000):
        num = {"number": i}
        producer.send(topic, num)

def consume():
    consumer = KafkaConsumer(topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    
    #t = TopicPartition("foo", 1)
    #consumer.seek(t, 100)
    return consumer.poll(timeout_ms=1000, max_records=100)

def pandas(messages):
    l = []
    for m in messages.values():
        msg = [i.value for i in m]
        l.append(msg)
    print(l)
    return pd.DataFrame(l[0])


if __name__ == '__main__':
	#producer()
	c = consume()
	df = pandas(c)
	print(df.head())
