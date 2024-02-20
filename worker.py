# worker.py: RQ(Redis Queue)의 작업을 처리하기 위한 워커를 실행하는 스크립트
from rq import Worker, Queue, Connection
from redis import Redis

# Redis 연결 설정. Redis 서버의 주소와 포트를 명시.
def runTask():
    redis_conn = Redis(host='localhost', port=6379)
    with Connection(connection=redis_conn):
        worker = Worker(Queue('default'), connection=redis_conn)
        worker.work()

if __name__ == "__main__":
    runTask()
