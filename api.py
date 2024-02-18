from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
# FastAPI 애플리케이션과 Redis 초기화
app = FastAPI()

redis_conn = Redis(host='test_redis', port=6379)
q = Queue('my_queue', connection=redis_conn) # Redis와 연결하여 RQ 큐 생성 

@app.get('/hello')
def hello():
    """Test endpoint"""
    return {'hello': 'world'}

# 1. uuid v4를 key로, 생성 시간을 value로 가지는 객체를 10초동안 랜덤 시간 간격으로 50개 생성해서 redis에 삽입하는 함수    
import random
from datetime import timedelta
from worker import runTask
@app.post("/insert/") # 클라이언트에서 FastAPI 엔드포인트 호출
def insert_data():
    for i in range(50):
        delay = random.uniform(0, 10)
        # RQ를 사용하여 runTask 작업을 랜덤 딜레이 후에 실행하도록 스케줄링
        # RQ worker 프로세스에 의해 비동기적으로 처리
        q.enqueue_in(timedelta(seconds=delay), runTask)
    return {"message": "UUIDs insertion scheduled."}




