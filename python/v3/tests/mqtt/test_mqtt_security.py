#!/usr/bin/env python3
"""
Integration Tests for MQTT Security
Tests authentication enforcement, security logging, and unauthorized access prevention

Following TDD - These tests should FAIL until security implementation is complete
Issue #44 - MQTT Authentication Not Always Enforced
"""

import pytest
import logging
import os
import time
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any

# Imports will work once implemented
try:
    from mqtt_handler import MQTTHandler
    from mqtt_authenticator import MQTTAuthenticator
except ImportError:
    # Placeholders for test discovery
    class MQTTHandler:
        pass
    class MQTTAuthenticator:
        pass

from config import SystemConfig


# Test Fixtures
@pytest.fixture
def valid_config():
    """Fixture for valid MQTT configuration"""
    config = Mock(spec=SystemConfig)
    config.mqtt_broker = "192.168.0.110"
    config.mqtt_port = 1883
    config.mqtt_username = "test_user"
    config.mqtt_password = "test_password"
    config.mqtt_client_id = "test_client"
    return config


@pytest.fixture
def invalid_username_config():
    """Fixture for config with invalid username"""
    config = Mock(spec=SystemConfig)
    config.mqtt_broker = "192.168.0.110"
    config.mqtt_port = 1883
    config.mqtt_username = "invalid_user"
    config.mqtt_password = "test_password"
    config.mqtt_client_id = "test_client"
    return config


@pytest.fixture
def invalid_password_config():
    """Fixture for config with invalid password"""
    config = Mock(spec=SystemConfig)
    config.mqtt_broker = "192.168.0.110"
    config.mqtt_port = 1883
    config.mqtt_username = "test_user"
    config.mqtt_password = "wrong_password"
    config.mqtt_client_id = "test_client"
    return config


@pytest.fixture
def missing_credentials_config():
    """Fixture for config with missing credentials"""
    config = Mock(spec=SystemConfig)
    config.mqtt_broker = "192.168.0.110"
    config.mqtt_port = 1883
    config.mqtt_username = None
    config.mqtt_password = None
    config.mqtt_client_id = "test_client"
    return config


# Test Class: Configuration Validation
class TestConfigurationValidation:
    """Test that configuration is properly validated before use"""
    
    def test_config_accepts_valid_credentials(self, valid_config):
        """Should accept valid credentials without error"""
        # Act & Assert - should not raise
        handler = MQTTHandler(valid_config)
        assert handler is not None
    
    def test_config_rejects_missing_username(self):
        """Should raise ValueError for missing username"""
        # Arrange
        config = Mock(spec=SystemConfig)
        config.mqtt_broker = "192.168.0.110"
        config.mqtt_port = 1883
        config.mqtt_username = None
        config.mqtt_password = "password"
        config.mqtt_client_id = "client"
        
        # Act & Assert
        with pytest.raises(ValueError, match="credential"):
            MQTTHandler(config)
    
    def test_config_rejects_missing_password(self):
        """Should raise ValueError for missing password"""
        # Arrange
        config = Mock(spec=SystemConfig)
        config.mqtt_broker = "192.168.0.110"
        config.mqtt_port = 1883
        config.mqtt_username = "username"
        config.mqtt_password = None
        config.mqtt_client_id = "client"
        
        # Act & Assert
        with pytest.raises(ValueError, match="credential"):
            MQTTHandler(config)
    
    def test_config_rejects_empty_username(self):
        """Should raise ValueError for empty username"""
        # Arrange
        config = Mock(spec=SystemConfig)
        config.mqtt_broker = "192.168.0.110"
        config.mqtt_port = 1883
        config.mqtt_username = ""
        config.mqtt_password = "password"
        config.mqtt_client_id = "client"
        
        # Act & Assert
        with pytest.raises(ValueError, match="credential"):
            MQTTHandler(config)
    
    def test_config_rejects_empty_password(self):
        """Should raise ValueError for empty password"""
        # Arrange
        config = Mock(spec=SystemConfig)
        config.mqtt_broker = "192.168.0.110"
        config.mqtt_port = 1883
        config.mqtt_username = "username"
        config.mqtt_password = ""
        config.mqtt_client_id = "client"
        
        # Act & Assert
        with pytest.raises(ValueError, match="credential"):
            MQTTHandler(config)


