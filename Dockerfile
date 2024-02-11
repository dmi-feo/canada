FROM python:3.12

RUN mkdir /src
COPY . /src

RUN pip install -r /src/requirements.txt
RUN pip install /src

CMD ["python", "/src/canada/app.py"]
