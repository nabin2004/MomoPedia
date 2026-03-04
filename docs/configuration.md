# ⚙️ Configuration Guide

**Customizing MomoPedia's AI System**

---

## Overview

MomoPedia provides extensive configuration options to tailor the AI behavior, quality standards, and system performance to your specific needs. This guide covers all configuration aspects from basic settings to advanced customizations.

## Configuration Files

### Main Configuration Structure

```
/config/
├── settings.py          # Core application settings
├── agents/             
│   ├── author.yaml     # Author agent configuration
│   ├── reviewer.yaml   # Reviewer agent configuration
│   └── chair.yaml      # Editorial chair configuration
├── quality/
│   ├── metrics.yaml    # Quality scoring configuration
│   └── thresholds.yaml # Acceptance criteria
├── environments/
│   ├── development.env # Dev environment settings
│   ├── staging.env     # Staging environment
│   └── production.env  # Production environment
└── monitoring/
    ├── logging.yaml    # Logging configuration
    └── metrics.yaml    # Monitoring settings
```

## Core Settings

### Application Configuration

```python
# src/momopedia/config/settings.py
from pydantic import BaseSettings, Field
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # API Keys
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")
    
    # Database
    database_url: str = Field("sqlite:///./momopedia.db", env="DATABASE_URL")
    database_pool_size: int = Field(5, env="DATABASE_POOL_SIZE")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    cache_ttl: int = Field(3600, env="CACHE_TTL")  # 1 hour
    
    # AI Configuration
    default_model: str = Field("anthropic/claude-3-sonnet", env="DEFAULT_MODEL")
    max_tokens: int = Field(4000, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    
    # Quality Control
    min_quality_score: float = Field(0.70, env="MIN_QUALITY_SCORE")
    auto_approve_threshold: float = Field(0.85, env="AUTO_APPROVE_THRESHOLD")
    max_revisions: int = Field(3, env="MAX_REVISIONS")
    
    # Performance
    max_concurrent_generations: int = Field(5, env="MAX_CONCURRENT_GENERATIONS")
    generation_timeout: int = Field(300, env="GENERATION_TIMEOUT")  # 5 minutes
    
    # Monitoring
    enable_monitoring: bool = Field(True, env="ENABLE_MONITORING")
    metrics_port: int = Field(9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

### Environment Variables

Create a `.env` file in your project root:

```env
# Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# API Keys (Required)
OPENROUTER_API_KEY=your_openrouter_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/momopedia
DATABASE_POOL_SIZE=10

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=1800

# AI Model Configuration
DEFAULT_MODEL=anthropic/claude-3-sonnet
MAX_TOKENS=4000
TEMPERATURE=0.7

# Quality Control
MIN_QUALITY_SCORE=0.70
AUTO_APPROVE_THRESHOLD=0.85
MAX_REVISIONS=3

# Performance Tuning
MAX_CONCURRENT_GENERATIONS=5
GENERATION_TIMEOUT=300

# Monitoring
ENABLE_MONITORING=true
METRICS_PORT=9090
```

## Agent Configuration

### Author Agent Settings

```yaml
# config/agents/author.yaml
author:
  # Model Configuration
  model: "anthropic/claude-3-sonnet"
  temperature: 0.7
  max_tokens: 3000
  
  # Content Settings
  min_word_count: 500
  max_word_count: 2000
  target_word_count: 1200
  
  # Research Configuration
  web_research:
    enabled: true
    max_sources: 10
    search_depth: "comprehensive"  # basic, standard, comprehensive
    source_verification: true
    
  # Cultural Sensitivity
  cultural_awareness:
    enabled: true
    sensitivity_level: "high"  # low, medium, high
    cultural_consultant_mode: false
    require_cultural_validation: true
    
  # Quality Self-Assessment
  self_assessment:
    enabled: true
    completeness_check: true
    factual_verification: true
    citation_validation: true
    
  # Writing Style
  style:
    tone: "informative_friendly"  # academic, professional, friendly, informative_friendly
    audience: "general"  # academic, professional, general
    include_personal_anecdotes: false
    use_regional_terminology: true
    
  # Specializations by Region
  regional_expertise:
    nepal:
      cultural_weight: 0.95
      historical_focus: true
      traditional_recipes: true
    tibet:
      altitude_considerations: true
      buddhist_context: true
      yak_products: true
    bhutan:
      ema_datshi_variations: true
      festival_connections: true
      organic_focus: true
