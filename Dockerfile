FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

COPY . .

EXPOSE 5000

CMD ["cd", "app", "&&", "uvicorn", "main:app", "--port=5000"]

