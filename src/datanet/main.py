"""
FastAPI Application Bootstrap

Main entry point for the FastAPI application.
"""

import logging
from .api import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting TAMPA Datanet Agent API...")
    uvicorn.run(
        "src.datanet.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
