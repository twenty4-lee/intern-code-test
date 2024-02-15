from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue

from worker import runTask

app = FastAPI()

redis_conn = Redis(host='test_redis', port=6379)
q = Queue('my_queue', connection=redis_conn)

@app.get('/hello')
def hello():
    """Test endpoint"""
    return {'hello': 'world'}
