"""Suraksha - Flask REST API (Stage 1: auth, contacts, SOS)."""
import os
import re
from datetime import timedelta

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required)
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-only-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
jwt = JWTManager(app)

PHONE_RE = re.compile(r"^\d{10,15}$")
PIN_RE = re.compile(r"^\d{4,6}$")


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "suraksha"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def error(msg, code=400):
    return jsonify({"error": msg}), code


# ---------- Auth ----------
@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    pin = str(data.get("pin") or "")

    if not name:
        return error("Name is required")
    if not PHONE_RE.match(phone):
        return error("Phone must be 10-15 digits")
    if not PIN_RE.match(pin):
        return error("PIN must be 4-6 digits")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE phone=%s", (phone,))
            if cur.fetchone():
                return error("Phone already registered", 409)
            cur.execute(
                "INSERT INTO users (name, phone, pin_hash) VALUES (%s,%s,%s)",
                (name, phone, generate_password_hash(pin)),
            )
        return jsonify({"message": "Registered successfully"}), 201
    finally:
        db.close()


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()
    pin = str(data.get("pin") or "")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, name, pin_hash FROM users WHERE phone=%s", (phone,))
            user = cur.fetchone()
    finally:
        db.close()

    if not user or not check_password_hash(user["pin_hash"], pin):
        return error("Invalid phone or PIN", 401)

    token = create_access_token(identity=str(user["id"]))
    return jsonify({"token": token, "name": user["name"]})


# ---------- Emergency contacts ----------
@app.get("/api/contacts")
@jwt_required()
def list_contacts():
    uid = int(get_jwt_identity())
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, phone FROM emergency_contacts WHERE user_id=%s", (uid,)
            )
            return jsonify(cur.fetchall())
    finally:
        db.close()


@app.post("/api/contacts")
@jwt_required()
def add_contact():
    uid = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name or not PHONE_RE.match(phone):
        return error("Valid name and 10-15 digit phone required")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS c FROM emergency_contacts WHERE user_id=%s", (uid,)
            )
            if cur.fetchone()["c"] >= 5:
                return error("Maximum 5 emergency contacts allowed")
            try:
                cur.execute(
                    "INSERT INTO emergency_contacts (user_id, name, phone) VALUES (%s,%s,%s)",
                    (uid, name, phone),
                )
            except pymysql.err.IntegrityError:
                return error("Contact already added", 409)
        return jsonify({"message": "Contact added"}), 201
    finally:
        db.close()


@app.delete("/api/contacts/<int:contact_id>")
@jwt_required()
def delete_contact(contact_id):
    uid = int(get_jwt_identity())
    db = get_db()
    try:
        with db.cursor() as cur:
            n = cur.execute(
                "DELETE FROM emergency_contacts WHERE id=%s AND user_id=%s",
                (contact_id, uid),
            )
        if not n:
            return error("Contact not found", 404)
        return jsonify({"message": "Contact deleted"})
    finally:
        db.close()


# ---------- SOS ----------
@app.post("/api/sos")
@jwt_required()
def sos():
    uid = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    try:
        lat = float(data.get("lat"))
        lng = float(data.get("lng"))
    except (TypeError, ValueError):
        return error("lat and lng are required numbers")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return error("Coordinates out of range")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO alerts (user_id, latitude, longitude) VALUES (%s,%s,%s)",
                (uid, lat, lng),
            )
            alert_id = cur.lastrowid
            cur.execute(
                "SELECT name, phone FROM emergency_contacts WHERE user_id=%s", (uid,)
            )
            contacts = cur.fetchall()
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"
        return jsonify(
            {
                "alert_id": alert_id,
                "maps_link": maps_link,
                "contacts": contacts,
                "message": "SOS recorded",
            }
        ), 201
    finally:
        db.close()


@app.get("/api/alerts")
@jwt_required()
def alert_history():
    uid = int(get_jwt_identity())
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, latitude, longitude, status, created_at "
                "FROM alerts WHERE user_id=%s ORDER BY created_at DESC LIMIT 50",
                (uid,),
            )
            rows = cur.fetchall()
        for r in rows:
            r["latitude"] = float(r["latitude"])
            r["longitude"] = float(r["longitude"])
            r["created_at"] = r["created_at"].isoformat()
        return jsonify(rows)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
