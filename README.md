# Ticket Master Backend API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Postgres](https://img.shields.io/badge/Postgres-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## Tech Stack

- FastAPI
- PostGres
- Swagger
- Docker

## Introduction

This is the back-end API written to support the front-end App "TicketMaster".

## Updates

- Any updates in the project would be added in future

## Screenshots

Any screenshots of the APIs go here

## Deployment using Docker containers

```sh
$ docker-compose up -d --build
$ docker-compose exec web alembic upgrade head
```

## Alembic

```
alembic revision --autogenerate -m "Initial tables"
```

```
alembic upgrade head
```

```
pip install 'pydantic[email]'
```

## Testing using pytest

```
pytest --cov
```

Type in the following command to run the test cases with coverage. Right now the coverage is around 88%. Here's a sample test file for the root app

```Python
from fastapi.testclient import TestClient
import sys
import os

# Get the absolute path to the project's root directory (one level up from the 'tests' folder)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI Ticket Master App!"}
```

Pytest sneak peeks into your code-base and inspects what piece of code you wrote is not covered in your test cases. For instance, if you have a function defined to get_user_by_id and then there is no route or test for it. It would reduce your test case coverage %.

