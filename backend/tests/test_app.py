import pytest
from unittest.mock import patch, MagicMock
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the health check endpoint returns 200 OK."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok', 'service': 'backend'}

@patch('backend.app.get_db')
@patch('backend.app.get_redis')
def test_get_tasks_mocked(mock_redis, mock_db, client):
    """Test getting tasks with mocked DB and Redis."""
    # Mock Redis (cache miss)
    mock_redis.return_value.get.return_value = None
    
    # Mock Database
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        {'id': 1, 'title': 'Test Task', 'description': 'desc', 'done': False, 'created_at': '2024-01-01'}
    ]
    
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert 'tasks' in data
    assert data['tasks'][0]['title'] == 'Test Task'

def test_create_task_invalid_data(client):
    """Test that creating a task without a title returns a 400 error."""
    response = client.post('/api/tasks', json={'description': 'No title'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

@patch('backend.app.get_db')
def test_stats_mocked(mock_db, client):
    """Test stats endpoint with mocked DB."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    # First call to COUNT(*)
    # Second call to COUNT(*) WHERE done = TRUE
    mock_cur.fetchone.side_effect = [(10,), (4,)]
    
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_tasks'] == 10
    assert data['done_tasks'] == 4
    assert data['pending_tasks'] == 6
