FROM python:3.12

RUN mkdir /src
COPY . /src

RUN pip install /src

RUN pip install gunicorn==21.0.1

CMD ["gunicorn", "-c", "/src/gunicorn/config.py", "canada.app:gunicorn_app", "--access-logfile", "'-'"]
