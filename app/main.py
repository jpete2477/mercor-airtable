import os
import sys
import redis
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from app.models.airtable_client import AirtableClient
from app.models.compression import JSONCompressor, DataRestorer
from app.models.llm_service import LLMService, LLMHistory
from app.models.shortlist_engine import ShortlistEngine

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

# Initialize Redis for rate limiting
try:
    redis_client = redis.from_url(Config.REDIS_URL)
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis not available, using in-memory rate limiting: {e}")
    redis_client = None

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{Config.RATE_LIMIT_PER_MINUTE} per minute"],
    storage_uri=Config.REDIS_URL if redis_client else None
)
limiter.init_app(app)

# Initialize services
airtable_client = AirtableClient()
json_compressor = JSONCompressor()
data_restorer = DataRestorer(airtable_client)
llm_service = LLMService()
llm_history = LLMHistory(airtable_client)
shortlist_engine = ShortlistEngine(airtable_client)


@app.route('/')
def index():
    """Main application form page."""
    return render_template('index.html')


@app.route('/admin')
def admin_dashboard():
    """Admin dashboard for viewing shortlisted candidates."""
    try:
        shortlisted_leads = shortlist_engine.get_shortlisted_leads(limit=50)
        return render_template('admin.html', leads=shortlisted_leads)
    except Exception as e:
        return render_template('admin.html', error=str(e))


@app.route('/api/submit-application', methods=['POST'])
@limiter.limit("10 per minute")
def submit_application():
    """Submit a new job application."""
    try:
        # Validate required fields
        required_fields = ['full_name', 'email', 'work_experience']
        for field in required_fields:
            if not request.json.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create applicant in Airtable
        applicant_id = airtable_client.create_applicant(request.json)
        
        # For now, skip processing since some tables don't exist
        # processing_result = process_applicant(applicant_id)
        processing_result = {"message": "Application submitted successfully, processing skipped"}
        
        return jsonify({
            'success': True,
            'applicant_id': applicant_id,
            'processing_result': processing_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/process-applicant/<applicant_id>', methods=['POST'])
def process_applicant(applicant_id: str):
    """Process an applicant through compression, LLM evaluation, and shortlisting."""
    try:
        # Get applicant data
        applicant_data = airtable_client.get_applicant_data(applicant_id)
        
        # Step 1: Compress data
        current_hash = applicant_data["applicant"]["fields"].get("Last Hash", "")
        compression_result = json_compressor.compress_applicant_data({
            **applicant_data,
            "current_hash": current_hash
        })
        
        processing_results = {
            "compression": compression_result,
            "llm_evaluation": None,
            "shortlisting": None
        }
        
        # Only proceed if data has changed
        if compression_result.get("changed", True):
            # Update Airtable with compressed data
            airtable_client.update_record("Applicants", applicant_id, {
                "Compressed JSON": compression_result["compressed_json"],
                "Last Hash": compression_result["hash"],
                "Status": "Processed"
            })
            
            # Step 2: LLM Evaluation
            llm_result = llm_service.evaluate_applicant(applicant_data, current_hash)
            processing_results["llm_evaluation"] = llm_result
            
            if llm_result.get("success") and llm_result.get("changed"):
                # Store LLM results
                airtable_client.update_record("Applicants", applicant_id, {
                    "LLM Summary": llm_result.get("summary", ""),
                    "LLM Score": llm_result.get("score", 0)
                })
                
                # Store in history
                usage_log = llm_service.log_usage(llm_result, applicant_id)
                llm_history.store_evaluation(applicant_id, llm_result, usage_log)
            
            # Step 3: Shortlisting
            shortlist_result = shortlist_engine.evaluate_applicant(applicant_id, applicant_data)
            processing_results["shortlisting"] = shortlist_result
        
        return jsonify({
            'success': True,
            'results': processing_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decompress-applicant/<applicant_id>', methods=['POST'])
def decompress_applicant(applicant_id: str):
    """Decompress and restore applicant data from compressed JSON."""
    try:
        # Get compressed data
        applicant = airtable_client.get_record("Applicants", applicant_id)
        compressed_json = applicant["fields"].get("Compressed JSON", "")
        
        if not compressed_json:
            return jsonify({
                'success': False,
                'error': 'No compressed data found for this applicant'
            }), 400
        
        # Restore data
        restore_result = data_restorer.restore_from_compressed(applicant_id, compressed_json)
        
        return jsonify(restore_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/shortlisted-leads')
def get_shortlisted_leads():
    """Get all shortlisted leads."""
    try:
        limit = request.args.get('limit', 50, type=int)
        leads = shortlist_engine.get_shortlisted_leads(limit=limit)
        return jsonify({
            'success': True,
            'leads': leads
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/applicant/<applicant_id>')
def get_applicant(applicant_id: str):
    """Get applicant details."""
    try:
        applicant_data = airtable_client.get_applicant_data(applicant_id)
        return jsonify({
            'success': True,
            'applicant': applicant_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint with hot reload test."""
    try:
        # Test Airtable connection
        airtable_client.list_records("Applicants", max_records=1)
        
        # Test Redis connection if available
        redis_status = "connected" if redis_client else "not configured"
        if redis_client:
            try:
                redis_client.ping()
            except:
                redis_status = "error"
        
        return jsonify({
            'status': 'healthy',
            'airtable': 'connected',
            'redis': redis_status,
            'llm_provider': Config.LLM_PROVIDER
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit error handler."""
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.'
    }), 429


@app.errorhandler(404)
def not_found(e):
    """404 error handler."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)