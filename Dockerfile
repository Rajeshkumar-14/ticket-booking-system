# Use official Python 3.13 slim image
FROM python:3.13-slim

# Create and set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1  

# Install system dependencies for psycopg2 and other needs
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy Poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the project
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn ticket_system_project.wsgi:application --bind 0.0.0.0:8000"]