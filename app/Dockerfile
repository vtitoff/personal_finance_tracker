FROM python:3.12

WORKDIR /opt/app/src

COPY . .

RUN apt-get update \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root \
    && rm -rf ~/.cache

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
