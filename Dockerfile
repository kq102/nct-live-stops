FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8917

# Set environment variables
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"

# Create non-root user first
RUN adduser -u 5678 --disabled-password --gecos "" appuser

# Set up directories and permissions
WORKDIR /app
RUN mkdir -p /tmp/chrome /app/json_files && \
    chown -R appuser:appuser /tmp/chrome /app

# Copy and install requirements
COPY flask/requirements.txt /app/
RUN python -m pip install -r requirements.txt

# Copy application files
COPY flask/json_files/stops.json /app/json_files/
COPY flask/ /app/
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8917","--timeout", "120", "--workers", "2", "--threads", "2", "serve:app"]