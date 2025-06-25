# Universal MCP Server

A comprehensive Model Context Protocol (MCP) server that provides multiple powerful capabilities for document processing, database operations, file management, and project integration.

## 🚀 Features

### 📖 Document Reader
- **PDF Support**: Extract text content from PDF files with page-by-page breakdown
- **Word Documents**: Read .docx files including paragraphs, tables, and formatting
- **Excel Files**: Process .xlsx/.xls files with sheet analysis and data extraction
- **CSV Files**: Parse CSV data with automatic type inference and summary statistics

### 🗄️ Database Connector
- **SQLite Integration**: Local SQLite database operations with full SQL support
- **Query History**: Track all executed queries with performance metrics
- **Schema Management**: Table creation, inspection, and metadata management
- **Data Import**: Create tables from structured data (JSON, CSV)

### 📁 Enhanced File Browser
- **Advanced Directory Listing**: Recursive browsing with file metadata
- **File Search**: Pattern-based search with optional content searching
- **File Information**: Detailed file stats, permissions, and content previews
- **File Operations**: Create, delete files and directories

### 🐙 Project Management (GitHub Integration)
- **Repository Management**: List, inspect, and manage GitHub repositories
- **Issue Tracking**: Create, list, and manage GitHub issues
- **User Information**: Access GitHub user and organization data
- **Collaboration Tools**: Monitor project activity and contributions

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone or create the project directory**:
   ```bash
   mkdir universal-mcp-server
   cd universal-mcp-server
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

## ⚙️ Configuration

Create a `.env` file in the project root with the following optional settings:

```env
# GitHub API Token (for project management features)
GITHUB_TOKEN=your_github_token_here

# Database path (defaults to ./data.db)
DATABASE_PATH=./data.db

# Server configuration (defaults shown)
SERVER_HOST=localhost
SERVER_PORT=8000

# Debug mode (defaults to False)
DEBUG=False
```

### GitHub Token Setup (Optional)

To use project management features:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with appropriate permissions:
   - `repo` (for repository access)
   - `issues` (for issue management)
   - `user` (for user information)
3. Add the token to your `.env` file as `GITHUB_TOKEN`

## 🔧 Usage

### Starting the Server

Run the MCP server using:

```bash
python -m src.universal_mcp_server.main
```

### Available Tools

#### Document Processing
- `read_document(file_path, format="auto")` - Read and extract content from documents
- Supported formats: PDF, DOCX, XLSX, CSV

#### Database Operations
- `execute_sql(query, params=[])` - Execute SQL queries on SQLite database
- `list_tables()` - List all database tables with metadata
- `describe_table(table_name)` - Get detailed table schema information

#### File System Operations
- `browse_directory(path=".", include_hidden=False, max_depth=1)` - Browse directory contents
- `get_file_info(file_path)` - Get detailed file/directory information
- `search_files(directory=".", pattern="*", include_content=False)` - Search for files

#### Project Management (GitHub)
*Available only when GitHub token is configured*

- `list_repositories(username=None, organization=None)` - List repositories
- `get_repository_info(repo_name, owner=None)` - Get detailed repository information
- `list_issues(repo_name, owner=None, state="open")` - List repository issues
- `create_issue(repo_name, title, body="", owner=None)` - Create new issues

## 📋 Examples

### Document Processing

```python
# Read a PDF file
result = read_document("document.pdf")
print(f"Pages: {result['content']['total_pages']}")
print(f"Text: {result['content']['text_content'][:200]}...")

# Process Excel file
result = read_document("data.xlsx")
for sheet in result['content']['sheets']:
    print(f"Sheet: {sheet['sheet_name']} ({sheet['rows']} rows)")
```

### Database Operations

```python
# Create a table
execute_sql("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert data
execute_sql(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    ["John Doe", "john@example.com"]
)

# Query data
result = execute_sql("SELECT * FROM users WHERE name LIKE ?", ["%John%"])
```

### File System Operations

```python
# Browse directory
result = browse_directory("/path/to/directory", max_depth=2)
print(f"Found {result['summary']['total_items']} items")

# Search for Python files
result = search_files(".", "*.py", include_content=True)
for match in result['matches']:
    print(f"Found: {match['path']}")
```

### GitHub Integration

```python
# List repositories
repos = list_repositories("username")
for repo in repos['repositories']:
    print(f"{repo['name']}: {repo['description']}")

# Create an issue
issue = create_issue("my-repo", "Bug Report", "Description of the bug")
print(f"Created issue #{issue['issue']['number']}")
```

## 🧪 Testing

Run the basic functionality tests:

```bash
python test_simple.py
```

For more comprehensive testing:

```bash
pip install pytest
python -m pytest tests/
```

## 🏗️ Architecture

### Core Components

- **FastMCP Server**: Main MCP server implementation using the FastMCP framework
- **Document Reader**: Handles PDF, Word, Excel, and CSV file processing
- **Database Connector**: SQLite operations with query history and metadata
- **File Browser**: Enhanced file system operations and search
- **Project Manager**: GitHub API integration for project management
- **Configuration Manager**: Environment-based configuration system

### Data Flow

1. **Client Request** → FastMCP Server → Tool Router
2. **Tool Execution** → Component (Document/DB/File/GitHub)
3. **Processing** → Data transformation and validation
4. **Response** → Structured JSON response to client

## 🔧 Development

### Project Structure

```
universal-mcp-server/
├── src/universal_mcp_server/
│   ├── __init__.py
│   ├── main.py              # Main server entry point
│   ├── config.py            # Configuration management
│   ├── document_reader.py   # Document processing
│   ├── database_connector.py # SQLite operations
│   ├── project_manager.py   # GitHub integration
│   └── file_browser.py      # File system operations
├── tests/
│   ├── __init__.py
│   └── test_basic_functionality.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

### Adding New Features

1. **Create new module** in `src/universal_mcp_server/`
2. **Import in main.py** and initialize component
3. **Add MCP tools** using `@mcp.tool()` decorator
4. **Update documentation** and tests

### Dependencies

- **Core**: `mcp`, `fastmcp` (MCP server framework)
- **Documents**: `PyPDF2`, `python-docx`, `pandas`, `openpyxl` (document processing)
- **GitHub**: `PyGithub` (GitHub API integration)
- **Utils**: `python-dotenv`, `requests` (utilities)

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies installed
2. **Permission Errors**: Check file/directory permissions for database and document access
3. **GitHub API Errors**: Verify token validity and permissions
4. **Memory Issues**: Large files may cause memory issues; consider file size limits

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your `.env` file.

### Logs

The server provides detailed logging for:
- Tool execution and performance
- Database query history
- Error tracking and debugging
- API request/response cycles

## 📄 License

This project is open source. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples and documentation
3. Create an issue with detailed information about your problem

---

**Universal MCP Server** - Bringing powerful document processing, database operations, and project management capabilities to the Model Context Protocol ecosystem.