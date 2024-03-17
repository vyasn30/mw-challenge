import boto3
from dotenv import load_dotenv
from threading import Lock

class S3ClientSingleton:
    _instance = None
    _lock = Lock()

    def __new__(
            cls, 
            aws_client_id,
            aws_secret_key,
            region_name,
        ):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(S3ClientSingleton, cls).__new__(cls)
                cls._instance.client = boto3.client(
                    "s3",
                    aws_access_key_id = aws_client_id,
                    aws_secret_access_key = aws_secret_key,
                    region_name = region_name,    
                )   
            
        return cls._instance