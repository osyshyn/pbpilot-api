# Job Domain Model & Relations

This document describes the data model starting from `jobs` and all directly
related tables: `units`, `rooms`, `observations`, `photos`, `coc_forms`,
`samples`, `job_documents`, and `calendar_events`.

---

## 1. High‑Level Relationship Overview

Textual graph (one `Job` as the root):

```text
ProjectProperty (project_properties)
        ▲
        │  N:1
        │
      Job (jobs) ────────────► Inspector (inspectors)
        │   ▲
        │   │
        │   ├──────────────► COCForm (coc_forms) ─────────► Sample (samples)
        │   │                   1:N                            1:N
        │   ├──────────────► JobDocument (job_documents)
        │   │                       1:N
        │   ├──────────────► CalendarEvent (calendar_events)
        │   │                       1:N
        │   │
        │   └──────────────► Unit (units) ────────────────► Room (rooms)
        │                       1:N                             1:N
        │                       │
        │                       └──────────────► COCForm (coc_forms, per‑unit)
        │
        └────────────────────────────────────────────────────────┘
                                        1:N
                                       Observation (observations) ───► Photo (photos)
                                            (interior & exterior)          1:N
```

Key points:

- A **Job** belongs to a **ProjectProperty** and (optionally) to an **Inspector**.
- Jobs можуть утворювати ланцюжки `parent_job_id` → `retest_jobs`, де
  повторні перевірки (`RETEST`) посилаються на оригінальну інспекцію.
- Each **Job** can have:
  - Many **Units** (`units`)
  - Many **COCForms** (`coc_forms`)
  - Many **JobDocuments** (`job_documents`) — attached PDF/DOCX files.
  - Many **CalendarEvents** (`calendar_events`) — re-test visits, etc.
  - Many **Observations** with `is_exterior = TRUE` (exposed as
    `Job.exterior_observations`).
- A **Unit** has its own **Rooms** and a floor plan.
- An **Observation** may be linked to a **Room** (interior) or have
  `room_id = NULL` (exterior).
- Each **Observation** can have many **Photos** stored in S3.
- Each **COCForm** can have many **Samples** with type‑specific metadata.

---

## 2. Job (`jobs`)

**Model:** `models.jobs.Job`  
**Base mixins:** `BaseIdMixin`, `BaseTimeStampMixin`, `SoftDelete`

- **Primary key**
  - `id: int` — auto‑increment integer.
- **Foreign keys**
  - `property_id: int` → `project_properties.id`, `ondelete='CASCADE'`,
    indexed, soft‑delete aware via partial index.
  - `inspector_id: int | None` → `inspectors.id`, `ondelete='SET NULL'`,
    nullable, indexed.
- **Business fields**
  - `inspection_type: InspectionTypeEnum` — required enum:
    `PERSONAL_BUSINESS_METING`, `CONSULTATION`, `RISK_ASSESSMENT`, `LIRA`,
    `CLEARANCE`, `PRE_INSPECTION`, `SAMPLING`, `RETEST`.
  - `status: JobStatusEnum` — required enum:
    `COMPLETED`, `IN_PROGRESS`, `SCHEDULED`, `AWAITING_RESULTS`.
  - `notes: str | None` — free‑form notes (up to 2048 chars).
- **Relationships**
  - `property: ProjectProperty` — `ProjectProperty.jobs` (1:N).
  - `inspector: Inspector | None` — direct relation to assigned inspector.
  - `units: list[Unit]` — `Unit.job`, cascade `all, delete-orphan`.
  - `coc_forms: list[COCForm]` — `COCForm.job`, cascade `all, delete-orphan`.
  - `exterior_observations: list[Observation]` — filtered view‑only
    relationship (`Observation.job_id = Job.id AND is_exterior = TRUE`).
  - `documents: list[JobDocument]` — `JobDocument.job`,
    cascade `all, delete-orphan`.
  - `calendar_events: list[CalendarEvent]` — `CalendarEvent.job`,
    cascade `all, delete-orphan`.

---

## 3. Units & Rooms

### 3.1 Unit (`units`)

**Model:** `models.unit.Unit`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

