# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . /app/

# Run migrations
RUN python manage.py makemigrations

EXPOSE 8000

# Command to run the application
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
