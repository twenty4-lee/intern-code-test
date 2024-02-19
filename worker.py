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
