FROM python:3.8.2

WORKDIR /root/app

COPY main.py .
COPY requirements.txt .

RUN pip3.8 install -r requirements.txt

CMD python3.8 -u main.py