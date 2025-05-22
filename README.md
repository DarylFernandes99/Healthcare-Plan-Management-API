# Healthcare Plan Management API

A robust, scalable RESTful API service for managing healthcare plans with high-performance data storage, retrieval, and search capabilities using microservices architecture.

## 🏥 Overview

This Healthcare Plan Management API provides a comprehensive solution for healthcare plan management, leveraging modern technologies for efficient data handling. The system implements a sophisticated microservices architecture with dual storage systems, asynchronous processing, and advanced search capabilities to ensure high performance, scalability, and reliability.

### Key Highlights
- **Dual Storage Architecture**: Redis for fast key-value operations + Elasticsearch for complex queries
- **Asynchronous Processing**: RabbitMQ message queuing for non-blocking operations
- **Parent-Child Relationships**: Complex hierarchical data modeling with Elasticsearch join fields
- **OAuth Authentication**: Secure API access with token-based authentication
- **Containerized Infrastructure**: Production-ready Docker setup with multi-node Elasticsearch cluster

## ✨ Features

### Core Functionality
- **Complete CRUD Operations** for healthcare plans with nested object support
- **Hierarchical Data Management** for complex healthcare plan structures
- **Real-time Search** with Elasticsearch full-text and structured queries
- **ETag Support** for conditional requests and caching optimization
- **Data Validation** using JSON Schema validation
- **Asynchronous Processing** for improved response times

### Technical Features
- **Dual Storage System**:
  - **Redis**: Primary storage for fast key-value retrieval and caching
  - **Elasticsearch**: Advanced indexing, search, and analytics
- **Message Queue Integration**: RabbitMQ for asynchronous plan processing
- **RESTful API Design** with comprehensive HTTP methods support
- **OAuth 2.0 Authentication** for secure API access
- **Swagger Documentation** for API exploration and testing
- **Multi-Environment Support** (Development/Production configurations)

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | Python Flask | RESTful API development |
| **Primary Database** | Redis | Fast key-value storage and caching |
| **Search Engine** | Elasticsearch 7.12.0 | Advanced search and analytics |
| **Message Queue** | RabbitMQ | Asynchronous task processing |
| **Authentication** | OAuth 2.0 | Secure API access |
| **Containerization** | Docker & Docker Compose | Infrastructure orchestration |
| **API Documentation** | Swagger/OpenAPI | Interactive API documentation |
| **Data Visualization** | Kibana | Elasticsearch data visualization |

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Flask API     │───▶│   RabbitMQ      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │   Consumer      │
                       │   (Primary)     │    │   Service       │
                       └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Elasticsearch   │
                                              │   Cluster       │
                                              └─────────────────┘
```

### Data Flow
1. **API Request**: Client sends HTTP request to Flask API
2. **Authentication**: OAuth middleware validates request
3. **Immediate Response**: API responds immediately for non-blocking operations
4. **Queue Processing**: RabbitMQ queues tasks for asynchronous processing
5. **Data Storage**: Consumer processes queue items and stores in Redis + Elasticsearch
6. **Search & Retrieval**: Dual storage system provides optimized read operations

## 📊 Data Model

### Healthcare Plan Structure

```json
{
  "objectId": "12xvxc345ssdsds-508",
  "objectType": "plan",
  "planType": "inNetwork",
  "creationDate": "12-12-2017",
  "_org": "example.com",
  "planCostShares": {
    "objectId": "1234vxc2324sdf-501",
    "objectType": "membercostshare",
    "deductible": 2000,
    "copay": 23,
    "_org": "example.com"
  },
  "linkedPlanServices": [
    {
      "objectId": "27283xvx9asdff-504",
      "objectType": "planservice",
      "_org": "example.com",
      "linkedService": {
        "objectId": "1234520xvc30asdf-502",
        "objectType": "service",
        "name": "Yearly physical",
        "_org": "example.com"
      },
      "planserviceCostShares": {
        "objectId": "1234512xvc1314asdfs-503",
        "objectType": "membercostshare",
        "deductible": 10,
        "copay": 0,
        "_org": "example.com"
      }
    }
  ]
}
```

### Entity Relationships
- **Plan** (Root entity)
  - **PlanCostShares** (1:1 relationship)
  - **LinkedPlanServices** (1:Many relationship)
    - **LinkedService** (1:1 per plan service)
    - **PlanServiceCostShares** (1:1 per plan service)

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:
- **Python 3.7+**
- **Docker & Docker Compose**
- **Git**

### 1. Clone Repository

```bash
git clone <repository-url>
cd Healthcare-Plan-Management-API
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# Environment
PYTHON_ENV=development

# Development Configuration
DEV_PORT=5000
DEV_HOST=localhost
DEV_VERSION=v1
DEV_OAUTH_CLIENT_ID=your_oauth_client_id_here

