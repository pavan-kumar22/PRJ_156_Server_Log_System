# AICTE Server Log Monitoring & Intelligent Alert System

An AI-powered, containerized server log monitoring and intelligent alerting system designed to ingest, analyze, classify, store, and respond to server and application log events.

The system combines automated log collection, machine-learning-based log classification, centralized OpenSearch storage, intelligent alert generation, notification services, sensitive-data protection, and a demonstration Action API into an end-to-end monitoring pipeline.

---

## 📌 Project Information

| Field | Details |
|---|---|
| **Project Title** | AICTE Server Log Monitoring & Intelligent Alert System |
| **Category** | Software |
| **Project Type** | AI-Based Log Monitoring & Observability System |
| **Primary Domain** | Artificial Intelligence, Machine Learning, DevOps & Observability |
| **Architecture** | Microservice / Containerized Architecture |
| **Deployment** | Docker & Docker Compose |
| **Repository** | `PRJ_156_Server_Log_System` |
| **Status** | Completed / Demonstration Ready |

---

## 🎯 Problem Statement

Modern server environments generate large volumes of logs from web applications, APIs, databases, containers, and infrastructure services.

Traditional log monitoring approaches often depend on:

- Manual log inspection
- Static keyword-based rules
- Separate monitoring tools
- Delayed incident detection
- Limited contextual understanding
- High operational effort

These limitations make it difficult to identify important operational events quickly and consistently.

This project addresses the problem by developing an intelligent log monitoring platform that automatically:

1. Collects server and application logs.
2. Processes and normalizes log events.
3. Classifies logs using a machine-learning model.
4. Assigns confidence scores to classifications.
5. Stores classified events in OpenSearch.
6. Identifies events requiring alerts.
7. Sends notifications through configured channels.
8. Provides an Action API for controlled test-event generation.
9. Protects sensitive information during processing.
10. Measures system performance and reliability.

---

# 🚀 Objectives

The major objectives of the project are:

- Develop an automated server log ingestion pipeline.
- Implement AI/ML-based log classification.
- Categorize operational events based on log content.
- Store classified logs in a centralized OpenSearch environment.
- Detect critical operational events automatically.
- Generate intelligent alerts.
- Integrate notification mechanisms.
- Provide a demonstration Action API for controlled event generation.
- Implement sensitive-data protection mechanisms.
- Validate system reliability and failure recovery.
- Evaluate classifier accuracy and confidence.
- Measure ingestion throughput.
- Measure end-to-end pipeline latency.
- Deploy the complete system using Docker containers.

---

# 🏗️ System Architecture

The project follows a containerized microservice architecture.

```text
                    ┌──────────────────────────┐
                    │  Server / Application    │
                    │          Logs            │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │        Vector            │
                    │ Log Ingestion &           │
                    │ Processing                │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     AI Log Classifier     │
                    │   TF-IDF + LinearSVC      │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────┴─────────────┐
                    │                          │
                    ▼                          ▼
          ┌──────────────────┐       ┌──────────────────┐
          │    OpenSearch    │       │   Notification   │
          │ Classified Logs  │       │   Slack / Email  │
          └──────────────────┘       └──────────────────┘
                    ▲
                    │
          ┌─────────┴─────────┐
          │    Action API     │
          │ Controlled Test   │
          │ Event Generation  │
          └──────────────────┘
```

---

# 🔄 End-to-End Workflow

The system processes log events through the following pipeline:

```text
Log Generation
      ↓
Vector Ingestion
      ↓
Log Parsing / Processing
      ↓
AI Classification
      ↓
Confidence Evaluation
      ↓
Sensitive Data Protection
      ↓
OpenSearch Storage
      ↓
Alert Detection
      ↓
Notification
```

The Action API can be used to generate controlled demonstration events for testing and validation.

---

# 🤖 AI / Machine Learning Component

The project uses a machine-learning-based log classification approach.

### Classification Pipeline

```text
Raw Log Message
      ↓
Text Processing
      ↓
TF-IDF Feature Extraction
      ↓
LinearSVC Classifier
      ↓
Predicted Log Category
      ↓
Confidence / Classification Evaluation
```

### Technologies Used

- Python
- TF-IDF feature extraction
- LinearSVC
- Machine-learning-based classification
- Structured log processing

The classifier is designed to identify different operational log categories based on their textual characteristics.

---

# 🧩 Microservices

## 1. Vector

The Vector service is responsible for log ingestion and processing.

**Directory:**

```text
vector/
└── vector.toml
```

Responsibilities include:

- Log collection
- Log processing
- Pipeline forwarding
- Communication with downstream services

