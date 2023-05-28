FROM ubuntu

COPY . .

EXPOSE 8080

CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
