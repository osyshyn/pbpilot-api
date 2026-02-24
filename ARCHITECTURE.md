# Complete Project Architecture & Codebase Guide: `pbpilot-api`

Welcome to the detailed architectural guide for the `pbpilot-api` project. This document goes beyond the basics to explain the mechanics of how different components interact, how configuration is managed, and the strict standards applied across the codebase.

---

## 1. Technology Stack and Tooling

*   **Core Framework**: FastAPI (Python >= 3.13)
*   **ASGI Servers**: Uvicorn (local development) & Mangum (AWS Lambda adapter for serverless deployment)
*   **Database Engine**: PostgreSQL, accessed via `asyncpg` (fully asynchronous communication).
*   **ORM**: SQLAlchemy v2.0+ (using `Mapped` declarative syntax).
*   **Migrations**: Alembic (`alembic/` and `alembic.ini`).
*   **Data Validation & Serialization**: Pydantic v2.
*   **Code Quality**: `Ruff` (linter & formatter), `MyPy` (strict static typing), `pre-commit` hooks.
*   **Admin Panel**: `sqladmin` (integrated directly into the FastAPI application).

---

## 2. Application Core & Configuration

### Environment Management (`config/settings.py`)
Configuration is managed using `pydantic-settings`. 
*   **Environments**: The app determines its environment (`local`, `dev`, `prod`) via the `ENV` system variable and loads the corresponding `.env` file (e.g., `.env.local`).
*   **Settings Classes**: Configuration is strictly typed and broken down into logical sub-classes: `TokenSettings`, `DatabaseSettings`, `LoggingSettings`, `AwsSettings`, and `EmailSettings`.
*   **Singleton Pattern**: The settings are loaded using `@cache` on the `Settings.load()` classmethod, ensuring only one instance is created per process for performance.

### Application Routing (`config/router.py`)
*   **API Versioning**: All main endpoints are prefixed with `/api/v1` (controlled by `settings.API_VERSION`).
*   **Modular Routers**: Routers are modularized by domain (e.g., `user_router`, `company_router`, `job_router`). They are aggregated in `initialize_routers()`.
*   **Admin Panel Integration**: If the environment is `local` or `dev`, an instance of `sqladmin.Admin` is initialized and attached to the FastAPI `app`, registering views defined in the `admins/` directory.

---

## 3. Dependency Injection System

FastAPI's `Depends` is highly utilized to build a clean, testable dependency graph. Look in `core/dependencies.py` and `dependencies/auth.py`.

*   **Database Sessions**: `get_session()` is an async generator that yields an `AsyncSession`. It ensures the session is safely closed after the request lifecycle.
*   **Service Injection**: `get_service(ServiceClass)` is a factory dependency. It takes an active database connection and strictly instantiates complex services dynamically.
    ```python
    # Example from an endpoint:
    service: Annotated[CompanyService, Depends(get_service(CompanyService))]
    ```
*   **Authentication Flow**: 
    1.  The `oauth_scheme` extracts a bearer token.
    2.  `get_current_user` decodes the token using `AuthService` and fetches the `User` from `UserService`.
    3.  Role-based dependencies (`get_admin_user_from_token`, `get_manager_user_from_token`, etc.) wrap `get_current_user` to restrict endpoint access easily.

---

## 4. Deep Dive into Architectural Layers

The system follows a strict inward-facing dependency rule: **Endpoints -> Services -> DAOs -> Database**.

### 1️⃣ Models (Database Layer)
**Directory:** `models/`, `core/models.py`
SQLAlchemy 2.0 explicitly typed models. To reduce boilerplate, models inherit from shared mixins in `core.models.py`:
*   `BaseIdMixin`: Provides the auto-incrementing integer `id` primary key.
*   `BaseTimeStampMixin`: Provides standardized `created_at` and `updated_at` (auto-updating) fields.
*   `SoftDelete`: Provides an `is_active` boolean and a `deleted_at` timestamp. Records using this are "archived" rather than permanently deleted via SQL `DELETE`.

