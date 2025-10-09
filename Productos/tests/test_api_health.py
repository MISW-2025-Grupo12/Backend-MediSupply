import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app


class TestAPIHealth:
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """Test endpoint de health check"""
        # Act
        response = self.client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'up'
        assert 'endpoints' in data
