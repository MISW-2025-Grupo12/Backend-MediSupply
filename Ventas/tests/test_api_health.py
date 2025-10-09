import pytest
import sys
import os
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app


class TestAPIHealth:
    
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        response = self.client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'up'
        assert data['mode'] == 'simplified'
        assert 'endpoints' in data
        assert len(data['endpoints']) > 0