---

## 2. AI Log Classifier

**Directory:**

```text
classifier/
├── Dockerfile
├── __init__.py
├── main.py
├── model.py
├── model_day16_backup.py
└── schemas.py
```

Responsibilities include:

- Receiving processed log events
- Classifying log messages
- Assigning classification information
- Evaluating classification confidence
- Forwarding classified events

Machine-learning approach:

```text
TF-IDF + LinearSVC
```

---

## 3. OpenSearch

OpenSearch provides centralized storage and search capabilities for classified log events.

**Directory:**

```text
opensearch/
└── classified-log-template.json
```

Responsibilities include:

- Storing classified logs
- Providing centralized log search
- Supporting structured log indexing

---

## 4. Notification Service

**Directory:**

```text
notification/
├── Dockerfile
├── __init__.py
├── main.py
└── sanitizer.py
```

Responsibilities include:

- Processing alert notifications
- Slack notification integration
- Email notification integration
- Sensitive-data sanitization
- Handling notification configuration

Notification credentials are expected to be supplied through environment variables rather than hard-coded into source code.

---

## 5. Action API

**Directory:**

```text
action_api/
├── Dockerfile
├── __init__.py
└── main.py
```

The Action API provides controlled event generation for:

- Demonstrations
- Pipeline testing
- Alert testing
- Failure/recovery validation
- End-to-end testing

It allows controlled operational scenarios to be generated without manually modifying log files.

---

# 📁 Project Structure

```text
PRJ_156_Server_Log_System/
│
├── action_api/
│   ├── Dockerfile
│   ├── __init__.py
│   └── main.py
│
├── classifier/
│   ├── Dockerfile
│   ├── __init__.py
│   ├── main.py
│   ├── model.py
│   ├── model_day16_backup.py
│   └── schemas.py
│
├── generator/
│   └── generator.py
│
├── notification/
│   ├── Dockerfile
│   ├── __init__.py
│   ├── main.py
│   └── sanitizer.py
│
├── opensearch/
│   └── classified-log-template.json
│
├── tests/
│   ├── performance/
│   │   ├── test_classifier_accuracy.py
│   │   ├── test_ingestion_throughput.py
│   │   └── test_pipeline_latency.py
│   │
│   ├── DAY25_E2E_RESULTS.md
│   ├── DAY26_RESILIENCE_RESULTS.md
│   ├── DAY27_HEALTH_MONITORING_RESULTS.md
│   ├── DAY29_FAILURE_RECOVERY_RESULTS.md
│   ├── health_check.py
│   ├── test_classifier_confidence.py
│   ├── test_classifier_evaluation.py
│   └── test_sanitizer.py
│
├── vector/
│   └── vector.toml
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Application and ML services |
| **Docker** | Containerization |
| **Docker Compose** | Multi-service orchestration |
| **Vector** | Log ingestion and processing |
| **OpenSearch** | Centralized log storage and search |
| **TF-IDF** | Text feature extraction |
| **LinearSVC** | Log classification |
| **Slack / Email** | Alert notification channels |
| **Pytest** | Testing and validation |
| **Git / GitHub** | Version control and source management |

---

# ⚙️ Prerequisites

Before running the project, install:

- Docker
- Docker Compose
- Python 3.x
- Git

Verify the installations:

```bash
docker --version
docker compose version
python --version
git --version
```

---

# 🔐 Environment Configuration

The repository intentionally does **not** contain real credentials.

Create a local `.env` file based on the provided example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then configure the required environment variables in `.env`.

Example:

```env
OPENSEARCH_PASSWORD=your_local_password
SLACK_WEBHOOK_URL=
SMTP_PASSWORD=
```

### Important

Do **not** commit `.env` to Git.

The repository `.gitignore` excludes:

```text
.env
.env.*
```

while allowing:

```text
.env.example
```

The `.env.example` file contains placeholders only and should not contain real credentials.

---

# 🐳 Running the Project

Clone the repository:

```bash
git clone https://github.com/pavan-kumar22/PRJ_156_Server_Log_System.git
```

Enter the project directory:

```bash
cd PRJ_156_Server_Log_System
```

Create the environment configuration:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the local environment variables in `.env`.

Start the complete system:

```bash
docker compose up --build
```

To run the services in detached mode:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

View service logs:

```bash
docker compose logs
```

Stop the system:

```bash
docker compose down
```

---

# 🧪 Testing

The project contains functional, reliability, security, and performance-oriented tests.

## Test Categories

### Classifier Evaluation

```text
tests/test_classifier_evaluation.py
tests/test_classifier_confidence.py
```

These tests evaluate:

- Classification behavior
- Prediction confidence
- Model performance characteristics

---

### Sensitive Data Protection

```text
tests/test_sanitizer.py
```

This validates the sanitization mechanism used to protect sensitive information before further processing or notification.

---

### Health Monitoring

```text
tests/health_check.py
```

Used for checking service health and system availability.

---

### End-to-End Validation

```text
tests/DAY25_E2E_RESULTS.md
```

Contains results related to end-to-end pipeline validation.

---

### Resilience Testing

```text
tests/DAY26_RESILIENCE_RESULTS.md
```

Contains validation results for system resilience.

---

### Health Monitoring Validation

```text
tests/DAY27_HEALTH_MONITORING_RESULTS.md
```

Contains health-monitoring validation results.

---

### Failure Recovery

```text
tests/DAY29_FAILURE_RECOVERY_RESULTS.md
```

Contains failure and recovery validation results.

---

# 📊 Performance Testing

Performance-oriented tests are available under:

```text
tests/performance/
```

### Classifier Accuracy

```text
test_classifier_accuracy.py
```

Used to evaluate classifier accuracy.

### Ingestion Throughput

```text
test_ingestion_throughput.py
```

Used to evaluate the number of events the ingestion pipeline can process over a given period.

### Pipeline Latency

```text
test_pipeline_latency.py
```

Used to evaluate end-to-end processing latency.

These tests provide quantitative validation of the system's performance characteristics.

---

# 🛡️ Security & Sensitive Data Protection

Security was considered during the implementation of the project.

The repository follows these practices:

- Real credentials are not stored in source code.
- `.env` is excluded from version control.
- `.env.example` contains placeholders only.
- Notification credentials are loaded from environment variables.
- Sensitive data sanitization is implemented in the notification service.
- Generated logs and local runtime artifacts are excluded from Git.
- Virtual environments and Python cache files are excluded from Git.

Example ignored files/directories include:

```text
.env
.venv/
venv/
__pycache__/
logs/
performance_results/
classified.json
vector_metrics.txt
.pytest_cache/
.coverage
```

---

# 📈 Reliability & Validation

The system was validated through multiple stages of development, including:

- End-to-end pipeline validation
- Classifier evaluation
- Confidence evaluation
- Sensitive-data protection testing
- Service health monitoring
- Resilience testing
- Failure recovery testing
- Ingestion throughput testing
- Pipeline latency testing

The corresponding validation documentation is available in:

```text
tests/
```

---

# 🔄 Complete Pipeline

A typical event moves through the system as follows:

```text
1. Server/Application generates a log
                ↓
