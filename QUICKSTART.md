# Quick Start Guide

Get up and running with Universal MCP Server in minutes!

## 🚀 Installation (5 minutes)

1. **Navigate to the project directory**:
   ```bash
   cd /mnt/c/workspace/MCPTool
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Test the installation**:
   ```bash
   python test_simple.py
   ```
   You should see: `🎉 All component tests completed!`

## ⚡ Quick Test

Try these commands to test core functionality:

### 📖 Read a Document
```bash
python -c "
from src.universal_mcp_server.document_reader import DocumentReader
reader = DocumentReader()
result = reader.read_document('test_data.csv')
print('Success:', result['success'])
print('Rows:', result['content']['summary']['rows'])
"
```

### 🗄️ Database Operations
```bash
python -c "
from src.universal_mcp_server.database_connector import DatabaseConnector
db = DatabaseConnector('./quicktest.db')
result = db.execute_query('CREATE TABLE test (id INTEGER, name TEXT)')
print('Table created:', result['success'])
"
```

### 📁 Browse Files
```bash
python -c "
from src.universal_mcp_server.file_browser import FileBrowser
browser = FileBrowser()
result = browser.browse_directory('.')
print('Files found:', result['summary']['total_items'])
"
```

## 🔧 Claude Code Integration

### Option 1: Use with Claude Code MCP

1. **Copy the MCP configuration**:
   ```bash
   cp mcp_config.json ~/.config/claude-code/mcp_servers.json
   ```

2. **Restart Claude Code** to load the new MCP server

3. **Test in Claude Code**:
   - Try: "List files in the current directory"
   - Try: "Read the test_data.csv file"
   - Try: "Create a database table for storing notes"

### Option 2: Manual Configuration

Add this to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "universal-mcp-server": {
      "command": "python",
      "args": ["-m", "src.universal_mcp_server.main"],
      "cwd": "/mnt/c/workspace/MCPTool",
      "env": {
        "PYTHONPATH": "/mnt/c/workspace/MCPTool"
      }
    }
  }
}
```

## 🔑 Optional: GitHub Integration

1. **Get a GitHub token**:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Create token with `repo`, `issues`, and `user` permissions

2. **Configure the token**:
   ```bash
   echo "GITHUB_TOKEN=your_token_here" > .env
   ```

3. **Test GitHub features**:
   ```bash
   python -c "
   from src.universal_mcp_server.project_manager import ProjectManager
   pm = ProjectManager('your_token')
   print('GitHub user:', pm.user.login)
   "
   ```

## 🎯 Common Use Cases

### Document Analysis
- "Read this PDF and summarize the key points"
- "Extract data from this Excel file into a database"
- "What's in this Word document?"

### Database Work
- "Create a table to store customer information"
- "Insert some sample data and then query it"
- "Show me all tables in the database"

### File Management
- "Search for all Python files in this directory"
- "What files were modified in the last week?"
- "Browse the project structure"

### Project Management
- "List all my GitHub repositories"
- "Create an issue for this bug"
- "What are the open issues in this project?"

## 🚨 Troubleshooting

### Server won't start?
```bash
# Check Python environment
source venv/bin/activate
python --version

# Test imports
python -c "from src.universal_mcp_server.main import mcp; print('OK')"
```

### Module not found?
```bash
# Ensure you're in the right directory
pwd  # Should show: /mnt/c/workspace/MCPTool

# Check PYTHONPATH
export PYTHONPATH=/mnt/c/workspace/MCPTool
```

### Permission errors?
```bash
# Check file permissions
ls -la
chmod +x venv/bin/activate
```

## 📚 Next Steps

1. **Read the full [README.md](README.md)** for detailed documentation
2. **Try the examples** in the README
3. **Customize configuration** in `.env` file
4. **Add your own tools** by extending the server

## 💡 Pro Tips

- Use **descriptive file names** for better document processing
- **Organize data** in tables for better database querying  
- **Use patterns** in file searches (e.g., "*.py", "test_*")
- **Set up GitHub token** for full project management features

**Happy building! 🚀**