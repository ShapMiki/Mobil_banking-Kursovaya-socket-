FROM python:3.9-slim

RUN mkdir -p /ShadyPayServer
WORKDIR /ShadyPayServer

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /ShadyPayServer/docker/*.sh

CMD ["python", "main.py"]