- **Primary key**
  - `id: uuid.UUID` — UUIDv4, generated in the backend but compatible with
    offline clients (Flutter).
- **Foreign keys**
  - `job_id: int` → `jobs.id`, `ondelete='CASCADE'`, `nullable=False`,
    indexed.
- **Business fields**
  - `name: str` — human‑readable unit identifier (`'Unit 2A'`, `'Basement'`),
    `String(255)`, required.
  - `is_common_area: bool` — whether this unit is a common area (hallway,
    stairwell, lobby), default `False`.
  - `floor_plan_s3_key: str | None` — S3 key for floor plan image/PDF,
    `String(512)`, nullable.
  - `floor_plan_data: dict | None` — JSONB‑поле з довільними даними з Flutter
    (координати, геометрія, службові метадані), що описують план поверху
    конкретного юніта.
- **Relationships**
  - `job: Job` — `Job.units`.
  - `rooms: list[Room]` — `Room.unit`, cascade `all, delete-orphan`.
  - `coc_forms: list[COCForm]` — `COCForm.unit`, пер‑юніт COC‑форми
    для інтер’єрних зразків.

### 3.2 Room (`rooms`)

**Model:** `models.unit.Room`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `unit_id: uuid.UUID` → `units.id`, `ondelete='CASCADE'`, required,
    indexed.
- **Business fields**
  - `name: str` — room/section name (`'Living Room'`, `'Kitchen'`),
    `String(255)`, required.
- **Relationships**
  - `unit: Unit` — `Unit.rooms`.
  - `observations: list[Observation]` — `Observation.room`,
    cascade `all, delete-orphan`.

---

## 4. Observations & Photos

### 4.1 Observation (`observations`)

**Model:** `models.observation.Observation`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `job_id: int` → `jobs.id`, `ondelete='CASCADE'`, required, indexed.
  - `room_id: uuid.UUID | None` → `rooms.id`, `ondelete='CASCADE'`,
    nullable, indexed.
    - `NULL` ⇒ exterior observation (no specific room).
    - Not `NULL` ⇒ interior observation bound to a concrete room.
- **Business fields**
  - `category: ObservationCategoryEnum`:
    - `HAZARD`
    - `FUTURE_RISK`
    - `EXCLUSION`
    - `INFO` — informational / general (e.g. title-page photos for PDF reports).
  - `is_exterior: bool` — `True` for exterior, `False` for interior.
  - `component: str` — inspected component (`'Window Sill'`, `'Door Frame'`),
    `String(255)`, required.
  - `side: str | None` — side label (`'A'`, `'B'`, `'C'`, `'D'`, `'All'`),
    `String(50)`, nullable.
  - `condition: str | None` — condition (`'peeling'`, `'intact'`, etc.),
    `String(255)`, nullable.
  - `identifiers: str | None` — IDs/numbering (`'1-2'`, `'1-5'`),
    `String(255)`, nullable.
  - `raw_text: str | None` — original text fragment from report,
    `String(1024)`, nullable.
- **Relationships**
  - `job: Job` — `Job.exterior_observations` (subset via filter) and any
    future `Job.observations` relation.
  - `room: Room | None` — `Room.observations`.
  - `photos: list[Photo]` — `Photo.observation`, cascade `all, delete-orphan`.

### 4.2 Photo (`photos`)

**Model:** `models.observation.Photo`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `observation_id: uuid.UUID` → `observations.id`, `ondelete='CASCADE'`,
    required, indexed.
- **Business fields**
  - `s3_key: str` — S3 key to the photo file, `String(512)`, required.
- **Relationships**
  - `observation: Observation` — `Observation.photos`.

---

## 5. Sampling: COCForm & Sample

### 5.1 COCForm (`coc_forms`)

**Model:** `models.sampling.COCForm`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `job_id: int` → `jobs.id`, `ondelete='CASCADE'`, `nullable=False`,
    indexed.
  - `unit_id: uuid.UUID | None` → `units.id`, `ondelete='CASCADE'`,
    nullable, indexed.
    - `NULL` ⇒ exterior COC‑форма / зразки, що не прив’язані до конкретного
      юніта (наприклад, ґрунт, зовнішній пил).
    - не `NULL` ⇒ COC‑форма для конкретного юніта (квартири).
