import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.shortlist_engine import ShortlistEngine

class TestShortlistEngine:
    def setup_method(self):
        # Mock Airtable client
        self.mock_airtable = Mock()
        self.engine = ShortlistEngine(self.mock_airtable)
        
        # Sample applicant data
        self.sample_applicant_data = {
            "personal_details": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "location": "San Francisco, CA",
                "linkedin": "https://linkedin.com/in/johndoe"
            },
            "work_experience": [
                {
                    "company": "Tech Corp",
                    "title": "Senior Software Engineer",
                    "start": "2020-01",
                    "end": "2023-12",
                    "technologies": ["Python", "JavaScript", "React", "AWS"]
                },
                {
                    "company": "Startup Inc",
                    "title": "Full Stack Developer",
                    "start": "2018-06",
                    "end": "2019-12",
                    "technologies": ["Node.js", "MongoDB", "Vue.js"]
                }
            ],
            "salary_preferences": {
                "preferred_rate": 95,
                "min_rate": 80,
                "currency": "USD",
                "availability": 40
            }
        }
        
        # Sample shortlisting rules
        self.sample_rules = [
            {
                "id": "rule1",
                "criterion": "experience",
                "rule": ">=3 years",
                "points": 1,
                "description": "At least 3 years of experience"
            },
            {
                "id": "rule2", 
                "criterion": "compensation",
                "rule": "<=$100/hr",
                "points": 1,
                "description": "Rate under $100/hour"
            },
            {
                "id": "rule3",
                "criterion": "location",
                "rule": "US",
                "points": 1,
                "description": "Located in US"
            }
        ]
    
    def test_evaluate_applicant_shortlisted(self):
        # Mock active rules
        self.mock_airtable.list_records.return_value = [
            {"id": rule["id"], "fields": rule} for rule in self.sample_rules
        ]
        
        # Mock shortlisted lead creation
        self.mock_airtable.create_record.return_value = {"id": "lead123"}
        
        result = self.engine.evaluate_applicant("app123", self.sample_applicant_data)
        
        assert result["success"] is True
        assert result["shortlisted"] is True
        assert result["score"] >= self.engine.min_score
        assert "score_reason" in result
        assert result["shortlist_id"] == "lead123"
    
    def test_evaluate_applicant_not_shortlisted(self):
        # Create rules that won't match
        failing_rules = [
            {
                "id": "rule1",
                "criterion": "experience", 
                "rule": ">=10 years",  # Too high
                "points": 2,
                "description": "At least 10 years experience"
            }
        ]
        
        self.mock_airtable.list_records.return_value = [
            {"id": rule["id"], "fields": rule} for rule in failing_rules
        ]
        
        result = self.engine.evaluate_applicant("app123", self.sample_applicant_data)
        
        assert result["success"] is True
        assert result["shortlisted"] is False
        assert result["score"] < self.engine.min_score
    
    def test_evaluate_experience_rule(self):
        # Test experience rule evaluation
        assert self.engine._evaluate_rule(self.sample_applicant_data, "experience", ">=3 years") is True
        assert self.engine._evaluate_rule(self.sample_applicant_data, "experience", ">=6 years") is False
        assert self.engine._evaluate_rule(self.sample_applicant_data, "experience", ">=2 years in Python") is True
    
    def test_evaluate_compensation_rule(self):
        # Test compensation rule evaluation
        assert self.engine._evaluate_rule(self.sample_applicant_data, "compensation", "<=$100/hr") is True
        assert self.engine._evaluate_rule(self.sample_applicant_data, "compensation", "<=$80/hr") is False
        assert self.engine._evaluate_rule(self.sample_applicant_data, "compensation", ">=90/hr") is True
    
    def test_evaluate_location_rule(self):
        # Test location rule evaluation  
        assert self.engine._evaluate_rule(self.sample_applicant_data, "location", "US only") is True
        assert self.engine._evaluate_rule(self.sample_applicant_data, "location", "Europe") is False
    
    def test_evaluate_technology_rule(self):
        # Test technology rule evaluation
        assert self.engine._evaluate_rule(self.sample_applicant_data, "technology", "has Python") is True
        assert self.engine._evaluate_rule(self.sample_applicant_data, "technology", "React experience") is True
        assert self.engine._evaluate_rule(self.sample_applicant_data, "technology", "has Go") is False
    
    def test_evaluate_availability_rule(self):
        # Test availability rule evaluation
        assert self.engine._evaluate_rule(self.sample_applicant_data, "availability", ">=40 hours") is True
        assert self.engine._evaluate_rule(self.sample_applicant_data, "availability", ">=50 hours") is False
        assert self.engine._evaluate_rule(self.sample_applicant_data, "availability", "full-time") is True
    
    def test_calculate_total_experience_years(self):
        work_exp = self.sample_applicant_data["work_experience"]
        total_years = self.engine._calculate_total_experience_years(work_exp)
        
        # Should calculate approximately 5.5 years total
        assert total_years > 4.0
        assert total_years < 7.0
    
    def test_calculate_tech_experience_years(self):
        work_exp = self.sample_applicant_data["work_experience"] 
        python_years = self.engine._calculate_tech_experience_years(work_exp, "python")
        
        # Python only in first job (4 years)
        assert python_years > 3.0
        assert python_years < 5.0
    
    def test_no_active_rules(self):
        # Mock no active rules
        self.mock_airtable.list_records.return_value = []
        
        result = self.engine.evaluate_applicant("app123", self.sample_applicant_data)
        
        assert result["success"] is False
        assert "No active shortlisting rules" in result["error"]
        assert result["shortlisted"] is False
    
    def test_airtable_error_handling(self):
        # Mock Airtable error
        self.mock_airtable.list_records.side_effect = Exception("Airtable connection failed")
        
        result = self.engine.evaluate_applicant("app123", self.sample_applicant_data)
        
        assert result["success"] is False
        assert "evaluation failed" in result["error"]
        assert result["shortlisted"] is False