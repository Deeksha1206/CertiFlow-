# ⚡ CertiFlow

<p align="center">
  <strong>Bulk Certificate Generation & Verification API</strong>
</p>

<p align="center">
  A production-style backend system for generating, tracking, verifying, and downloading digital certificates in bulk.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-11%20Passed-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

</p>

---

## 🚀 Overview

**CertiFlow** is a REST API designed to automate certificate generation and verification at scale.

Instead of generating certificates one by one, an organization can submit a single bulk generation job containing multiple recipients.

CertiFlow then:

```text
Submit Job
    ↓
Validate Request
    ↓
Create Job + Certificate Records
    ↓
Background Processing
    ↓
Generate Individual PDFs
    ↓
Track Success / Failure
    ↓
Generate QR Verification
    ↓
Download or Verify Certificate
```

### 🎯 Core Principle

> **Generate → Track → Verify**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📦 **Bulk Generation** | Generate certificates for multiple recipients through one API request |
| ⚡ **Background Processing** | Process certificate generation asynchronously |
| 📊 **Progress Tracking** | Track successful, failed, pending, and completed certificates |
| 🛡️ **Failure Isolation** | One failed certificate does not stop the remaining batch |
| 📄 **PDF Generation** | Generate professionally formatted certificate PDFs |
| 🔍 **QR Verification** | Verify certificates using a unique QR code |
| 🆔 **Unique Certificate IDs** | Every certificate receives a unique identifier |
| 📥 **PDF Download** | Download successfully generated certificates |
| ✅ **Request Validation** | Validate recipient and job data before processing |
| 🧪 **Automated Testing** | 11 automated tests covering core functionality |
| 📚 **Swagger UI** | Interactive API documentation through FastAPI |

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │       CLIENT        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FASTAPI REST API  │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
           ┌──────────────────┐          ┌──────────────────┐
           │  JOB MANAGEMENT  │          │ CERTIFICATE API  │
           └────────┬─────────┘          └────────┬─────────┘
                    │                             │
                    ▼                             ├── Retrieve
           ┌──────────────────┐                   ├── Verify
           │ BACKGROUND TASK  │                   └── Download
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ CERTIFICATE      │
           │ SERVICE          │
           └────────┬─────────┘
                    │
             ┌──────┴──────┐
             │             │
             ▼             ▼
      ┌──────────────┐  ┌──────────────┐
      │ PDF Generator│  │   Database   │
      │  ReportLab   │  │  SQLAlchemy  │
      └──────┬───────┘  └──────────────┘
             │
             ▼
      ┌─────────────────────┐
      │ Generated PDFs      │
      └─────────────────────┘
```

---

# 🔄 Processing Workflow

```text
┌───────────────────────┐
│ Client submits job    │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Validate request      │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Create Job            │
│ + Certificate records │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Background processing │
└───────────┬───────────┘
            ↓
    ┌───────┴────────┐
    ↓                ↓
 SUCCESS           FAILURE
    ↓                ↓
 Generate PDF     Store Error
    ↓                ↓
    └───────┬────────┘
            ↓
┌───────────────────────┐
│ Update Job Progress   │
└───────────┬───────────┘
            ↓
