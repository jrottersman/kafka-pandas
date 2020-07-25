import json
from pprint import pprint

from kafka import KafkaConsumer
from kafka.structs import TopicPartition
import pandas as pd

topic = "foo"

def consume():
    consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    

    return consumer.poll(timeout_ms=1000, max_records=100)

def pandas(messages):
    l = []
    for m in messages.values():
        for i in m:
            l.append(i.value)
    return pd.DataFrame(l)


if __name__ == '__main__':
	c = consume()
	df = pandas(c)
	print(df.head())
