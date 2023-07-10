FROM ubuntu

COPY . .

EXPOSE 8080

RUN source venv/bin/activate

CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
