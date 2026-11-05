# Suraksha — Personal Safety App

Suraksha is a local-development web app with a plain HTML/CSS/JavaScript frontend, Java 17 + Spring Boot REST API, JWT authentication, and MySQL 8 database.

## Project structure

- `backend/` — Spring Boot REST API (port 8080)
- `frontend/` — HTML/CSS/JavaScript app (serve on port 5500)
- `db/schema.sql` — MySQL database and table definitions
- `docs/api-spec.md` — API notes
- `.vscode/` — useful VS Code tasks

## Prerequisites

Install **JDK 17 or newer**, **Maven 3.8+**, **MySQL 8**, and **VS Code**. In VS Code, the Extension Pack for Java is useful but optional. Check installations in a terminal:

```bash
java -version
mvn -version
mysql --version
```

## 1. Open the project in VS Code

Extract the ZIP, then open the **`suraksha` folder** (the folder containing `backend`, `frontend`, `db`, and `docs`) in VS Code: **File → Open Folder**.

## 2. Create the database

Start the MySQL service, then from the `suraksha` project root run:

```bash
mysql -u root -p < db/schema.sql
```

Enter the MySQL root password when prompted. This creates the `suraksha` database and its tables. If your MySQL root account has no password, omit `-p` only if your local MySQL setup permits it. You can verify the database with:

```sql
SHOW DATABASES;
USE suraksha;
SHOW TABLES;
```

## 3. Start the backend

Open a VS Code terminal in `suraksha/backend` and set environment variables for your terminal session.

**Windows PowerShell:**

```powershell
$env:DB_USER = "root"
$env:DB_PASSWORD = "YOUR_MYSQL_PASSWORD"
$env:JWT_SECRET = "replace-this-with-a-random-secret-at-least-32-characters-long"
# Optional: set this only if configuring Google Sign-In
# $env:GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
mvn spring-boot:run
```

**macOS / Linux:**

```bash
export DB_USER=root
export DB_PASSWORD='YOUR_MYSQL_PASSWORD'
export JWT_SECRET='replace-this-with-a-random-secret-at-least-32-characters-long'
# Optional: export GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
mvn spring-boot:run
```

Wait until Spring Boot reports that it has started. The API base URL is `http://localhost:8080/api/v1`. Keep this terminal running. If the database connection fails, confirm MySQL is running, the database exists, and the username/password are correct.

## 4. Start the frontend

Open a **second** VS Code terminal at the project root.

```bash
cd frontend
python -m http.server 5500
```

On systems where Python is named `python3`, use `python3 -m http.server 5500`. Open **http://localhost:5500** in Chrome or Edge. Do not open `index.html` directly as a `file://` URL. The frontend's API URL is configured in `frontend/js/api.js` as `http://localhost:8080/api/v1`.

## 5. Test the app

1. Open the frontend and choose **Register**.
2. Create an account using your name, phone number, and a 4–6 digit PIN.
3. Log in with that phone number and PIN.
4. Allow browser location permission on the dashboard.
5. Add at least one emergency contact before testing the SOS workflow.
6. Use **End SOS** to resolve a test alert.

Use a test contact/number when developing. **The current `AlertService` logs alerts; it does not deliver real SMS or email.** The offline fallback only opens the device's SMS application with a prefilled message; the user must press Send.

## Google Sign-In (optional)

Create a Google OAuth **Web application** client ID. Add `http://localhost:5500` as an authorised JavaScript origin. Set the same client ID in `frontend/index.html` (`YOUR_GOOGLE_CLIENT_ID`) and the backend's `GOOGLE_CLIENT_ID` environment variable, then restart both servers. PIN login works without Google Sign-In.

## Troubleshooting

- **`mvn` not recognized:** install Maven and ensure it is on PATH; restart the terminal/VS Code.
- **Java version error:** install JDK 17+ and verify `java -version`.
- **Communications link failure / Access denied:** start MySQL and check `DB_USER` / `DB_PASSWORD`.
- **Frontend says Failed to fetch:** ensure backend is running at port 8080 and frontend is served from `http://localhost:5500`.
- **401 Unauthorized:** log in again; the JWT expires after one hour.
- **Location unavailable:** allow location access in the browser. Geolocation and voice recognition require localhost or HTTPS; voice recognition support varies by browser and may require internet.
- **Port in use:** stop the other process or change the port and update `frontend/js/api.js` accordingly.

## Important limitations

- Alerts are logged, not sent to contacts until an SMS/email provider is integrated.
- A public contact tracking page is not implemented.
- This is a development project, not a certified emergency-response service. Do not rely on it as your only means of getting help. Before real deployment, add HTTPS, production secrets, rate limiting, privacy/security review, and tested delivery monitoring.
