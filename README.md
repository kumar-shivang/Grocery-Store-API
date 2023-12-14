# Grocery Store API

## Description

This API is a part of my university project. It is a simple REST API for a grocery store. It allows to manage products, orders and users. It is written in Python using Flask framework and SQLAlchemy ORM. It uses JWT for authentication and authorization.
It also uses celery and redis for asynchronous tasks.

## Installation

1. Clone the repository and enter it

    ```bash
    git clone
    cd grocery-store-api
    ```

2. Create virtual environment and activate it

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

4. Start redis server

    ```bash
    redis-server
    ```

5. Start celery worker and beat

    ```bash
    celery -A app.celery worker --loglevel=info -B
    ```

6. Run the application

    ```bash
    python3 app.py
    ```

7. You can also use a shell script to run the application

    ```bash
    ./run.sh
    ```

It is advised to run a listener on smtp port 1025 to see the emails sent by the application. Otherwise you may face some errors.
