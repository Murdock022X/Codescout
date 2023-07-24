FROM python:3.9 as runtime

ARG CODE_SCOUT_HOME="/opt/codescout"

ARG CODE_SCOUT_PORT="8080"

ARG CODE_SCOUT_UID="50000"
ARG CODE_SCOUT_GID="0"

ENV CODE_SCOUT_HOME=${CODE_SCOUT_HOME}

RUN mkdir ${CODE_SCOUT_HOME}

WORKDIR ${CODE_SCOUT_HOME}

RUN mkdir ./logs

RUN touch ./logs/gunicorn.access.log

RUN touch ./logs/gunicorn.error.log

COPY ./website ./website

COPY ./app.py ./

COPY requirements.txt requirements.txt

COPY ./gunicorn_config.py .

COPY ./setup-db.py .

RUN python3 -m venv venv

ENV PATH="$CODE_SCOUT_HOME/venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${CODE_SCOUT_PORT}

CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
