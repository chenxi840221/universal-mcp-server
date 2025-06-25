"""Main entry point for the Universal MCP Server."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.resources import Resource
from fastmcp.tools import Tool

from .config import config
from .document_reader import DocumentReader
from .database_connector import DatabaseConnector
from .project_manager import ProjectManager
from .file_browser import FileBrowser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the FastMCP server
mcp = FastMCP("Universal MCP Server")

# Initialize components
document_reader = DocumentReader()
database_connector = DatabaseConnector(config.database_path)
project_manager = ProjectManager(config.github_token) if config.has_github_token() else None
file_browser = FileBrowser()


@mcp.tool()
def read_document(file_path: str, format: str = "auto") -> Dict[str, Any]:
    """
    Read and extract content from various document formats.
    
    Args:
        file_path: Path to the document file
        format: Document format ('pdf', 'docx', 'xlsx', or 'auto' for auto-detection)
    
    Returns:
        Dictionary containing extracted content and metadata
    """
    try:
        return document_reader.read_document(file_path, format)
    except Exception as e:
        logger.error(f"Error reading document {file_path}: {e}")
        return {"error": str(e), "file_path": file_path}


@mcp.tool()
def execute_sql(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """
    Execute SQL query on the local SQLite database.
    
    Args:
        query: SQL query to execute
        params: Optional parameters for the query
    
    Returns:
        Query results or execution status
    """
    try:
        return database_connector.execute_query(query, params or [])
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        return {"error": str(e), "query": query}


@mcp.tool()
def list_tables() -> Dict[str, Any]:
    """
    List all tables in the SQLite database.
    
    Returns:
        List of table names and their schemas
    """
    try:
        return database_connector.list_tables()
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return {"error": str(e)}


@mcp.tool()
def describe_table(table_name: str) -> Dict[str, Any]:
    """
    Get schema information for a specific table.
    
    Args:
        table_name: Name of the table to describe
    
    Returns:
        Table schema information
    """
    try:
        return database_connector.describe_table(table_name)
    except Exception as e:
        logger.error(f"Error describing table {table_name}: {e}")
        return {"error": str(e), "table_name": table_name}


@mcp.tool()
def browse_directory(path: str = ".", include_hidden: bool = False, max_depth: int = 1) -> Dict[str, Any]:
    """
    Browse and list directory contents with enhanced information.
    
    Args:
        path: Directory path to browse (default: current directory)
        include_hidden: Include hidden files and directories
        max_depth: Maximum depth for recursive listing
    
    Returns:
        Directory listing with file information
    """
    try:
        return file_browser.browse_directory(path, include_hidden, max_depth)
    except Exception as e:
        logger.error(f"Error browsing directory {path}: {e}")
        return {"error": str(e), "path": path}


@mcp.tool()
def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get detailed information about a file or directory.
    
    Args:
        file_path: Path to the file or directory
    
    Returns:
        Detailed file information including size, permissions, dates, etc.
    """
    try:
        return file_browser.get_file_info(file_path)
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {"error": str(e), "file_path": file_path}


@mcp.tool()
def search_files(directory: str = ".", pattern: str = "*", include_content: bool = False) -> Dict[str, Any]:
    """
    Search for files matching a pattern with optional content search.
    
    Args:
        directory: Directory to search in
        pattern: File name pattern (supports wildcards)
        include_content: Whether to search within file contents
    
    Returns:
        List of matching files with optional content matches
    """
    try:
        return file_browser.search_files(directory, pattern, include_content)
    except Exception as e:
        logger.error(f"Error searching files in {directory}: {e}")
        return {"error": str(e), "directory": directory, "pattern": pattern}


# GitHub/Project Management tools (only if token is configured)
if project_manager:
    @mcp.tool()
    def list_repositories(username: Optional[str] = None, organization: Optional[str] = None) -> Dict[str, Any]:
        """
        List repositories for a user or organization.
        
        Args:
            username: GitHub username (optional)
            organization: GitHub organization name (optional)
        
        Returns:
            List of repositories with basic information
        """
        try:
            return project_manager.list_repositories(username, organization)
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_repository_info(repo_name: str, owner: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a repository.
        
        Args:
            repo_name: Repository name
            owner: Repository owner (optional, uses authenticated user if not provided)
        
        Returns:
            Detailed repository information
        """
        try:
            return project_manager.get_repository_info(repo_name, owner)
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {"error": str(e), "repo_name": repo_name}

    @mcp.tool()
    def list_issues(repo_name: str, owner: Optional[str] = None, state: str = "open") -> Dict[str, Any]:
        """
        List issues for a repository.
        
        Args:
            repo_name: Repository name
            owner: Repository owner (optional)
            state: Issue state ('open', 'closed', or 'all')
        
        Returns:
            List of issues
        """
        try:
            return project_manager.list_issues(repo_name, owner, state)
        except Exception as e:
            logger.error(f"Error listing issues: {e}")
            return {"error": str(e), "repo_name": repo_name}

    @mcp.tool()
    def create_issue(repo_name: str, title: str, body: str = "", owner: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new issue in a repository.
        
        Args:
            repo_name: Repository name
            title: Issue title
            body: Issue description
            owner: Repository owner (optional)
        
        Returns:
            Created issue information
        """
        try:
            return project_manager.create_issue(repo_name, title, body, owner)
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return {"error": str(e), "repo_name": repo_name, "title": title}


def main():
    """Main entry point for the server."""
    logger.info("Starting Universal MCP Server...")
    logger.info(f"Database path: {config.database_path}")
    logger.info(f"GitHub integration: {'enabled' if project_manager else 'disabled (no token)'}")
    
    # Run the server
    mcp.run(
        host=config.server_host,
        port=config.server_port,
        transport="stdio"  # Use stdio transport for MCP
    )


if __name__ == "__main__":
    main()