# Docker image location:
# https://hub.docker.com/repository/docker/hschickdevs/ai-software-architect/general

# How to install docker engine on Ubuntu:
# https://docs.docker.com/engine/install/ubuntu/

# Use an official Python runtime as a parent image
FROM python:3.11

ARG YOUR_ENV

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.7.1
  # ^^^
  # Make sure to update it!

# System deps:
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN groupadd -r puser && useradd -ms /bin/sh -g puser puser

WORKDIR /home/puser/app
COPY poetry.lock pyproject.toml README.md /home/puser/app/

# Project initialization:
RUN poetry install --only=main --no-interaction --no-ansi

COPY ./src ./src

RUN chown puser:puser -R /home/puser/app
USER puser

ENV USE_DOCKER True

# Run the bot when the container launches
CMD ["python", "-m", "src"]

# ------- Docker Deployment Commands: -------
# docker build -t telegram-crypto-alerts .
# docker tag telegram-crypto-alerts hschickdevs/telegram-crypto-alerts:latest
# docker push hschickdevs/telegram-crypto-alerts:latest
# docker rmi -f $(docker images -aq)

# FOR TESTING:
# docker run --env-file .env telegram-crypto-alerts

# ------- Docker Pull & Run Commands: -------
# docker pull hschickdevs/telegram-crypto-alerts:latest

# docker run -d --name telegram-crypto-alerts \
#   -e TELEGRAM_USER_ID=<YOUR_ID> \
#   -e TELEGRAM_BOT_TOKEN=<YOUR_TOKEN> \
#   -e TAAPIIO_APIKEY=<YOUR_KEY> \
#   hschickdevs/telegram-crypto-alerts

# docker attach telegram-crypto-alerts