FROM python:3.11.9

WORKDIR /app

COPY requirements.txt .
COPY *.py .
COPY Module/ Module/
COPY utils/ utils/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
