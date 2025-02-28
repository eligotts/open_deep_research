import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Hardcoded path for logs
LOGS_DIR = "/Users/eligottlieb/Documents/open_deep_research/src/open_deep_research/logs"

class NewsletterLogger:
    """A simplified logging system for the newsletter generation process that focuses on LLM interactions."""
    
    _instance = None
    
    @classmethod
    def initialize_new_logger(cls) -> 'NewsletterLogger':
        """Create a new logger instance with a fresh log file."""
        cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_current_logger(cls) -> Optional['NewsletterLogger']:
        """Get the current logger instance if it exists."""
        return cls._instance
    
    def __init__(self):
        """Initialize the logger with the hardcoded logs directory."""
        self.log_dir = Path(LOGS_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a unique log file name using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"newsletter_generation_{timestamp}.log"
        
        # Initialize the log file with a header
        print(f"\n{'='*80}\nNEWSLETTER GENERATION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*80}\n")
        self._write_log_entry({
            "type": "initialization",
            "timestamp": self._get_timestamp(),
            "message": "Newsletter generation process started"
        })
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def _write_log_entry(self, entry: Dict[str, Any]) -> None:
        """Write a log entry to the log file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_llm_interaction(self, 
                          prompt: str, 
                          response: Any, 
                          context: Optional[str] = None) -> None:
        """Log an interaction with an LLM with clean console output."""
        # Create a clean, readable console output
        node_info = f"[NODE: {context}]" if context else "[UNKNOWN NODE]"
        
        print(f"\n{'-'*80}")
        print(f"{node_info} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'-'*80}")
        
        # Print a truncated version of the prompt (first 500 chars)
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        print(f"\nPROMPT PREVIEW:\n{prompt_preview}\n")
        
        # Format the response based on its type
        if isinstance(response, dict):
            try:
                # Try to format as JSON for better readability
                response_str = json.dumps(response, indent=2)
                print(f"RESPONSE (JSON):\n{response_str}\n")
            except:
                # Fall back to string representation
                print(f"RESPONSE (DICT):\n{response}\n")
        elif hasattr(response, 'model_dump'):
            # Handle Pydantic models
            try:
                response_str = json.dumps(response.model_dump(), indent=2)
                print(f"RESPONSE (PYDANTIC):\n{response_str}\n")
            except:
                print(f"RESPONSE (OBJECT):\n{response}\n")
        else:
            # Default string representation
            print(f"RESPONSE:\n{response}\n")
        
        # Log to file
        entry = {
            "type": "llm_interaction",
            "timestamp": self._get_timestamp(),
            "node": context,
            "prompt": prompt,
            "response": str(response)
        }
        self._write_log_entry(entry)
    
    def log_web_search(self, 
                      queries: List[str], 
                      results: Any,
                      search_api: str) -> None:
        """Log web search queries and results with clean console output."""
        # Create a clean, readable console output
        print(f"\n{'-'*80}")
        print(f"[WEB SEARCH: {search_api}] - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'-'*80}")
        
        # Print the queries
        print(f"\nQUERIES:")
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
        
        # Print a summary of results
        if isinstance(results, list):
            print(f"\nRESULTS SUMMARY: {len(results)} results retrieved")
        else:
            print(f"\nRESULTS RETRIEVED")
        
        # Log to file
        entry = {
            "type": "web_search",
            "timestamp": self._get_timestamp(),
            "search_api": search_api,
            "queries": queries,
            "results": str(results)
        }
        self._write_log_entry(entry)
    
    def log_state_update(self, 
                        state_name: str,
                        state_data: Dict[str, Any],
                        node_name: Optional[str] = None) -> None:
        """Log updates to the newsletter state."""
        # Only print a minimal notification to console
        print(f"\n[STATE UPDATE: {state_name}] from node {node_name or 'unknown'}")
        
        # Log full details to file
        entry = {
            "type": "state_update",
            "timestamp": self._get_timestamp(),
            "state_name": state_name,
            "node_name": node_name,
            "state_data": state_data
        }
        self._write_log_entry(entry)
    
    def log_execution_item(self, 
                         item_type: str,
                         item_id: str,
                         description: str,
                         status: str,
                         output: Optional[str] = None) -> None:
        """Log information about execution items with minimal console output."""
        # Print a simple notification
        print(f"\n[EXECUTION ITEM: {item_type}] {item_id} - Status: {status}")
        
        # Log full details to file
        entry = {
            "type": "execution_item",
            "timestamp": self._get_timestamp(),
            "item_type": item_type,
            "item_id": item_id,
            "description": description,
            "status": status,
            "output": output
        }
        self._write_log_entry(entry)
    
    def log_error(self, 
                 error: Exception,
                 context: Optional[str] = None) -> None:
        """Log error information with prominent console output."""
        # Create a very visible error message
        print(f"\n{'!'*80}")
        print(f"ERROR in {context or 'unknown context'}: {type(error).__name__} - {str(error)}")
        print(f"{'!'*80}\n")
        
        # Log to file
        entry = {
            "type": "error",
            "timestamp": self._get_timestamp(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self._write_log_entry(entry)
    
    def log_template_update(self, 
                          template: Any,
                          reason: Optional[str] = None,
                          node_name: Optional[str] = None) -> None:
        """Log updates to the newsletter template with minimal console output."""
        # Print a simple notification
        node_info = f"[NODE: {node_name}]" if node_name else ""
        print(f"\n[TEMPLATE UPDATE] {node_info} {reason or ''}")
        
        # Log to file
        entry = {
            "type": "template_update",
            "timestamp": self._get_timestamp(),
            "template": str(template),
            "reason": reason,
            "node_name": node_name
        }
        self._write_log_entry(entry)
    
    def log_tool_call(self,
                     tool_name: str,
                     tool_args: Any,
                     tool_response: Any,
                     context: Optional[str] = None) -> None:
        """Log a tool call and its response with clean console output."""
        # Create a clean, readable console output
        print(f"\n{'-'*80}")
        print(f"[TOOL CALL: {tool_name}] - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'-'*80}")
        
        # Print the tool arguments
        if isinstance(tool_args, dict):
            try:
                args_str = json.dumps(tool_args, indent=2)
                print(f"\nTOOL ARGS (JSON):\n{args_str}\n")
            except:
                print(f"\nTOOL ARGS:\n{tool_args}\n")
        else:
            print(f"\nTOOL ARGS:\n{tool_args}\n")
        
        # Print a preview of the response
        response_preview = str(tool_response)
        if len(response_preview) > 500:
            response_preview = response_preview[:500] + "..."
        print(f"TOOL RESPONSE PREVIEW:\n{response_preview}\n")
        
        # Log to file
        entry = {
            "type": "tool_call",
            "timestamp": self._get_timestamp(),
            "tool_name": tool_name,
            "tool_args": str(tool_args),
            "tool_response": str(tool_response),
            "context": context
        }
        self._write_log_entry(entry) 