# Redis Configuration
REDIS_DEV_HOST=localhost
REDIS_DEV_PORT=6379

# RabbitMQ Configuration
RABBITMQ_DEV_HOST=localhost
RABBITMQ_DEV_PORT=15672

# Elasticsearch Configuration
DEV_ELASTIC_HOST=http://localhost:9200/

# Production Configuration (Optional)
PROD_PORT=5000
PROD_HOST=0.0.0.0
PROD_VERSION=v1
PROD_OAUTH_CLIENT_ID=your_prod_oauth_client_id_here
REDIS_PROD_HOST=localhost
REDIS_PROD_PORT=6379
RABBITMQ_PROD_HOST=localhost
RABBITMQ_PROD_PORT=15672
PROD_ELASTIC_HOST=http://localhost:9200/
```

### 3. Infrastructure Setup

#### Start Elasticsearch Cluster with Kibana
```bash
docker-compose up -d
```

This starts:
- 3-node Elasticsearch cluster (ports 9200, 9201, 9202)
- Kibana dashboard (port 5601)

#### Start Redis
```bash
docker run -d --name healthcare-redis -p 6379:6379 redis:latest
```

#### Start RabbitMQ
```bash
docker run -d --name healthcare-rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### 4. Application Setup

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run the Application
```bash
python app.py
```

The API will be available at: `http://localhost:5000`

### 5. Verify Installation

#### Check Service Health
- **Elasticsearch**: `http://localhost:9200`
- **Kibana**: `http://localhost:5601`
- **RabbitMQ Management**: `http://localhost:15672` (guest/guest)

## 📚 API Documentation

### Authentication

All endpoints require OAuth authentication. Include the authorization header:
```
Authorization: Bearer <your_oauth_token>
```

### Available Endpoints

#### Plan Management

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `POST` | `/v1/plan` | Create new healthcare plan | Plan JSON | 201 Created |
| `GET` | `/v1/plan` | Retrieve all plans | - | 200 OK |
| `GET` | `/v1/plan/{id}` | Retrieve specific plan from Redis | - | 200 OK |
| `PATCH` | `/v1/plan/{id}` | Update existing plan | Partial plan JSON | 200 OK |
| `DELETE` | `/v1/plan/{id}` | Delete plan | - | 200 OK |

#### Elasticsearch Operations

| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `GET` | `/v1/plan/es_plan/{id}` | Retrieve plan from Elasticsearch | - | 200 OK |
| `GET` | `/v1/plan/es_data` | Search Elasticsearch objects | `id`, `parent_type` | 200 OK |

### Request/Response Examples

#### Create Plan
```bash
curl -X POST http://localhost:5000/v1/plan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "objectId": "plan_001",
    "objectType": "plan",
    "planType": "inNetwork",
    "creationDate": "2023-12-01",
    "_org": "healthcare.com",
    "planCostShares": {
      "objectId": "cost_001",
      "objectType": "membercostshare",
      "deductible": 1000,
      "copay": 20,
      "_org": "healthcare.com"
    },
    "linkedPlanServices": []
  }'
```

#### Retrieve Plan
```bash
curl -X GET http://localhost:5000/v1/plan/plan_001 \
  -H "Authorization: Bearer <token>"
```

#### Search in Elasticsearch
```bash
curl -X GET "http://localhost:5000/v1/plan/es_data?id=plan_001" \
  -H "Authorization: Bearer <token>"
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 304 | Not Modified (ETag validation) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 409 | Conflict (Plan already exists) |
| 412 | Precondition Failed (ETag mismatch) |
| 500 | Internal Server Error |

## 🔍 Advanced Features

### ETag Support

The API supports ETags for conditional requests:

```bash
# Get plan with ETag
curl -X GET http://localhost:5000/v1/plan/plan_001 \
  -H "Authorization: Bearer <token>" \
  -I

# Use ETag for conditional update
curl -X PATCH http://localhost:5000/v1/plan/plan_001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "If-Match: \"etag_value_here\"" \
  -d '{"planType": "outOfNetwork"}'
