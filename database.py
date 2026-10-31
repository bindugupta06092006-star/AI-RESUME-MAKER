# database.py

import sqlite3
from datetime import datetime
import hashlib


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_NAME = "resume_database.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    conn = get_db()
    cursor = conn.cursor()

    # ---------------- USER TABLE ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ---------------- RESUME TABLE ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            name TEXT,
            job_title TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            linkedin TEXT,
            portfolio TEXT,

            summary TEXT,
            skills TEXT,
            education TEXT,
            certifications TEXT,
            experience TEXT,

            languages TEXT,
            interests TEXT,
            achievements TEXT,

            style TEXT,
            template TEXT,

            resume_text TEXT,

            created_at TEXT,
            updated_at TEXT,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# Create tables automatically
create_tables()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# USER FUNCTIONS
# ============================================================

def register_user(name, email, password):

    conn = get_db()

    try:

        conn.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hash_password(password)
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# ============================================================
# LOGIN USER
# ============================================================

def login_user(email, password):

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        AND password = ?
        """,
        (
            email,
            hash_password(password)
        )
    ).fetchone()

    conn.close()

    return user


# ============================================================
# SAVE RESUME
# ============================================================

def save_resume(user_id, data, resume_text):

    conn = get_db()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO resumes (

            user_id,

            name,
            job_title,
            email,
            phone,
            location,
            linkedin,
            portfolio,

            summary,
            skills,
            education,
            certifications,
            experience,

            languages,
            interests,
            achievements,

            style,
            template,

            resume_text,

            created_at,
            updated_at

        )

        VALUES (

            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?,
            ?, ?

        )
        """,
        (

            user_id,

            data["name"],
            data["job_title"],
            data["email"],
            data["phone"],
            data["location"],
            data["linkedin"],
            data["portfolio"],

            data["summary"],
            data["skills"],
            data["education"],
            data["certifications"],
            data["experience"],

            data["languages"],
            data["interests"],
            data["achievements"],

            data["style"],
            data["template"],

            resume_text,

            now,
            now
        )
    )

    resume_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return resume_id


# ============================================================
# GET ALL RESUMES OF A USER
# ============================================================

def get_user_resumes(user_id):

    conn = get_db()

    resumes = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return resumes


# ============================================================
# GET ONE RESUME
# ============================================================

def get_resume(resume_id, user_id):

    conn = get_db()

    resume = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE id = ?
        AND user_id = ?
        """,
        (
            resume_id,
            user_id
        )
    ).fetchone()

    conn.close()

    return resume


# ============================================================
# UPDATE RESUME
# ============================================================

def update_resume(
    resume_id,
    user_id,
    data,
    resume_text
):

    conn = get_db()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute(
        """
        UPDATE resumes

        SET

            name = ?,
            job_title = ?,
            email = ?,
            phone = ?,
            location = ?,
            linkedin = ?,
            portfolio = ?,

            summary = ?,
            skills = ?,
            education = ?,
            certifications = ?,
            experience = ?,

            languages = ?,
            interests = ?,
            achievements = ?,

            style = ?,
            template = ?,

            resume_text = ?,

            updated_at = ?

        WHERE id = ?
        AND user_id = ?
        """,
        (

            data["name"],
            data["job_title"],
            data["email"],
            data["phone"],
            data["location"],
            data["linkedin"],
            data["portfolio"],

            data["summary"],
            data["skills"],
            data["education"],
            data["certifications"],
            data["experience"],

            data["languages"],
            data["interests"],
            data["achievements"],

            data["style"],
            data["template"],

            resume_text,

            now,

            resume_id,
            user_id
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# DELETE RESUME
# ============================================================

def delete_resume(resume_id, user_id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM resumes
        WHERE id = ?
        AND user_id = ?
        """,
        (
            resume_id,
            user_id
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# GET RESUME COUNT
# ============================================================

def get_resume_count(user_id):

    conn = get_db()

    result = conn.execute(
        """
        SELECT COUNT(*)
        AS total
        FROM resumes
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return result["total"]