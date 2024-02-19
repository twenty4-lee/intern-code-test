from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
# FastAPI 애플리케이션과 Redis 초기화
app = FastAPI()
# redis_conn = Redis 인스턴스에 연결하기 위한 객체, Python 애플리케이션과 Redis 서버 사이의 연결을 관리
# 이 객체를 통해 데이터를 저장, 조회, 수정, 삭제하는 등의 Redis 작업을 수행
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
    for _ in range(50):
        delay = random.uniform(0, 10)
        # RQ를 사용하여 runTask 작업을 랜덤 딜레이 후에 실행하도록 스케줄링
        # RQ worker 프로세스에 의해 비동기적으로 처리
        q.enqueue_in(timedelta(seconds=delay), runTask)
    return {"message": "UUIDs insertion scheduled."}

# 2. Redis에 저장된 객체를 0~10개 사이로 랜덤하게 삭제하는 함수 
@app.delete("/delete/") # 클라이언트에서 FastAPI 엔드포인트 호출
async def delete_data():
    delete_number = random.randint(0,10)
    for _ in range(delete_number):
        # random 함수를 통해 임의의 key 획득
        random_key = redis_conn.randomkey()
        # 획득된 key의 item 삭제
        redis_conn.delete(random_key)
    return {"message": f"{delete_number} items deleted."}

# 3. Redis에 저장된 객체가 몇 개인지 리턴하는 함수
@app.get("/get count/")
async def get_count():
    count = len(redis_conn.keys("*"))
    return {"Number of items": count}

#4. Redis에 저장된 객체를 입력한 값 수 만큼 리턴하는 함수
from typing import List, Dict
@app.get("/get items/{item_count}", response_model=List[Dict[str, str]])
async def get_items(item_count: int):
    if item_count < 1:
        raise HTTPException(status_code=400, detail="item_count must be at least 1.")
    try:
        # Redis에서 모든 키를 조회
        keys = redis_conn.keys("*")
        if item_count > len(keys):
            raise HTTPException(status_code=400, detail=f"Requested item_count ({item_count}) exceeds the number of stored items ({len(keys)}).")
        else:
            items = []
            for i in range(item_count):
                # 각 키에 대한 값을 조회하여 items 리스트에 추가
                value = redis_conn.hget(keys[i], "created_at") # 'created_at' 필드의 값을 조회
                if value:
                    items.append({"key": keys[i], "value": value})
            return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

