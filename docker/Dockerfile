FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY src/ ./src/
COPY configs/ ./configs/

EXPOSE 8000

CMD ["python", "-m", "src.api.main"]