"""
Enhanced LLM module with configuration management, error handling, and monitoring
"""

import os
import time
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv

from momopedia.config.settings import get_config
from momopedia.monitoring.system_monitor import get_logger, performance_monitor

# Load environment variables
load_dotenv()

logger = get_logger()

class EnhancedLLM:
    """Enhanced LLM wrapper with monitoring and error handling"""
    
    def __init__(self, model: Optional[str] = None, **kwargs):
        self.config = get_config()
        
        # Use provided model or default from config
        self.model_name = model or self.config.llm.model
        
        # Set up API credentials
        os.environ["OPENAI_API_KEY"] = self.config.llm.api_key or os.getenv("OPENROUTER_API_KEY", "")
        os.environ["OPENAI_BASE_URL"] = self.config.llm.base_url or os.getenv("OPENAI_BASE_URL", "")
        
        # Create LLM instance with configuration
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=kwargs.get('temperature', self.config.llm.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.llm.max_tokens),
            timeout=kwargs.get('timeout', self.config.llm.timeout),
            max_retries=kwargs.get('max_retries', self.config.llm.max_retries)
        )
        
        logger.logger.info(f"Initialized Enhanced LLM with model: {self.model_name}")
    
    @performance_monitor("llm_invoke")
    def invoke(self, messages: List[BaseMessage], **kwargs) -> Any:
        """Invoke LLM with monitoring and error handling"""
        try:
            start_time = time.time()
            
            # Log request details (without sensitive content)
            logger.log_agent_activity(
                "LLM", 
                "invoke_request", 
                {
                    "model": self.model_name,
                    "message_count": len(messages),
                    "kwargs": {k: v for k, v in kwargs.items() if k not in ['messages', 'content']}
                }
            )
            
            # Make the API call
            response = self.llm.invoke(messages, **kwargs)
            
            duration = time.time() - start_time
            
            # Log successful response
            logger.log_performance("llm_invoke", duration, True)
            logger.log_agent_activity(
                "LLM",
                "invoke_success",
                {
                    "duration": duration,
                    "response_type": type(response).__name__
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error details
            logger.log_error(e, {
                "operation": "llm_invoke",
                "model": self.model_name,
                "duration": duration,
                "message_count": len(messages)
            })
            
            # Re-raise with enhanced error message
            error_message = f"LLM invoke failed for model {self.model_name}: {str(e)}"
            logger.logger.error(error_message)
            raise Exception(error_message) from e
    
    def with_structured_output(self, schema):
        """Create structured output LLM with monitoring"""
        structured_llm = self.llm.with_structured_output(schema)
        
        # Wrap the structured LLM to maintain monitoring
        class MonitoredStructuredLLM:
            def __init__(self, base_llm, enhanced_wrapper):
                self.base_llm = base_llm
                self.enhanced_wrapper = enhanced_wrapper
            
            @performance_monitor("structured_llm_invoke")
            def invoke(self, messages, **kwargs):
                try:
                    start_time = time.time()
                    
                    logger.log_agent_activity(
                        "StructuredLLM",
                        "invoke_request",
                        {
                            "model": self.enhanced_wrapper.model_name,
                            "schema": schema.__name__ if hasattr(schema, '__name__') else str(schema),
                            "message_count": len(messages) if isinstance(messages, list) else 1
                        }
                    )
                    
                    response = self.base_llm.invoke(messages, **kwargs)
                    
                    duration = time.time() - start_time
                    logger.log_performance("structured_llm_invoke", duration, True)
                    logger.log_agent_activity(
                        "StructuredLLM",
                        "invoke_success",
                        {"duration": duration, "response_type": type(response).__name__}
                    )
                    
                    return response
                    
                except Exception as e:
                    duration = time.time() - start_time
                    logger.log_error(e, {
                        "operation": "structured_llm_invoke",
                        "model": self.enhanced_wrapper.model_name,
                        "duration": duration,
                        "schema": str(schema)
                    })
                    raise
        
        return MonitoredStructuredLLM(structured_llm, self)
    
    def bind_tools(self, tools: List):
        """Bind tools to LLM with monitoring"""
        tools_llm = self.llm.bind_tools(tools)
        
        # Wrap tools LLM to maintain monitoring
        class MonitoredToolsLLM:
            def __init__(self, base_llm, enhanced_wrapper, tools):
                self.base_llm = base_llm
                self.enhanced_wrapper = enhanced_wrapper
                self.tools = tools
            
            @performance_monitor("tools_llm_invoke")
            def invoke(self, messages, **kwargs):
                try:
                    start_time = time.time()
                    
                    logger.log_agent_activity(
                        "ToolsLLM",
                        "invoke_request",
                        {
                            "model": self.enhanced_wrapper.model_name,
                            "tools_count": len(self.tools),
                            "tool_names": [getattr(tool, 'name', str(tool)) for tool in self.tools]
                        }
                    )
                    
                    response = self.base_llm.invoke(messages, **kwargs)
                    
                    duration = time.time() - start_time
                    logger.log_performance("tools_llm_invoke", duration, True)
                    
                    return response
                    
                except Exception as e:
                    duration = time.time() - start_time
                    logger.log_error(e, {
                        "operation": "tools_llm_invoke",
                        "model": self.enhanced_wrapper.model_name,
                        "duration": duration,
                        "tools": len(self.tools)
                    })
                    raise
            
            def with_structured_output(self, schema):
                """Allow chaining structured output after binding tools"""
                return self.enhanced_wrapper.with_structured_output(schema)
        
        return MonitoredToolsLLM(tools_llm, self, tools)

# Global enhanced LLM instance
_enhanced_llm = None

def get_llm(model: Optional[str] = None, **kwargs) -> EnhancedLLM:
    """
    Get enhanced LLM instance with configuration and monitoring
    
    Args:
        model: Optional model name override
        **kwargs: Additional LLM parameters
        
    Returns:
        Enhanced LLM instance
    """
    global _enhanced_llm
    
    config = get_config()
    
    # Create new instance if none exists or model changed
    requested_model = model or config.llm.model
    
    if _enhanced_llm is None or _enhanced_llm.model_name != requested_model:
        logger.logger.info(f"Creating new Enhanced LLM instance for model: {requested_model}")
        _enhanced_llm = EnhancedLLM(model=requested_model, **kwargs)
    
    return _enhanced_llm

def get_simple_llm(model: Optional[str] = None, **kwargs) -> ChatOpenAI:
    """
    Get basic ChatOpenAI instance for backward compatibility
    
    Args:
        model: Optional model name override  
        **kwargs: Additional LLM parameters
        
    Returns:
        Basic ChatOpenAI instance
    """
    config = get_config()
    
    # Set up credentials
    os.environ["OPENAI_API_KEY"] = config.llm.api_key or os.getenv("OPENROUTER_API_KEY", "")
    os.environ["OPENAI_BASE_URL"] = config.llm.base_url or os.getenv("OPENAI_BASE_URL", "")
    
    return ChatOpenAI(
        model=model or config.llm.model,
        temperature=kwargs.get('temperature', config.llm.temperature),
        max_tokens=kwargs.get('max_tokens', config.llm.max_tokens),
        timeout=kwargs.get('timeout', config.llm.timeout),
        max_retries=kwargs.get('max_retries', config.llm.max_retries)
    )

def validate_llm_configuration() -> Dict[str, Any]:
    """
    Validate LLM configuration and connectivity
    
    Returns:
        Dictionary with validation results
    """
    config = get_config()
    validation_result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "config": {
            "model": config.llm.model,
            "has_api_key": bool(config.llm.api_key),
            "has_base_url": bool(config.llm.base_url),
            "temperature": config.llm.temperature,
            "timeout": config.llm.timeout
        }
    }
    
    # Check API key
    if not config.llm.api_key:
        validation_result["errors"].append("Missing API key")
    
    # Check base URL
    if not config.llm.base_url:
        validation_result["warnings"].append("No base URL specified, using default")
    
    # Test connectivity (optional)
    try:
        llm = get_simple_llm()
        test_response = llm.invoke([{"role": "user", "content": "Hello"}])
        validation_result["valid"] = True
        validation_result["test_response"] = True
    except Exception as e:
        validation_result["errors"].append(f"Connectivity test failed: {str(e)}")
        validation_result["test_response"] = False
    
    return validation_result