- **Business fields**
  - `is_active: bool` — logical flag for current/archived COC forms,
    default `True`.
- **Relationships**
  - `job: Job` — `Job.coc_forms`.
  - `unit: Unit | None` — `Unit.coc_forms`, якщо форма прив’язана до юніта.
  - `samples: list[Sample]` — `Sample.coc_form`,
    cascade `all, delete-orphan`.

### 5.2 Sample (`samples`)

**Model:** `models.sampling.Sample`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `coc_form_id: uuid.UUID` → `coc_forms.id`, `ondelete='CASCADE'`,
    required, indexed.
- **Business fields**
  - `sample_type: SampleTypeEnum` (from `models.jobs`):
    - `PAINT_CHIP`
    - `DUST_WIPE`
    - `WATER`
    - `SOIL`
  - `barcode_id: str` — short barcode/ID (`"01"`, `"02"`), `String(100)`,
    required.
  - `location_description: str | None` — human description
    (`"Kitchen floor window sill"`), `String(512)`, nullable.
  - `side: str | None` — mainly for Paint Chip (`"Side A"`, `"Side B"`),
    `String(50)`, nullable.
  - `component: str | None` — e.g. `"Wall"` for Paint Chip,
    `String(255)`, nullable.
  - `soil_area: str | None` — `"Dripline"`, `"Play Area"`, etc. for Soil,
    `String(100)`, nullable.
  - `photo_s3_key: str | None` — optional photo of sampling location,
    `String(512)`, nullable.
- **Relationships**
  - `coc_form: COCForm` — `COCForm.samples`.

---

## 6. Job documents & calendar events

### 6.1 JobDocument (`job_documents`)

**Model:** `models.job_auxiliary.JobDocument`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

Stores PDF/DOCX files attached to an inspection (e.g. Clearance: control
orders, legacy reports, estimates).

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `job_id: int` → `jobs.id`, `ondelete='CASCADE'`, required, indexed.
- **Business fields**
  - `document_type: str` — e.g. `'CONTROL_ORDER'`, `'OLD_LAB_RESULTS'`,
    `'OTHER'`, `String(100)`, required.
  - `s3_key: str` — object key in bucket (e.g. `jobs/123/documents/abc.pdf`),
    `String(512)`, required.
  - `file_name: str` — original file name for UI, `String(255)`, required.
- **Relationships**
  - `job: Job` — `Job.documents`.

### 6.2 CalendarEvent (`calendar_events`)

**Model:** `models.job_auxiliary.CalendarEvent`  
**Base mixins:** `BaseUUIDMixin`, `BaseTimeStampMixin`

Stores calendar events for the inspector (e.g. re-test visits) without
duplicating the Job entity.

- **Primary key**
  - `id: uuid.UUID`.
- **Foreign keys**
  - `job_id: int` → `jobs.id`, `ondelete='CASCADE'`, required, indexed.
- **Business fields**
  - `scheduled_date: str` — ISO date/time from mobile, `String(255)`, required.
  - `event_type: str` — e.g. `'RE_TEST_VISIT'`, `'SAMPLE_PICKUP'`,
    `String(100)`, required.
  - `note: str | None` — inspector/manager notes, `String(1024)`, nullable.
- **Relationships**
  - `job: Job` — `Job.calendar_events`.

---

## 7. Summary

- `Job` зберігається з **integer** `id` і є коренем всіх доменних сутностей
  для інспекції, включно з ланцюжками `parent_job_id` → `retest_jobs` для
  повторних перевірок.
- Всі похідні сутності (Units, Rooms, Observations, Photos, COCForms, Samples,
  JobDocuments, CalendarEvents) використовують **UUID primary key**, що добре
  узгоджується з офлайн‑клієнтами.
- Всі зв’язки побудовані за принципом:
  - чіткі FK з `ondelete` (`CASCADE` або `SET NULL`);
  - `cascade='all, delete-orphan'` для дочірніх колекцій;
  - окремі enum‑типи для статусів/категорій/типів зразків;
  - COC‑форми можуть бути як unit‑scoped (`unit_id` не `NULL`), так і
    exterior‑scoped (`unit_id` = `NULL`).

