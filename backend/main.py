
import secrets
import string
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from database import get_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    original_url TEXT UNIQUE NOT NULL,
                    short_code VARCHAR(20) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        connection.commit()
        print("URLs table ready")
    finally:
        connection.close()

    yield


app = FastAPI(title="URL Shortener API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    url: HttpUrl


def generate_short_code():
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(6))


@app.get("/")
def home():
    return {"message": "URL Shortener API is running"}


@app.post("/shorten")
def shorten_url(data: URLRequest):
    original_url = str(data.url)
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT short_code FROM urls WHERE original_url = %s",
                (original_url,)
            )
            existing = cursor.fetchone()

            if existing:
                return {
                    "message": "URL already exists",
                    "shortUrl": f"http://localhost:8000/{existing[0]}"
                }

            for _ in range(10):
                short_code = generate_short_code()

                cursor.execute(
                    """
                    INSERT INTO urls (original_url, short_code)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING short_code
                    """,
                    (original_url, short_code)
                )

                result = cursor.fetchone()

                if result:
                    connection.commit()
                    return {
                        "message": "URL shortened successfully",
                        "shortUrl": f"http://localhost:8000/{result[0]}"
                    }

                cursor.execute(
                    "SELECT short_code FROM urls WHERE original_url = %s",
                    (original_url,)
                )
                existing = cursor.fetchone()

                if existing:
                    connection.commit()
                    return {
                        "message": "URL already exists",
                        "shortUrl": f"http://localhost:8000/{existing[0]}"
                    }

            connection.rollback()
            raise HTTPException(
                status_code=503,
                detail="Could not generate a unique code. Try again."
            )
    finally:
        connection.close()


@app.get("/{short_code}")
def redirect_url(short_code: str):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT original_url FROM urls WHERE short_code = %s",
                (short_code,)
            )
            result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found"
            )

        return RedirectResponse(url=result[0], status_code=307)
    finally:
        connection.close()