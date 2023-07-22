FROM python:3.8-slim-buster as runtime

ARG CODE_SCOUT_HOME="/opt/code-scout"

ARG CODE_SCOUT_USER_HOME="/home/code-scout"

ARG CODE_SCOUT_PORT="8080"

ARG CODE_SCOUT_UID="50000"
ARG CODE_SCOUT_GID="0"

ENV CODE_SCOUT_HOME=${CODE_SCOUT_HOME}

ENV CODE_SCOUT_USER_HOME=${CODE_SCOUT_USER_HOME}

# RUN useradd -u ${CODE_SCOUT_UID} -g ${CODE_SCOUT_GID} "codescout"

RUN mkdir ${CODE_SCOUT_HOME}

RUN mkdir ${CODE_SCOUT_USER_HOME}

WORKDIR ${CODE_SCOUT_HOME}

RUN mkdir ./logs

COPY ./website ./website

COPY ./app.py ./

COPY requirements.txt requirements.txt

COPY ./gunicorn_config.py .

COPY ./setup-db.py .

RUN chown -R ${CODE_SCOUT_UID}:${CODE_SCOUT_GID} ${CODE_SCOUT_HOME}

RUN chown -R ${CODE_SCOUT_UID}:${CODE_SCOUT_GID} ${CODE_SCOUT_USER_HOME}

RUN pip3 install -r requirements.txt

EXPOSE ${CODE_SCOUT_PORT}

CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
