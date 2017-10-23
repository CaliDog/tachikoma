FROM python:latest

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

