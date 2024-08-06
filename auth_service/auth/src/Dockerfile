FROM python:3.10

WORKDIR /opt/auth

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]