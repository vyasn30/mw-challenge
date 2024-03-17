from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import Response
from typing import List, Optional
from dotenv import load_dotenv
import os
import redis
from app.internal.models.log_model import Log
from app.s3_service.s3_singleton import S3ClientSingleton
import json
from starlette.concurrency import run_in_threadpool
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


app = FastAPI()
load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("S3_Bucket_Name")
AWS_SECRET_ACCESS_KEY = os.environ.get("Secret")
AWS_REGION = os.environ.get("Region")
S3_BUCKET_NAME = os.environ.get("S3_Bucket_Name")

FOLDER_NAME = os.environ.get("Folder_Name")
BUCKET_NAME = os.environ.get("S3_Bucket_Name")

s3_client_singleton = S3ClientSingleton(
    aws_client_id=AWS_ACCESS_KEY_ID,
    aws_secret_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
s3_client = s3_client_singleton.client

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

app = FastAPI()


async def init_s3():
    s3_client_singleton = S3ClientSingleton(
        aws_client_id=AWS_ACCESS_KEY_ID,
        aws_secret_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    s3_client = s3_client_singleton.client

async def start_background_tasks():
    bg_tasks = BackgroundTasks()
    bg_tasks.add_task(process_logs_from_redis)




async def sort_and_store_logs(logs: List[Log], background_tasks: BackgroundTasks):
    if not logs:
        return

    logs_dicts = [log.model_dump() for log in logs]
    sorted_logs = sorted(logs_dicts, key=lambda x: x['time'])
    filename = f"{FOLDER_NAME}/{sorted_logs[0]['time']}.json"
    logs_json = json.dumps(sorted_logs)

    async def upload_to_s3(bucket_name, key, body):
        s3_client = S3ClientSingleton().client
        await run_in_threadpool(
            s3_client.put_object,
            Bucket=bucket_name,
            Key=key,
            Body=body
        )
 
    background_tasks.add_task(upload_to_s3, S3_BUCKET_NAME, filename, logs_json)



def ingest_log(log):
    redis_client.rpush("logs:cache", json.dumps(log.dict()))



async def process_logs_from_redis():
    batch_size = 100
    while True:
        logs = [redis_client.lpop("logs:cache") for _ in range(batch_size)]
        logs = [log for log in logs if log]  # Removing Nones
        if not logs:
            break
        logs_dicts = [json.loads(log) for log in logs]
        await sort_and_store_logs(logs_dicts)


app.add_event_handler("startup", init_s3)
app.add_event_handler("startup", start_background_tasks)


@app.post("/ingest")
async def ingest_logs(log_batch: List[Log], background_tasks: BackgroundTasks):
    for log in log_batch:
        background_tasks.add_task(ingest_log, log)
    return {"message": "Logs ingested successfully"}



#Just a download endpoint for checking
@app.get("/download")
def download():
    local_directory = 'downloaded_files/'

    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER_NAME)

    if 'Contents' in response:
        for item in response['Contents']:
            file_name = item['Key']
            local_file_path = os.path.join(local_directory, file_name[len(FOLDER_NAME):])
            
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            s3_client.download_file(BUCKET_NAME, file_name, local_file_path)
            print(f'Downloaded {file_name} to {local_file_path}')
    else:
        print("No files found in the specified path.")


#Very primitive search
"""
TODO: 
-Add levels for logs so that search space becomes smaller,
-Experiment with Elastic Search or FAISS if we are feeling more optimistic
-API access has been revoked, try once we get it back 
-Pagination
"""        

@app.get("/query")
async def query_logs(start: int, end: int, text: str):
    start_datetime = datetime.fromtimestamp(start)
    end_datetime = datetime.fromtimestamp(end)

    date_range_prefixes = generate_date_range_prefixes(start_datetime, end_datetime)
    
    matching_logs = []
    for prefix in date_range_prefixes:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        
        for obj in response.get('Contents', []):
            log_data = s3_client.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            logs = log_data['Body'].read().decode('utf-8')
            if text in logs:
                matching_logs.append(logs)  

    return matching_logs


def generate_date_range_prefixes(start_datetime, end_datetime):
    prefixes = []
    current_date = start_datetime
    while current_date <= end_datetime:
        prefixes.append(f"{FOLDER_NAME}/{current_date.strftime('%Y/%m/%d/')}")
        current_date += timedelta(days=1)
    return prefixes