┌─────────────────────────────┐
│ COMPLETED                   │
│ COMPLETED_WITH_ERRORS       │
│ FAILED                      │
└─────────────────────────────┘
```

---

# 🛡️ Failure Isolation

One of CertiFlow's important design decisions is **individual certificate failure isolation**.

A failure while generating one certificate does **not** terminate the entire batch.

### Example

```text
Certificate 1  →  ✅ SUCCESS
Certificate 2  →  ❌ FAILED
Certificate 3  →  ✅ SUCCESS
Certificate 4  →  ✅ SUCCESS
```

The final job becomes:

```text
COMPLETED_WITH_ERRORS
```

The successful certificates remain available for retrieval and download.

This behavior is explicitly tested in the automated test suite.

---

# 📊 Job Tracking

Each generation job maintains detailed processing information.

### Example

```json
{
  "status": "COMPLETED_WITH_ERRORS",
  "total_recipients": 10,
  "successful_count": 9,
  "failed_count": 1,
  "pending_count": 0,
  "progress_percent": 100.0
}
```

### Tracked Information

- 👥 Total recipients
- ✅ Successful certificates
- ❌ Failed certificates
- ⏳ Pending certificates
- 📈 Progress percentage
- 🔄 Current job status
- 🕐 Start timestamp
- 🏁 Completion timestamp

---

# 🔍 QR-Based Certificate Verification

Every successfully generated certificate receives:

```text
┌───────────────────────────────────────┐
│                                       │
│       CERTIFICATE OF COMPLETION       │
│                                       │
│             Recipient Name            │
│                                       │
│          Event / Workshop             │
│                                       │
│      Certificate ID: CERT-XXXX        │
│                                       │
│                  ┌─────────┐          │
│                  │   QR    │          │
│                  │  CODE   │          │
│                  └─────────┘          │
│                                       │
│              ✓ VERIFIED               │
│                                       │
└───────────────────────────────────────┘
```

The QR code points to:

```http
GET /api/v1/certificates/{certificate_id}/verify
```

Verification provides:

- Certificate ID
- Recipient name
- Event name
- Event date
- Issue timestamp
- Verification status

---

# 🔌 REST API

## ❤️ Health

```http
GET /health
```

Returns the service health status.

---

## 📦 Jobs

### Create Generation Job

```http
POST /api/v1/jobs
```

### Example Request

```json
{
  "event_name": "Aereo Cloud Engineering Workshop",
  "event_date": "2026-10-07",
  "recipients": [
    {
      "name": "Deeksha Sharma",
      "email": "deeksha@example.com"
    },
    {
      "name": "Rahul Kumar",
      "email": "rahul@example.com"
    }
  ]
}
```

### Example Response

```json
{
  "job_id": "example-job-id",
  "status": "QUEUED",
  "message": "Certificate generation job accepted.",
  "total_recipients": 2
}
```

---

### Get Job Status

```http
GET /api/v1/jobs/{job_id}
```

Returns:

- Job status
- Total recipients
- Successful certificates
- Failed certificates
- Pending certificates
- Progress percentage
- Start time
- Completion time

---

# 🎓 Certificate API

### Retrieve Certificate

```http
GET /api/v1/certificates/{certificate_id}
```

### Verify Certificate

```http
GET /api/v1/certificates/{certificate_id}/verify
```

### Download Certificate

```http
GET /api/v1/certificates/{certificate_id}/download
```

---

# 🧪 Testing

CertiFlow includes an automated test suite covering the major functional requirements.

### Current Result

```text
╔══════════════════════════════╗
║       CERTIFLOW TESTS        ║
╠══════════════════════════════╣
║                              ║
║          11 PASSED ✅        ║
║                              ║
╚══════════════════════════════╝
```

### Covered Scenarios

- ✅ Health endpoint
- ✅ Job creation
- ✅ Missing job handling
- ✅ Invalid email validation
- ✅ Empty recipient validation
- ✅ Invalid recipient name validation
- ✅ Bulk certificate generation
- ✅ Job completion
- ✅ Progress tracking
- ✅ Certificate retrieval
- ✅ Certificate verification
- ✅ PDF download
- ✅ Individual certificate failure isolation

Run the complete suite:

```bash
pytest -v
```

---

# 🧰 Technology Stack

### Backend

```text
Python 3.11
FastAPI
Pydantic
SQLAlchemy
```

### Database

```text
SQLite
SQLAlchemy ORM
```

### Document Generation

```text
ReportLab
QRCode
Pillow
```

### Testing

```text
Pytest
FastAPI TestClient
HTTPX
```

### API Documentation

```text
OpenAPI
Swagger UI
ReDoc
```

---

# 📁 Project Structure

```text
CertiFlow/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── certificates.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── job_service.py
│   │   └── certificate_service.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_jobs.py
│   ├── test_validation.py
│   ├── test_certificates.py
│   └── test_failure_isolation.py
│
├── templates/
├── generated_certificates/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Deeksha1206/CertiFlow-.git
cd CertiFlow-
```

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure Environment

Create a `.env` file:

```env
CERTIFLOW_BASE_URL=http://127.0.0.1:8000
```

## 5. Start the API

```powershell
uvicorn app.main:app --reload
```

---

# 📚 API Documentation

Once the server is running:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

FastAPI automatically provides interactive OpenAPI documentation for all endpoints.

---

# 🧠 Engineering Decisions

### ⚡ Background Processing

Certificate generation is delegated to FastAPI background tasks so the API can accept a bulk job without forcing the client to wait for every PDF.

### 🛡️ Individual Error Handling

Each certificate is processed independently.

This ensures:

```text
One failure ≠ Entire batch failure
```

### 🗃️ Persistent Job Tracking

Jobs and certificates are represented as separate database entities.

```text
Job
│
├── Certificate 1
├── Certificate 2
├── Certificate 3
└── Certificate N
```

This allows detailed tracking of individual certificate outcomes.

### 🆔 Unique Certificate IDs

Every certificate receives a unique identifier used for retrieval and verification.

### 🔍 Digital Verification

QR codes connect generated certificates directly to the verification API.

---

# 🔮 Future Enhancements

The architecture can be extended with:

- 🐘 PostgreSQL
- ⚡ Redis + Celery distributed workers
- 🔐 JWT authentication
- 👥 Role-based access control
- 📧 Email certificate delivery
- 📤 CSV bulk upload
- 🎨 Multiple certificate templates
- 🚫 Certificate revocation
- 📊 Admin dashboard
- ☁️ Cloud object storage
- 🐳 Docker deployment
- 🚦 Rate limiting
- 📈 Observability and metrics
- 🔁 Retry mechanisms
- ☁️ Cloud deployment

---

# 🎯 Engineering Highlights

CertiFlow demonstrates practical backend engineering concepts:

```text
REST API Design
       │
       ▼
Request Validation
       │
       ▼
Background Processing
       │
       ▼
Database Persistence
       │
       ▼
PDF Generation
       │
       ▼
Fault Isolation
       │
       ▼
Progress Tracking
       │
       ▼
Digital Verification
       │
       ▼
Automated Testing
```

The project focuses on more than simply making an API work.

It demonstrates:

> **Reliability + Maintainability + Fault Isolation + Testability + Extensibility**

---

# 👩‍💻 Author

## Deeksha S

**B.Tech Computer Science & Engineering**  
**REVA University**

---

<p align="center">

### ⚡ CertiFlow

**Generate. Track. Verify.**

Built with Python + FastAPI ❤️

</p>
