from fastapi import FastAPI
from routes.routes import router
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from cronjobs import check_meeting_schedule

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: Add and start the job
    scheduler.add_job(check_meeting_schedule, CronTrigger(minute="*/1"), misfire_grace_time=1000) # Example: Runs daily at 1:00 AM
    scheduler.start()
    print("Scheduler started.")
    yield
    # Shutdown event: Shut down the scheduler
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello():
    return {"message": "App is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)