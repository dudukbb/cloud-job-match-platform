"""
Authentication tests
"""
import pytest
from app.auth import TokenManager, PasswordManager


class TestPasswordManager:
    """Password hashing and verification tests"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = 'mypassword123'
        hashed = PasswordManager.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = 'mypassword123'
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(password, hashed)
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = 'mypassword123'
        wrong_password = 'wrongpassword123'
        hashed = PasswordManager.hash_password(password)
        
        assert not PasswordManager.verify_password(wrong_password, hashed)


class TestTokenManager:
    """JWT token management tests"""
    
    def test_generate_access_token(self, app):
        """Test access token generation"""
        with app.app_context():
            user_id = '550e8400-e29b-41d4-a716-446655440000'
            token = TokenManager.generate_access_token(user_id)
            
            assert token is not None
            assert isinstance(token, str)
    
    def test_verify_valid_access_token(self, app):
        """Test verification of valid access token"""
        with app.app_context():
            user_id = '550e8400-e29b-41d4-a716-446655440000'
            token = TokenManager.generate_access_token(user_id)
            
            payload = TokenManager.verify_token(token, token_type='access')
            
            assert payload is not None
            assert payload['user_id'] == user_id
            assert payload['type'] == 'access'
    
    def test_verify_invalid_token(self, app):
        """Test verification of invalid token"""
        with app.app_context():
            invalid_token = 'invalid.token.string'
            payload = TokenManager.verify_token(invalid_token)
            
            assert payload is None
    
    def test_generate_refresh_token(self, app):
        """Test refresh token generation"""
        with app.app_context():
            user_id = '550e8400-e29b-41d4-a716-446655440000'
            token = TokenManager.generate_refresh_token(user_id)
            
            assert token is not None
            assert isinstance(token, str)
    
    def test_verify_refresh_token(self, app):
        """Test verification of refresh token"""
        with app.app_context():
            user_id = '550e8400-e29b-41d4-a716-446655440000'
            token = TokenManager.generate_refresh_token(user_id)
            
            payload = TokenManager.verify_token(token, token_type='refresh')
            
            assert payload is not None
            assert payload['user_id'] == user_id
            assert payload['type'] == 'refresh'
    
    def test_token_wrong_type(self, app):
        """Test token verification with wrong type"""
        with app.app_context():
            user_id = '550e8400-e29b-41d4-a716-446655440000'
            access_token = TokenManager.generate_access_token(user_id)
            
            # Try to verify as refresh token
            payload = TokenManager.verify_token(access_token, token_type='refresh')
            
            assert payload is None
