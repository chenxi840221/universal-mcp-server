# Claude Code Integration Setup

This Universal MCP Server provides document reading capabilities for Claude Code, allowing it to read PDF, Word, Excel, and CSV files directly.

## Setup Instructions

### 1. Install Dependencies

```bash
cd /mnt/c/workspace/MCPTool
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Claude Code

Add this MCP server to your Claude Code configuration:

**For Claude Code CLI:**
Create or update your `~/.config/claude/mcp_config.json`:

```json
{
  "mcpServers": {
    "document-reader": {
      "command": "python",
      "args": ["-m", "src.universal_mcp_server.main"],
      "cwd": "/mnt/c/workspace/MCPTool",
      "env": {
        "PYTHONPATH": "/mnt/c/workspace/MCPTool"
      },
      "description": "Universal document reader for PDF, Word, Excel, and CSV files"
    }
  }
}
```

**For Claude Code Desktop:**
Add the server configuration to your MCP settings.

### 3. Available Tools

Once configured, Claude Code will have access to these document reading tools:

- `read_document`: Auto-detect and read any supported document format
- `read_pdf`: Specifically read PDF files with page-by-page extraction
- `read_word_document`: Read Word documents (.docx, .doc) with formatted output
- `read_excel_file`: Read Excel files with optional sheet selection
- `browse_directory`: Browse files and directories
- `search_files`: Search for files by pattern
- `execute_sql`: Query local SQLite databases
- `list_tables`: List database tables
- `describe_table`: Get table schema information

### 4. Usage Examples

Once configured, you can ask Claude Code to:

- "Read the PDF report in the documents folder"
- "Extract data from the Excel spreadsheet"
- "What's in the Word document?"
- "Read all CSV files in this directory"
- "Show me the structure of the database"

### 5. Supported File Formats

- **PDF**: Text extraction with page information
- **Word**: (.docx, .doc) Paragraphs, tables, and formatting
- **Excel**: (.xlsx, .xls) All sheets with data and statistics  
- **CSV**: Data with column information and statistics

### 6. Troubleshooting

If the server doesn't start:

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check the Python path in the configuration
3. Verify the virtual environment is activated
4. Check Claude Code logs for error messages

The server uses stdio transport for communication with Claude Code and includes comprehensive error handling and logging.