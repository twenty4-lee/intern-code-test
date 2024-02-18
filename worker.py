from redis import Redis
from uuid import uuid4
from datetime import datetime

# Redis 연결 설정. Redis 서버의 주소와 포트를 명시.
redis_conn = Redis(host='localhost', port=6379, decode_responses=True)

def runTask():
    key = str(uuid4())
    value = datetime.utcnow().isoformat()
    redis_conn.set(key, value)