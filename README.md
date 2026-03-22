# Table of Contents

* [What is General Library?](#what-is-general-library)
* [Origin](#origin)
* [Features](#features)

  * [Authentication](#authentication)
  * [Books & Categories](#books--categories)
  * [Exchange System](#exchange-system)
  * [Cart](#cart)
  * [File Storage](#file-storage)
  * [Other](#other)
  * [Upcoming features](#upcoming-features)
* [How to use](#how-to-use)
* [Tech Stack](#tech-stack)
* [Installation for developers](#installation-for-developers)
* [Project plan](#project-plan)

<br />

---

# General Library

Backend service for a book exchange platform.

(Вставить фото: схема или Swagger)

---

## What is General Library?

General Library is a backend system designed to support a **peer-to-peer book exchange platform**.

Unlike typical CRUD-based projects, it already includes core mechanics required for real interaction between users:

* authentication
* exchange offers
* active orders
* carts
* file storage

The goal is to simulate a real-world service where users can exchange books, not just store them.

---

## Origin

The project started as a simple idea:
most books are read once and then stay unused.

At the same time, someone else might be looking for exactly that book.

This system is an attempt to build a backend that allows books to circulate between users, forming a simple exchange network.

---

## Features

### Authentication

* [x] JWT-based authentication
* [x] Protected routes via dependencies
* [x] User management

(Вставить фото: пример запроса логина / токена)

---

### Books & Categories

* [x] Create and manage books
* [x] Assign categories
* [x] Structured schemas and models

(Вставить фото: создание книги / список)

---

### Exchange System

* [x] Exchange offers between users
* [x] Active orders (accepted exchanges)
* [x] Separate logic layer for exchange handling

This is the core of the system — interaction between users is built around these modules.

(Вставить фото: схема обмена)

---

### Cart

* [x] Add/remove books
* [x] Intermediate step before exchange

---

### File Storage

* [x] File upload support
* [x] Integration with MinIO
* [x] Separate client layer

---

### Other

* [x] Rate limiting (`core/limiter.py`)
* [x] Error handling layer (`sqlErrors.py`)
* [x] Dependency system (`deps.py`)
* [x] Background tasks (`tasks/`)

---

### Upcoming features

* [ ] Improve exchange flow (statuses, lifecycle)
* [ ] Logging system
* [ ] Permissions / roles
* [ ] Notifications
* [ ] Better search & filtering

---

## How to use

After starting the project:

```
http://localhost:8000/docs
```

All endpoints are available via Swagger UI.

(Вставить фото: Swagger)

---

## Tech Stack

Backend

* FastAPI
* SQLAlchemy

Database

* PostgreSQL

Infrastructure

* Docker / Docker Compose
* MinIO

Security

* JWT

---

## Installation for developers

1. Clone the repository

```
git clone https://github.com/YoungFire812/general_library.git
cd general_library
```

2. Run the project

```
docker-compose up --build
```

3. Open:

```
http://localhost:8000/docs
```

---

## Project plan

### Stage 1 — Core backend (done)

* authentication
* books / categories
* carts
* exchange offers
* active orders

### Stage 2 — Stabilization

* improve exchange lifecycle
* add logging
* improve validation

### Stage 3 — Interaction

* notifications
* better user interaction
* permissions

### Stage 4 — Scaling

* caching
* performance improvements
* monitoring

---
