# worker.py: RQ(Redis Queue)의, 큐에 대기 중인 작업을 처리하기 위한 워커를 실행하는 스크립트
# API 서버와 분리되어 실행되며, 별도의 프로세스로 실행

# 현재 api.py에서는 RQ 큐에 추가한 작업이 없음. 
# background_tasks.add_task(q.enqueue, generate_item)으로 변경한다면 generate_item 함수를 RQ 큐에 추가할 수 있음.
# 이렇게 변경함으로써 generate_item 함수가 RQ 큐에 추가되고, worker.py 파일에서 실행되는 워커가 해당 작업을 처리할 수 있음.

from rq import Worker, Queue, Connection
from redis import Redis

# Redis 연결 설정. Redis 서버의 주소와 포트를 명시.
def runTask():
    redis_conn = Redis(host='test_redis', port=6379)
    with Connection(connection=redis_conn):
        worker = Worker(Queue('default'), connection=redis_conn)
        # RQ 워커를 실행
        worker.work()

if __name__ == "__main__":
    # 함수를 호출하여 워커를 실행
    runTask()
