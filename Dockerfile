FROM python:3.12-slim

WORKDIR /app

COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]