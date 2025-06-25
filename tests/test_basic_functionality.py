"""Basic functionality tests for Universal MCP Server components."""

import pytest
import tempfile
import os
from pathlib import Path
import csv

from src.universal_mcp_server.document_reader import DocumentReader
from src.universal_mcp_server.database_connector import DatabaseConnector
from src.universal_mcp_server.file_browser import FileBrowser


class TestDocumentReader:
    """Test the document reader functionality."""
    
    def setup_method(self):
        self.reader = DocumentReader()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_csv_reading(self):
        """Test CSV file reading."""
        csv_file = Path(self.temp_dir) / "test.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['John', '30', 'NYC'])
            writer.writerow(['Jane', '25', 'LA'])
        
        result = self.reader.read_document(str(csv_file))
        assert result['success'] == True
        assert result['content']['type'] == 'csv'
        assert result['content']['summary']['rows'] == 2
        assert len(result['content']['data']) == 2
    
    def test_unsupported_format(self):
        """Test handling of unsupported file formats."""
        with pytest.raises(ValueError, match="Unsupported format"):
            self.reader.read_document("test.unknown", format=".unknown")
    
    def test_nonexistent_file(self):
        """Test handling of non-existent files."""
        with pytest.raises(FileNotFoundError):
            self.reader.read_document("nonexistent.txt")


class TestDatabaseConnector:
    """Test the database connector functionality."""
    
    def setup_method(self):
        self.temp_db = tempfile.mktemp(suffix='.db')
        self.db = DatabaseConnector(self.temp_db)
    
    def teardown_method(self):
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)
    
    def test_create_table(self):
        """Test table creation."""
        result = self.db.execute_query("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        assert result['success'] == True
        assert result['query_type'] == 'CREATE'
    
    def test_insert_and_select(self):
        """Test data insertion and selection."""
        # Create table
        self.db.execute_query("""
            CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)
        """)
        
        # Insert data
        insert_result = self.db.execute_query(
            "INSERT INTO test_table (value) VALUES (?)",
            ['test_value']
        )
        assert insert_result['success'] == True
        assert insert_result['rows_affected'] == 1
        
        # Select data
        select_result = self.db.execute_query("SELECT * FROM test_table")
        assert select_result['success'] == True
        assert select_result['rows_returned'] == 1
        assert select_result['data'][0]['value'] == 'test_value'
    
    def test_list_tables(self):
        """Test table listing functionality."""
        # Create a test table
        self.db.execute_query("CREATE TABLE test_list (id INTEGER)")
        
        result = self.db.list_tables()
        assert result['success'] == True
        assert any(table['name'] == 'test_list' for table in result['tables'])
    
    def test_invalid_sql(self):
        """Test handling of invalid SQL."""
        with pytest.raises(Exception):
            self.db.execute_query("INVALID SQL STATEMENT")


class TestFileBrowser:
    """Test the file browser functionality."""
    
    def setup_method(self):
        self.browser = FileBrowser()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test structure
        (Path(self.temp_dir) / "subdir").mkdir()
        (Path(self.temp_dir) / "test.txt").write_text("test content")
        (Path(self.temp_dir) / "subdir" / "nested.txt").write_text("nested content")
    
    def test_browse_directory(self):
        """Test directory browsing."""
        result = self.browser.browse_directory(self.temp_dir)
        assert result['success'] == True
        assert result['summary']['total_items'] >= 2
        assert result['summary']['files'] >= 1
        assert result['summary']['directories'] >= 1
    
    def test_get_file_info(self):
        """Test file information retrieval."""
        test_file = Path(self.temp_dir) / "test.txt"
        result = self.browser.get_file_info(str(test_file))
        
        assert result['success'] == True
        assert result['file_info']['type'] == 'file'
        assert result['file_info']['name'] == 'test.txt'
        assert result['file_info']['size'] > 0
    
    def test_search_files(self):
        """Test file search functionality."""
        result = self.browser.search_files(self.temp_dir, "*.txt")
        assert result['success'] == True
        assert result['total_matches'] >= 2  # test.txt and nested.txt
    
    def test_nonexistent_directory(self):
        """Test handling of non-existent directories."""
        with pytest.raises(FileNotFoundError):
            self.browser.browse_directory("/nonexistent/directory")


def run_basic_tests():
    """Run basic functionality tests without pytest."""
    print("Running basic functionality tests...")
    
    # Test DocumentReader
    print("Testing DocumentReader...")
    reader = DocumentReader()
    formats = reader.get_supported_formats()
    print(f"  Supported formats: {formats}")
    assert '.csv' in formats
    assert '.pdf' in formats
    print("  ✓ DocumentReader basic test passed")
    
    # Test DatabaseConnector
    print("Testing DatabaseConnector...")
    temp_db = tempfile.mktemp(suffix='.db')
    try:
        db = DatabaseConnector(temp_db)
        result = db.execute_query("SELECT 1 as test")
        assert result['success'] == True
        assert result['data'][0]['test'] == 1
        print("  ✓ DatabaseConnector basic test passed")
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)
    
    # Test FileBrowser
    print("Testing FileBrowser...")
    browser = FileBrowser()
    result = browser.browse_directory(".")
    assert result['success'] == True
    assert result['summary']['total_items'] > 0
    print("  ✓ FileBrowser basic test passed")
    
    print("All basic tests passed! ✓")


if __name__ == "__main__":
    run_basic_tests()