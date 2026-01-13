# Trip Management System (Local Demo)

Lightweight Flask demo for managing trips, bookings, agents and admins. Built for local development on Windows. Includes role-aware booking flows, agent onboarding via secret URL, CSRF protection, and a reseed script that recreates the SQLite DB.

---

## Features (high level)
- Browse trips (public).
- Customer booking flow: booking form → payment page → confirmation → bookings list.
- Role-based bookings listing: customers see only their bookings; agents/admins see all.
- Agents require admin approval before full access.
- Agent onboarding via secret URL: `/agent/onboard/<token>` (not linked in UI).
- Unique usernames — signup will fail if username exists.
- CSRF protection enabled for POST forms.
- Admin pages: manage trips, view users and agents, approve/reject agents.
- Simple carousel and improved UI, footer, password show/hide eye icon.

---

## Quick start (Windows PowerShell)

1. Open PowerShell in project folder:
   cd "C:\Users\lenovo\OneDrive\Desktop\Trip Management System\Trip-Management-System"

2. Create & activate virtual env:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install requirements:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Reset and seed the database:
   ```powershell
   python .\reset_db.py
   ```

5. Run the app:
   ```powershell
   python .\app.py
   ```
   Open: http://127.0.0.1:5000

---

## Default seeded accounts
- admin / password — admin (approved)  
- jane / secret — customer  
- john / secret — customer  
- agentjohn / agentpass — agent (approved)  
- newagent / pending123 — agent (pending approval)

Reset the DB (step 4 above) to recreate these accounts.

---

## Agent onboarding
Agent sign-up is only available via the onboarding URL:
- /agent/onboard/<token>

Set a custom token (optional):
```powershell
$env:ONBOARD_TOKEN = "my-secret-token"
```
Then share the onboarding link:
- https://.../agent/onboard/my-secret-token

---

## Important notes
- Usernames are enforced unique. AuthService.create_user returns None if username exists.
- There is no endpoint in the UI that publicly advertises agent signup — onboarding is token-restricted.
- CSRF is enabled. All POST forms must include `{{ csrf_token() }}` (templates already updated).
- To change the app secret (recommended for production), edit `app.secret_key` in `app.py`.

SMTP email notifications for agent approval are optional and controlled with env vars:
- SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL

---

## File locations (edit points)
- app entry and routes: `app.py`
- DB services and business logic: `services.py`
- DB models: `models.py`
- Templates: `templates/` (index.html, add_booking.html, payment.html, booking_confirmation.html, admin_*.html, login.html, signup_*.html, etc.)
- Static assets: `static/style.css`, `static/carousel.js`
- DB reseed script: `reset_db.py`
- Notifications helper: `notifications.py`

---

## Troubleshooting
- BuildError: "Could not build url for endpoint '...'" — template calls an endpoint name that doesn't exist. Either add the route or update the template to the correct endpoint name. Inspect the traceback to find which template/endpoint is failing.
- CSRF token missing (Bad Request) — ensure POST form includes `<input name="csrf_token" value="{{ csrf_token() }}">` and the session/secret is active.
- If you change routes, restart the app to clear Flask routing state.

---

## Housekeeping
- `.gitignore` added to ignore `.venv`, `__pycache__`, `trip.db`, etc.
- To remove compiled caches (PowerShell):
  ```powershell
  Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
  Get-ChildItem -Path . -Recurse -Include *.pyc -File | Remove-Item -Force
  ```

---