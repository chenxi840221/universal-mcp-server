"""Enhanced file browser module for advanced file system operations."""

import os
import stat
import logging
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib
import mimetypes

logger = logging.getLogger(__name__)


class FileBrowser:
    """Enhanced file browser with advanced file system operations."""
    
    def __init__(self):
        # Initialize mimetypes
        mimetypes.init()
    
    def browse_directory(self, path: str = ".", include_hidden: bool = False, 
                        max_depth: int = 1) -> Dict[str, Any]:
        """
        Browse and list directory contents with enhanced information.
        
        Args:
            path: Directory path to browse
            include_hidden: Include hidden files and directories
            max_depth: Maximum depth for recursive listing
        
        Returns:
            Directory listing with file information
        """
        try:
            path = Path(path).resolve()
            
            if not path.exists():
                raise FileNotFoundError(f"Path does not exist: {path}")
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            
            result = {
                "success": True,
                "path": str(path),
                "items": [],
                "summary": {
                    "total_items": 0,
                    "directories": 0,
                    "files": 0,
                    "total_size": 0
                }
            }
            
            items = self._scan_directory(path, include_hidden, max_depth, 0)
            result["items"] = items
            
            # Calculate summary
            for item in items:
                result["summary"]["total_items"] += 1
                if item["type"] == "directory":
                    result["summary"]["directories"] += 1
                else:
                    result["summary"]["files"] += 1
                    result["summary"]["total_size"] += item.get("size", 0)
            
            return result
        
        except Exception as e:
            logger.error(f"Error browsing directory {path}: {e}")
            raise e
    
    def _scan_directory(self, path: Path, include_hidden: bool, 
                       max_depth: int, current_depth: int) -> List[Dict[str, Any]]:
        """Recursively scan directory contents."""
        items = []
        
        try:
            for item_path in path.iterdir():
                # Skip hidden files if not requested
                if not include_hidden and item_path.name.startswith('.'):
                    continue
                
                try:
                    item_info = self._get_item_info(item_path)
                    
                    # If it's a directory and we haven't reached max depth, recurse
                    if (item_path.is_dir() and current_depth < max_depth - 1):
                        item_info["children"] = self._scan_directory(
                            item_path, include_hidden, max_depth, current_depth + 1
                        )
                        item_info["child_count"] = len(item_info["children"])
                    
                    items.append(item_info)
                
                except (PermissionError, OSError) as e:
                    # Add item with error info if we can't access it
                    items.append({
                        "name": item_path.name,
                        "path": str(item_path),
                        "error": f"Access denied: {e}",
                        "type": "unknown"
                    })
        
        except PermissionError as e:
            logger.warning(f"Permission denied accessing directory {path}: {e}")
        
        return sorted(items, key=lambda x: (x.get("type", "unknown"), x.get("name", "")))
    
    def _get_item_info(self, path: Path) -> Dict[str, Any]:
        """Get detailed information about a file or directory."""
        try:
            path_stat = path.stat()
            
            item_info = {
                "name": path.name,
                "path": str(path),
                "type": "directory" if path.is_dir() else "file",
                "size": path_stat.st_size,
                "permissions": self._get_permissions(path_stat.st_mode),
                "owner_uid": path_stat.st_uid,
                "group_gid": path_stat.st_gid,
                "created": datetime.fromtimestamp(path_stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(path_stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(path_stat.st_atime).isoformat()
            }
            
            # Add file-specific information
            if path.is_file():
                item_info.update({
                    "extension": path.suffix.lower(),
                    "mime_type": mimetypes.guess_type(str(path))[0],
                    "size_human": self._format_size(path_stat.st_size)
                })
                
                # Add file hash for small files (< 10MB)
                if path_stat.st_size < 10 * 1024 * 1024:
                    try:
                        item_info["md5_hash"] = self._calculate_md5(path)
                    except Exception:
                        pass  # Don't fail if hash calculation fails
            
            # Add directory-specific information
            elif path.is_dir():
                try:
                    # Count items in directory (non-recursive)
                    item_count = sum(1 for _ in path.iterdir())
                    item_info["item_count"] = item_count
                except PermissionError:
                    item_info["item_count"] = None
                    item_info["access_error"] = "Permission denied"
            
            return item_info
        
        except Exception as e:
            return {
                "name": path.name,
                "path": str(path),
                "error": str(e),
                "type": "unknown"
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory.
        
        Args:
            file_path: Path to the file or directory
        
        Returns:
            Detailed file information
        """
        try:
            path = Path(file_path).resolve()
            
            if not path.exists():
                raise FileNotFoundError(f"Path does not exist: {path}")
            
            item_info = self._get_item_info(path)
            
            # Add additional information
            item_info.update({
                "absolute_path": str(path),
                "parent_directory": str(path.parent),
                "is_symlink": path.is_symlink(),
                "is_readable": os.access(path, os.R_OK),
                "is_writable": os.access(path, os.W_OK),
                "is_executable": os.access(path, os.X_OK)
            })
            
            # Add symlink target if it's a symlink
            if path.is_symlink():
                try:
                    item_info["symlink_target"] = str(path.readlink())
                except Exception as e:
                    item_info["symlink_error"] = str(e)
            
            # Add content preview for text files
            if path.is_file() and item_info.get("mime_type", "").startswith("text/"):
                try:
                    if path.stat().st_size < 1024 * 1024:  # Less than 1MB
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            preview = f.read(1000)  # First 1000 characters
                            item_info["content_preview"] = preview
                            item_info["line_count"] = preview.count('\n') + 1
                except Exception:
                    pass  # Don't fail if preview can't be generated
            
            return {
                "success": True,
                "file_info": item_info
            }
        
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise e
    
    def search_files(self, directory: str = ".", pattern: str = "*", 
                    include_content: bool = False) -> Dict[str, Any]:
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
            directory = Path(directory).resolve()
            
            if not directory.exists():
                raise FileNotFoundError(f"Directory does not exist: {directory}")
            
            if not directory.is_dir():
                raise ValueError(f"Path is not a directory: {directory}")
            
            matches = []
            content_pattern = None
            
            # If pattern contains content search syntax (pattern:content)
            if ':' in pattern and include_content:
                file_pattern, content_pattern = pattern.split(':', 1)
            else:
                file_pattern = pattern
            
            # Search for files
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    # Check filename pattern
                    if fnmatch.fnmatch(file_path.name, file_pattern):
                        match_info = {
                            "path": str(file_path),
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "match_type": "filename"
                        }
                        
                        # Search file content if requested
                        if content_pattern and self._is_text_file(file_path):
                            content_matches = self._search_file_content(file_path, content_pattern)
                            if content_matches:
                                match_info["content_matches"] = content_matches
                                match_info["match_type"] = "content"
                        
                        matches.append(match_info)
            
            return {
                "success": True,
                "directory": str(directory),
                "pattern": pattern,
                "total_matches": len(matches),
                "matches": matches
            }
        
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            raise e
    
    def _search_file_content(self, file_path: Path, pattern: str) -> List[Dict[str, Any]]:
        """Search for pattern within file content."""
        matches = []
        
        try:
            # Skip large files (> 10MB)
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return matches
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.lower() in line.lower():
                        matches.append({
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "match_position": line.lower().find(pattern.lower())
                        })
                        
                        # Limit matches per file
                        if len(matches) >= 50:
                            break
        
        except Exception as e:
            logger.warning(f"Error searching content in {file_path}: {e}")
        
        return matches
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely a text file."""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type.startswith('text/'):
                return True
            
            # Check common text file extensions
            text_extensions = {
                '.txt', '.md', '.py', '.js', '.html', '.css', '.json', 
                '.xml', '.yaml', '.yml', '.csv', '.log', '.cfg', '.conf',
                '.ini', '.sh', '.bat', '.sql', '.r', '.java', '.c', '.cpp',
                '.h', '.hpp', '.php', '.rb', '.go', '.rs', '.ts', '.vue'
            }
            
            if file_path.suffix.lower() in text_extensions:
                return True
            
            # Check file content (first 1024 bytes)
            if file_path.stat().st_size > 1024 * 1024:  # Skip large files
                return False
            
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
                # Check if content is mostly printable ASCII
                try:
                    sample.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        
        except Exception:
            return False
    
    def _get_permissions(self, mode: int) -> Dict[str, Any]:
        """Get human-readable permission information."""
        permissions = {
            "octal": oct(stat.S_IMODE(mode)),
            "symbolic": stat.filemode(mode),
            "owner": {
                "read": bool(mode & stat.S_IRUSR),
                "write": bool(mode & stat.S_IWUSR),
                "execute": bool(mode & stat.S_IXUSR)
            },
            "group": {
                "read": bool(mode & stat.S_IRGRP),
                "write": bool(mode & stat.S_IWGRP),
                "execute": bool(mode & stat.S_IXGRP)
            },
            "others": {
                "read": bool(mode & stat.S_IROTH),
                "write": bool(mode & stat.S_IWOTH),
                "execute": bool(mode & stat.S_IXOTH)
            }
        }
        return permissions
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a new directory.
        
        Args:
            path: Path for the new directory
        
        Returns:
            Creation result
        """
        try:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=False)
            
            return {
                "success": True,
                "path": str(path),
                "message": "Directory created successfully"
            }
        
        except FileExistsError:
            return {
                "success": False,
                "path": str(path),
                "error": "Directory already exists"
            }
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            raise e
    
    def delete_item(self, path: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            force: Force deletion of non-empty directories
        
        Returns:
            Deletion result
        """
        try:
            path = Path(path)
            
            if not path.exists():
                raise FileNotFoundError(f"Path does not exist: {path}")
            
            if path.is_file():
                path.unlink()
                return {
                    "success": True,
                    "path": str(path),
                    "type": "file",
                    "message": "File deleted successfully"
                }
            
            elif path.is_dir():
                if force:
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.rmdir()  # Only works for empty directories
                
                return {
                    "success": True,
                    "path": str(path),
                    "type": "directory",
                    "message": "Directory deleted successfully"
                }
        
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            raise e