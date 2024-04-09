FROM python:3.9

WORKDIR /first_flask

COPY . /first_flask

RUN pip install -r requirements.txt


CMD ["python", "main.py"]