```

### Reviewer Agent (Dr. Spicy) Settings

```yaml
# config/agents/reviewer.yaml
reviewer:
  # Personality Configuration
  name: "Dr. Spicy"
  personality:
    strictness_level: "high"  # low, medium, high, very_high
    feedback_style: "constructive_critical"
    cultural_sensitivity: "maximum"
    humor_level: "subtle"
    
  # Review Criteria Weights
  scoring_weights:
    cultural_authenticity: 0.30
    factual_accuracy: 0.25
    writing_quality: 0.20
    completeness: 0.15
    citation_quality: 0.10
    
  # Quality Thresholds
  thresholds:
    auto_approve: 0.85
    acceptable: 0.70
    needs_revision: 0.50
    reject: 0.30
    
  # Review Process
  review_process:
    detailed_feedback: true
    specific_examples: true
    improvement_suggestions: true
    cultural_notes: true
    fact_checking: true
    source_verification: true
    
  # Regional Expertise
  expertise_areas:
    - "South Asian cuisine"
    - "Tibetan food culture"
    - "Himalayan traditions"
    - "Dumpling varieties worldwide"
    - "Cultural food practices"
    
  # Feedback Templates
  feedback_templates:
    cultural_issue: "This section doesn't accurately represent {culture}. Consider {suggestion}."
    factual_error: "The claim about {topic} needs verification. Sources suggest {correction}."
    writing_improvement: "This paragraph could be clearer. Try {suggestion}."
    missing_content: "Important aspects missing: {missing_items}."
```

### Editorial Chair Settings

```yaml
# config/agents/chair.yaml
editorial_chair:
  # Decision Making
  decision_criteria:
    min_acceptance_score: 0.75
    override_threshold: 0.90  # Can override reviewer rejection
    strategic_alignment_weight: 0.20
    
  # Revision Management
  revision_policy:
    max_revisions_per_article: 3
    escalation_threshold: 0.60
    final_decision_score: 0.65
    
  # Editorial Standards
  editorial_priorities:
    - cultural_authenticity
    - factual_accuracy
    - reader_engagement
    - educational_value
    - cultural_diversity
    
  # Content Strategy
  content_strategy:
    regional_balance: true
    traditional_vs_modern_ratio: 0.7  # 70% traditional, 30% modern
    difficulty_distribution:
      beginner: 0.40
      intermediate: 0.40
      advanced: 0.20
      
  # Publication Standards
  publication_standards:
    minimum_sources: 3
    cultural_validation_required: true
    fact_check_verification: true
    readability_score: 0.70
```

## Quality Control Configuration

### Quality Metrics Settings

```yaml
# config/quality/metrics.yaml
quality_metrics:
  # Scoring System
  scoring_system:
    scale: "0-1"  # 0-1, 0-10, 0-100
    precision: 2  # decimal places
    
  # Cultural Authenticity (30% weight)
  cultural_authenticity:
    weight: 0.30
    factors:
      terminology_accuracy: 0.30
      cultural_context: 0.25
      respectful_representation: 0.25
      traditional_knowledge: 0.20
    
  # Factual Accuracy (25% weight)
  factual_accuracy:
    weight: 0.25
    factors:
      verifiable_claims: 0.40
      source_reliability: 0.30
      historical_accuracy: 0.30
      
  # Writing Quality (20% weight)
  writing_quality:
    weight: 0.20
    factors:
      clarity: 0.30
      engagement: 0.25
      structure: 0.25
      grammar: 0.20
      
  # Completeness (15% weight)
  completeness:
    weight: 0.15
    factors:
      topic_coverage: 0.40
      depth_of_information: 0.30
      balanced_perspective: 0.30
      
  # Citation Quality (10% weight)
  citation_quality:
    weight: 0.10
    factors:
      source_diversity: 0.35
      authority: 0.35
      recency: 0.30

# Quality Improvement Tracking
improvement_tracking:
  enabled: true
  track_over_time: true
  benchmark_comparisons: true
  individual_metric_trends: true
```

### Quality Thresholds

```yaml
# config/quality/thresholds.yaml
quality_thresholds:
  # Overall Score Thresholds
  overall:
    excellent: 0.90
    good: 0.80
    acceptable: 0.70
    needs_improvement: 0.60
    unacceptable: 0.50
    
  # Dimension-Specific Thresholds
  cultural_authenticity:
    minimum_acceptable: 0.75
    preferred: 0.85
    excellent: 0.95
    
  factual_accuracy:
    minimum_acceptable: 0.80
    preferred: 0.90
    excellent: 0.95
    
  writing_quality:
    minimum_acceptable: 0.65
    preferred: 0.75
    excellent: 0.85
    
  # Regional Variations (stricter for sensitive topics)
  regional_overrides:
    tibet:
      cultural_authenticity: 0.85  # Higher standard
    nepal:
      factual_accuracy: 0.85
    bhutan:
      cultural_authenticity: 0.80
      
  # Content Type Variations
  content_type_overrides:
    traditional_recipes:
      cultural_authenticity: 0.90
      factual_accuracy: 0.85
    historical_articles:
      factual_accuracy: 0.90
      citation_quality: 0.80
    modern_variations:
      writing_quality: 0.80
      engagement: 0.75
