# --- Builder stage: install dependencies ---
FROM python:3.10-slim AS builder

# Install system build deps
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# --- Runtime stage: minimal image ---
FROM python:3.10-slim AS runtime

# Create non-root user
RUN useradd --no-log-init -m appuser

WORKDIR /app
USER appuser

# Copy installed packages and app code from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

# Expose application port (matches settings.project.port)
EXPOSE 8000

# Prevent Python from buffering stdout/stderr and .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Launch the app using custom entrypoint that includes aiomonitor
# Assumes there is a run.py in the project root defining run()
CMD ["python", "-u", "-c", "from main import run; run()"]