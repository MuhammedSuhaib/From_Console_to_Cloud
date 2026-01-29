# Phase V: Advanced Cloud Deployment with Kafka and Dapr

## 1. Problem Statement

Transform the existing cloud-native Todo Chatbot application into an enterprise-grade event-driven system using Apache Kafka for messaging, Dapr (Distributed Application Runtime) for microservices orchestration, and deploy to production-grade Kubernetes on Azure (AKS), Google Cloud (GKE), or Oracle Cloud (OKE). The system should support advanced features like recurring tasks, due dates & reminders, and follow cloud-native patterns with event sourcing architecture.

## 2. User Stories

### 2.1 Advanced Task Management
- **As an authenticated user**, I want to create tasks with due dates so that I can track deadlines effectively
- **As an authenticated user**, I want to set reminders for tasks so that I receive notifications before deadlines
- **As an authenticated user**, I want to create recurring tasks so that repetitive tasks are automatically scheduled
- **As an authenticated user**, I want to manage task priorities, tags, and search functionality so that I can organize my work efficiently

### 2.2 Event-Driven Architecture
- **As a system**, I want to process task events asynchronously via Kafka so that the system remains responsive during heavy loads
- **As a system**, I want to decouple services using Dapr pub/sub so that services can scale independently
- **As a system**, I want to use Dapr state management so that conversation state is reliably persisted across service instances
- **As a system**, I want to use Dapr service invocation so that services can communicate securely with automatic retries

### 2.3 Cloud Deployment
- **As a developer**, I want to deploy the application to AKS/GKE/OKE with Dapr and Kafka so that it runs in production
- **As a developer**, I want to use CI/CD pipelines via GitHub Actions so that deployments are automated and reliable
- **As an operator**, I want comprehensive monitoring and logging so that system health can be observed
- **As a user**, I want the application to remain highly available and resilient to failures

## 3. Functional Requirements

### 3.1 Advanced Task Features
- **Due Date Support**: Tasks can have optional due dates with timezone awareness
- **Reminder System**: Tasks can have optional reminder times that trigger notifications
- **Recurring Tasks**: Tasks can be configured to repeat on specific schedules (daily, weekly, monthly, yearly)
- **Enhanced Search**: Tasks can be searched by title, tags, categories, priority, and status
- **Filtering & Sorting**: Advanced filtering by due date, priority, creation date, etc.

### 3.2 Event-Driven Architecture
- **Kafka Integration**: All task operations published as events to Kafka topics for downstream processing
- **Dapr Pub/Sub**: Use Dapr's pub/sub building block to abstract Kafka complexity
- **Event Processing**: Separate services consume events for reminders, auditing, and analytics
- **Real-time Sync**: Multiple client sessions synchronized via events

### 3.3 Dapr Integration
- **Dapr Pub/Sub**: Abstract Kafka through Dapr's pub/sub building block for vendor neutrality
- **Dapr State Management**: Store conversation state using Dapr's state management API
- **Dapr Service Invocation**: Use Dapr's service invocation for inter-service communication
- **Dapr Secrets Management**: Securely manage secrets through Dapr's secrets API
- **Dapr Jobs API**: Use Dapr's Jobs API for scheduled reminders instead of cron bindings

### 3.4 API Endpoints
- **POST /api/{user_id}/tasks/reminder**: Schedule a reminder for a task with specific timing
- **POST /api/{user_id}/tasks/recurring**: Create a recurring task with schedule pattern
- **GET /api/{user_id}/tasks/search**: Search tasks by various criteria (title, tags, due date, etc.)
- **PATCH /api/{user_id}/tasks/{id}/due-date**: Update task due date and reminder settings
- **GET /api/{user_id}/tasks/calendar**: Get tasks in calendar format with due dates

## 4. Non-Functional Requirements

### 4.1 Performance
- Event publishing to Kafka should complete within 100ms
- Reminder delivery should occur within 1 minute of scheduled time
- API endpoints should respond within 500ms under normal load
- System should handle 1000+ concurrent users without degradation

### 4.2 Scalability
- Kafka partitions should support horizontal scaling of event consumers
- Dapr-enabled services should scale independently based on demand
- Kubernetes deployments should auto-scale based on CPU/memory metrics
- Event processing should handle peak loads without message loss

### 4.3 Reliability
- Event-driven architecture should ensure eventual consistency
- Dapr's built-in retries and circuit breakers should handle transient failures
- Kafka should provide message durability and replay capability
- Kubernetes should ensure high availability through pod replicas

