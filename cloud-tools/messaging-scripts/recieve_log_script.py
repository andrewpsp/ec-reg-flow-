#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
                         type='topic')

result = channel.queue_declare(exclusive=True)
all_flex = result.method.queue

channel.queue_bind(exchange='topic_logs',
                   queue=all_flex)

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)


    for binding_key in binding_keys: 
    	channel.queue_bind(exchange='topic_logs',
    						queue=all_flex,
    						routing_key=binding_key
    						)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r:%r" %( method.routing_key, body)) 

channel.basic_consume(callback,
                      queue=all_flex,
                      no_ack=True)

channel.start_consuming()
