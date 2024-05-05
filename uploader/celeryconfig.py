import os

worker_send_task_events = True
task_send_sent_event = True
brokerURL = os.environ.get('BROKER_URL', 'broker')
broker_url = f'redis://{brokerURL}:6379/0'
