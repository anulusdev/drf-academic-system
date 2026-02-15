# Edusystem – Academic Management System API

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.0+-green?style=for-the-badge&logo=django)
![DRF](https://img.shields.io/badge/DRF-Latest-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)

**Edusystem** is a comprehensive backend API designed to digitize and streamline core academic operations for higher education institutions.

While many school management systems struggle with data fragmentation and administrative bottlenecks, Edusystem provides a centralized, scalable architecture to manage the entire academic lifecycle—from student admission and course enrollment to departmental oversight and session management.

---

## 🎯 The Problem & Solution Edusystem Provides

### Real-World Challenges
Universities and colleges often face significant operational inefficiencies:
1.  **Fragmented Data:** Student records, course registrations, and results are often disconnected, leading to errors.
2.  **Administrative Bottlenecks:** Manual course registration and verification processes slow down the academic calendar.
3.  **Lack of Historical Context:** Difficulty in distinguishing between current active records and historical data from previous academic sessions.
4.  **Complex Access Needs:** Distinguishing between what a Student, a Lecturer, and a Head of Department (HOD) should see requires complex logic that basic tools fail to handle.

### The Edusystem Solution
Edusystem solves these problems by providing:
* **Automated Enrollment Flow:** A structured system for course registration that links students, courses, and academic sessions efficiently.
* **Session-Scoped Data:** Built-in management for `AcademicSession` (e.g., 2024/2025), ensuring that historical records remain intact while operations focus on the current term.
* **Hierarchical Data Integrity:** Ensures that a Department HOD has oversight over their department's data, while Lecturers retain control over their specific courses.
* **Scalable Architecture:** Built to handle the complex relationships between thousands of students, hundreds of courses, and shifting faculty roles.

---

## ⚙️ Implementation & Architecture Decisions

This project follows a **Domain-Driven Design (DDD)** approach to ensure scalability and maintainability. Below are the key architectural decisions:

### 1. Decoupled Authentication & Profiling (Separation of Concerns)
Instead of overloading the default Django `User` model, we strictly separate **Authentication** from **Domain Logic**.
* **`CustomUser` (Auth):** Handles only login credentials (email, password, staff status).
* **`StudentProfile` / `LecturerProfile` (Domain):** Stores academic data (Department, Level, Faculty ID).
* **Why?** This prevents "God Models" and allows a single user to theoretically hold multiple roles (e.g., a Staff member who is also a Student) without schema conflicts.

### 2. Explicit Junction Tables (The Enrollment Model)
We intentionally avoided Django's standard Many-to-Many field for Course Registration. Instead, we utilized an explicit **`Enrollment`** model.
* **Why?** A simple M2M link cannot store critical metadata such as:
    * *When* the student registered.
    * *Which* Academic Session the course belongs to (e.g., 2023 vs 2024).
    * *Status* of the course (Registered, Approved, Failed, Passed).

### 3. Session-Scoped Data Architecture
To solve the problem of historical data integrity, the system relies on an **`AcademicSession`** model.
* **Design:** All enrollment and academic records are tied to a specific session.
* **Benefit:** This allows the system to remain "active" for the current year while preserving immutable records of previous years, preventing data loss during year transitions.

### 4. Two-Layer Security Implementation (RBAC)
Security is enforced at both the Database and Application levels:
* **Layer 1: Queryset Scoping:** Overridden `get_queryset()` methods ensure that users never fetch data outside their permission scope (e.g., A student querying `/results/` receives only *their* results—filtering happens at the SQL level).
* **Layer 2: Object Permissions:** Custom permission classes (e.g., `IsHodOrReadOnly`, `IsOwner`) act as a final gatekeeper to prevent unauthorized modifications.

### Database Schema
Below is the architectural overview of the database relationships:

![Alt text](https://github.com/anulusdev/drf-academic-system/blob/a14cf8028fff31bb7cc3643dadd81fc74255bc59/DB%20schema%20file.png)

---

## 🛠 Tech Stack

- **Language:** Python 3.12+
- **Framework:** Django & Django Rest Framework (DRF)
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens) via `djoser`
- **Utilities:** `django-filter`, `psycopg2`

---

## 📂 Project Structure

```text
edusystem/
├── account/                 # User Identity & Profile Management
│   ├── models.py            # CustomUser, StudentProfile, LecturerProfile
│   ├── permissions.py       # Profile-based permissions
│   └── views.py             # Auth endpoints
│
├── academics/               # Academic Operations
│   ├── models.py            # Department, Course, Enrollment, AcademicSession
│   ├── permissions.py       # Object-level permissions (Course ownership, HOD rights)
│   └── views.py             # Academic CRUD operations
│
└── config/                  # Settings & URL Routing
```

## 🚀 Installation & Setup
### Prerequisites
  - Python 3.12+

  - PostgreSQL

  - Pipenv (recommended) or pip

### Steps
  1. Clone the repository
  ```bash
    git clone [https://github.com/anulusdev/drf-academic-system.git]
    cd drf-academic-system
  ```

  2. Install Dependencies
     ```bash
     pipenv install
     pipenv shell
     ```
     
  3. Run Migrations
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```
     
  4. Create Superuser
     ```bash
       python manage.py createsuperuser
     ```
     
  5. Start Server
     ```bash
       python manage.py runserver
     ```
     
