import pytest
import sys
import os
from unittest.mock import Mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_airtable_client():
    """Mock Airtable client for testing."""
    mock_client = Mock()
    
    # Default mock responses
    mock_client.create_record.return_value = {"id": "test_record_123"}
    mock_client.get_record.return_value = {
        "id": "test_record_123",
        "fields": {
            "Status": "Pending",
            "Last Hash": "",
            "Compressed JSON": ""
        }
    }
    mock_client.update_record.return_value = {"id": "test_record_123"}
    mock_client.list_records.return_value = []
    
    return mock_client

@pytest.fixture
def sample_form_data():
    """Sample form submission data for testing."""
    return {
        "full_name": "John Doe",
        "email": "john@example.com",
        "location": "San Francisco, CA",
        "linkedin": "https://linkedin.com/in/johndoe",
        "preferred_rate": 95,
        "min_rate": 80,
        "currency": "USD",
        "availability": 40,
        "work_experience": [
            {
                "company": "Tech Corp",
                "title": "Software Engineer",
                "start": "2020-01",
                "end": "2023-12",
                "technologies": ["Python", "JavaScript", "React"]
            }
        ]
    }

@pytest.fixture
def sample_applicant_data():
    """Sample applicant data structure from Airtable."""
    return {
        "applicant": {
            "id": "app123",
            "fields": {
                "Status": "Pending",
                "Last Hash": "",
                "Compressed JSON": ""
            }
        },
        "personal_details": {
            "id": "personal123",
            "fields": {
                "Full Name": "John Doe",
                "Email": "john@example.com",
                "Location": "San Francisco, CA",
                "LinkedIn": "https://linkedin.com/in/johndoe"
            }
        },
        "work_experience": [
            {
                "id": "work123",
                "fields": {
                    "Company": "Tech Corp",
                    "Title": "Software Engineer",
                    "Start": "2020-01",
                    "End": "2023-12",
                    "Technologies": ["Python", "JavaScript", "React"]
                }
            }
        ],
        "salary_preferences": {
            "id": "salary123",
            "fields": {
                "Preferred Rate": 95,
                "Min Rate": 80,
                "Currency": "USD",
                "Availability": 40
            }
        }
    }