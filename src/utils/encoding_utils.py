"""
Encoding utilities for safe file loading across different systems.
"""
import os
from pathlib import Path
from typing import Optional
import warnings


def safe_load_dotenv(dotenv_path: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Safely load .env file with encoding fallback mechanism.
    
    Tries to load the .env file with UTF-8 encoding first, then falls back to
    other common encodings if UTF-8 fails. This ensures compatibility across
    different operating systems and file encodings.
    
    Args:
        dotenv_path: Path to .env file. If None, searches for .env in current directory.
        verbose: If True, prints warnings when fallback encodings are used.
    
    Returns:
        True if .env was loaded successfully, False otherwise.
    """
    from dotenv import load_dotenv
    
    # Determine .env file path
    if dotenv_path is None:
        dotenv_path = Path.cwd() / '.env'
    else:
        dotenv_path = Path(dotenv_path)
    
    # If file doesn't exist, return False
    if not dotenv_path.exists():
        if verbose:
            warnings.warn(f".env file not found at {dotenv_path}")
        return False
    
    # List of encodings to try, in order of preference
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            # Try to load with current encoding
            load_dotenv(dotenv_path=str(dotenv_path), encoding=encoding)
            
            # If we used a fallback encoding, warn the user
            if encoding != 'utf-8' and verbose:
                warnings.warn(
                    f"Loaded .env file using {encoding} encoding instead of UTF-8. "
                    f"Consider re-saving the file as UTF-8 for better compatibility.",
                    UserWarning
                )
            
            return True
            
        except UnicodeDecodeError:
            # This encoding didn't work, try the next one
            continue
        except Exception as e:
            # Some other error occurred
            if verbose:
                warnings.warn(f"Error loading .env with {encoding}: {e}")
            continue
    
    # If we get here, none of the encodings worked
    if verbose:
        warnings.warn(
            f"Failed to load .env file from {dotenv_path} with any supported encoding. "
            f"Tried: {', '.join(encodings)}",
            UserWarning
        )
    return False


def ensure_utf8_env_file(dotenv_path: Optional[str] = None) -> bool:
    """
    Re-save .env file as UTF-8 without BOM.
    
    This function reads the .env file with encoding detection and re-saves it
    as UTF-8, which ensures compatibility across all systems.
    
    Args:
        dotenv_path: Path to .env file. If None, uses .env in current directory.
    
    Returns:
        True if successful, False otherwise.
    """
    if dotenv_path is None:
        dotenv_path = Path.cwd() / '.env'
    else:
        dotenv_path = Path(dotenv_path)
    
    if not dotenv_path.exists():
        return False
    
    # Try to read with various encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(dotenv_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        return False
    
    # Write back as UTF-8 without BOM
    try:
        with open(dotenv_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False
