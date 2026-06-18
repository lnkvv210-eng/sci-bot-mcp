FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install mcp requests

CMD ["python", "server.py"]
