# scripts/cbs_data_extractor.py
import requests
from datetime import datetime
import logging
import os

# Initialize module-level logger
logger = logging.getLogger(__name__)

def fetch_dutch_housing_data():
    """
    Fetch Dutch housing price index data from CBS Open Data API
    
    Returns:
        list: Parsed JSON data from CBS API
    Raises:
        RuntimeError: When API request fails
    """
    try:
        # CBS Open Data API endpoint (Dutch Central Bureau of Statistics)
        api_url = "https://opendata.cbs.nl/ODataApi/odata/83710NED/TypedDataSet"
        
        # Get API key from environment variables (security best practice)
        api_key = os.getenv("CBS_API_KEY")
        if not api_key:
            raise ValueError("CBS_API_KEY environment variable not set")
        
        # Configure request with timeout (production reliability requirement)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(api_url, headers=headers, timeout=10)
        
        # Validate HTTP response status
        response.raise_for_status()
        
        # Log successful data retrieval with UTC timestamp
        logger.info(f"CBS data fetched successfully at {datetime.utcnow().isoformat()}Z")
        
        return response.json().get('value', [])
        
    except requests.exceptions.RequestException as e:
        # Log error without exposing sensitive data (GDPR compliance)
        logger.error(f"API request failed: {str(e)}", exc_info=False)
        raise RuntimeError("CBS API service unavailable") from e