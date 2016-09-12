FROM python:2.7
MAINTAINER Felix Enescu <felix@enescu.name>

ADD . /experiment
WORKDIR /experiment/

RUN pip install -r requirements.txt


