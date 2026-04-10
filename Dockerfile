FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY strata.py .

ENV STRATA_DATA_DIR=/app/data
EXPOSE 8000

CMD ["python", "strata.py"]
