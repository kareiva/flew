# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set environment variables for Django and Database
ENV SECRET_KEY=change-me-in-production
ENV DEBUG=False
ENV ALLOWED_HOSTS=localhost
ENV DATABASE_URL=postgres://user:password@flewdb:5432/dbname

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install system dependencies and Python dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy the Django project into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the Django application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "flew.wsgi:application"] 