from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from worker import runTask

# FastAPI 애플리케이션과 Redis 초기화
app = FastAPI()
# redis_conn = Redis 인스턴스에 연결하기 위한 객체, Python 애플리케이션과 Redis 서버 사이의 연결을 관리
# 이 객체를 통해 데이터를 저장, 조회, 수정, 삭제하는 등의 Redis 작업을 수행
redis_conn = Redis(host='test_redis', port=6379)
q = Queue('my_queue', connection=redis_conn) # Redis와 연결하여 RQ 큐 생성 

@app.get('/hello')
def hello():
    """Test endpoint"""
    return {'hello': 'world'} # 결과값을 Json타입으로 return

# 1. uuid v4를 key로, 생성 시간을 value로 가지는 객체를 10초동안 랜덤 시간 간격으로 50개 생성해서 redis에 삽입하는 함수    
from uuid import uuid4
from datetime import datetime
import asyncio
import random
from fastapi import BackgroundTasks

async def generate_item():
    for _ in range(50):
        key = str(uuid4())
        value = datetime.utcnow().isoformat()
        redis_conn.set(key, value)  # 비동기로 키-값 쌍 저장
        delay = random.uniform(0, 10)
        # 랜덤 시간 동안 비동기 작업이 블록되지 않고, 다른 작업을 동시에 수행
        await asyncio.sleep(delay)

@app.post("/insert/") # 클라이언트에서 FastAPI 엔드포인트 호출
async def insert_item(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_item) # 비동기 백그라운드 작업으로 generate_item 실행 
    return {"message": "UUIDs insertion scheduled."}

# 2. Redis에 저장된 객체를 0~10개 사이로 랜덤하게 삭제하는 함수 
@app.delete("/delete/") # 클라이언트에서 FastAPI 엔드포인트 호출
async def delete_data():
    delete_number = random.randint(0,10)
    for _ in range(delete_number):
        # random 함수를 통해 임의의 key 획득
        random_key = redis_conn.randomkey()
        # 획득된 key의 item 삭제
        if random_key:
            redis_conn.delete(random_key)
    return {"message": f"{delete_number} items deleted."}

# 3. Redis에 저장된 객체가 몇 개인지 리턴하는 함수
@app.get("/get count/")
async def get_count():
    count = len(redis_conn.keys("*"))
    return {"Number of items": count}


#4. Redis에 저장된 객체를 입력한 값 수 만큼 리턴하는 함수
# Pydantic 모델 정의
from typing import List
class Item(BaseModel):
    key: str
    value: str

@app.get("/get_items/{item_count}", response_model=List[Item])
async def get_items(item_count: int):
    if item_count < 1:
        raise HTTPException(status_code=400, detail="item_count must be at least 1.")
    try:
        keys = redis_conn.keys("*")
        keys = [key.decode("utf-8") for key in keys]  # 바이트 문자열을 일반 문자열로 변환
        valid_keys = [key for key in keys if key not in ('rq:scheduled:my_queue', 'rq:queues')]  # 'rq:scheduled:my_queue'와 'rq:queues'를 제외한 유효한 키만 필터링
        items = []
        for key in valid_keys[:item_count]:
            value = redis_conn.hget(key, "created_at")
            if value:
                items.append(Item(key=key, value=value))  # Pydantic 모델 인스턴스 생성 및 추가
        return items
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))