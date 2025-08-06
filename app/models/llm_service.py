import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from config.settings import Config

class LLMService:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.model = Config.LLM_MODEL
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.client = None
        self.enabled = False
        
        try:
            if self.provider == 'openai' and Config.OPENAI_API_KEY and not Config.OPENAI_API_KEY.startswith('sk-test-'):
                import openai
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                self.enabled = True
            elif self.provider == 'anthropic' and Config.ANTHROPIC_API_KEY and not Config.ANTHROPIC_API_KEY.startswith('sk-ant-test-'):
                import anthropic
                self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                self.enabled = True
            else:
                print(f"Warning: LLM service disabled. Provider: {self.provider}, API key valid: {bool(Config.OPENAI_API_KEY or Config.ANTHROPIC_API_KEY)}")
        except Exception as e:
            print(f"Warning: Failed to initialize LLM service: {e}")
            self.enabled = False
    
    def evaluate_applicant(self, applicant_data: Dict[str, Any], 
                          current_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate applicant using LLM and return structured insights.
        """
        # Return early if LLM service is disabled
        if not self.enabled:
            return {
                "success": False,
                "error": "LLM service is disabled (no valid API key)",
                "hash": self._compute_data_hash(applicant_data),
                "changed": False,
                "summary": "LLM evaluation not available",
                "score": 0,
                "follow_ups": []
            }
        
        # Check if we need to skip due to unchanged data
        if current_hash:
            data_hash = self._compute_data_hash(applicant_data)
            if data_hash == current_hash:
                return {
                    "success": True,
                    "hash": data_hash,
                    "changed": False,
                    "summary": None,
                    "score": None,
                    "follow_ups": None
                }
        
        try:
            # Prepare the prompt
            prompt = self._prepare_evaluation_prompt(applicant_data)
            
            # Call LLM with retry logic
            response = self._call_llm_with_retry(prompt)
            
            if not response["success"]:
                return response
            
            # Parse structured output
            evaluation = self._parse_llm_response(response["content"])
            evaluation["hash"] = self._compute_data_hash(applicant_data)
            evaluation["changed"] = True
            
            return evaluation
            
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM evaluation failed: {str(e)}",
                "hash": None,
                "changed": False
            }
    
    def _prepare_evaluation_prompt(self, applicant_data: Dict[str, Any]) -> str:
        """
        Prepare a structured prompt for LLM evaluation.
        """
        personal = applicant_data.get("personal_details", {})
        work_exp = applicant_data.get("work_experience", [])
        salary = applicant_data.get("salary_preferences", {})
        
        # Format work experience
        work_exp_text = ""
        for i, exp in enumerate(work_exp[:5], 1):  # Limit to top 5
            tech_list = ", ".join(exp.get("technologies", []))
            work_exp_text += f"{i}. {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('start', '')} - {exp.get('end', 'Present')})\n"
            if tech_list:
                work_exp_text += f"   Technologies: {tech_list}\n"
        
        prompt = f"""
Analyze the following job applicant profile and provide a structured evaluation.

APPLICANT PROFILE:
Name: {personal.get('full_name', 'N/A')}
Location: {personal.get('location', 'N/A')}
Email: {personal.get('email', 'N/A')}
LinkedIn: {personal.get('linkedin', 'N/A')}

WORK EXPERIENCE:
{work_exp_text if work_exp_text else 'No work experience provided.'}

SALARY PREFERENCES:
- Preferred Rate: ${salary.get('preferred_rate', 0)}/hr ({salary.get('currency', 'USD')})
- Minimum Rate: ${salary.get('min_rate', 0)}/hr
- Availability: {salary.get('availability', 0)} hours/week

EVALUATION INSTRUCTIONS:
1. Write a concise 100-word summary of the applicant's qualifications
2. Assign a score from 0-10 based on experience, skills, and market fit
3. Generate up to 3 relevant follow-up questions to ask this applicant

Return your evaluation in this exact JSON format:
{{
    "summary": "Your 100-word summary here",
    "score": 8.5,
    "follow_ups": [
        "Question 1?",
        "Question 2?",
        "Question 3?"
    ]
}}

Ensure the JSON is valid and properly formatted.
        """.strip()
        
        return prompt
    
    def _call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Call LLM API with exponential backoff retry logic.
        """
        for attempt in range(max_retries):
            try:
                if self.provider == 'openai':
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an expert recruiter evaluating job applicants. Always respond with valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                    content = response.choices[0].message.content
                    
                elif self.provider == 'anthropic':
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=0.3,
                        messages=[
                            {"role": "user", "content": f"{prompt}\n\nIMPORTANT: Respond only with valid JSON, no additional text."}
                        ]
                    )
                    content = response.content[0].text
                
                return {
                    "success": True,
                    "content": content,
                    "tokens_used": self._estimate_tokens(prompt, content),
                    "attempt": attempt + 1
                }
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"LLM call failed after {max_retries} attempts: {str(e)}",
                        "content": None,
                        "attempt": attempt + 1
                    }
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """
        Parse and validate LLM response.
        """
        try:
            response_data = json.loads(content.strip())
            
            # Validate required fields
            required_fields = ["summary", "score", "follow_ups"]
            for field in required_fields:
                if field not in response_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate data types and ranges
            summary = response_data["summary"]
            score = float(response_data["score"])
            follow_ups = response_data["follow_ups"]
            
            if not isinstance(summary, str) or len(summary) < 10:
                raise ValueError("Summary must be a non-empty string")
            
            if not 0 <= score <= 10:
                raise ValueError("Score must be between 0 and 10")
            
            if not isinstance(follow_ups, list) or len(follow_ups) > 3:
                raise ValueError("follow_ups must be a list with at most 3 items")
            
            return {
                "success": True,
                "summary": summary,
                "score": score,
                "follow_ups": follow_ups,
                "error": None
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "summary": None,
                "score": None,
                "follow_ups": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Response validation failed: {str(e)}",
                "summary": None,
                "score": None,
                "follow_ups": None
            }
    
    def _compute_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Compute hash of applicant data for change detection.
        """
        import hashlib
        # Remove metadata and timestamps for consistent hashing
        hash_data = {
            "personal_details": data.get("personal_details", {}),
            "work_experience": data.get("work_experience", []),
            "salary_preferences": data.get("salary_preferences", {})
        }
        json_str = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """
        Rough estimation of token usage (1 token ≈ 4 characters).
        """
        total_chars = len(prompt) + len(response or "")
        return total_chars // 4
    
    def log_usage(self, evaluation_result: Dict[str, Any], applicant_id: str) -> Dict[str, Any]:
        """
        Create a usage log entry for monitoring and billing.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "applicant_id": applicant_id,
            "provider": self.provider,
            "model": self.model,
            "tokens_estimated": evaluation_result.get("tokens_used", 0),
            "success": evaluation_result.get("success", False),
            "error": evaluation_result.get("error", None),
            "attempt": evaluation_result.get("attempt", 1)
        }