```

## Performance Configuration

### System Performance Settings

```python
# config/performance.py
PERFORMANCE_CONFIG = {
    # Concurrency Settings
    "max_concurrent_generations": 5,
    "agent_pool_size": {
        "author": 3,
        "reviewer": 2,
        "chair": 1
    },
    
    # Timeout Settings
    "timeouts": {
        "article_generation": 300,  # 5 minutes
        "review_process": 180,      # 3 minutes
        "chair_decision": 60,       # 1 minute
        "web_research": 120         # 2 minutes
    },
    
    # Queue Management
    "queue_settings": {
        "max_queue_size": 100,
        "priority_levels": 3,
        "batch_processing": True,
        "batch_size": 5
    },
    
    # Caching Configuration
    "caching": {
        "enabled": True,
        "ttl_seconds": 3600,       # 1 hour
        "max_cache_size_mb": 500,
        "cache_article_results": True,
        "cache_research_results": True
    },
    
    # Memory Management
    "memory": {
        "max_memory_per_agent_mb": 512,
        "gc_frequency": 10,         # Every 10 operations
        "memory_threshold": 0.85    # 85% memory usage
    }
}
```

### Database Performance

```yaml
# config/database.yaml
database:
  connection_pool:
    size: 10
    max_overflow: 20
    timeout: 30
    recycle: 3600
    
  query_optimization:
    enable_query_cache: true
    slow_query_threshold: 1.0  # seconds
    explain_analyze: false
    
  maintenance:
    auto_vacuum: true
    analyze_threshold: 0.1
    vacuum_threshold: 0.2
```

## Monitoring Configuration

### Logging Settings

```yaml
# config/monitoring/logging.yaml
logging:
  version: 1
  disable_existing_loggers: false
  
  formatters:
    detailed:
      format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    json:
      class: 'pythonjsonlogger.jsonlogger.JsonFormatter'
      format: '%(asctime)s %(name)s %(levelname)s %(message)s'
      
  handlers:
    console:
      class: 'logging.StreamHandler'
      level: 'INFO'
      formatter: 'detailed'
      
    file:
      class: 'logging.handlers.RotatingFileHandler'
      filename: '/var/log/momopedia/app.log'
      maxBytes: 10485760  # 10MB
      backupCount: 5
      level: 'DEBUG'
      formatter: 'json'
      
    error_file:
      class: 'logging.handlers.RotatingFileHandler'
      filename: '/var/log/momopedia/error.log'
      maxBytes: 10485760
      backupCount: 5
      level: 'ERROR'
      formatter: 'json'
      
  loggers:
    momopedia:
      level: 'DEBUG'
      handlers: ['console', 'file', 'error_file']
      propagate: false
      
    agents:
      level: 'INFO'
      handlers: ['file']
      propagate: false
      
    quality:
      level: 'DEBUG'
      handlers: ['file']
      propagate: false
```

### Metrics Configuration

```yaml
# config/monitoring/metrics.yaml
metrics:
  # Prometheus Configuration
  prometheus:
    enabled: true
    port: 9090
    path: '/metrics'
    
  # Custom Metrics
  custom_metrics:
    - name: 'articles_generated_total'
      type: 'counter'
      description: 'Total number of articles generated'
      labels: ['agent_type', 'region', 'quality_level']
      
    - name: 'quality_score_histogram'
      type: 'histogram'
      description: 'Distribution of quality scores'
      buckets: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
      
    - name: 'generation_duration_seconds'
      type: 'histogram'
      description: 'Time taken for article generation'
      buckets: [1, 5, 10, 30, 60, 120, 300]
      
  # Alert Rules
  alerts:
    - name: 'high_error_rate'
      condition: 'rate(errors_total[5m]) > 0.1'
      severity: 'warning'
      
    - name: 'low_quality_trend'
      condition: 'avg_over_time(quality_score[1h]) < 0.7'
      severity: 'critical'
```

## Regional Customization

### Creating Regional Profiles

```python
# config/regions.py
REGIONAL_CONFIGS = {
    "nepal": {
        "cultural_weight": 0.95,
        "mandatory_elements": [
            "mention_of_traditional_preparation",
            "cultural_context",
            "festival_associations"
        ],
        "preferred_sources": [
            "nepali_cultural_institutions",
            "local_food_historians",
            "traditional_cookbooks"
        ],
        "language_considerations": {
            "use_nepali_terms": True,
            "pronunciation_guides": True,
            "cultural_sensitivity_high": True
        }
    },
    
    "tibet": {
        "cultural_weight": 0.90,
        "mandatory_elements": [
            "buddhist_context_when_relevant",
            "high_altitude_considerations",
            "traditional_ingredients"
        ],
        "environmental_factors": {
            "altitude_effects": True,
            "seasonal_availability": True,
            "yak_products_prominence": True
        }
    },
    
    "bhutan": {
        "cultural_weight": 0.85,
        "mandatory_elements": [
            "organic_emphasis",
            "festival_connections",
            "royal_cuisine_notes"
        ],
        "special_requirements": {
            "emphasize_sustainability": True,
            "mention_gross_national_happiness": False,
            "traditional_vs_modern_balance": 0.8
        }
    }
}
```

## Advanced Configuration

### Custom Agent Personalities

```python
# config/custom_agents.py
from momopedia.agents import EnhancedReviewerAgent

