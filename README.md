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

## 🏗 System Architecture

The codebase is structured to ensure long-term maintainability and security.

### 1. Domain-Driven Design
* **`academics` App:** Handles the core business logic (Departments, Courses, Enrollments, Sessions).
* **`account` App:** Manages authentication and user profiles (Student vs. Lecturer).
* **Separation of Concerns:** Authentication logic (`CustomUser`) is strictly separated from academic profiles (`StudentProfile`, `LecturerProfile`). This allows for flexible role assignment without bloating the auth system.

### 2. Explicit Enrollment Modeling
We utilize an explicit **Enrollment** model rather than a simple Many-to-Many relationship. This decision allows the institution to track:
* When a student registered for a course.
* The specific academic session the course was taken.
* The status of the enrollment (e.g., registered, approved, carry-over).

### 3. Role-Based Access Control (RBAC)
Security is baked into the architecture using a two-layer approach:
1.  **Queryset Scoping:** Users can only query data relevant to them (e.g., a Student can only see their own results; a Lecturer sees only their students).
2.  **Permission Policies:** Strict rules (e.g., `IsHodOrReadOnly`, `IsOwnerOrReadOnly`) prevent unauthorized modifications.

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
     
