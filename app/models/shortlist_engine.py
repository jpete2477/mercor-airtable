import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config.settings import Config

class ShortlistEngine:
    def __init__(self, airtable_client):
        self.airtable_client = airtable_client
        self.min_score = Config.SHORTLIST_MIN_SCORE
    
    def evaluate_applicant(self, applicant_id: str, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an applicant against shortlisting rules and create shortlisted lead if qualified.
        """
        try:
            # Get active shortlisting rules
            rules = self._get_active_rules()
            if not rules:
                return {
                    "success": False,
                    "error": "No active shortlisting rules found",
                    "shortlisted": False
                }
            
            # Calculate score
            evaluation_result = self._calculate_score(applicant_data, rules)
            
            # Check if applicant meets minimum score
            if evaluation_result["total_score"] >= self.min_score:
                # Create shortlisted lead
                compressed_json = self._prepare_compressed_data(applicant_data)
                shortlist_result = self._create_shortlisted_lead(
                    applicant_id,
                    compressed_json,
                    evaluation_result["total_score"],
                    evaluation_result["score_reason"]
                )
                
                return {
                    "success": True,
                    "shortlisted": True,
                    "score": evaluation_result["total_score"],
                    "score_reason": evaluation_result["score_reason"],
                    "shortlist_id": shortlist_result.get("id"),
                    "rules_evaluated": len(rules)
                }
            else:
                return {
                    "success": True,
                    "shortlisted": False,
                    "score": evaluation_result["total_score"],
                    "score_reason": evaluation_result["score_reason"],
                    "min_score_required": self.min_score,
                    "rules_evaluated": len(rules)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Shortlisting evaluation failed: {str(e)}",
                "shortlisted": False
            }
    
    def _get_active_rules(self) -> List[Dict[str, Any]]:
        """
        Get all active shortlisting rules from Airtable.
        """
        try:
            records = self.airtable_client.list_records(
                "Shortlist Rules",
                formula="{Active} = TRUE()"
            )
            
            rules = []
            for record in records:
                fields = record.get("fields", {})
                rules.append({
                    "id": record["id"],
                    "criterion": fields.get("Criterion", ""),
                    "rule": fields.get("Rule", ""),
                    "points": fields.get("Points", 0),
                    "description": fields.get("Description", "")
                })
            
            return rules
            
        except Exception as e:
            print(f"Error fetching shortlist rules: {e}")
            return []
    
    def _calculate_score(self, applicant_data: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate total score and generate score reason.
        """
        total_score = 0
        matched_criteria = []
        failed_criteria = []
        
        for rule in rules:
            criterion = rule["criterion"].lower()
            rule_text = rule["rule"]
            points = rule["points"]
            
            passed = self._evaluate_rule(applicant_data, criterion, rule_text)
            
            if passed:
                total_score += points
                matched_criteria.append(f"{criterion} ({rule_text}): +{points} points")
            else:
                failed_criteria.append(f"{criterion} ({rule_text}): 0 points")
        
        # Generate score reason
        score_reason_parts = []
        if matched_criteria:
            score_reason_parts.append("✅ Passed criteria:")
            score_reason_parts.extend([f"  • {criteria}" for criteria in matched_criteria])
        
        if failed_criteria:
            score_reason_parts.append("❌ Failed criteria:")
            score_reason_parts.extend([f"  • {criteria}" for criteria in failed_criteria])
        
        score_reason_parts.append(f"\nTotal Score: {total_score}/{sum(rule['points'] for rule in rules)}")
        
        return {
            "total_score": total_score,
            "score_reason": "\n".join(score_reason_parts),
            "matched_criteria": len(matched_criteria),
            "failed_criteria": len(failed_criteria)
        }
    
    def _evaluate_rule(self, applicant_data: Dict[str, Any], criterion: str, rule_text: str) -> bool:
        """
        Evaluate a single shortlisting rule against applicant data.
        """
        try:
            if "experience" in criterion:
                return self._evaluate_experience_rule(applicant_data, rule_text)
            elif "compensation" in criterion or "rate" in criterion or "salary" in criterion:
                return self._evaluate_compensation_rule(applicant_data, rule_text)
            elif "location" in criterion:
                return self._evaluate_location_rule(applicant_data, rule_text)
            elif "technology" in criterion or "skill" in criterion:
                return self._evaluate_technology_rule(applicant_data, rule_text)
            elif "availability" in criterion:
                return self._evaluate_availability_rule(applicant_data, rule_text)
            else:
                # Generic rule evaluation
                return self._evaluate_generic_rule(applicant_data, criterion, rule_text)
                
        except Exception as e:
            print(f"Error evaluating rule '{criterion}: {rule_text}': {e}")
            return False
    
    def _evaluate_experience_rule(self, applicant_data: Dict[str, Any], rule_text: str) -> bool:
        """
        Evaluate experience-based rules (e.g., ">=4 years", ">=2 years in Python").
        """
        work_experience = applicant_data.get("work_experience", [])
        
        # Extract years requirement from rule text
        years_match = re.search(r'>=?(\d+)\s*years?', rule_text.lower())
        if not years_match:
            return False
        
        required_years = int(years_match.group(1))
        
        # Calculate total experience
        total_experience_years = self._calculate_total_experience_years(work_experience)
        
        # Check for specific technology requirement
        tech_match = re.search(r'in\s+([a-zA-Z+\s]+)', rule_text.lower())
        if tech_match:
            required_tech = tech_match.group(1).strip()
            tech_experience_years = self._calculate_tech_experience_years(work_experience, required_tech)
            return tech_experience_years >= required_years
        else:
            return total_experience_years >= required_years
    
    def _evaluate_compensation_rule(self, applicant_data: Dict[str, Any], rule_text: str) -> bool:
        """
        Evaluate compensation-based rules (e.g., "<=$100/hr", ">=50k annually").
        """
        salary_prefs = applicant_data.get("salary_preferences", {})
        preferred_rate = salary_prefs.get("preferred_rate", 0)
        
        # Extract rate and operator from rule text
        rate_match = re.search(r'([<>=]+)\s*\$?(\d+)', rule_text.lower())
        if not rate_match:
            return False
        
        operator = rate_match.group(1)
        threshold_rate = int(rate_match.group(2))
        
        if "≤" in operator or "<=" in operator:
            return preferred_rate <= threshold_rate
        elif "≥" in operator or ">=" in operator:
            return preferred_rate >= threshold_rate
        elif "<" in operator:
            return preferred_rate < threshold_rate
        elif ">" in operator:
            return preferred_rate > threshold_rate
        elif "=" in operator:
            return preferred_rate == threshold_rate
        
        return False
    
    def _evaluate_location_rule(self, applicant_data: Dict[str, Any], rule_text: str) -> bool:
        """
        Evaluate location-based rules (e.g., "US only", "remote friendly").
        """
        personal_details = applicant_data.get("personal_details", {})
        location = personal_details.get("location", "").lower()
        
        rule_lower = rule_text.lower()
        
        if "us" in rule_lower and "only" in rule_lower:
            return any(country in location for country in ["us", "usa", "united states", "america"])
        elif "remote" in rule_lower:
            return "remote" in location or "anywhere" in location
        elif "europe" in rule_lower:
            eu_countries = ["uk", "germany", "france", "spain", "italy", "netherlands", "belgium", "poland"]
            return any(country in location for country in eu_countries)
        else:
            # Direct location match
            return rule_lower in location
    
    def _evaluate_technology_rule(self, applicant_data: Dict[str, Any], rule_text: str) -> bool:
        """
        Evaluate technology/skill-based rules (e.g., "has Python", "React experience").
        """
        work_experience = applicant_data.get("work_experience", [])
        
        # Collect all technologies from work experience
        all_technologies = []
        for exp in work_experience:
            technologies = exp.get("technologies", [])
            all_technologies.extend([tech.lower() for tech in technologies])
        
        # Extract required technology from rule text
        tech_keywords = ["has", "experience", "with", "in"]
        rule_lower = rule_text.lower()
        
        for keyword in tech_keywords:
            rule_lower = rule_lower.replace(keyword, "").strip()
        
        # Check if required technology is in applicant's tech stack
        return any(rule_lower in tech for tech in all_technologies)
    
    def _evaluate_availability_rule(self, applicant_data: Dict[str, Any], rule_text: str) -> bool:
        """
        Evaluate availability-based rules (e.g., ">=40 hours/week", "full-time").
        """
        salary_prefs = applicant_data.get("salary_preferences", {})
        availability = salary_prefs.get("availability", 0)
        
        # Extract hours requirement
        hours_match = re.search(r'([<>=]+)\s*(\d+)\s*hours?', rule_text.lower())
        if hours_match:
            operator = hours_match.group(1)
            required_hours = int(hours_match.group(2))
            
            if "≥" in operator or ">=" in operator:
                return availability >= required_hours
            elif "≤" in operator or "<=" in operator:
                return availability <= required_hours
            elif ">" in operator:
                return availability > required_hours
            elif "<" in operator:
                return availability < required_hours
        
        # Check for full-time/part-time keywords
        if "full-time" in rule_text.lower():
            return availability >= 35
        elif "part-time" in rule_text.lower():
            return availability < 35
        
        return False
    
    def _evaluate_generic_rule(self, applicant_data: Dict[str, Any], criterion: str, rule_text: str) -> bool:
        """
        Generic rule evaluation for custom criteria.
        """
        # This is a fallback for custom rules that don't fit standard categories
        # For now, return False to be conservative
        return False
    
    def _calculate_total_experience_years(self, work_experience: List[Dict[str, Any]]) -> float:
        """
        Calculate total years of work experience.
        """
        total_months = 0
        
        for exp in work_experience:
            months = self._calculate_experience_months(exp)
            total_months += months
        
        return total_months / 12.0
    
    def _calculate_tech_experience_years(self, work_experience: List[Dict[str, Any]], 
                                       required_tech: str) -> float:
        """
        Calculate years of experience with a specific technology.
        """
        total_months = 0
        required_tech_lower = required_tech.lower()
        
        for exp in work_experience:
            technologies = [tech.lower() for tech in exp.get("technologies", [])]
            if any(required_tech_lower in tech for tech in technologies):
                months = self._calculate_experience_months(exp)
                total_months += months
        
        return total_months / 12.0
    
    def _calculate_experience_months(self, experience: Dict[str, Any]) -> int:
        """
        Calculate months of experience for a single job.
        """
        try:
            start_str = experience.get("start", "")
            end_str = experience.get("end", "")
            
            if not start_str:
                return 0
            
            # Parse dates (assuming YYYY-MM format)
            start_date = datetime.strptime(start_str, "%Y-%m")
            
            if end_str and end_str.lower() != "present":
                end_date = datetime.strptime(end_str, "%Y-%m")
            else:
                end_date = datetime.now()
            
            # Calculate months difference
            months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            return max(0, months_diff)
            
        except Exception:
            return 0
    
    def _prepare_compressed_data(self, applicant_data: Dict[str, Any]) -> str:
        """
        Prepare compressed JSON data for shortlisted lead.
        """
        from app.models.compression import JSONCompressor
        
        compressor = JSONCompressor()
        result = compressor.compress_applicant_data(applicant_data)
        
        return result.get("compressed_json", "")
    
    def _create_shortlisted_lead(self, applicant_id: str, compressed_json: str, 
                               score: int, score_reason: str) -> Dict[str, Any]:
        """
        Create a new shortlisted lead record.
        """
        fields = {
            "Applicant": [applicant_id],
            "Compressed JSON": compressed_json,
            "Score": score,
            "Score Reason": score_reason,
            "Created At": datetime.now().isoformat()
        }
        
        return self.airtable_client.create_record("Shortlisted Leads", fields)
    
    def get_shortlisted_leads(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all shortlisted leads, optionally limited.
        For now, return all Applicants since Shortlisted Leads table doesn't exist.
        Transform data to match admin dashboard expectations.
        """
        records = self.airtable_client.list_records("Applicants", max_records=limit)
        
        # Transform records to match admin dashboard template expectations
        transformed_records = []
        for record in records:
            fields = record.get("fields", {})
            
            # Create transformed record with expected field names
            transformed_record = {
                "id": record.get("id"),
                "createdTime": record.get("createdTime"),
                "fields": {
                    # Map existing fields to expected names
                    "Score": fields.get("LLM Score", 0),
                    "Applicant": [record.get("id")],  # Use record ID as applicant reference
                    "Created At": record.get("createdTime", ""),
                    "Compressed JSON": fields.get("Compressed JSON", ""),
                    "Score Reason": fields.get("LLM Summary", ""),
                    # Keep original fields as well
                    **fields
                }
            }
            transformed_records.append(transformed_record)
        
        return transformed_records