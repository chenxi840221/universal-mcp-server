"""Database connector module for SQLite operations."""

import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """SQLite database connector with enhanced functionality."""
    
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database and create metadata table
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create system tables."""
        with self._get_connection() as conn:
            # Create a metadata table for storing table descriptions and other info
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _mcp_metadata (
                    table_name TEXT PRIMARY KEY,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create a query history table for tracking executed queries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _mcp_query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    parameters TEXT,
                    execution_time REAL,
                    rows_affected INTEGER,
                    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Optional[List] = None) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            params: Optional parameters for the query
        
        Returns:
            Query results and execution information
        """
        params = params or []
        start_time = __import__('time').time()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                execution_time = __import__('time').time() - start_time
                
                # Determine if this is a SELECT query or a modification query
                query_type = query.strip().upper().split()[0]
                
                if query_type == "SELECT":
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    result = {
                        "success": True,
                        "query_type": "SELECT",
                        "rows_returned": len(rows),
                        "columns": columns,
                        "data": [dict(row) for row in rows],
                        "execution_time": execution_time
                    }
                    
                    # Log the query
                    self._log_query(query, params, execution_time, len(rows), True)
                    
                else:
                    # For INSERT, UPDATE, DELETE, etc.
                    conn.commit()
                    rows_affected = cursor.rowcount
                    
                    result = {
                        "success": True,
                        "query_type": query_type,
                        "rows_affected": rows_affected,
                        "execution_time": execution_time
                    }
                    
                    # For INSERT, return the last inserted row ID if applicable
                    if query_type == "INSERT" and cursor.lastrowid:
                        result["last_insert_id"] = cursor.lastrowid
                    
                    # Log the query
                    self._log_query(query, params, execution_time, rows_affected, True)
                
                return result
        
        except Exception as e:
            execution_time = __import__('time').time() - start_time
            error_msg = str(e)
            
            # Log the failed query
            self._log_query(query, params, execution_time, 0, False, error_msg)
            
            logger.error(f"Database query failed: {error_msg}")
            raise e
    
    def _log_query(self, query: str, params: List, execution_time: float, 
                   rows_affected: int, success: bool, error_message: str = None):
        """Log query execution to history table."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO _mcp_query_history 
                    (query, parameters, execution_time, rows_affected, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    query,
                    json.dumps(params) if params else None,
                    execution_time,
                    rows_affected,
                    success,
                    error_message
                ])
                conn.commit()
        except Exception as e:
            # Don't let logging errors break the main operation
            logger.warning(f"Failed to log query: {e}")
    
    def list_tables(self) -> Dict[str, Any]:
        """List all tables in the database with metadata."""
        try:
            with self._get_connection() as conn:
                # Get all user tables (excluding system tables)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '_mcp_%'
                    ORDER BY name
                """)
                
                user_tables = [row[0] for row in cursor.fetchall()]
                
                # Get table metadata
                tables_info = []
                for table_name in user_tables:
                    table_info = self._get_table_info(conn, table_name)
                    tables_info.append(table_info)
                
                # Get database statistics
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                total_tables = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "total_tables": len(user_tables),
                    "system_tables": total_tables - len(user_tables),
                    "tables": tables_info,
                    "database_path": str(self.database_path)
                }
        
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise e
    
    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a table."""
        try:
            with self._get_connection() as conn:
                # Check if table exists
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, [table_name])
                
                if not cursor.fetchone():
                    raise ValueError(f"Table '{table_name}' does not exist")
                
                table_info = self._get_table_info(conn, table_name, detailed=True)
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                table_info["sample_data"] = {
                    "columns": columns,
                    "rows": [dict(row) for row in sample_rows]
                }
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                table_info["row_count"] = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "table_info": table_info
                }
        
        except Exception as e:
            logger.error(f"Error describing table {table_name}: {e}")
            raise e
    
    def _get_table_info(self, conn, table_name: str, detailed: bool = False) -> Dict[str, Any]:
        """Get information about a table."""
        cursor = conn.cursor()
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        column_info = []
        for col in columns:
            col_data = {
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "default_value": col[4],
                "primary_key": bool(col[5])
            }
            column_info.append(col_data)
        
        table_info = {
            "name": table_name,
            "columns": column_info,
            "column_count": len(column_info)
        }
        
        if detailed:
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            table_info["indexes"] = [
                {
                    "name": idx[1],
                    "unique": bool(idx[2]),
                    "origin": idx[3]
                }
                for idx in indexes
            ]
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            table_info["foreign_keys"] = [
                {
                    "id": fk[0],
                    "sequence": fk[1],
                    "table": fk[2],
                    "from_column": fk[3],
                    "to_column": fk[4],
                    "on_update": fk[5],
                    "on_delete": fk[6]
                }
                for fk in foreign_keys
            ]
        
        # Get metadata if available
        try:
            cursor.execute("SELECT description FROM _mcp_metadata WHERE table_name=?", [table_name])
            metadata_row = cursor.fetchone()
            if metadata_row:
                table_info["description"] = metadata_row[0]
        except:
            pass  # Metadata table might not exist or be accessible
        
        return table_info
    
    def create_table_from_data(self, table_name: str, data: List[Dict], 
                             description: str = None) -> Dict[str, Any]:
        """
        Create a table from a list of dictionaries.
        
        Args:
            table_name: Name of the table to create
            data: List of dictionaries representing rows
            description: Optional table description
        
        Returns:
            Creation result
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not table_name.replace('_', '').isalnum():
            raise ValueError("Table name must be alphanumeric (underscores allowed)")
        
        try:
            # Infer column types from the first few rows
            columns = self._infer_columns(data[:10])  # Use first 10 rows for type inference
            
            # Create table
            column_defs = []
            for col_name, col_type in columns.items():
                column_defs.append(f"{col_name} {col_type}")
            
            create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
            
            with self._get_connection() as conn:
                conn.execute(create_sql)
                
                # Insert data
                if data:
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns.keys())}) VALUES ({placeholders})"
                    
                    for row in data:
                        values = [row.get(col, None) for col in columns.keys()]
                        conn.execute(insert_sql, values)
                
                # Add metadata
                if description:
                    conn.execute("""
                        INSERT OR REPLACE INTO _mcp_metadata (table_name, description)
                        VALUES (?, ?)
                    """, [table_name, description])
                
                conn.commit()
            
            return {
                "success": True,
                "table_name": table_name,
                "rows_inserted": len(data),
                "columns": columns
            }
        
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            raise e
    
    def _infer_columns(self, sample_data: List[Dict]) -> Dict[str, str]:
        """Infer column types from sample data."""
        columns = {}
        
        # Get all column names from all sample rows
        all_columns = set()
        for row in sample_data:
            all_columns.update(row.keys())
        
        # Infer type for each column
        for col_name in all_columns:
            # Clean column name
            clean_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(col_name))
            if not clean_name[0].isalpha():
                clean_name = 'col_' + clean_name
            
            # Get sample values for this column
            values = [row.get(col_name) for row in sample_data if row.get(col_name) is not None]
            
            if not values:
                columns[clean_name] = "TEXT"
                continue
            
            # Determine type based on values
            if all(isinstance(v, bool) for v in values):
                columns[clean_name] = "BOOLEAN"
            elif all(isinstance(v, int) for v in values):
                columns[clean_name] = "INTEGER"
            elif all(isinstance(v, (int, float)) for v in values):
                columns[clean_name] = "REAL"
            else:
                columns[clean_name] = "TEXT"
        
        return columns
    
    def get_query_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent query execution history."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT query, parameters, execution_time, rows_affected, 
                           executed_at, success, error_message
                    FROM _mcp_query_history
                    ORDER BY executed_at DESC
                    LIMIT ?
                """, [limit])
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        "query": row[0],
                        "parameters": json.loads(row[1]) if row[1] else None,
                        "execution_time": row[2],
                        "rows_affected": row[3],
                        "executed_at": row[4],
                        "success": bool(row[5]),
                        "error_message": row[6]
                    })
                
                return {
                    "success": True,
                    "history": history
                }
        
        except Exception as e:
            logger.error(f"Error getting query history: {e}")
            raise e