### 2️⃣ DAO (Data Access Object Layer)
**Directory:** `dao/`, `core/dao.py`
*   **Purpose**: Complete isolation of SQL. No other layer imports `select` or `insert` from SQLAlchemy.
*   **BaseDAO**: Provides common utilities like asynchronous pagination (`paginate` method calculating totals and limits).
*   **Design**: DAO methods expect primitives or schema fragments and return SQLAlchemy fully mapped objects. They heavily use SQLAlchemy 2.0 features like `selectinload` to fetch related relationships optimally avoiding N+1 query problems.

### 3️⃣ Services (Business Logic Layer)
**Directory:** `services/`, `core/service.py`
*   **Purpose**: The heart of the application. Services inherit from `core.service.BaseService`.
*   **Orchestration**: A Service instantiates required DAOs, runs transactions, catches database errors (like `IntegrityError`), and converts them into Domain errors (custom Exceptions).
*   **State**: They are single-request scoped. They hold the active `AsyncSession`, so multiple DAOs can share the same SQL transaction seamlessly before a final `session.commit()` is called within the Service logic.

### 4️⃣ Endpoints (Presentation Layer)
**Directory:** `endpoints/`
*   **Purpose**: The outer shell. Extremely thin handlers.
*   **Flow**:
    1. Define routes using `APIRouter`.
    2. Enforce authentication via `Depends(get_current_user)`.
    3. Validate JSON payload using Request Schemas (Pydantic).
    4. Call the injected Service.
    5. Return Data wrapped in a Response Schema (using `ResponseSchema.model_validate(domain_object)`).

### 5️⃣ Schemas and DTOs
**Directory:** `schemas/`, `dto/`
*   **Schemas**: Pydantic v2 models. They manage API contracts (Input/Output). They handle validation (like email regexes or string lengths).
*   **DTOs (Data Transfer Objects)**: Lightweight classes (potentially Python `dataclasses` or pure typed dicts) meant for internal component communication, shielding the Service layer from web layer (Pydantic) specifics.

---

## 5. Error Handling and Exceptions

**Directory:** `exceptions/`
The project does not raise generic HTTP 400s inside the deepest parts of code. 
*   **Domain Exceptions**: Instead, business logic errors are represented as custom Python exceptions (e.g., `CompanyAlreadyExistsException`, `UserHasNoPermissionPermission`).
*   **Handling**: These exceptions bubble up and are intercepted by global exception handlers configured at the FastAPI `app` level. The handlers map specific Exceptions (like "Not Found") to proper HTTP status codes (like 404) and standardize the JSON error structure returned to the client.

---

## 6. Strict Coding Standards Enforced

If you contribute to this project, your code must pass strict automated checks defined in `pyproject.toml`:

1.  **Fully Asynchronous**: You cannot use synchronous blocking calls (like `requests` or synchronous `time.sleep`). Use `httpx`, `asyncio.sleep`, and native SQLAlchemy async features.
2.  **MyPy `strict=True`**: 
    *   No dynamic `Any` logic without explicit ignoring.
    *   All functions must have explicit return types (`-> None`, `-> int`).
    *   All class attributes and variables should use modern Python type hinting.
3.  **Ruff Formatting**:
    *   Max line length: **80 characters**.
    *   **Single quotes** strictly enforced for strings (unless inside another string).
    *   `ruff check --fix` will automatically sort imports (`I`), rewrite old syntax (`UP`), and remove unused code. No commented-out code (`ERA001`) or print statements are permitted in commits.
4.  **No Logic in Init**: `__init__.py` files are kept clean and are primarily used for explicit exports. 

---

## 🌟 How to Add a New Feature

1.  **Database**: Create tables using declarative syntax in `models/your_feature.py`. Do not forget to use `BaseIdMixin`.
2.  **Migrations**: Run `alembic revision --autogenerate -m "Add your feature"`. Review the generated migration and execute it.
3.  **Data Models**: Create `schemas/your_feature.py` for API JSON requests/responses using `pydantic.BaseModel`.
4.  **Database Access**: Create `dao/your_feature.py` extending `BaseDAO`. Build your `select`, `insert`, and `update` queries here.
5.  **Business Rules**: Create `services/your_feature.py`. Inject dependencies, call DAOs, handle edge cases, and raise custom exceptions from `exceptions/`.
6.  **API Routes**: Create `endpoints/your_feature.py`. Map HTTP verbs, ensure security by including `Depends(get_current_user)`, and call the service.
7.  **Registration**: Finally, include your router in `config/router.py` to expose it on the server.
