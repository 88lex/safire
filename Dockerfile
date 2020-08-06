FROM python:3.8.5-alpine3.12

ENV MAX_PROJECTS=100
ENV SAS_PER_PROJECT=100
ENV EMAIL_PREFIX=svcacc
ENV PROJECT_PREFIX=UniqPrefix
ENV JSON_PREFIX=svcacc

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry
WORKDIR /opt
COPY poetry.lock pyproject.toml /opt/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction
COPY . /opt