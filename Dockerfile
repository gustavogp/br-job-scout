# Use a slim, stable Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies directly to speed up builds
RUN pip install --no-cache-dir google-genai pydantic

# Copy your script into the container
COPY scout.py .

# Command executed when Cloud Run invokes the job
CMD ["python", "scout.py"]