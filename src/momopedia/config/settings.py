"""
MomoPedia Configuration Management
Centralized configuration for all AI agents and system components
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class LLMConfig:
    """Configuration for Language Models"""
    model: str = "xiaomi/mimo-v2-flash:free"
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout: int = 60
    max_retries: int = 3
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    def __post_init__(self):
        # Set API credentials from environment
        self.api_key = self.api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = self.base_url or os.getenv("OPENAI_BASE_URL")

@dataclass
class AgentConfig:
    """Configuration for AI agents"""
    max_iterations: int = 3
    quality_threshold: float = 0.8
    enable_web_search: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    
@dataclass
class AuthorConfig(AgentConfig):
    """Configuration specific to Author agent"""
    research_depth: str = "comprehensive"  # basic, standard, comprehensive
    citation_requirements: int = 3
    min_word_count: int = 500
    max_word_count: int = 2000
    cultural_sensitivity_check: bool = True

@dataclass  
class ReviewerConfig(AgentConfig):
    """Configuration specific to Reviewer agent (Dr. Spicy)"""
    strictness_level: str = "high"  # low, medium, high, extreme
    cultural_accuracy_weight: float = 0.4
    factual_accuracy_weight: float = 0.4
    writing_quality_weight: float = 0.2
    auto_approve_threshold: float = 0.9

@dataclass
class ChairConfig(AgentConfig):
    """Configuration specific to Editorial Chair agent"""
    publication_standards: str = "world-class"
    override_reviewer_threshold: float = 0.7
    final_review_required: bool = True

@dataclass
class WebResearchConfig:
    """Configuration for web research tools"""
    max_results: int = 5
    search_timeout: int = 30
    trusted_domains: list = field(default_factory=lambda: [
        "wikipedia.org",
        "britannica.com", 
        "nationalgeographic.com",
        "smithsonianmag.com",
        "foodandwine.com"
    ])
    excluded_domains: list = field(default_factory=lambda: [
        "pinterest.com",
        "facebook.com",
        "instagram.com"
    ])

@dataclass
class MonitoringConfig:
    """Configuration for monitoring and analytics"""
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_port: int = 8080
    enable_tracing: bool = True
    
@dataclass
class ContentConfig:
    """Configuration for content generation and management"""
    supported_languages: list = field(default_factory=lambda: ["en", "ne", "hi", "zh", "bo"])
    default_language: str = "en"
    enable_multilingual: bool = False
    content_versioning: bool = True
    auto_translate: bool = False

@dataclass
class MomoPediaConfig:
    """Main configuration container for MomoPedia"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    author: AuthorConfig = field(default_factory=AuthorConfig)
    reviewer: ReviewerConfig = field(default_factory=ReviewerConfig)
    chair: ChairConfig = field(default_factory=ChairConfig)
    web_research: WebResearchConfig = field(default_factory=WebResearchConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    
    # Global settings
    environment: str = "development"
    debug: bool = False
    version: str = "1.0.0"
    
    @classmethod
    def from_file(cls, config_path: str) -> 'MomoPediaConfig':
        """Load configuration from JSON file"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
            return cls(**data)
        return cls()
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclasses to dict
        data = {
            'llm': self.llm.__dict__,
            'author': self.author.__dict__,
            'reviewer': self.reviewer.__dict__,
            'chair': self.chair.__dict__,
            'web_research': self.web_research.__dict__,
            'monitoring': self.monitoring.__dict__,
            'content': self.content.__dict__,
            'environment': self.environment,
            'debug': self.debug,
            'version': self.version
        }
        
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate API credentials
        if not self.llm.api_key:
            errors.append("Missing LLM API key")
            
        # Validate thresholds
        if not 0 <= self.reviewer.auto_approve_threshold <= 1:
            errors.append("Reviewer auto-approve threshold must be between 0 and 1")
            
        if not 0 <= self.chair.override_reviewer_threshold <= 1:
            errors.append("Chair override threshold must be between 0 and 1")
            
        # Validate weights sum to 1
        weights_sum = (self.reviewer.cultural_accuracy_weight + 
                      self.reviewer.factual_accuracy_weight + 
                      self.reviewer.writing_quality_weight)
        if abs(weights_sum - 1.0) > 0.01:
            errors.append("Reviewer weight values must sum to 1.0")
            
        return errors
        
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

# Global configuration instance
config = MomoPediaConfig()

# Load from environment-specific config file if it exists
config_dir = Path(__file__).parent
env_config_file = config_dir / f"config.{os.getenv('ENVIRONMENT', 'development')}.json"

if env_config_file.exists():
    config = MomoPediaConfig.from_file(str(env_config_file))
else:
    # Load from default config file
    default_config_file = config_dir / "config.json"
    if default_config_file.exists():
        config = MomoPediaConfig.from_file(str(default_config_file))

# Validate configuration on import
validation_errors = config.validate()
if validation_errors:
    print(f"Configuration validation errors: {validation_errors}")

def get_config() -> MomoPediaConfig:
    """Get the global configuration instance"""
    return config

def update_config(**kwargs) -> None:
    """Update configuration values"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Unknown configuration key '{key}'")

def reset_config() -> None:
    """Reset configuration to defaults"""
    global config
    config = MomoPediaConfig()