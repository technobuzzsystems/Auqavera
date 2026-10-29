# AQUAVERA — Premium Water Purifier Platform

> **"Pure Water. Thoughtfully Designed."**

A modern, responsive, full-stack water purifier e-commerce and customer service demonstration platform built with **Python 3.14 / Django 5.2**, **PostgreSQL**, and a custom-designed **CSS design system**.

---

## 1. Project Overview & Original Brand Identity

AQUAVERA is a demonstration water purification brand inspired by contemporary Indian residential water realities (borewell, municipal tap, and tanker water). It provides a full-featured customer experience including an interactive product catalogue, multi-attribute filtering, side-by-side product comparison, interactive product finder wizard, customer enquiries, doorstep service ticket booking, user accounts, and a staff operations dashboard.

### Brand Personality & Visual Design
- **Brand Name:** AQUAVERA
- **Tagline:** Pure Water. Thoughtfully Designed.
- **Palette:**
  - Deep Navy: `#102A43`
  - Aqua Blue: `#19B6C9`
  - Soft Light Cyan: `#DDF7F7`
  - Off-White Background: `#F8FBFC`
  - Slate Secondary: `#526477`
  - Dark Slate Text: `#172B3A`
  - Accent Gradient: `linear-gradient(135deg, #16B8C8 0%, #65D6D0 100%)`
- **Typography:** Inter and Plus Jakarta Sans with a clear typographic hierarchy.
- **Logo:** Typographic wordmark with an original inline SVG abstract water-drop geometry.

### Critical Image Requirement Compliance
- **No external water purifier photographs are used.**
- All product cards and detail views utilize an **abstract CSS placeholder system** composed of multi-layer radial gradients, dashed water-rings, abstract vector waves, and a camera concept badge.
- Reserves a consistent 240px image container on cards and 380px on detail views.
- **Future-Ready:** If an image is uploaded in the future via the Admin Dashboard or Django Admin (`product.image`), the system automatically switches to rendering the real uploaded photo.

---

## 2. Technology Stack

- **Backend:** Python 3.14+, Django 5.2 LTS, Django ORM, Django Forms & Authentication
- **Database:** PostgreSQL (with `psycopg` 3.3 binary driver)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Security:** CSRF tokens on all forms, honeypot spam protection, role-based authorization (`is_staff`), session isolation, XSS-safe templates

---

## 3. Implemented URL Routes

| URL Route | Description | Access Level |
|---|---|---|
| `/` | Homepage with hero art, trust stats, categories, featured products, and purification steps | Public |
| `/products/` | Product catalogue with search, category, technology, price, capacity filters, and sorting | Public |
| `/products/<slug>/` | Detailed product showcase with tabs (specs, maintenance, FAQs, related, enquiry modal) | Public |
| `/compare/` | Side-by-side comparison matrix for up to 3 purifiers | Public |
| `/product-finder/` | 4-question interactive wizard recommending matching purifiers | Public |
| `/about/` | Original brand story, engineering philosophy, and water stewardship values | Public |
| `/contact/` | Contact inquiry form with demo business details and support numbers | Public |
| `/service-request/` | Doorstep service booking form (installation, maintenance, repair, filter replacement) | Public |
| `/enquiry/success/` | Confirmation screen displaying unique tracking reference (e.g. `ENQ-20261029-XXXX`) | Public |
| `/service-request/success/` | Confirmation screen displaying unique service reference (e.g. `SRV-20261029-XXXX`) | Public |
| `/accounts/register/` | Customer self-registration with profile fields | Public |
| `/accounts/login/` | Customer & staff authentication | Public |
| `/accounts/logout/` | Safe sign-out handler | Public |
| `/accounts/profile/` | Customer profile management (address, phone, city) | Authenticated |
| `/accounts/my-enquiries/` | Customer's private history of submitted product inquiries | Authenticated (Owner only) |
| `/accounts/my-service-requests/`| Customer's private history of booked service tickets | Authenticated (Owner only) |
| `/dashboard/` | Branded staff overview with summary metrics and activity feeds | Staff Only (`is_staff=True`) |
| `/dashboard/products/` | Product catalogue management table (add, edit, delete, activate) | Staff Only (`is_staff=True`) |
| `/dashboard/enquiries/` | Manage and update status of customer enquiries | Staff Only (`is_staff=True`) |
| `/dashboard/service-requests/` | Manage and update status of technician service requests | Staff Only (`is_staff=True`) |
| `/admin/` | Standard secure Django Admin foundation | Superuser / Staff |

---

## 4. Setup & Running Instructions (Windows PowerShell)

### Prerequisites
- Python 3.12+ (tested with Python 3.14.4)
- PostgreSQL (running locally on port 5432)

### Step 1: Open PowerShell and Navigate to Project Directory
```powershell
cd "h:\WATER PURIFIRE"
```

### Step 2: Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

*(If creating a fresh virtual environment from scratch:)*
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Configure Database Credentials
Edit `.env` (a ready template is provided in `.env.example`):
```ini
SECRET_KEY=aquavera-dev-super-secure-key-demo-2026-prod-grade
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

DB_NAME=aquavera_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 4: Apply Database Migrations
```powershell
python manage.py migrate
```

### Step 5: Seed Demo Data (Repeatable Command)
Run the built-in, idempotent seeding command to populate categories, 10 fictional water purifiers, FAQs, demo testimonials, and accounts:
```powershell
python manage.py seed_demo_data
```
> **Note:** This command can be executed repeatedly without generating duplicate records.

### Step 6: Run Automated Tests
```powershell
python manage.py test
```
*(All 25 automated unit and integration tests will execute against a clean test database).*

### Step 7: Launch the Development Server
```powershell
python manage.py runserver
```
Visit **[http://localhost:8000/](http://localhost:8000/)** in your browser.

---

## 5. Demo Accounts

The database seed command automatically initializes two accounts:

### Staff Operations Account
- **Username:** `admin`
- **Password:** `Admin@12345`
- **Access:** Grants full access to `/dashboard/`, `/dashboard/products/`, `/dashboard/enquiries/`, `/dashboard/service-requests/`, and `/admin/`.

### Demo Customer Account
- **Username:** `customer`
- **Password:** `Customer@12345`
- **Access:** Grants access to `/accounts/profile/`, `/accounts/my-enquiries/`, and `/accounts/my-service-requests/`.

---

## 6. Testing Results

All 25 automated tests passed successfully:
```text
Creating test database for alias 'default'...
.........................
----------------------------------------------------------------------
Ran 25 tests in 7.397s

OK
Destroying test database for alias 'default'...
System check identified no issues (0 silenced).
```

### Covered Test Areas:
- Product list and product detail page rendering
- Category filtering, full-text search, and price sorting
- Product image CSS placeholder rendering (when `image` is null)
- Valid and invalid enquiry submissions with honeypot spam protection
- Valid and invalid service request bookings (date validation)
- Customer registration, login, and logout
- Customer privacy isolation (preventing cross-account viewing)
- Staff-only dashboard access control (redirecting unauthorized customers)
- Model unique constraint validation and reference number generation
