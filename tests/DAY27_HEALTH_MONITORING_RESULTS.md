# Day 27 - Automated System Health Monitoring

## Project
AICTE Server Log Monitoring & Intelligent Alert System

## Objective

Implement and validate an automated health-check mechanism
for the monitoring platform infrastructure.

## Components Monitored

1. Classifier Service
2. Notification Service
3. OpenSearch

## Test 1 - Normal Health

All services were running normally.

Result: PASS

Expected:
3/3 services healthy

## Test 2 - Classifier Failure Detection

The classifier service was intentionally stopped.

The health-check script correctly detected the classifier
as unavailable while the remaining services remained healthy.

Result: PASS

Expected:
2/3 services healthy
Overall status: DEGRADED

## Test 3 - Classifier Recovery

The classifier service was restarted.

The health-check script correctly detected all services
as healthy.

Result: PASS

Expected:
3/3 services healthy
Overall status: HEALTHY

## Conclusion

The automated health monitoring mechanism successfully
detects service failures and confirms service recovery.

DAY 27 HEALTH MONITORING TEST: PASSED