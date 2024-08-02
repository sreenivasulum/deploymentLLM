from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import time
import os
import app1

app = Flask(__name__)

# Connect to Redis
redis_conn = Redis.from_url(os.getenv('REDIS_URL'))
q = Queue(connection=redis_conn)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World'

@app.route('/start-task', methods=['POST'])
def start_task():
    data = request.get_json()
    job = q.enqueue(app1.background_task, data['n'])
    return jsonify({'job_id': job.get_id()})

@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = q.fetch_job(job_id)
    if job.is_finished:
        return jsonify({'status': 'finished', 'result': job.result})
    elif job.is_failed:
        return jsonify({'status': 'failed'})
    else:
        return jsonify({'status': 'in progress'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
