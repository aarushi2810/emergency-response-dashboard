import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# Initialize FastAPI app
app = FastAPI()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Database Setup
# ---------------------------
def init_db():
    try:
        with sqlite3.connect("alerts.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing the database: {e}")
        raise HTTPException(status_code=500, detail="Database initialization failed")

init_db()  # Initialize DB on startup

# ---------------------------
# Pydantic Model
# ---------------------------
class Alert(BaseModel):
    type: str
    location: str

# ---------------------------
# API Routes
# ---------------------------
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/alert")
def trigger_alert(alert: Alert):
    try:
        with sqlite3.connect("alerts.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO alerts (type, location) VALUES (?, ?)",
                (alert.type, alert.location)
            )
            conn.commit()
            logger.info(f"Alert stored: {alert}")
        return {"message": "✅ Alert stored successfully"}
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error when storing alert: {e}")
        raise HTTPException(status_code=400, detail="Integrity error while storing alert")
    except sqlite3.OperationalError as e:
        logger.error(f"Operational error when storing alert: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")
    except sqlite3.Error as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/alerts")
def get_alerts():
    try:
        with sqlite3.connect("alerts.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            logger.info(f"Fetched {len(rows)} alerts from the database.")
        return {"alerts": rows}
    except sqlite3.Error as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Global Exception Handling (Optional, for uncaught exceptions)
@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return {"detail": "An unexpected error occurred. Please try again later."}