# Social Networking API with Django Rest Framework

This project is a Django Rest Framework (DRF) API for a social networking application. It includes user authentication, user search, friend requests, and friend management functionalities.


## Description

This Django Rest Framework API provides various functionalities for a social networking application, including user authentication (login/signup), user search, friend requests, and friend management.

## Features

- User Login/Signup with email
- User Search by email and name
- Send/Accept/Reject friend requests
- List friends
- List pending friend requests
- Rate limiting for friend requests

## Requirements

- Python 3.12.0
- Django 5.0.4
- Django Rest Framework (DRF) 3.15.1
- PostgreSQL 16
- Docker
- Docker Compose

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your_username/social-networking-api.git
   cd social-networking-api
   ```
2. **Set Up Environment Variables Create a .env file in the project root directory with the following variables:**
   (Keep POSGRES_HOST as db only if you are running it with docker compose)
    ```bash
    SECRET_KEY=""
    POSTGRES_DB=""
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
   
The project is containerized using Docker. Docker Compose file (docker-compose.yml) and Dockerfile (Dockerfile) are provided for easy deployment.
You can directly use below docker commands directly. Or you can set it up manually from here - [Manual Setup](#manual-setup)
3. **Build and Run Docker Containers**
    ```bash
    docker-compose up --build -d
   ```
### Manual Setup

2. **Install Python Dependencies**

    ```bash
    pip install -r requirements.txt
   ```

4. **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5. **Run the development server**
    ```bash
   python manage.py runserver
   ```
   

## Postman Collection
For easy testing and evaluation, a Postman collection with all API endpoints is available. You can import it using the following link:

[Social Networking API Postman Collection](Social Media Networking.postman_collection.json)
