from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import redis
import json
import os
import time

app = Flask(__name__)
CORS(app)

# ── helpers ──────────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres'),
        database=os.environ.get('DB_NAME', 'taskdb'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'secret')
    )

def get_redis():
    return redis.Redis(
        host=os.environ.get('REDIS_HOST', 'redis'),
        port=6379,
        decode_responses=True
    )

def init_db():
    for attempt in range(10):
        try:
            conn = get_db()
            cur = conn.cursor()
            with open('init.sql', 'r') as f:
                cur.execute(f.read())
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully.")
            return
        except Exception as e:
            print(f"DB not ready (attempt {attempt + 1}/10): {e}")
            time.sleep(3)
    print("Could not connect to database after 10 attempts.")

# ── routes ───────────────────────────────────────────────────────────────────

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'backend'})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    r = get_redis()
    cached = r.get('all_tasks')
    if cached:
        print("Serving tasks from Redis cache")
        return jsonify({'tasks': json.loads(cached), 'source': 'cache'})

    print("Serving tasks from PostgreSQL")
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()

    for task in tasks:
        if task.get('created_at'):
            task['created_at'] = str(task['created_at'])

    r.setex('all_tasks', 30, json.dumps(tasks))
    return jsonify({'tasks': tasks, 'source': 'database'})

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        'INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING *',
        (title, description)
    )
    task = dict(cur.fetchone())
    task['created_at'] = str(task['created_at'])
    conn.commit()
    cur.close()
    conn.close()

    get_redis().delete('all_tasks')
    return jsonify({'task': task}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def toggle_task(task_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        'UPDATE tasks SET done = NOT done WHERE id = %s RETURNING *',
        (task_id,)
    )
    task = cur.fetchone()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    task = dict(task)
    task['created_at'] = str(task['created_at'])
    conn.commit()
    cur.close()
    conn.close()

    get_redis().delete('all_tasks')
    return jsonify({'task': task})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s RETURNING id', (task_id,))
    deleted = cur.fetchone()
    if not deleted:
        return jsonify({'error': 'Task not found'}), 404
    conn.commit()
    cur.close()
    conn.close()

    get_redis().delete('all_tasks')
    return jsonify({'message': f'Task {task_id} deleted'})

@app.route('/api/stats')
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM tasks')
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM tasks WHERE done = TRUE')
    done = cur.fetchone()[0]
    cur.close()
    conn.close()

    r = get_redis()
    cache_info = r.info('stats')

    return jsonify({
        'total_tasks': total,
        'done_tasks': done,
        'pending_tasks': total - done,
        'redis_hits': cache_info.get('keyspace_hits', 0),
        'redis_misses': cache_info.get('keyspace_misses', 0)
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
