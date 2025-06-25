"""Configuration management for Universal MCP Server."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the Universal MCP Server."""
    
    def __init__(self):
        # GitHub API configuration
        self.github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
        
        # Database configuration
        self.database_path: str = os.getenv("DATABASE_PATH", "./data.db")
        
        # Server configuration
        self.server_host: str = os.getenv("SERVER_HOST", "localhost")
        self.server_port: int = int(os.getenv("SERVER_PORT", "8000"))
        
        # Debug mode
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        
        # Ensure data directory exists
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def has_github_token(self) -> bool:
        """Check if GitHub token is configured."""
        return self.github_token is not None and len(self.github_token.strip()) > 0


# Global configuration instance
config = Config()