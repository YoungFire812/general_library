# Table of Contents

* [General Library](#general-library)
* [Что такое General Library?](#что-такое-general-library)
* [Идея проекта](#идея-проекта)
* [Ключевые особенности](#ключевые-особенности)
* [Project Structure](#project-structure)
* [API Endpoints](#api-endpoints)

  * [Authentication](#authentication)
  * [Users](#users)
  * [Books](#books)
  * [Cart](#cart-корзина)
  * [Categories](#categories)
  * [Exchange Offers](#exchange-offers)
  * [Active Orders](#active-orders)
  * [Files Upload](#files-upload)
  * [Lockers](#lockers)
* [Функциональность](#функциональность)

  * [Аутентификация](#аутентификация)
  * [Книги и категории](#книги-и-категории)
  * [Система обмена](#система-обмена)
  * [Корзина](#корзина)
  * [Файлы (MinIO)](#файлы-minio)
  * [Дополнительно](#дополнительно)
* [Технологии](#технологии)

  * [Backend](#backend)
  * [База данных](#база-данных)
  * [Инфраструктура](#инфраструктура)
  * [Безопасность](#безопасность)
* [Установка и запуск](#установка-и-запуск)
* [План развития](#план-развития)

---

# General Library

Backend-сервис для платформы обмена книгами.

(Вставить фото: Swagger или схема проекта)

---

## Что такое General Library?

**General Library** — это backend-приложение для построения сервиса, в котором пользователи могут обмениваться книгами между собой.

Проект не ограничивается простым хранением данных. В его основе лежит логика взаимодействия между пользователями: от добавления книг до формирования и завершения обмена.

Основная цель — создать систему, в которой книги не простаивают, а продолжают использоваться другими людьми.

---

## Идея проекта

У многих людей есть книги, которые уже прочитаны и больше не используются.

В то же время другим пользователям эти книги могут быть действительно нужны.

**General Library** решает эту проблему через механизм обмена. Пользователи могут предлагать свои книги и получать другие взамен, формируя живую экосистему взаимодействия.

---

## Ключевые особенности

Проект сфокусирован на взаимодействии пользователей, а не только на CRUD-операциях.

Реализованы:

- система предложений обмена  
- управление активными сделками  
- контроль и отслеживание статуса каждого обмена 
- гибкое формирование предложений перед отправкой 
- безопасная аутентификация и изоляция пользовательских данных

Такой подход позволяет рассматривать проект как полноценную модель реального сервиса с пользовательским взаимодействием.

---

## Project Structure

```
general_library/
│
├── src/                           # Application package
│   ├── routers/                   # API routes
│   │   ├── active_orders.py       # Active orders endpoints
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── books.py               # Books endpoints
│   │   ├── carts.py               # Cart endpoints
│   │   ├── categories.py          # Categories endpoints
│   │   ├── exchange_offers.py     # Exchange offers endpoints
│   │   ├── files.py               # File upload endpoints
│   │   ├── lockers.py             # Locker endpoints
│   │   └── users.py               # User management endpoints
│   │
│   ├── core/                       # Core functionality
│   │   ├── config.py               # Configuration settings
│   │   ├── deps.py                 # Dependency injection
│   │   ├── jwt.py                  # JWT handling
│   │   ├── limiter.py              # Request limiting
│   │   ├── security.py             # Security utilities
│   │   └── sqlErrors.py            # Database error handling
│   │
│   ├── db/                         # Database layer
│   │   ├── base.py                 # Base models
│   │   └── database.py             # Database connection
│   │
│   ├── minio/                      # File storage layer
│   │   └── minio_client.py         # MinIO client
│   │
│   ├── models/                     # SQLAlchemy models
│   │   ├── events.py
│   │   ├── models.py
│   │   └── __init__.py
│   │
│   ├── schemas/                    # Pydantic schemas
│   │   ├── active_orders.py
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── carts.py
│   │   ├── categories.py
│   │   ├── dto.py
│   │   ├── exchange_offers.py
│   │   ├── lockers.py
│   │   └── users.py
│   │
│   ├── services/                   # Business logic
│   │   ├── active_orders.py
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── carts.py
│   │   ├── categories.py
│   │   ├── exchange_offers.py
│   │   ├── lockers.py
│   │   └── users.py
│   │
│   ├── main.py                     # Application entry point
│   └──constants.py                # Application Enum constants 
│
├── tests/                          # Test suite
├── .env                            # Example environment variables
├── docker-compose.yml              # Docker Compose configuration
└── Dockerfile                      # Docker image definition
```

### Description

- **src/** — основной код приложения  
- **routers/** — маршруты API  
- **core/** — конфигурация, безопасность, JWT, лимитирование и обработка ошибок  
- **db/** — подключение к базе данных и базовые модели  
- **minio/** — работа с файловым хранилищем  
- **models/** — SQLAlchemy модели  
- **schemas/** — Pydantic-схемы для валидации данных  
- **services/** — бизнес-логика приложения  
- **main.py** — точка входа FastAPI приложения  
- **tests/** — тесты проекта  
- **docker-compose.yml / Dockerfile** — контейнеризация и запуск

---

# API Endpoints

### Authentication

* `POST /api/v1/auth/registration` – Регистрация нового пользователя
* `POST /api/v1/auth/login` – Вход и получение токена
* `POST /api/v1/auth/token` – Получение access token через форму
* `POST /api/v1/auth/refresh` – Обновление токена пользователя

---

### Users

* `GET /api/v1/users/{user_id}` – Получить пользователя по ID
* `PATCH /api/v1/users/{user_id}` – Обновить данные пользователя (своя учетная запись)
* `DELETE /api/v1/users/{user_id}` – Удалить пользователя (своя учетная запись)

---

### Books

* `GET /api/v1/books/get_limited` – Получить книги с пагинацией и фильтром по категории/поиску
* `GET /api/v1/books/{book_id}` – Получить информацию о конкретной книге
* `POST /api/v1/books` – Создать новую книгу
* `PATCH /api/v1/books/{book_id}` – Обновить данные книги
* `DELETE /api/v1/books/{book_id}` – Удалить книгу

---

### Cart (Корзина)

* `GET /api/v1/users/{user_id}/cart/products` – Получить товары в корзине пользователя с пагинацией
* `POST /api/v1/cart/products` – Добавить книгу в корзину
* `GET /api/v1/users/{user_id}/cart` – Получить конкретную корзину пользователя

---

### Categories

* `GET /api/v1/categories/all` – Получить все категории
* `GET /api/v1/categories/{category_id}` – Получить категорию по ID
* `POST /api/v1/categories/create` – Создать новую категорию (только админ)
* `PATCH /api/v1/categories/patch` – Обновить категорию (только админ)
* `DELETE /api/v1/categories/{category_id}` – Удалить категорию (только админ)

---

### Exchange Offers

* `GET /api/v1/offers/` – Получить все предложения пользователя с фильтром и пагинацией
* `GET /api/v1/offers/{offer_id}` – Получить конкретное предложение обмена
* `POST /api/v1/offers/` – Создать предложение обмена
* `POST /api/v1/offers/{offer_id}/decline` – Отклонить предложение
* `POST /api/v1/offers/{offer_id}/accept` – Принять предложение и сформировать активный заказ

---

### Active Orders

* `POST /api/v1/active_orders/deliver/{order_id}` – Подтвердить доставку заказа
* `POST /api/v1/active_orders/drop_pickup/{order_id}` – Подтвердить сдачу/получение книги
* `POST /api/v1/active_orders/lockers/{order_id}` – Выбрать шкаф для передачи книги
* `POST /api/v1/active_orders/cancel/{order_id}` – Отменить активный заказ
* `GET /api/v1/active_orders/{order_id}` – Получить конкретный активный заказ
* `GET /api/v1/active_orders/` – Получить все заказы пользователя с пагинацией

---

### Files Upload

* `POST /api/v1/upload-files/` – Загрузка файлов в MinIO

---

### Lockers

* `POST /api/v1/lockers/` – Создать новый постамат (только админ)
* `GET /api/v1/lockers/{locker_id}` – Получить информацию о постамате по ID
* `GET /api/v1/lockers/` – Получить все постаматы

---
## Функциональность

### Аутентификация

- JWT-аутентификация  
- Защита маршрутов через зависимости  
- Управление пользователями  

Система построена с возможностью дальнейшего расширения (роли, права доступа).

---

### Книги и категории

- Создание и управление книгами  
- Связь книг с категориями 
- Участие в обмене только доступных книг  
- Поиск книг по категориям и ключевым словам 

Формируется структурированная база для работы с каталогом.

---

### Система обмена

- Гибкая система обмена книгами с выбором доступных экземпляров  
- Формирование и согласование предложений обмена между пользователями  
- Активные сделки с отслеживанием статусов и безопасной сделкой

Это центральная часть проекта. Именно здесь реализуется логика взаимодействия между пользователями.

---

### Корзина

- Добавление и удаление книг  
- Используется для хранения книг, как промежуточный этап перед обменом

Позволяет гибко формировать предложения.

---

### Файлы (MinIO)

- Загрузка файлов в удобное хранилище
- Отдельный клиент для работы с хранилищем  
- Подготовка к использованию внешнего storage  

Решение позволяет легко масштабировать работу с медиа.

---

### Дополнительно

- Ограничение запросов (`core/limiter.py`)  
- Обработка ошибок базы данных (`sqlErrors.py`)  
- Dependency Injection (`deps.py`)  

Повышает стабильность и управляемость системы.

---

## Технологии

### Backend

- FastAPI  
- SQLAlchemy  

FastAPI выбран за высокую производительность, простоту разработки и встроенную поддержку асинхронности.  
SQLAlchemy обеспечивает гибкую и мощную работу с базой данных.

---

### База данных

- PostgreSQL  

Надежная реляционная база данных с поддержкой сложных запросов и расширяемости.

---

### Инфраструктура

- Docker / Docker Compose  
- MinIO  

Контейнеризация упрощает запуск и развёртывание проекта.  
MinIO используется как S3-совместимое хранилище для работы с файлами.

---

### Безопасность

- JWT  

Позволяет реализовать stateless-аутентификацию и масштабировать систему без привязки к сессиям.

---

## Установка и запуск

1. Клонировать репозиторий
```
git clone https://github.com/YoungFire812/general_library.git
cd general_library
```

2. Запустить проект

```
docker-compose up --build
```

3. Открыть документацию
```
http://localhost:8000/docs
```

---

## План развития

### Этап 1 — Базовый функционал (реализовано)

- аутентификация  
- книги и категории  
- корзина  
- предложения обмена  
- активные сделки  

---

### Этап 2 — Стабилизация

- доработка логики обмена  
- улучшение валидации  
- обработка ошибок  

---

### Этап 3 — Взаимодействие пользователей

- уведомления  
- расширение логики обмена  
- роли и права доступа  

---

### Этап 4 — Масштабирование

- кэширование  
- оптимизация запросов  
- мониторинг  