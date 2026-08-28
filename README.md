# AICTE Server Log Monitoring & Intelligent Alert System

An AI-powered, containerized server log monitoring and intelligent alerting system designed to ingest, analyze, classify, store, and respond to server and application log events in real time.

The system combines log collection, AI-based log classification, centralized search and storage, intelligent alert generation, notification services, and a demonstration Action API into a complete end-to-end observability pipeline.

---

## 📌 Project Information

| Field | Details |
|---|---|
| Project Title | AICTE Server Log Monitoring & Intelligent Alert System |
| Category | Software |
| Project Type | AI-Based Log Monitoring & Observability System |
| Primary Domain | Artificial Intelligence, Machine Learning, DevOps & Observability |
| Architecture | Microservice / Containerized Architecture |
| Deployment | Docker & Docker Compose |
| Repository | `PRJ_156_Server_Log_System` |
| Status | Completed / Demonstration Ready |

---

# 🎯 Problem Statement

Modern server environments generate a large volume of logs from web applications, APIs, databases, containers, and infrastructure services.

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
3. Classifies log messages using machine learning.
4. Assigns a confidence score to classifications.
5. Stores classified events in OpenSearch.
6. Identifies events requiring alerts.
7. Sends notifications for important events.
8. Provides APIs for testing and automated demonstrations.
9. Measures system performance and reliability.

---

# 🚀 Objectives

The major objectives of the project are:

- Develop an automated server log ingestion pipeline.
- Implement AI-based log classification.
- Categorize operational events based on their content.
- Store classified logs in a centralized OpenSearch environment.
- Detect critical operational events automatically.
- Generate intelligent alerts.
- Integrate notification mechanisms.
- Provide a demonstration Action API for controlled event generation.
- Implement sensitive-data protection mechanisms.
- Validate system reliability and failure recovery.
- Evaluate classifier accuracy and confidence.
- Measure ingestion throughput and end-to-end latency.
- Deploy the complete system using Docker containers.

---

# 🏗️ System Architecture

The project follows a containerized microservice architecture.

```text
                    ┌───────────────────────┐
                    │   Server/Application  │
                    │         Logs          │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │        Vector         │
                    │   Log Ingestion &     │
                    │      Processing       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   AI Log Classifier   │
                    │                       │
                    │ TF-IDF + LinearSVC    │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
          ┌──────────────────┐    ┌──────────────────┐
          │    OpenSearch    │    │ Notification     │
          │                  │    │     Service      │
          │ Classified Logs  │    │ Slack / Email    │
          └──────────────────┘    └──────────────────┘

                                ▲
                                │
                    ┌───────────┴───────────┐
                    │      Action API       │
                    │                       │
                    │ Controlled Test/Event │
                    │      Generation       │
                    └───────────────────────┘
