# H-Link: Alberta Healthcare Claims Adjudication System

## Project Overview

H-Link is a comprehensive, modern healthcare claims processing platform designed for the Alberta healthcare system. It facilitates the end-to-end lifecycle of claims, from submission by healthcare providers to automated adjudication and final settlement. The system emphasizes compliance, auditability, and efficiency, replacing legacy manual workflows with a robust, rule-based engine.

### Key Features

*   **Provider Portal**: Secure interface for submitting claims, uploading supporting documents, and tracking claim status.
*   **Automated Adjudication Engine**: Configurable rule-based engine that validates claims against AHCIP (Alberta Health Care Insurance Plan) regulations in real-time.
*   **Admin Dashboard**: Centralized control for system administrators to manage users, configure rules, and oversee system health.
*   **Claims Management**: Advanced tools for manual review, flagging, and adjustment of complex claims.
*   **Dynamic Rule Builder**: Visual editor allowing administrators to create and modify adjudication logic without code deployment.
*   **Audit & Compliance**: HIPAA-compliant logging of all actions, with detailed reporting and data retention policies.
*   **Document Management**: Secure storage and retrieval of claim-related documentation (PDFs, images) linked to specific claims.

## Tech Stack

### Frontend
*   **Framework**: Vue 3 (Composition API)
*   **Language**: TypeScript
*   **State Management**: Pinia
*   **Routing**: Vue Router
*   **Styling**: Tailwind CSS
*   **Build Tool**: Vite

### Backend
*   **Framework**: FastAPI (Python)
*   **Database**: PostgreSQL (with SQLAlchemy ORM & Alembic)
*   **Caching**: Redis
*   **Validation**: Pydantic
*   **Testing**: Pytest
*   **Documentation**: OpenAPI (Swagger UI)

## Project Structure

```
.
├── backend/                # FastAPI Backend Application
│   ├── app/
│   │   ├── api/            # API Route handlers (v1)
│   │   ├── core/           # Core config, security, and database logic
│   │   ├── middleware/     # Custom middleware (Audit, Auth, Rate Limit)
│   │   ├── models/         # SQLAlchemy Database Models
│   │   ├── schemas/        # Pydantic Schemas (Request/Response)
│   │   ├── services/       # Business logic layer
│   │   └── main.py         # Application entry point
│   ├── tests/              # Pytest test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variable template
│
└── frontend/               # Vue 3 Frontend Application
    ├── src/
    │   ├── components/     # Reusable UI components
    │   ├── composables/    # Shared logic hooks
    │   ├── layouts/        # Page layouts
    │   ├── stores/         # State management
    │   ├── views/          # Application pages
    │   └── services/       # API client services
    └── package.json        # Node dependencies
```

## Getting Started

### Prerequisites

*   **Node.js** (v18+)
*   **Python** (v3.10+)
*   **PostgreSQL** (v14+)
*   **Redis** (v6+)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Copy the example environment file and update it with your local settings.
    ```bash
    cp .env.example .env
    ```
    *Ensure your PostgreSQL database is running and the credentials in `.env` match.*

5.  **Run the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.
    API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Start the Development Server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## Database Management

The project uses **Alembic** for database migrations (setup required in backend).

*   **Initialize DB**: The application attempts to create tables on startup if they don't exist (dev mode).
*   **Production**: Use Alembic to manage schema changes.

## Testing

*   **Backend**: Run `pytest` from the `backend/` directory.
*   **Frontend**: Run `npm run test` from the `frontend/` directory.

## User Roles

*   **Provider**: Submit and track claims.
*   **Adjudicator**: Review flagged claims and process manual adjustments.
*   **Admin**: Configure system rules, users, and view audit logs.
*   **Auditor**: Read-only access for compliance verification.

*   **Auditor**: Read-only access to audit logs and reports.
