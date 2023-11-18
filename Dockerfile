FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app
RUN python3 -m venv /app/venv --upgrade-deps
ENV PATH="/app/venv/bin:$PATH"
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./gymlog /app/gymlog

# Create directory for data
RUN mkdir -p /app/data

CMD ["gunicorn",  "--chdir", "/app", "--bind", "0.0.0.0:5000", "gymlog:app"]