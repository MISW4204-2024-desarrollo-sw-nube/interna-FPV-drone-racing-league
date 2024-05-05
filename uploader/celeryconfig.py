import os


worker_send_task_events = True
task_send_sent_event = True
brokerURL = os.environ['BROKER_URL', 'broker']
broker_url = 'redis://${brokerURL}:6379/0'
