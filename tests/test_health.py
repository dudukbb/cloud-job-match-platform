"""
Health check and API endpoint tests
"""
import pytest


class TestHealthEndpoints:
    """Health check endpoint tests"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'dependencies' in data
        assert 'database' in data['dependencies']
        assert 'cache' in data['dependencies']
    
    def test_liveness_probe(self, client):
        """Test Kubernetes liveness probe"""
        response = client.get('/health/live')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'alive'
    
    def test_readiness_probe(self, client):
        """Test Kubernetes readiness probe"""
        response = client.get('/health/ready')
        assert response.status_code in [200, 503]
        data = response.get_json()
        assert 'status' in data
    
    def test_startup_probe(self, client):
        """Test Kubernetes startup probe"""
        response = client.get('/health/startup')
        assert response.status_code in [200, 503]
        data = response.get_json()
        assert 'status' in data


class TestAPIEndpoints:
    """API endpoint tests"""
    
    def test_api_status(self, client):
        """Test API status endpoint"""
        response = client.get('/api/v1/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['api'] == 'online'
        assert 'version' in data
    
    def test_api_info(self, client):
        """Test API info endpoint"""
        response = client.get('/api/v1/info')
        assert response.status_code == 200
        data = response.get_json()
        assert 'name' in data
        assert 'version' in data
        assert 'endpoints' in data


class TestAuthenticationEndpoints:
    """Authentication endpoint tests"""
    
    def test_user_registration(self, client):
        """Test user registration"""
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = client.post('/auth/register', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
    
    def test_user_registration_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        payload = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'pass123'
        }
        response = client.post('/auth/register', json=payload)
        assert response.status_code == 409
    
    def test_user_registration_missing_fields(self, client):
        """Test registration with missing fields"""
        payload = {
            'username': 'newuser'
        }
        response = client.post('/auth/register', json=payload)
        assert response.status_code == 400
    
    def test_user_login(self, client, test_user):
        """Test user login"""
        payload = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post('/auth/login', json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
    
    def test_user_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        payload = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = client.post('/auth/login', json=payload)
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user"""
        response = client.get('/auth/me', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'username' in data
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without auth"""
        response = client.get('/auth/me')
        assert response.status_code == 401


class TestJobEndpoints:
    """Job listing API tests"""
    
    def test_get_jobs(self, client, test_job):
        """Test getting jobs list"""
        response = client.get('/api/v1/jobs')
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'pagination' in data
    
    def test_get_job_by_id(self, client, test_job):
        """Test getting specific job"""
        response = client.get(f'/api/v1/jobs/{test_job.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Test Job'
    
    def test_get_nonexistent_job(self, client):
        """Test getting nonexistent job"""
        response = client.get('/api/v1/jobs/00000000-0000-0000-0000-000000000000')
        assert response.status_code == 404
    
    def test_create_job(self, client, auth_headers):
        """Test creating a job listing"""
        payload = {
            'title': 'New Job',
            'description': 'Job description',
            'company': 'Test Company',
            'location': 'Test City',
            'job_type': 'Full-time'
        }
        response = client.post('/api/v1/jobs', json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert 'job' in data
        assert data['job']['title'] == 'New Job'
    
    def test_create_job_no_auth(self, client):
        """Test creating job without auth"""
        payload = {
            'title': 'New Job',
            'description': 'Job description',
            'company': 'Test Company'
        }
        response = client.post('/api/v1/jobs', json=payload)
        assert response.status_code == 401
    
    def test_create_job_missing_fields(self, client, auth_headers):
        """Test creating job with missing fields"""
        payload = {
            'title': 'New Job'
        }
        response = client.post('/api/v1/jobs', json=payload, headers=auth_headers)
        assert response.status_code == 400


class TestErrorHandlers:
    """Error handler tests"""
    
    def test_404_error(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_400_bad_request(self, client):
        """Test 400 error handler"""
        response = client.post('/api/v1/jobs', json={})
        assert response.status_code in [400, 401]  # Depends on auth
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling"""
        response = client.post(
            '/api/v1/jobs',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400
