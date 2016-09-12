
# experiment
Demo of distributed system using gRPC, Celery and Redis in Docker containers

## Running the demo

You need a linux box to run this example. Make sure you have docker installed. For help installing docker see here: https://docs.docker.com/v1.11/engine/installation/linux/ubuntulinux/

Checkout the source code:
```
$ git clone git@github.com:blueCat1301/experiment.git
$ cd async
```

Install requirements to run the client:
```
$ pip install -r requirements.txt
```

Start the application:
```
$ docker-compose up --build
```

This will start the application containers in foreground so you can see the logs. On another terminal test using the client:
```
$ python client.py -c start -i 123
Sent command start
Received answer: Started experiment id 123, name Experiment, task id 6df82a50-9c49-493f-97d9-34529f1dbe86
$ python client.py -c start -i 125
Sent command start
Received answer: Started experiment id 125, name Experiment, task id be0d9e5b-dda3-423c-b0e4-f8c11227cc6b
$ python client.py -c status -i 125
Sent command status
Received answer: Experiment 125 is in state PROGRESS; current seconds 8, status message: transglutinating radiant post-processor (125)...
$ python client.py -c start -i 127
Sent command start
Received answer: Started experiment id 127, name Experiment, task id d757d41a-1c6c-4de5-ba7a-5eca21cb74f4
$ python client.py -c stop -i 123
Sent command stop
Received answer: Stoped experiment id 123, name Experiment, task id 6df82a50-9c49-493f-97d9-34529f1dbe86
$ python client.py -c status -i 127
Sent command status
Received answer: Experiment 127 is in state PROGRESS; current seconds 74, status message: fine-tuning injector post-processor (127)...
```

Notes:
 - The system is configured to run two worker containers, each with up to two experiments in parallel. Further tasks are put in queue.
 - Any worker with spare capacity will pick up next task
 - Functions implemented are: StartExperiment, StopExperiment and GetExperimentStatus


## Load balancing

This is a typical task queue problem. Furthermore our tasks are CPU (or even GPU bound) so we need raw computing power, any tricks developed to cope with I/O bound problems (like web scrapping) will not help here. So no gevent, greenlets or threads here. :-(

Indeed a task queue is a complicated piece of software, not something one write over a week-end. Fortunately Python have a very solid one: celery. We can use gRPC to gather commands from any client written in any programming language and dispatch tasks using celery.

A quick review of celery features shows it fulfill all requirements of his brief:
 - scalability: start any number of workers on any number of servers
 - ability to control tasks: can stop and interrogate status of any task, no matter where it runs
 - autoscaling: ability to start more worker processes to fully utilize each servers capabilities

The built in features of celery makes entire problem of load balancer irrelevant.

## Autoscaling

If we look for example to AWs we have few options:
 - "manually" autoscaling: review periodically the number of tasks in celery and start or stop instances
 - SQS based scaling: use celery with SQS as broker and use AWS Autoscaling based on queue length
 - CloudWatch alarms based: scale based on any CloudWatch metric

Similar solutions exists also for Google Cloud.

Important cost notes:
 - if tasks are restartable we should evaluate spot instances. In some case they can be up 10 times less expensive than on demand instances.
 - if the load is predictable we should evaluate reserved instances. In mane cases we can achieve important cost savings






