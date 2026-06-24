FROM python:3.12

WORKDIR /app

COPY requirments.txt .

RUN pip install -r requirments.txt

COPY . .

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]


