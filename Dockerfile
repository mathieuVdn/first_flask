FROM python:3.9

WORKDIR /first_flask

COPY . /first_flask

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