# Test Class: Authentication Success
class TestSuccessfulAuthentication:
    """Test successful authentication scenarios"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    def test_successful_connection_with_valid_credentials(self, mock_client_class, valid_config):
        """Should connect successfully with valid credentials"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        handler = MQTTHandler(valid_config)
        
        # Act
        result = handler.connect()
        
        # Assert
        assert result is True
        assert handler.connected is True
        mock_client.username_pw_set.assert_called_once_with("test_user", "test_password")
        mock_client.connect.assert_called_once()
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_successful_connection_logs_correctly(self, mock_logger, mock_client_class, valid_config):
        """Should log successful connection with audit info"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Simulate successful connection callback
        handler._on_connect(mock_client, None, None, 0)
        
        # Assert
        logger_instance.info.assert_called()
        log_message = str(logger_instance.info.call_args)
        assert "success" in log_message.lower() or "connected" in log_message.lower()
        assert "test_user" in log_message  # Username for audit trail
        assert "test_password" not in log_message  # Password NOT logged


# Test Class: Authentication Failures
class TestAuthenticationFailures:
    """Test authentication failure scenarios"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_connection_fails_with_bad_username_or_password(self, mock_logger, mock_client_class, invalid_username_config):
        """Should fail connection with RC=4 for bad credentials"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(invalid_username_config)
        handler.logger = logger_instance
        
        # Act - Simulate connection callback with RC=4 (bad auth)
        handler._on_connect(mock_client, None, None, 4)
        
        # Assert
        assert handler.connected is False
        logger_instance.error.assert_called()
        error_message = str(logger_instance.error.call_args)
        assert "4" in error_message
        assert "auth" in error_message.lower() or "password" in error_message.lower() or "username" in error_message.lower()
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_connection_fails_with_not_authorized(self, mock_logger, mock_client_class, valid_config):
        """Should fail connection with RC=5 for not authorized"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Act - Simulate connection callback with RC=5 (not authorized)
        handler._on_connect(mock_client, None, None, 5)
        
        # Assert
        assert handler.connected is False
        logger_instance.error.assert_called()
        error_message = str(logger_instance.error.call_args)
        assert "5" in error_message
        assert "author" in error_message.lower()
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_auth_failure_does_not_expose_password(self, mock_logger, mock_client_class, invalid_password_config):
        """Should NEVER log password even in error messages"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(invalid_password_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 4)
        
        # Assert - password should NEVER appear in any log
        all_log_calls = str(logger_instance.mock_calls)
        assert "wrong_password" not in all_log_calls
        assert "test_password" not in all_log_calls


# Test Class: Connection Logging
class TestConnectionLogging:
    """Test comprehensive connection logging"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_logs_include_timestamp(self, mock_logger, mock_client_class, valid_config):
        """Should include timestamp in logs (implicit via logging framework)"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 0)
        
        # Assert - logger.info was called (timestamp added by logging framework)
        logger_instance.info.assert_called()
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_logs_include_client_id(self, mock_logger, mock_client_class, valid_config):
        """Should include client ID in connection logs"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 0)
        
        # Assert
        all_log_calls = str(logger_instance.mock_calls)
        assert "test_client" in all_log_calls or handler.client_id in all_log_calls
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_logs_include_return_code(self, mock_logger, mock_client_class, valid_config):
        """Should include return code in logs"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 4)
        
        # Assert
        all_log_calls = str(logger_instance.mock_calls)
        assert "4" in all_log_calls  # RC should be in logs
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_logs_include_username_for_audit(self, mock_logger, mock_client_class, valid_config):
        """Should include username in logs for audit trail"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 0)
        
        # Assert
        all_log_calls = str(logger_instance.mock_calls)
        assert "test_user" in all_log_calls


