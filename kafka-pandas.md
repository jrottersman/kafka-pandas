# Loading data from kafka to a pandas dataframe

Kafka is a messaging framework and pandas is a data exploration tool. They do not naturally play super well together and that makes sense since you would normally use Kafka to load data into a database. On the other hand, pandas are pretty much just for data exploration. However, there is usually some point where you want to dive into what data is in a Kafka topic and go beyond what you can easily do with Kafkacat and JQ. This guide will show how to load a subset of data from a topic into a pandas dataframe.


## Introduction
In this tutorial we walk through setting up a local version of Kafka, pushing some sample data to it. We will follow this up with reading from that topic and loading the data to a pandas dataframe. The code for this project can be found [here](https://github.com/jrottersman/kafka-pandas).

## setup
To get this up and running we will need a running version of Kafka to set up Kafka using homebrew you can follow these instructions.

1. `brew cask install homebrew/cask-versions/adoptopenjdk8`
2. `brew install Kafka`
3. `brew services start zookeeper`
4. `brew services start Kafka`

From there we will need to create a topic which we can do with the following command. `Kafka-topics --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic foo`

The last piece of the setup that we will need to do is to install Kafka-python and pandas if you cloned the repo you can run `pip install -r requirments.txt` otherwise run `pip install kafka-python pandas`

## Produce Data

Next up we are going to send some sample data to the Kafka topic.

```
def producer():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8'))
    
    for i in range(1000):
        num = {"number": i}
        producer.send(topic, num)
```

The producer will send the records to the topic as JSON. The value serializer field handles the conversion for us. Kafka needs to recieve records as bytes.

# Consume the records
First, we will set up a Kafka consumer as follows
```
    consumer = KafkaConsumer(
    topics,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))
```
This consumer will allow us to read the Kafka topics that we specified. In our case foo and the value deserializer will turn the JSON blob back to a dictionary. For the purposes of this example, we are going read from offset zero. If you need to read from an arbitary offset use consumer.seek to set the reset to the offset in a partition.

The standard way to consumer messages using Kafka python is.
```
for message in consumer:
    # do something with message
```
However, that is a blocking call so we are going to use poll instead. 
```
consumer.poll(timeout_ms=1000, max_records=100)
```
An important thing to note is that just because the max records are set at 100 in this example does not guarantee that we will get 100 records back!

# reading the data into the dataframe

The data that is returned from the poll is a dictionary where each key is the topic and partition that the data came from. The value is a list of consumer records. These consumer records are stored as a python class. The following code will extract each record value and place it in a list.

```
    l = []
    for m in messages.values():
        for i in m:
            l.append(i.value)
```
We are iterating thorugh the values in the dictionary that was returned by the consumers poll. We only passed a single topic to the consumer which has one partition so in this case that dictionary only has one element.

That value is a list of consumer records. There is metadata in those records like offsets, timestamps and more. Exploring what is in the consumer record is a good exercise to know what data that kafka is storing. For this we just care about the actual value that we placed on the topic.

Once we have that  list of dictionaries that we can easily turn into a pandas dataframe like so. 
```
df = pd.DataFrame(l)
print(df.head())
```
