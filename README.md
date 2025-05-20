# Healthcare Plan Management API

A robust RESTful API service for managing healthcare plans with high-performance data storage, retrieval, and search capabilities.

![Architecture](Architecture.png)

## 🏥 Overview

This API provides a comprehensive solution for healthcare plan management, leveraging modern technologies for efficient data handling. The system utilizes a microservices architecture with multiple data stores and asynchronous processing to ensure high performance and scalability.

## ✨ Key Features

- **Complete CRUD Operations** for healthcare plans
- **Dual Storage System**:
  - Redis for fast key-value storage and retrieval
  - Elasticsearch for powerful indexing and complex searches
- **Asynchronous Processing** via RabbitMQ message queuing
- **RESTful API Design** with comprehensive endpoints
- **OAuth Authentication** for secure access
- **Containerized Deployment** with Docker and docker-compose
- **Hierarchical Data Management** for complex healthcare plan structures

## 🛠️ Technology Stack

- **Backend**: Python Flask RESTful API
- **Database**: Redis (primary storage)
- **Search Engine**: Elasticsearch (indexing and search)
- **Message Queue**: RabbitMQ (asynchronous processing)
- **Authentication**: OAuth 2.0
- **Containerization**: Docker & docker-compose
- **API Documentation**: Swagger/OpenAPI

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Docker and docker-compose
- Redis
- RabbitMQ
- Elasticsearch & Kibana

### Environment Setup

1. Clone this repository
2. Create a `.env` file in the root directory with the following content:

```env
# .env
PYTHON_ENV = "development"

DEV_PORT = "5000"
DEV_HOST = "localhost"
REDIS_DEV_HOST = "localhost"
REDIS_DEV_PORT = "6379"
RABBITMQ_DEV_HOST = "localhost"
RABBITMQ_DEV_PORT = "15672"
DEV_VERSION = "v1"
DEV_OAUTH_CLIENT_ID = "<YOUR_OAUTH_CLIENT_ID>"
DEV_ELASTIC_HOST = "http://localhost:9200/"

PROD_PORT = "5000"
PROD_HOST = "localhost"
REDIS_PROD_HOST = "localhost"
REDIS_PROD_PORT = "6379"
RABBITMQ_PROD_HOST = "localhost"
RABBITMQ_PROD_PORT = "15672"
PROD_VERSION = "v1"
PROD_OAUTH_CLIENT_ID = "<YOUR_OAUTH_CLIENT_ID>"
PROD_ELASTIC_HOST = "http://localhost:9200/"
```

### Infrastructure Setup

1. **Start Redis**:
   ```bash
   docker run -d --name my-redis-stack -p 6379:6379 redis
   ```

2. **Start RabbitMQ**:
   ```bash
   docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

3. **Start Elasticsearch & Kibana Cluster**:
   ```bash
   docker-compose up -d
   ```

### Application Setup

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

## 📚 API Documentation

### Available Endpoints

#### Create a Healthcare Plan
- **POST** `/v1/plan`
- Creates a new healthcare plan and stores nested objects as separate entities
- Processes request asynchronously via RabbitMQ

#### Update a Healthcare Plan
- **PATCH** `/v1/plan/<plan_id>`
- Updates an existing healthcare plan in both Redis and Elasticsearch
- Handles partial updates to nested objects

#### Retrieve a Healthcare Plan from Redis
- **GET** `/v1/plan/<plan_id>`
- Fetches plan data from Redis for fast retrieval

#### Retrieve a Healthcare Plan from Elasticsearch
- **GET** `/v1/plan/es_plan/<plan_id>`
- Fetches plan data from Elasticsearch with full search capabilities

#### Search for Objects in Elasticsearch
- **GET** `/v1/plan/es_data`
- Parameters:
  - `id` (required): Object ID (plan or child)
  - `parent_type` (optional): Object type

#### Delete a Healthcare Plan
- **DELETE** `/v1/plan/<plan_id>`
- Removes the plan from both Redis and Elasticsearch

## 🔍 Data Model

The API handles complex healthcare plan structures with nested objects:

- **Plan**: The root object containing all plan details
- **PlanCostShares**: Cost-sharing details for the plan
- **LinkedPlanServices**: Services covered by the plan
  - **LinkedService**: Details of each covered service
  - **PlanServiceCostShares**: Cost-sharing details specific to each service

## 🧪 Advanced Elasticsearch Queries

The system supports advanced search capabilities through Elasticsearch, including:

- Parent-child relationship queries
- Range-based searches
- Complex boolean queries
- Full-text search

## 🔒 Security

- OAuth 2.0 authentication for secure API access
- HTTPS support for encrypted communication
- Docker container isolation for infrastructure components

## 📄 License

This project is licensed under the terms of the included LICENSE file.
