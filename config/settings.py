import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Airtable settings
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_BASE_TABLE = os.getenv('AIRTABLE_BASE_TABLE')
    
    # LLM settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # 'openai' or 'anthropic'
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '512'))
    
    # Redis settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    
    # Application settings
    MAX_JSON_SIZE = int(os.getenv('MAX_JSON_SIZE', '102400'))  # 100KB
    SHORTLIST_MIN_SCORE = int(os.getenv('SHORTLIST_MIN_SCORE', '2'))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    @classmethod
    def validate(cls):
        required_vars = [
            'AIRTABLE_API_KEY',
            'AIRTABLE_BASE_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate LLM configuration
        if cls.LLM_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            missing_vars.append('OPENAI_API_KEY')
        elif cls.LLM_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            missing_vars.append('ANTHROPIC_API_KEY')
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables for LLM: {', '.join(missing_vars)}")