2. Vector ingests the log
                ↓
3. Vector processes and forwards the event
                ↓
4. AI classifier analyzes the log
                ↓
5. TF-IDF converts text into features
                ↓
6. LinearSVC predicts the log category
                ↓
7. Classification confidence is evaluated
                ↓
8. Sensitive information is protected
                ↓
9. Classified event is stored in OpenSearch
                ↓
10. Important events are identified
                ↓
11. Notification service sends alerts
                ↓
12. Action API can generate controlled test events
```

---

# 🎓 Project Outcomes

The completed system demonstrates an end-to-end approach to intelligent server log monitoring by combining:

- Automated log ingestion
- Machine-learning-based classification
- Centralized log storage
- Intelligent alert generation
- Notification integration
- Sensitive-data protection
- Controlled event generation
- Automated testing
- Reliability validation
- Performance evaluation
- Containerized deployment

The project demonstrates how AI/ML techniques can be integrated with modern observability and DevOps components to improve automated operational monitoring.

---

# 🔮 Future Enhancements

Potential future improvements include:

- Web-based monitoring dashboard
- Real-time visualization of classified logs
- Advanced anomaly detection
- Deep-learning-based log classification
- Automatic incident correlation
- Distributed tracing integration
- Kubernetes deployment
- Horizontal scaling of classifier services
- Advanced alert prioritization
- Historical trend analysis
- Role-based access control
- Authentication and authorization for service APIs

---

# 📌 Current Status

**Project Status: Completed / Demonstration Ready**

The repository contains the implementation, configuration, testing, validation, and performance evaluation components required for demonstrating the AICTE Server Log Monitoring & Intelligent Alert System.

---

# 👨‍💻 Author

**Pavan Kumar**

GitHub:

https://github.com/pavan-kumar22

Project Repository:

https://github.com/pavan-kumar22/PRJ_156_Server_Log_System

---

# 📄 License

This project is developed as an academic/college project.

If this repository is intended for external distribution, an explicit open-source license can be added separately.
