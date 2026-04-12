FROM python:3.13-slim

WORKDIR /app

COPY update-job-requirements.txt .
RUN pip install --no-cache-dir -r update-job-requirements.txt

COPY gcp.py .
COPY update.py .
COPY update_main.py .

CMD ["python", "update_main.py"]
