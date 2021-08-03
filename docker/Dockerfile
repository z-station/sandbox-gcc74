FROM python:3.8

ARG SANDBOX_USER_UID
ARG SANDBOX_DIR

RUN apt-get update && \
    apt-get -y install nano g++-7 && \
    pip install --upgrade pip && \
    pip install pipenv

RUN adduser \
    --system \
    --gecos \
    --disabled-login \
    --disabled-password \
    --home ${SANDBOX_DIR} \
    --uid ${SANDBOX_USER_UID} \
    sandbox && \
    chown root:root ${SANDBOX_DIR}

COPY ./src/Pipfile ./src/Pipfile.lock /tmp/
RUN cd /tmp && pipenv install --deploy --system

WORKDIR ${SANDBOX_DIR}