# Create specialized reviewer for different regions
def create_regional_reviewer(region: str):
    regional_configs = {
        "nepal": {
            "name": "Dr. Karma Sherpa",
            "expertise": ["Nepali cuisine", "Himalayan culture"],
            "cultural_background": "Nepali",
            "strictness_level": "high",
            "personality_traits": {
                "emphasizes_traditional_methods": True,
                "values_cultural_accuracy": 0.95,
                "prefers_detailed_citations": True
            }
        },
        
        "tibet": {
            "name": "Lama Tenzin",
            "expertise": ["Tibetan cuisine", "Buddhist food culture"],
            "cultural_background": "Tibetan",
            "strictness_level": "very_high",
            "personality_traits": {
                "Buddhist_context_awareness": True,
                "high_altitude_expertise": True,
                "traditional_ingredient_focus": True
            }
        }
    }
    
    config = regional_configs.get(region, regional_configs["nepal"])
    return EnhancedReviewerAgent(**config)
```

### Workflow Customization

```python
# config/workflows.py
WORKFLOW_CONFIGS = {
    "standard": {
        "steps": ["author", "reviewer", "chair"],
        "revision_loops": 3,
        "quality_gates": [0.70, 0.80, 0.85]
    },
    
    "cultural_sensitive": {
        "steps": ["author", "cultural_expert", "reviewer", "chair"],
        "pre_generation_research": True,
        "cultural_validation_required": True,
        "min_cultural_score": 0.90
    },
    
    "fast_track": {
        "steps": ["author", "reviewer"],
        "auto_approve_threshold": 0.80,
        "max_iterations": 2,
        "skip_minor_revisions": True
    },
    
    "premium": {
        "steps": ["research", "author", "fact_checker", "reviewer", "cultural_expert", "chair"],
        "comprehensive_research": True,
        "multiple_reviewers": True,
        "final_editorial_review": True
    }
}
```

## Configuration Management

### Dynamic Configuration Updates

```python
# Dynamic configuration management
from momopedia.config import ConfigManager

config_manager = ConfigManager()

# Update configuration at runtime
config_manager.update_agent_config("author", {
    "cultural_sensitivity_level": "maximum",
    "min_word_count": 1000
})

# Environment-specific overrides
config_manager.set_environment_override("production", {
    "quality_thresholds": {
        "overall_minimum": 0.80,
        "cultural_authenticity_minimum": 0.85
    }
})

# Temporary configuration changes
with config_manager.temporary_override({"max_revisions": 5}):
    # Generate article with increased revision limit
    article = generate_article(topic)
```

### Configuration Validation

```python
# config/validation.py
from pydantic import BaseModel, validator
from typing import Dict, Any

class AgentConfig(BaseModel):
    temperature: float
    max_tokens: int
    cultural_sensitivity_level: str
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @validator('cultural_sensitivity_level')
    def validate_cultural_sensitivity(cls, v):
        if v not in ['low', 'medium', 'high', 'maximum']:
            raise ValueError('Invalid cultural sensitivity level')
        return v

class QualityThresholds(BaseModel):
    minimum_acceptable: float
    preferred: float
    excellent: float
    
    @validator('*')
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Scores must be between 0.0 and 1.0')
        return v
```

## Migration & Backup

### Configuration Migration

```bash
# Backup current configuration
cp -r config/ config_backup_$(date +%Y%m%d)/

# Migrate to new version
python scripts/migrate_config.py --from=v1.0 --to=v1.1

# Validate migrated configuration
python scripts/validate_config.py config/
```

### Version Control

```bash
# Track configuration changes
git add config/
git commit -m "Update quality thresholds for better cultural accuracy"

# Create configuration branches for different deployments
git checkout -b config/production
git checkout -b config/staging
git checkout -b config/development
```

---

**Configuration Best Practices**

1. **Start with defaults** and gradually customize
2. **Test changes** in development environment first
3. **Version control** all configuration changes
4. **Document** any custom modifications
5. **Monitor** system performance after changes
6. **Backup** configurations before major updates

*For help with specific configurations, check our [Support Resources](../README.md#support--contact)*