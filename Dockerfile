# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8917

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

ENV CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage --disable-software-rasterizer --disable-extensions --remote-debugging-port=9222 --memory-pressure-thresholds=1"
# Install pip requirements
WORKDIR /app
COPY flask/requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . .

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8917","--timeout", "120", "--workers", "1", "--threads", "2", "serve:app", "--chdir", "/app/flask"]
