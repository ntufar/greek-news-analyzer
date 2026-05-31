import pytest
import os
from unittest.mock import patch, MagicMock
from app import app, analyze_greek_news, extract_text_from_url

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route returns the main page."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'ΕΠΑΠ' in response.data.decode('utf-8')

def test_analyze_route_no_data(client):
    """Test analyze route with no data."""
    response = client.post('/analyze', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_analyze_route_empty_text_and_url(client):
    """Test analyze route with empty text and URL."""
    response = client.post('/analyze', json={'text': '', 'url': ''})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_analyze_route_short_text(client):
    """Test analyze route with text that's too short."""
    response = client.post('/analyze', json={'text': 'Short text'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_analyze_route_invalid_url(client):
    """Test analyze route with invalid URL."""
    response = client.post('/analyze', json={'url': 'not-a-url'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

@patch('app.mistral_client.chat.complete')
def test_analyze_greek_news_success(mock_complete):
    """Test successful Greek news analysis."""
    mock_message = MagicMock()
    mock_message.content = "Test analysis result"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_complete.return_value = mock_response
    
    result = analyze_greek_news("Test Greek text for analysis", "Test Source")
    assert result == "Test analysis result"
    mock_complete.assert_called_once()

@patch('app.mistral_client.chat.complete')
def test_analyze_greek_news_error(mock_complete):
    """Test Greek news analysis with error."""
    mock_complete.side_effect = Exception("API Error")
    
    result = analyze_greek_news("Test text", "Test Source")
    assert "Σφάλμα στην ανάλυση" in result

@patch('app.requests.get')
def test_extract_text_from_url_success(mock_get):
    """Test successful text extraction from URL."""
    mock_response = MagicMock()
    mock_response.content = b'<html><body><main><p>' + b'Long article content. ' * 20 + b'</p></main></body></html>'
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = extract_text_from_url("https://example.com/article")
    assert "Long article content" in result

@patch('app.requests.get')
def test_extract_text_from_url_error(mock_get):
    """Test text extraction from URL with error."""
    mock_get.side_effect = Exception("Network Error")
    
    result = extract_text_from_url("https://example.com/article")
    assert "Error extracting text" in result

def test_analyze_route_success(client):
    """Test successful analysis via API."""
    with patch('app.mistral_client.chat.complete') as mock_complete:
        mock_message = MagicMock()
        mock_message.content = "Test analysis result"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_complete.return_value = mock_response
        
        response = client.post('/analyze', json={
            'text': 'This is a longer Greek text that should be sufficient for analysis purposes and testing.',
            'source': 'Test Source'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'analysis' in data
        assert 'text_length' in data
        assert 'source' in data
        assert data['success'] is True

if __name__ == '__main__':
    pytest.main([__file__])
