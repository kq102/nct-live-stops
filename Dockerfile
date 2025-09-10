FROM python:3.10-slim

EXPOSE 8917

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create non-root user first
RUN adduser -u 5678 --disabled-password --gecos "" appuser

# Set up directories and permissions
WORKDIR /app
RUN mkdir -p /tmp/chrome /app/json_files

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