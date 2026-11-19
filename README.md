# Suraksha: Web-Based Personal Safety Application

Suraksha (Hindi for *safety*) is a web app that helps a person in danger alert their trusted contacts quickly. With one tap, it records the user's live location and prepares an emergency alert for saved contacts.

> **Status:** Backend (Stage 1) complete. Frontend, live tracking and voice trigger are in development. See the [Roadmap](#roadmap).

---

## Features

**Implemented**
- User registration and login with a phone number and a numeric PIN
- JWT-based session authentication (12-hour tokens)
- PINs stored as salted hashes, never in plain text
- Manage up to 5 emergency contacts per user
- One-tap SOS endpoint that saves the user's coordinates and returns a Google Maps link plus the contact list
- Alert history for each user

**Planned**
- Web frontend with an SOS button using browser geolocation
- Live location sharing through a tracking link (Leaflet and OpenStreetMap)
- Voice-activated trigger (Web Speech API)
- SMS fallback for low connectivity, using a pre-filled `sms:` link
- Nearby police stations and hospitals (Overpass API)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, REST API |
| Authentication | Flask-JWT-Extended, Werkzeug password hashing |
| Database | MySQL (PyMySQL driver) |
| Frontend (planned) | HTML, CSS, JavaScript |
| Maps (planned) | Leaflet, OpenStreetMap |
| Tools | Git, GitHub |

---

## Database Design

Three tables with foreign keys and cascading deletes:

```
users (id, name, phone UNIQUE, pin_hash, created_at)
   |
   |-- 1:N --> emergency_contacts (id, user_id FK, name, phone, UNIQUE(user_id, phone))
   |
   |-- 1:N --> alerts (id, user_id FK, latitude, longitude, status, created_at)
```

- Deleting a user automatically deletes their contacts and alerts (`ON DELETE CASCADE`).
- A composite index on `alerts (user_id, created_at)` keeps alert history queries fast.
- A unique key on `(user_id, phone)` prevents duplicate contacts.

The full schema is in `schema.sql`.

---

## API Reference

Base URL: `http://127.0.0.1:5000`. Routes marked **Auth** need the header `Authorization: Bearer <token>`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/register` | No | Create an account (`name`, `phone`, `pin`) |
| POST | `/api/login` | No | Log in and receive a JWT (`phone`, `pin`) |
| GET | `/api/contacts` | Yes | List emergency contacts |
| POST | `/api/contacts` | Yes | Add a contact (`name`, `phone`) |
| DELETE | `/api/contacts/<id>` | Yes | Delete a contact |
| POST | `/api/sos` | Yes | Record an alert (`lat`, `lng`) |
| GET | `/api/alerts` | Yes | View the last 50 alerts |
| GET | `/api/health` | No | Health check |

**Example**

```bash
# Register
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Asha","phone":"9876543210","pin":"1234"}'

# Log in (copy the token from the response)
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"9876543210","pin":"1234"}'

# Send an SOS
curl -X POST http://127.0.0.1:5000/api/sos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"lat":26.9124,"lng":75.7873}'
```

---

## Getting Started

### Prerequisites
- Python 3.10 or newer
- MySQL or MariaDB

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/suraksha.git
cd suraksha

# 2. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Create the database and tables
mysql -u root -p < schema.sql

# 4. Configure environment variables
cp .env.example .env            # then edit .env with your values

# 5. Run the server
python app.py
```

Open `http://127.0.0.1:5000/api/health`. You should see `{"status": "ok"}`.

### Running in GitHub Codespaces (no local install)

```bash
sudo apt update && sudo apt install -y mariadb-server
sudo service mariadb start
sudo mysql < schema.sql
sudo mysql -e "CREATE USER 'suraksha_user'@'localhost' IDENTIFIED BY 'choose_a_password'; GRANT ALL ON suraksha.* TO 'suraksha_user'@'localhost'; FLUSH PRIVILEGES;"
```

Then set `DB_USER=suraksha_user` and your chosen password in `.env`, install the Python packages, and run `python app.py`.

### Environment Variables

| Variable | Purpose |
|---|---|
| `DB_HOST` | MySQL host (usually `localhost`) |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | Database name (`suraksha`) |
| `JWT_SECRET_KEY` | Long random string used to sign tokens |

---

## Security Notes

- PINs are hashed with Werkzeug's salted hashing.
- All SQL uses parameterized queries, which prevents SQL injection.
- The user ID is read from the verified JWT, never from the request body, so users can only access their own data.
- Input is validated on every endpoint (phone format, PIN length, coordinate ranges).
- Secrets are kept in `.env`, which is excluded from Git.

---

## Roadmap

- [x] **Stage 1:** Database design, authentication, contacts and SOS API
- [ ] **Stage 2:** Frontend (login, contacts, SOS button with geolocation)
- [ ] **Stage 3:** Live location sharing with a tracking link
- [ ] **Stage 4:** Voice-activated trigger
- [ ] **Stage 5:** SMS fallback and nearby safe places

---

## Author

**Kamna Choudhary**
B.Tech Computer Science Engineering, JECRC University, Jaipur
[LinkedIn](https://linkedin.com/in/kamnachoudhary) | [GitHub](https://github.com/kamnachoudhary47-dev)