### 4.4 Security
- Dapr should handle service-to-service authentication with mTLS
- Kafka should use SSL/TLS encryption for message transport
- Secrets should be managed through Dapr's secrets API or Kubernetes secrets
- All API requests must include valid JWT tokens for authorization

## 5. Domain Model

Extended Todo model with advanced features:

```
Task (Phase I + II + V):
  - id: unique identifier (integer, auto-incrementing)
  - user_id: string (foreign key for user association)
  - title: short description (string, required)
  - description: detailed text (string, optional)
  - completed: boolean status (default: false)
  - priority: enum (low, medium, high) - Phase II addition
  - tags: list of strings - Phase II addition
  - category: single classification - Phase II addition
  - created_at: timestamp - Phase II addition
  - updated_at: timestamp - Phase II addition
  - due_date: datetime (optional) - Phase V addition
  - remind_at: datetime (optional) - Phase V addition
  - recurrence_pattern: string (optional, cron-like format) - Phase V addition
  - parent_task_id: integer (optional, for subtasks) - Phase V addition
```

New Event model for event-driven architecture:
```
TaskEvent:
  - id: unique identifier
  - user_id: string (for partitioning)
  - event_type: string (create, update, complete, delete, reminder, recurring_spawn)
  - task_id: integer (related task)
  - payload: json (event data)
  - timestamp: datetime (when event occurred)
```

## 6. Technical Constraints

### 6.1 Platform & Architecture
- **Event Streaming**: Apache Kafka (via Redpanda Cloud or self-hosted Strimzi)
- **Distributed Runtime**: Dapr for microservices building blocks
- **Orchestration**: Kubernetes on AKS/GKE/OKE
- **CI/CD**: GitHub Actions for automated deployments
- **Monitoring**: Prometheus and Grafana for metrics, centralized logging

### 6.2 Dependencies
- **Kafka Client**: Standard Kafka clients via Dapr pub/sub (no direct client code)
- **Dapr SDK**: HTTP/gRPC clients for Dapr building blocks
- **Kubernetes**: K8s-native deployment with proper resource definitions
- **Observability**: Prometheus metrics, centralized logging setup

### 6.3 Architecture
- **Event-Driven**: Loose coupling through Kafka/Dapr pub/sub
- **Microservices**: Services communicate through Dapr building blocks
- **Stateless**: Main services remain stateless with state stored via Dapr
- **Resilient**: Retry logic, circuit breakers, and fault tolerance built-in

## 7. Acceptance Criteria

### 7.1 Advanced Features
- [ ] Users can create tasks with due dates and receive timely reminders
- [ ] Recurring tasks are automatically spawned according to schedule
- [ ] Task search and filtering work across all supported criteria
- [ ] Priority, tags, and categorization features function correctly
- [ ] Calendar view shows tasks with due dates properly

### 7.2 Event-Driven Architecture
- [ ] All task operations generate appropriate events in Kafka
- [ ] Notification service consumes events and sends reminders
- [ ] Audit service consumes events and maintains history
- [ ] Multiple client sessions stay synchronized via events
- [ ] Event replay works for recovery scenarios

### 7.3 Dapr Integration
- [ ] Dapr pub/sub successfully abstracts Kafka for application code
- [ ] Dapr state management handles conversation state reliably
- [ ] Dapr service invocation enables secure inter-service communication
- [ ] Dapr secrets management securely handles configuration
- [ ] Dapr Jobs API schedules and executes reminders precisely

### 7.4 Cloud Deployment
- [ ] Application deploys successfully to AKS/GKE/OKE
- [ ] Dapr runs as sidecar containers alongside application services
- [ ] Kafka/Redpanda runs in the cluster or connects externally
- [ ] CI/CD pipeline automates testing and deployment
- [ ] Monitoring and logging capture system health

## 8. Success Metrics

- Event processing latency under 100ms for 95% of messages
- Reminder delivery accuracy within 1 minute of scheduled time
- System handles 1000+ concurrent users with <500ms response time
- 99.9% uptime in production environment
- All API endpoints properly secured with JWT authentication
- Zero data loss during normal operation and failover scenarios

## 9. Out of Scope

- Real-time collaboration beyond synchronization
- Machine learning features for task prediction
- Third-party calendar integrations (Google Calendar, Outlook)
- Email/SMS notification channels (notification service only handles internal events)
- Complex workflow engines beyond simple recurring tasks

## 10. Edge Cases

- Handling Kafka downtime gracefully with fallback mechanisms
- Managing reminder storms during system recovery
- Ensuring no duplicate recurring tasks are created
- Handling time zone differences for due dates and reminders
- Managing event ordering when multiple operations happen rapidly
- Recovering from service failures while maintaining consistency