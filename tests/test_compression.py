import pytest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.compression import JSONCompressor

class TestJSONCompressor:
    def setup_method(self):
        self.compressor = JSONCompressor()
        self.sample_applicant_data = {
            "personal_details": {
                "fields": {
                    "Full Name": "John Doe",
                    "Email": "john@example.com",
                    "Location": "New York, NY",
                    "LinkedIn": "https://linkedin.com/in/johndoe"
                }
            },
            "work_experience": [
                {
                    "fields": {
                        "Company": "Tech Corp",
                        "Title": "Software Engineer",
                        "Start": "2022-01",
                        "End": "2023-12",
                        "Technologies": ["Python", "JavaScript", "React"]
                    }
                },
                {
                    "fields": {
                        "Company": "Startup Inc",
                        "Title": "Full Stack Developer",
                        "Start": "2021-03",
                        "End": "2021-12",
                        "Technologies": ["Node.js", "MongoDB", "Vue.js"]
                    }
                }
            ],
            "salary_preferences": {
                "fields": {
                    "Preferred Rate": 85,
                    "Min Rate": 75,
                    "Currency": "USD",
                    "Availability": 40
                }
            }
        }
    
    def test_compress_applicant_data(self):
        result = self.compressor.compress_applicant_data(self.sample_applicant_data)
        
        assert result["changed"] is True
        assert result["compressed_json"] is not None
        assert result["hash"] is not None
        assert result["size"] > 0
        assert result["compression_ratio"] < 1.0
    
    def test_decompress_applicant_data(self):
        # First compress
        compress_result = self.compressor.compress_applicant_data(self.sample_applicant_data)
        compressed_json = compress_result["compressed_json"]
        
        # Then decompress
        decompress_result = self.compressor.decompress_applicant_data(compressed_json)
        
        assert decompress_result["success"] is True
        assert decompress_result["data"] is not None
        assert decompress_result["error"] is None
        
        # Verify data integrity
        decompressed_data = decompress_result["data"]
        assert "personal_details" in decompressed_data
        assert "work_experience" in decompressed_data
        assert "salary_preferences" in decompressed_data
        assert decompressed_data["personal_details"]["full_name"] == "John Doe"
    
    def test_hash_consistency(self):
        result1 = self.compressor.compress_applicant_data(self.sample_applicant_data)
        result2 = self.compressor.compress_applicant_data(self.sample_applicant_data)
        
        # Same data should produce same hash
        assert result1["hash"] == result2["hash"]
    
    def test_data_optimization(self):
        # Create large dataset
        large_data = self.sample_applicant_data.copy()
        large_work_exp = []
        
        # Add many work experiences
        for i in range(20):
            large_work_exp.append({
                "fields": {
                    "Company": f"Company {i}",
                    "Title": f"Position {i}",
                    "Start": f"202{i % 3}-01",
                    "End": f"202{(i % 3) + 1}-12",
                    "Technologies": [f"Tech{j}" for j in range(5)]
                }
            })
        
        large_data["work_experience"] = large_work_exp
        
        result = self.compressor.compress_applicant_data(large_data)
        
        # Should still compress successfully
        assert result["changed"] is True
        assert result["compressed_json"] is not None
        
        # Verify decompression still works
        decompress_result = self.compressor.decompress_applicant_data(result["compressed_json"])
        assert decompress_result["success"] is True
    
    def test_invalid_compressed_data(self):
        # Test with invalid base64
        result = self.compressor.decompress_applicant_data("invalid_base64_data")
        assert result["success"] is False
        assert result["error"] is not None
        
        # Test with valid base64 but invalid compressed data
        import base64
        invalid_compressed = base64.b64encode(b"not compressed data").decode()
        result = self.compressor.decompress_applicant_data(invalid_compressed)
        assert result["success"] is False
        assert result["error"] is not None