FROM python:3.8-slim

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN mkdir - /root/.aws
COPY src /src
COPY inputs /inputs