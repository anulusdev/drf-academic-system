# Edusystem – Academic Management System API

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.0+-green?style=for-the-badge&logo=django)
![DRF](https://img.shields.io/badge/DRF-Latest-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![pytest](https://img.shields.io/badge/Tests-pytest-orange?style=for-the-badge&logo=pytest)

**Edusystem** is a production-grade backend REST API that digitizes and centralizes the core academic operations of a higher education institution from user registration and role management to course allocation, student enrollment, and departmental oversight.

Built as a personal project to go beyond tutorial-level Django and confront real engineering decisions: schema design under constraint, role-based access control enforced at the database layer, atomic state transitions, and a tested, containerized codebase.

---

## The Problem

Nigerian universities and higher education institutions broadly manage academic operations through fragmented, manual processes:

- Course registration happens on paper or through disconnected portals
- Student records, enrollment statuses, and results live in separate systems with no integrity guarantees
- Access control is enforced at the frontend only the backend does not know or care who is calling it
- Role distinctions between Students, Lecturers, and Heads of Department are handled informally

Edusystem is a backend API designed to replace those gaps with a system where institutional rules are enforced at the data layer not just at the interface level.

---

## What It Does

- **Role-aware user registration** — users register as Students or Lecturers; the correct domain profile is created automatically via a post-save signal calling an explicit service layer
- **Departmental structure** — Departments have a designated Head of Department (HOD) with scoped write access over their department's data
- **Course management** — Lecturers can self-allocate to courses within their department; HODs manage course creation and updates
- **Student enrollment** — Students can enroll in courses within their department through a structured approval workflow with status tracking (Pending → Approved/Rejected)
- **Two-layer RBAC** — data access is filtered at the SQL level via `get_queryset()` overrides, then gated at the object level via custom permission classes
- **Role transitions** — a user's role can switch between Student and Lecturer; the old profile is soft-deleted and a new one is created atomically

---

## Architecture Decisions

### 1. Decoupled Authentication and Domain Identity

The default Django `User` model handles credentials only — email, password, role flag. Domain-specific data lives in separate `StudentProfile` and `LecturerProfile` models, each linked to `CustomUser` via a `OneToOneField` with `CASCADE` deletion.

```
CustomUser          →  credentials, role
StudentProfile      →  department, level, session, enrollment history
LecturerProfile     →  department, allocated courses
```

This separation prevents god-model anti-patterns. A `profile` property on `CustomUser` dynamically returns the correct profile based on the user's current role, giving views a single unified interface regardless of user type.

### 2. Explicit Junction Table for Enrollment

Django's built-in `ManyToManyField` was intentionally avoided for course registration. Instead, an explicit `Enrollment` model is used as the through table.

**Why?** A plain M2M link cannot carry the metadata that real academic enrollment requires:

| Field | Purpose |
|---|---|
| `status` | Tracks Pending / Approved / Rejected state |
| `approved_by` | FK to the user who approved — creates an audit trail |
| `approved_at` | Timestamp of approval |

A `UniqueConstraint` on `(student, course)` enforces idempotency at the database level — a student cannot enroll in the same course twice, even under concurrent requests.

### 3. Service Layer for Role Transitions

Complex business logic that touches multiple models is handled in `account/services.py` via an explicit `UserService` class — not in signals, not in views.

**Why not signals?** Signals are invisible — they fire on every model save regardless of context, are hard to debug, and make tests unreliable. Moving this logic into an explicit service makes it findable, traceable, and independently testable. The signal layer is kept minimal: it only handles new user creation by delegating to the same service.

### 4. Two-Layer RBAC

Security is enforced at two distinct points in the request lifecycle:

**Layer 1 — Queryset Scoping (SQL level)**

`get_queryset()` is overridden in each ViewSet to filter the dataset before it ever reaches serialization:

**Layer 2 — Object-Level Permissions (application level)**

Custom permission classes act as the final gatekeeper before any mutation:

| Permission Class | Behaviour |
|---|---|
| `IsAdminOrReadOnly` | Read: anyone. Write: staff only |
| `IsHodOrReadOnly` | Read: anyone. Write: HOD of the relevant department only |
| `IsStudent` | Access: authenticated users with a StudentProfile only |
| `IsLecturer` | Access: authenticated users with a LecturerProfile only |
| `IsOwnerOrReadOnly` | Read: anyone in scope. Write: the profile owner only |

`IsHodOrReadOnly` uses `hasattr` to handle both `Department` objects (checking `obj.hod`) and `Course` objects (checking `obj.department.hod`) with a single permission class — polymorphic permission logic.


### 5. Containerization with Docker

The entire application runs in Docker with `docker-compose`. The PostgreSQL service includes a health check — the Django container does not start until the database is confirmed ready:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

All secrets are managed via environment variables — no credentials are hardcoded.

---

## Database Schema

![DB Schema](https://github.com/anulusdev/drf-academic-system/blob/a14cf8028fff31bb7cc3643dadd81fc74255bc59/DB%20schema%20file.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | Django 5.0+, Django REST Framework |
| Database | PostgreSQL 16 |
| Authentication | JWT via `djoser` + `djangorestframework-simplejwt` |
| API Docs | `drf-spectacular` (Swagger UI + ReDoc) |
| Containerization | Docker, docker-compose |
| Testing | `pytest`, `pytest-django` |
| Filtering | `django-filter` |
| Dev Tools | `django-debug-toolbar`, Pipenv |

---

## Project Structure

```
drf-academic-system/
│
├── account/                        # User identity and profile management
│   ├── models.py                   # CustomUser, StudentProfile, LecturerProfile
│   ├── serializers.py              # User creation and profile serializers
│   ├── views.py                    # StudentViewSet, LecturerViewSet
│   ├── permissions.py              # IsOwnerOrReadOnly
│   ├── services.py                 # UserService — role transition business logic
│   ├── tests.py                    # Profile creation, queryset scoping, permission tests
│   └── signals/
│       └── handlers.py             # Minimal signal — delegates to UserService
│
├── academics/                      # Academic domain operations
│   ├── models.py                   # Department, Course, Enrollment, AcademicSession
│   ├── serializers.py              # Course and Department serializers
│   ├── views.py                    # CourseViewSet (enroll, allocate), DepartmentViewSet
│   ├── permissions.py              # IsAdminOrReadOnly, IsHodOrReadOnly, IsStudent, IsLecturer
│   └── tests.py                    # RBAC, enrollment logic, service layer tests
│
├── common/
│   └── seriliazers.py              # Shared serializers to resolve circular imports
│
├── Edusystem/                      # Project configuration
│   ├── settings.py                 # Main settings
│   ├── settings_test.py            # Test-specific settings (local DB host override)
│   └── urls.py                     # Root URL config including Swagger UI
│
├── conftest.py                     # Shared pytest fixtures (users, clients, api_client)
├── pytest.ini                      # pytest configuration
├── docker-compose.yaml             # Multi-service container setup
├── Dockerfile                      # Application container definition
└── Pipfile                         # Dependency management
```

---

## Testing

The test suite uses `pytest` and `pytest-django` and covers three layers:

**RBAC and Permission Tests**
- Unauthenticated users can browse courses (intentional — read-only public access)
- Students cannot create or modify courses
- Admins can create courses
- Lecturers are blocked from enrolling in courses

**Enrollment Business Logic**
- Students can enroll in courses within their department
- Duplicate enrollment is rejected at the application layer (backed by a `UniqueConstraint` at the database layer)
- Students cannot enroll in courses outside their department
- Lecturers cannot enroll in courses

**Service Layer Tests**
- Role switching creates the correct new profile
- The old profile is soft-deleted (`is_active=False`), not destroyed
- New user registration auto-creates the correct profile type

**Account and Queryset Scoping Tests**
- A student querying `/account/students/` receives only their own profile
- A lecturer receives only students in their department
- Anonymous users are denied access

### Running Tests

```bash
# Run all tests
pytest -v

# Run a specific test file
pytest academics/tests.py -v

# Run a specific test class
pytest account/tests.py::TestProfileAutoCreation -v

# Stop at first failure
pytest -x -v
```

> Tests run against a local PostgreSQL instance using `Edusystem/settings_test.py`,
> which overrides only the database host. Docker is not required to run the test suite locally.

---

## Installation & Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16
- Docker & docker-compose (optional but recommended)
- Pipenv

### Option A — Run with Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/anulusdev/drf-academic-system.git
cd drf-academic-system

# 2. Create a .env file in the project root
cp .env.example .env
# Edit .env with your credentials

# 3. Start the containers
docker-compose up --build

# 4. The API is available at http://localhost:8000
# Swagger UI is at http://localhost:8000/
```

### Option B — Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/anulusdev/drf-academic-system.git
cd drf-academic-system

# 2. Install dependencies
pipenv install
pipenv shell

# 3. Set environment variables (or create a .env file)
export SECRET_KEY=your-secret-key
export DB_NAME=Edusystem
export DB_USER=postgres
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=5432

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | Required |
| `DB_NAME` | PostgreSQL database name | `Edusystem` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | Required |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost` |

---

## API Documentation

Once the server is running, interactive API documentation is available at:

| Interface | URL |
|---|---|
| Swagger UI | `http://localhost:8000/` |
| ReDoc | `http://localhost:8000/redoc/` |
| Raw Schema | `http://localhost:8000/schema/` |

---

## Authentication

Edusystem uses JWT authentication via `djoser` and `djangorestframework-simplejwt`.

```bash
# Register a new user
POST /auth/users/

# Obtain a JWT token
POST /auth/jwt/create/
{
  "email": "user@example.com",
  "password": "yourpassword"
}

# Include the token in subsequent requests
Authorization: JWT <your_access_token>
```

---

## Key Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/academics/courses/` | Anyone | List all courses |
| `POST` | `/academics/courses/` | Admin only | Create a course |
| `POST` | `/academics/courses/{id}/enroll/` | Students only | Enroll in a course |
| `POST` | `/academics/courses/{id}/allocate/` | Lecturers only | Self-allocate to a course |
| `GET` | `/academics/department/` | Anyone | List all departments |
| `POST` | `/academics/department/` | Admin / HOD | Create a department |
| `GET` | `/account/students/` | Authenticated | Scoped by role |
| `GET` | `/account/lecturers/` | Authenticated | Scoped by role |
| `POST` | `/auth/users/` | Anyone | Register a new user |
| `POST` | `/auth/jwt/create/` | Anyone | Obtain JWT token |

---

## Planned Extensions

These are tracked improvements not yet implemented in the current version:

- **Session-scoped enrollment** — link `Enrollment` directly to an `AcademicSession` so records are scoped by academic year, allowing historical data to remain intact across year transitions
- **Enrollment approval endpoint** — an explicit action for HODs/Lecturers to approve or reject pending enrollments (the `status` and `approved_by` fields on `Enrollment` already support this workflow)
- **CI/CD pipeline** — GitHub Actions workflow for automated test runs on every pull request
- **Production deployment** — Railway or Render deployment with environment-based settings switching

---

## Contributing

Contributions, issues, and pull requests are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Write tests for your changes
4. Ensure all tests pass: `pytest -v`
5. Submit a pull request with a clear description of what changed and why

---

## Author

**Alhazan Khaleed Semilore**
Software Engineering Student — Federal University of Technology, Akure (FUTA)

- GitHub: [@anulusdev](https://github.com/anulusdev)
- Email: khaleedsemilore@gmail.com