# Test Class: Anonymous Connection Prevention
class TestAnonymousConnectionPrevention:
    """Test that anonymous connections are prevented"""
    
    def test_handler_requires_credentials(self, missing_credentials_config):
        """Should not allow initialization without credentials"""
        # Act & Assert
        with pytest.raises(ValueError, match="credential"):
            MQTTHandler(missing_credentials_config)
    
    @patch('mqtt_handler.mqtt_client.Client')
    def test_handler_always_sets_credentials(self, mock_client_class, valid_config):
        """Should always call username_pw_set before connecting"""
        # Arrange
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        handler = MQTTHandler(valid_config)
        
        # Act
        handler.connect()
        
        # Assert
        mock_client.username_pw_set.assert_called_once()
        # Verify it's called BEFORE connect
        calls = [call[0] for call in mock_client.method_calls]
        username_pw_index = calls.index('username_pw_set')
        connect_index = calls.index('connect')
        assert username_pw_index < connect_index


# Test Class: Reconnection Security
class TestReconnectionSecurity:
    """Test security during reconnection scenarios"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    def test_reconnection_validates_credentials(self, mock_client_class, valid_config):
        """Should re-validate credentials before each reconnection attempt"""
        # Arrange
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        handler = MQTTHandler(valid_config)
        
        # Act
        handler._reconnect()
        
        # Assert - should validate credentials (implementation detail)
        # This tests that reconnection doesn't bypass security
        assert mock_client.username_pw_set.called
    
    @patch('mqtt_handler.mqtt_client.Client')
    def test_reconnection_uses_same_credentials(self, mock_client_class, valid_config):
        """Should use same validated credentials on reconnection"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        handler = MQTTHandler(valid_config)
        original_username = handler.username
        original_password = handler.password
        
        # Act
        handler._reconnect()
        
        # Assert - credentials should not change
        assert handler.username == original_username
        assert handler.password == original_password