```

### Elasticsearch Query Examples

#### Parent-Child Queries
```json
{
  "query": {
    "has_parent": {
      "parent_type": "plan",
      "query": {
        "term": {
          "_id": "plan_001"
        }
      }
    }
  }
}
```

#### Range Queries
```json
{
  "query": {
    "range": {
      "deductible": {
        "gte": 500,
        "lte": 2000
      }
    }
  }
}
```

## 🗂️ Project Structure

```
Healthcare-Plan-Management-API/
├── app.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Elasticsearch cluster setup
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
├── LICENSE                        # License file
├── README.md                      # Project documentation
├── Architecture.png               # Architecture diagram
├── use case.txt                   # Sample data structure
├── ElasticSearch Queries.txt      # Sample ES queries
├── static/
│   ├── swagger.json              # API documentation
│   └── swagger copy.json         # Backup API docs
└── src/
    ├── __init__.py               # Package initialization
    ├── routes.py                 # Route definitions
    ├── utils.py                  # Utility functions
    ├── consumer.py               # RabbitMQ consumer
    ├── config/
    │   ├── __init__.py          # Config package init
    │   ├── config.py            # Main configuration
    │   ├── dev_config.py        # Development settings
    │   ├── production_config.py  # Production settings
    │   └── log_formatter.py     # Logging configuration
    ├── controllers/
    │   ├── __init__.py          # Controllers package init
    │   └── plans_controller.py   # Plan endpoint handlers
    ├── middlewares/
    │   ├── __init__.py          # Middleware package init
    │   └── auth_middleware.py    # OAuth authentication
    └── models/
        ├── __init__.py          # Models package init
        ├── plans_model.py        # Plan data operations
        ├── redis_model.py        # Redis operations
        ├── elastic_search_model.py # Elasticsearch operations
        ├── etag_model.py         # ETag management
        ├── useCaseSchema.json    # JSON Schema validation
        └── planMappings.json     # Elasticsearch mappings
```

## 🧪 Development & Testing

### Development Setup

1. **Install development dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set environment to development**:
```bash
export PYTHON_ENV=development
```

3. **Run in debug mode**:
```bash
python app.py
```

### Testing Data

Use the sample data from `use case.txt` for testing:

```bash
curl -X POST http://localhost:5000/v1/plan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d @"use case.txt"
```

### Logging

The application uses structured logging:
- **Development**: Debug level logging to console
- **Production**: Info level logging with structured format

## 🐳 Production Deployment

### Docker Setup (Recommended)

1. **Build application container**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

2. **Update docker-compose.yml** to include the API service:
```yaml
services:
  healthcare-api:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - es01
      - redis
      - rabbitmq
    environment:
      - PYTHON_ENV=production
    networks:
      - elastic
```

3. **Deploy the stack**:
```bash
docker-compose up -d
```

### Production Configuration

Set production environment variables:
```bash
export PYTHON_ENV=production
export PROD_HOST=0.0.0.0
export PROD_PORT=5000
# Set other production variables
```

## 📊 Monitoring & Observability

### Kibana Dashboards

Access Kibana at `http://localhost:5601` to:
- Monitor plan creation patterns
- Analyze search queries
- Track API performance metrics
- Visualize data relationships

### RabbitMQ Management

Monitor message queues at `http://localhost:15672`:
- Queue depth and processing rates
- Message throughput
- Consumer status
- Error tracking

### Health Checks

Monitor service health:
- **Redis**: `redis-cli ping`
- **Elasticsearch**: `curl http://localhost:9200/_health`
- **RabbitMQ**: Check management interface

## 🔧 Troubleshooting

### Common Issues

#### Elasticsearch Connection Issues
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health

# Restart cluster
docker-compose restart es01 es02 es03
```

#### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping

# Restart Redis
docker restart healthcare-redis
```

#### RabbitMQ Queue Issues
```bash
# Check queue status
curl -u guest:guest http://localhost:15672/api/queues

# Purge queue if needed
curl -u guest:guest -X DELETE http://localhost:15672/api/queues/%2f/plans/contents
```

#### Authentication Issues
- Verify OAuth client ID in `.env` file
- Check token expiration
- Ensure proper Authorization header format

### Performance Optimization

1. **Redis Optimization**:
   - Enable persistence with RDB snapshots
   - Configure appropriate memory policies
   - Use Redis clustering for high availability

2. **Elasticsearch Optimization**:
   - Tune JVM heap size (-Xms, -Xmx)
   - Configure appropriate shard and replica counts
   - Enable index lifecycle management

3. **Application Optimization**:
   - Implement connection pooling
   - Add caching layers
   - Use async/await for I/O operations

## 🔒 Security Considerations

### Authentication & Authorization
- OAuth 2.0 token validation on all endpoints
- Token expiration and refresh handling
- Role-based access control (future enhancement)

### Data Security
- Encrypt sensitive data in Redis
- Use TLS for inter-service communication
- Implement request rate limiting
- Add input validation and sanitization

### Infrastructure Security
- Network isolation using Docker networks
- Regular security updates for base images
- Secrets management for production deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code style
- Add unit tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📝 API Schema Validation

The API uses JSON Schema for request validation. The schema is defined in `src/models/useCaseSchema.json` and validates:

- Required fields for all objects
- Data types and formats
- Nested object structures
- Array constraints

## 📄 License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the API documentation
- Check application logs for error details
- Ensure all services are running and healthy

---

**Built with ❤️ for Healthcare Plan Management**
