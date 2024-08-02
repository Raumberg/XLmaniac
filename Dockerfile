FROM python:3.10-slim

WORKDIR /app

RUN mkdir assets

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD [ "flet", "run", "--web", "--port", "8080", "main.py" ]