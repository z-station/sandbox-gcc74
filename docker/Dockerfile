FROM python:3.8

ARG SANDBOX_USER_UID

RUN apt-get update && \
    apt-get -y install nano g++-7 && \
    pip install --upgrade pip && \
    pip install pipenv

RUN adduser \
    --system \
    --gecos \
    --disabled-login \
    --disabled-password \
    --no-create-home \
    --uid ${SANDBOX_USER_UID} \
    sandbox

COPY ./src/Pipfile ./src/Pipfile.lock /tmp/
RUN cd /tmp && pipenv install --deploy --system

WORKDIR /app/src
ENTRYPOINT ["./start.sh"]