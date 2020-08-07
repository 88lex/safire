FROM python:3.8.5-slim

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt && \
    pip3 install safire

WORKDIR /root/