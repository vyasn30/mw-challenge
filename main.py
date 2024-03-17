from fastapi import FastAPI
from fastapi.responses import Response
from log_model import Log
from typing import List

log_db = dict()

app = FastAPI()

@app.post("/ingest")
async def ingest(log_batch: List[Log]):
    try:
        sorted_log_batch = sort_logs(log_batch)
        for log in sorted_log_batch:
                print(log)

        
    except Exception as e: # Just for dev, be explicit late
        Response(status_code=500, message = f"Error {e}")    

def sort_logs(log_batch: List[Log]):
    sorted_logs = sorted(log_batch, key=lambda log: log.time)
    return sorted_logs

    