class LLMHistory:
    """
    Class to manage LLM evaluation history and versioning.
    """
    def __init__(self, airtable_client):
        self.airtable_client = airtable_client
    
    def store_evaluation(self, applicant_id: str, evaluation: Dict[str, Any], 
                        usage_log: Dict[str, Any]) -> str:
        """
        Store LLM evaluation result in history table.
        """
        fields = {
            "Applicant ID": [applicant_id],
            "Summary": evaluation.get("summary", ""),
            "Score": evaluation.get("score", 0),
            "Follow Up Questions": json.dumps(evaluation.get("follow_ups", [])),
            "Data Hash": evaluation.get("hash", ""),
            "Provider": usage_log["provider"],
            "Model": usage_log["model"],
            "Tokens Used": usage_log["tokens_estimated"],
            "Success": evaluation.get("success", False),
            "Error Message": evaluation.get("error", ""),
            "Timestamp": usage_log["timestamp"]
        }
        
        result = self.airtable_client.create_record("LLM History", fields)
        return result["id"]
    
    def get_latest_evaluation(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent successful evaluation for an applicant.
        """
        records = self.airtable_client.list_records(
            "LLM History",
            formula=f"AND({{Applicant ID}} = '{applicant_id}', {{Success}} = TRUE())"
        )
        
        if not records:
            return None
        
        # Sort by timestamp and get the latest
        records.sort(key=lambda x: x["fields"].get("Timestamp", ""), reverse=True)
        latest = records[0]["fields"]
        
        return {
            "summary": latest.get("Summary", ""),
            "score": latest.get("Score", 0),
            "follow_ups": json.loads(latest.get("Follow Up Questions", "[]")),
            "hash": latest.get("Data Hash", ""),
            "timestamp": latest.get("Timestamp", "")
        }