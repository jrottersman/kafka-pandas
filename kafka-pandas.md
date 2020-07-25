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

The easiest way to consumer messages using Kafka python is something like.
```
for message in consumer:
    # do something with message
```
However, that is a blocking call so we are going to use poll instead.
to do that we do the following 
```
consumer.poll(timeout_ms=1000, max_records=100)
```
An important thing to note is that just because the max records are set at 100 in this example does not guarantee that we will get 100 records back!

# reading the data into the dataframe

The data that is returned from the poll is a dictionary where each key is the topic and partition that the data came from and the value is a list of consumer records which is a python class. to extract the value of each record we will use the following code.

```
    l = []
    for m in messages.values():
        for i in m:
            l.append(i.value)
```
To walk through this code snippet we are iterating thorugh the values in the dictionary which we created from the poll. If you are following along with the tutorial that dictionary has a length of one since we setup a topic with only a single partition and the consumer only has one topic. 
The values in the dictionary are a list. So we are iterating over each of those lists and extracting the value from the consumer record. There are a bunch of other fields that exist on the consumer record including things like offsets, timestamps and other metadata. The value is simply the actual value that is on the kafka topic. Since we already have the deseralizer on the consumer above they are already dictionaries but if they were in a raw form we could pass them to a function at this point to convert them to a data structure. Once we get the values we append them to a list.

Once we have that  list of dictionaries that we can easily turn into a pandas dataframe like so 
```
df = pd.DataFrame(l)
print(df.head())
```
If that worked correctly you should see each a dataframe with numbers for each record.