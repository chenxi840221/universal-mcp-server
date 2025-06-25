"""Simple test script for Universal MCP Server."""

import tempfile
import os
from src.universal_mcp_server.document_reader import DocumentReader
from src.universal_mcp_server.database_connector import DatabaseConnector
from src.universal_mcp_server.file_browser import FileBrowser

def test_all_components():
    """Test all major components."""
    print("🧪 Testing Universal MCP Server Components...")
    
    # Test DocumentReader
    print("\n📖 Testing DocumentReader...")
    reader = DocumentReader()
    formats = reader.get_supported_formats()
    print(f"   Supported formats: {formats}")
    
    # Test with existing CSV file
    if os.path.exists('test_data.csv'):
        result = reader.read_document('test_data.csv')
        print(f"   CSV reading: {'✓' if result['success'] else '✗'}")
        if result['success']:
            print(f"   Found {result['content']['summary']['rows']} data rows")
    
    # Test DatabaseConnector
    print("\n🗄️  Testing DatabaseConnector...")
    temp_db = tempfile.mktemp(suffix='.db')
    try:
        db = DatabaseConnector(temp_db)
        
        # Test basic query
        result = db.execute_query("SELECT 1 as test_value")
        print(f"   Basic query: {'✓' if result['success'] else '✗'}")
        
        # Test table creation
        create_result = db.execute_query("""
            CREATE TABLE sample (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        """)
        print(f"   Table creation: {'✓' if create_result['success'] else '✗'}")
        
        # Test data insertion
        insert_result = db.execute_query(
            "INSERT INTO sample (name, value) VALUES (?, ?)",
            ['test_item', 42.5]
        )
        print(f"   Data insertion: {'✓' if insert_result['success'] else '✗'}")
        
        # Test data selection
        select_result = db.execute_query("SELECT * FROM sample")
        print(f"   Data selection: {'✓' if select_result['success'] else '✗'}")
        if select_result['success']:
            print(f"   Retrieved {select_result['rows_returned']} rows")
        
        # Test table listing
        tables_result = db.list_tables()
        print(f"   Table listing: {'✓' if tables_result['success'] else '✗'}")
        if tables_result['success']:
            print(f"   Found {tables_result['total_tables']} user tables")
            
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)
    
    # Test FileBrowser
    print("\n📁 Testing FileBrowser...")
    browser = FileBrowser()
    
    # Browse current directory
    browse_result = browser.browse_directory(".", max_depth=1)
    print(f"   Directory browsing: {'✓' if browse_result['success'] else '✗'}")
    if browse_result['success']:
        summary = browse_result['summary']
        print(f"   Found {summary['total_items']} items ({summary['files']} files, {summary['directories']} dirs)")
    
    # Get file info
    if os.path.exists('test_data.csv'):
        info_result = browser.get_file_info('test_data.csv')
        print(f"   File info: {'✓' if info_result['success'] else '✗'}")
    
    # Search files
    search_result = browser.search_files(".", "*.py")
    print(f"   File search: {'✓' if search_result['success'] else '✗'}")
    if search_result['success']:
        print(f"   Found {search_result['total_matches']} Python files")
    
    print("\n🎉 All component tests completed!")

if __name__ == "__main__":
    test_all_components()