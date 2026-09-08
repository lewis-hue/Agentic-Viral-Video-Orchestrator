# Start with an official Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Set environment variables to prevent Python from buffering output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y some-package

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy your application code into the container
COPY . .

# The CMD is a placeholder. We will override this in docker-compose.
# This makes the image reusable for multiple services.
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]