FROM python:3.8.5-slim
# FROM ubuntu
# RUN apt-get update -y
# RUN apt-get install -y python3-pip python-dev build-essential

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip3 install poetry
WORKDIR /root
COPY poetry.lock pyproject.toml /root/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction
COPY . /root

# CMD ["bash"]