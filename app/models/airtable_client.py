import requests
import hashlib
import json
from typing import Dict, List, Optional, Any
from config.settings import Config

class AirtableClient:
    def __init__(self):
        self.api_key = Config.AIRTABLE_API_KEY
        self.base_id = Config.AIRTABLE_BASE_ID
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def create_record(self, table_name: str, fields: Dict[str, Any]) -> Dict:
        data = {"fields": fields}
        return self._make_request("POST", table_name, data)
    
    def get_record(self, table_name: str, record_id: str) -> Dict:
        return self._make_request("GET", f"{table_name}/{record_id}")
    
    def update_record(self, table_name: str, record_id: str, fields: Dict[str, Any]) -> Dict:
        data = {"fields": fields}
        return self._make_request("PATCH", f"{table_name}/{record_id}", data)
    
    def list_records(self, table_name: str, formula: Optional[str] = None, 
                     max_records: Optional[int] = None) -> List[Dict]:
        params = {}
        if formula:
            params["filterByFormula"] = formula
        if max_records:
            params["maxRecords"] = max_records
        
        endpoint = table_name
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{table_name}?{param_str}"
        
        response = self._make_request("GET", endpoint)
        return response.get("records", [])
    
    def delete_record(self, table_name: str, record_id: str) -> Dict:
        return self._make_request("DELETE", f"{table_name}/{record_id}")
    
    def batch_create(self, table_name: str, records: List[Dict[str, Any]]) -> List[Dict]:
        data = {"records": [{"fields": record} for record in records]}
        response = self._make_request("POST", table_name, data)
        return response.get("records", [])
    
    def batch_update(self, table_name: str, updates: List[Dict]) -> List[Dict]:
        data = {"records": updates}
        response = self._make_request("PATCH", table_name, data)
        return response.get("records", [])
    
    # Specific methods for the applicant tracking system
    
    def create_applicant(self, form_data: Dict[str, Any]) -> str:
        # Create main applicant record
        applicant_fields = {
            "Name": form_data.get("full_name", ""),  # Using Name field as primary
            "Status": "Pending",
            "Last Hash": ""
        }
        applicant = self.create_record("Applicants", applicant_fields)
        applicant_id = applicant["id"]
        
        # Create linked records
        self._create_personal_details(applicant_id, form_data)
        # Note: Work Experience and Salary Preferences tables don't exist in current base
        # self._create_work_experience(applicant_id, form_data)
        # self._create_salary_preferences(applicant_id, form_data)
        
        return applicant_id
    
    def _create_personal_details(self, applicant_id: str, form_data: Dict[str, Any]):
        fields = {
            "Applicant Record": [applicant_id],  # Updated field name to match schema
            "Full Name": form_data.get("full_name", ""),
            "Email Address": form_data.get("email", ""),  # Updated field name
            "City Location": form_data.get("location", ""),  # Updated field name
            "LinkedIn Profile": form_data.get("linkedin", "")  # Updated field name
        }
        self.create_record("Personal Details", fields)
    
    def _create_work_experience(self, applicant_id: str, form_data: Dict[str, Any]):
        experiences = form_data.get("work_experience", [])
        for exp in experiences:
            fields = {
                "Applicant ID": [applicant_id],
                "Company": exp.get("company", ""),
                "Title": exp.get("title", ""),
                "Start": exp.get("start", ""),
                "End": exp.get("end", ""),
                "Technologies": exp.get("technologies", [])
            }
            self.create_record("Work Experience", fields)
    
    def _create_salary_preferences(self, applicant_id: str, form_data: Dict[str, Any]):
        fields = {
            "Applicant ID": [applicant_id],
            "Preferred Rate": form_data.get("preferred_rate", 0),
            "Min Rate": form_data.get("min_rate", 0),
            "Currency": form_data.get("currency", "USD"),
            "Availability": form_data.get("availability", 40)
        }
        self.create_record("Salary Preferences", fields)
    
    def get_applicant_data(self, applicant_id: str) -> Dict[str, Any]:
        # Get all related data for an applicant
        applicant = self.get_record("Applicants", applicant_id)
        
        # Get linked records using correct field name
        personal_details = self.list_records("Personal Details", 
                                            f"{{Applicant Record}} = '{applicant_id}'")
        # Note: These tables don't exist in current base
        # work_experience = self.list_records("Work Experience", 
        #                                   f"{{Applicant ID}} = '{applicant_id}'")
        # salary_preferences = self.list_records("Salary Preferences", 
        #                                      f"{{Applicant ID}} = '{applicant_id}'")
        
        return {
            "applicant": applicant,
            "personal_details": personal_details[0] if personal_details else {},
            "work_experience": [],  # Empty for now since table doesn't exist
            "salary_preferences": {}  # Empty for now since table doesn't exist
        }
    
    def get_shortlist_rules(self) -> List[Dict]:
        # Return empty list since Shortlist Rules table doesn't exist
        return []
        # return self.list_records("Shortlist Rules", formula="{Active} = TRUE()")
    
    def create_shortlisted_lead(self, applicant_id: str, compressed_json: str, 
                               score: int, score_reason: str) -> Dict:
        # Shortlisted Leads table doesn't exist, return placeholder
        return {"id": "placeholder", "message": "Shortlisted Leads table not implemented"}
        # fields = {
        #     "Applicant": [applicant_id],
        #     "Compressed JSON": compressed_json,
        #     "Score": score,
        #     "Score Reason": score_reason,
        #     "Created At": self._current_timestamp()
        # }
        # return self.create_record("Shortlisted Leads", fields)
    
    def _current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    def compute_data_hash(self, data: Dict) -> str:
        normalized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode()).hexdigest()