# Test Class: Error Message Security
class TestErrorMessageSecurity:
    """Test that error messages don't leak sensitive information"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_error_messages_dont_reveal_password(self, mock_logger, mock_client_class, invalid_password_config):
        """Should use generic error messages that don't reveal password"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(invalid_password_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 4)
        
        # Assert
        all_logs = str(logger_instance.mock_calls)
        # Password should NEVER appear
        assert "wrong_password" not in all_logs
        # Should have generic error
        assert "auth" in all_logs.lower() or "failed" in all_logs.lower()
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_error_messages_dont_distinguish_username_vs_password(self, mock_logger, mock_client_class, invalid_username_config):
        """Should not reveal whether username or password was wrong"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = False
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(invalid_username_config)
        handler.logger = logger_instance
        
        # Act
        handler._on_connect(mock_client, None, None, 4)
        
        # Assert
        error_message = str(logger_instance.error.call_args)
        # Should not specifically say "invalid username" or "invalid password"
        # Should use generic "authentication failed" or "bad username or password"
        assert not ("invalid username" in error_message.lower() and "invalid password" not in error_message.lower())


# Test Class: Broker Security Verification (Optional Feature)
class TestBrokerSecurityVerification:
    """Test optional broker security verification feature"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    @patch('mqtt_handler.logging.getLogger')
    def test_warns_if_broker_allows_anonymous(self, mock_logger, mock_client_class, valid_config):
        """Should warn if broker is detected to allow anonymous connections"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        logger_instance = Mock()
        mock_logger.return_value = logger_instance
        
        handler = MQTTHandler(valid_config)
        handler.logger = logger_instance
        
        # Mock authenticator to return False (insecure broker)
        handler.authenticator = Mock()
        handler.authenticator.verify_broker_security.return_value = False
        
        # Act
        handler._on_connect(mock_client, None, None, 0)
        
        # Assert
        logger_instance.warning.assert_called()
        warning_message = str(logger_instance.warning.call_args)
        assert "anonymous" in warning_message.lower() or "security" in warning_message.lower()


# Test Class: Integration with Existing System
class TestIntegrationWithExistingSystem:
    """Test that authentication doesn't break existing functionality"""
    
    @patch('mqtt_handler.mqtt_client.Client')
    def test_handler_still_supports_topic_subscription(self, mock_client_class, valid_config):
        """Should still subscribe to topics after auth success"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        handler = MQTTHandler(valid_config)
        
        # Act
        handler._on_connect(mock_client, None, None, 0)
        
        # Assert - should call subscribe method (implementation detail)
        assert handler.connected is True
    
    @patch('mqtt_handler.mqtt_client.Client')
    def test_handler_still_supports_message_handling(self, mock_client_class, valid_config):
        """Should still handle messages after authentication"""
        # Arrange
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client_class.return_value = mock_client
        
        handler = MQTTHandler(valid_config)
        handler._on_connect(mock_client, None, None, 0)
        
        # Act - simulate message received
        test_message = Mock()
        test_message.topic = "test/topic"
        test_message.payload = b"test_payload"
        
        # Should not raise exception
        try:
            handler._on_message(mock_client, None, test_message)
        except Exception as e:
            pytest.fail(f"Message handling failed after authentication: {e}")


# Test Class: Credential Rotation
class TestCredentialRotation:
    """Test support for credential rotation"""
    
    def test_handler_uses_config_credentials(self, valid_config):
        """Should use credentials from config (allowing rotation via config)"""
        # Arrange & Act
        handler = MQTTHandler(valid_config)
        
        # Assert
        assert handler.username == valid_config.mqtt_username
        assert handler.password == valid_config.mqtt_password
    
    def test_new_handler_uses_updated_credentials(self):
        """Should use new credentials if config is updated (requires restart)"""
        # Arrange
        config1 = Mock(spec=SystemConfig)
        config1.mqtt_broker = "192.168.0.110"
        config1.mqtt_port = 1883
        config1.mqtt_username = "old_user"
        config1.mqtt_password = "old_password"
        config1.mqtt_client_id = "client"
        
        config2 = Mock(spec=SystemConfig)
        config2.mqtt_broker = "192.168.0.110"
        config2.mqtt_port = 1883
        config2.mqtt_username = "new_user"
        config2.mqtt_password = "new_password"
        config2.mqtt_client_id = "client"
        
        # Act
        handler1 = MQTTHandler(config1)
        handler2 = MQTTHandler(config2)
        
        # Assert
        assert handler1.username == "old_user"
        assert handler1.password == "old_password"
        assert handler2.username == "new_user"
        assert handler2.password == "new_password"


# Hardware Test Markers (to be run on Raspberry Pi)
@pytest.mark.hardware
@pytest.mark.skipif(os.environ.get('CI') == 'true', reason="Requires actual MQTT broker")
class TestHardwareIntegration:
    """Hardware tests to be run on Raspberry Pi with actual MQTT broker"""
    
    def test_real_broker_requires_authentication(self):
        """Should fail to connect to real broker without credentials"""
        # This test requires actual MQTT broker
        pytest.skip("Run manually on Raspberry Pi with actual broker")
    
    def test_real_broker_accepts_valid_credentials(self):
        """Should connect to real broker with valid credentials"""
        # This test requires actual MQTT broker
        pytest.skip("Run manually on Raspberry Pi with actual broker")
    
    def test_home_assistant_integration_still_works(self):
        """Should maintain Home Assistant integration after auth changes"""
        # This test requires actual Home Assistant setup
        pytest.skip("Run manually on Raspberry Pi with actual Home Assistant")


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

