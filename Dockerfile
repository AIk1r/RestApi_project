FROM python:3.10
WORKDIR /RestApi_task
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"]
