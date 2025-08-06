import json
import gzip
import base64
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from config.settings import Config

class JSONCompressor:
    def __init__(self):
        self.max_size = Config.MAX_JSON_SIZE
    
    def compress_applicant_data(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress applicant data into a structured JSON with hash-based deduplication.
        Returns compressed JSON string and metadata.
        """
        # Normalize the data
        normalized_data = self._normalize_data(applicant_data)
        
        # Compute hash
        data_hash = self._compute_hash(normalized_data)
        
        # Check if data has changed (caller should provide current hash)
        current_hash = applicant_data.get("current_hash", "")
        if data_hash == current_hash:
            return {
                "compressed_json": None,
                "hash": data_hash,
                "size": 0,
                "changed": False
            }
        
        # Optimize data size
        optimized_data = self._optimize_data_size(normalized_data)
        
        # Compress the JSON
        json_str = json.dumps(optimized_data, separators=(',', ':'))
        compressed_bytes = gzip.compress(json_str.encode('utf-8'))
        compressed_b64 = base64.b64encode(compressed_bytes).decode('utf-8')
        
        return {
            "compressed_json": compressed_b64,
            "hash": data_hash,
            "size": len(compressed_b64),
            "changed": True,
            "original_size": len(json_str),
            "compression_ratio": len(compressed_b64) / len(json_str)
        }
    
    def decompress_applicant_data(self, compressed_json: str) -> Dict[str, Any]:
        """
        Decompress and restore applicant data from compressed JSON.
        """
        try:
            # Decode and decompress
            compressed_bytes = base64.b64decode(compressed_json.encode('utf-8'))
            json_str = gzip.decompress(compressed_bytes).decode('utf-8')
            data = json.loads(json_str)
            
            return {
                "success": True,
                "data": data,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def _normalize_data(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize data for consistent hashing and compression.
        """
        personal_details = applicant_data.get("personal_details", {}).get("fields", {})
        work_experience = applicant_data.get("work_experience", [])
        salary_preferences = applicant_data.get("salary_preferences", {}).get("fields", {})
        
        # Sort work experience by end date (most recent first)
        work_exp_normalized = []
        for exp in work_experience:
            fields = exp.get("fields", {})
            exp_data = {
                "company": fields.get("Company", ""),
                "title": fields.get("Title", ""),
                "start": fields.get("Start", ""),
                "end": fields.get("End", ""),
                "technologies": sorted(fields.get("Technologies", []))
            }
            work_exp_normalized.append(exp_data)
        
        # Sort by end date descending (most recent first)
        work_exp_normalized.sort(key=lambda x: x.get("end", ""), reverse=True)
        
        normalized = {
            "personal_details": {
                "full_name": personal_details.get("Full Name", ""),
                "email": personal_details.get("Email", ""),
                "location": personal_details.get("Location", ""),
                "linkedin": personal_details.get("LinkedIn", "")
            },
            "work_experience": work_exp_normalized,
            "salary_preferences": {
                "preferred_rate": salary_preferences.get("Preferred Rate", 0),
                "min_rate": salary_preferences.get("Min Rate", 0),
                "currency": salary_preferences.get("Currency", "USD"),
                "availability": salary_preferences.get("Availability", 40)
            },
            "metadata": {
                "compressed_at": datetime.now().isoformat(),
                "total_experience_entries": len(work_exp_normalized)
            }
        }
        
        return normalized
    
    def _optimize_data_size(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize data size by prioritizing most relevant work experience entries.
        """
        # If data is already small enough, return as-is
        json_str = json.dumps(data, separators=(',', ':'))
        if len(json_str) <= self.max_size:
            return data
        
        # Start reducing work experience entries
        work_experience = data["work_experience"]
        optimized_data = data.copy()
        
        # Keep reducing until we're under the size limit
        max_entries = len(work_experience)
        while max_entries > 1:
            max_entries -= 1
            optimized_data["work_experience"] = work_experience[:max_entries]
            optimized_data["metadata"]["truncated_entries"] = len(work_experience) - max_entries
            
            json_str = json.dumps(optimized_data, separators=(',', ':'))
            if len(json_str) <= self.max_size:
                break
        
        return optimized_data
    
    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """
        Compute SHA256 hash of normalized data.
        """
        # Remove metadata for hash computation
        hash_data = {k: v for k, v in data.items() if k != "metadata"}
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


class DataRestorer:
    def __init__(self, airtable_client):
        self.airtable_client = airtable_client
    
    def restore_from_compressed(self, applicant_id: str, compressed_json: str) -> Dict[str, Any]:
        """
        Restore linked table records from compressed JSON with data integrity.
        """
        compressor = JSONCompressor()
        decompression_result = compressor.decompress_applicant_data(compressed_json)
        
        if not decompression_result["success"]:
            return {
                "success": False,
                "error": f"Decompression failed: {decompression_result['error']}"
            }
        
        data = decompression_result["data"]
        
        try:
            # Start transaction-like operations
            self._soft_delete_existing_records(applicant_id)
            self._create_new_records(applicant_id, data)
            
            return {
                "success": True,
                "records_created": self._count_created_records(data),
                "error": None
            }
            
        except Exception as e:
            # Rollback: reactivate soft-deleted records
            self._rollback_soft_deletes(applicant_id)
            return {
                "success": False,
                "error": f"Restoration failed: {str(e)}"
            }
    
    def _soft_delete_existing_records(self, applicant_id: str):
        """
        Soft delete existing records by marking them as inactive.
        """
        tables = ["Personal Details", "Work Experience", "Salary Preferences"]
        
        for table in tables:
            records = self.airtable_client.list_records(
                table, formula=f"{{Applicant ID}} = '{applicant_id}'"
            )
            
            updates = []
            for record in records:
                updates.append({
                    "id": record["id"],
                    "fields": {"Inactive": True}
                })
            
            if updates:
                self.airtable_client.batch_update(table, updates)
    
    def _create_new_records(self, applicant_id: str, data: Dict[str, Any]):
        """
        Create new records from decompressed data.
        """
        # Create personal details
        personal_fields = data["personal_details"].copy()
        personal_fields["Applicant ID"] = [applicant_id]
        self.airtable_client.create_record("Personal Details", personal_fields)
        
        # Create work experience records
        for exp in data["work_experience"]:
            exp_fields = exp.copy()
            exp_fields["Applicant ID"] = [applicant_id]
            self.airtable_client.create_record("Work Experience", exp_fields)
        
        # Create salary preferences
        salary_fields = data["salary_preferences"].copy()
        salary_fields["Applicant ID"] = [applicant_id]
        self.airtable_client.create_record("Salary Preferences", salary_fields)
    
    def _rollback_soft_deletes(self, applicant_id: str):
        """
        Rollback soft deletes by reactivating records.
        """
        tables = ["Personal Details", "Work Experience", "Salary Preferences"]
        
        for table in tables:
            records = self.airtable_client.list_records(
                table, formula=f"AND({{Applicant ID}} = '{applicant_id}', {{Inactive}} = TRUE())"
            )
            
            updates = []
            for record in records:
                updates.append({
                    "id": record["id"],
                    "fields": {"Inactive": False}
                })
            
            if updates:
                self.airtable_client.batch_update(table, updates)
    
    def _count_created_records(self, data: Dict[str, Any]) -> Dict[str, int]:
        """
        Count the number of records that would be created.
        """
        return {
            "personal_details": 1,
            "work_experience": len(data["work_experience"]),
            "salary_preferences": 1
        }