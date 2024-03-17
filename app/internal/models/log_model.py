from pydantic import BaseModel

class Log(BaseModel):
    time : int #todo have a timestamp check
    log : str
