# 🚀 API Documentation

**MomoPedia REST API Reference**

---

## Overview

The MomoPedia API provides programmatic access to our AI-powered momo encyclopedia. Generate authentic, high-quality articles about momo culture, regional variations, recipes, and cultural heritage through simple HTTP requests.

### Base URL
```
Production: https://api.momopedia.org/v1
Development: http://localhost:8000/v1
```

### Authentication

```bash
# Include your API key in the Authorization header
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.momopedia.org/v1/articles
```

Get your API key by [creating an account](https://momopedia.org/signup).

## Quick Start

### Generate Your First Article

```bash
curl -X POST "https://api.momopedia.org/v1/articles/generate" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Traditional Nepali Momos",
    "style": "comprehensive",
    "cultural_focus": "high"
  }'
```

### Python SDK

```python
from momopedia_sdk import MomoPediaClient

client = MomoPediaClient(api_key="YOUR_API_KEY")

# Generate an article
article = client.generate_article(
    topic="Tibetan Momo Traditions in the Himalayas",
    style="comprehensive",
    cultural_focus="high",
    min_quality_score=0.8
)

print(f"Title: {article.title}")
print(f"Quality Score: {article.quality_score}")
```

## API Endpoints

### Articles

#### Generate Article
Create a new AI-generated article about momos.

```http
POST /v1/articles/generate
```

**Request Body**
```json
{
  "topic": "Traditional Nepali Momos: Cultural Heritage and Regional Variations",
  "style": "comprehensive",
  "cultural_focus": "high",
  "min_quality_score": 0.75,
  "include_sources": true,
  "max_word_count": 1500,
  "region_focus": "South Asia"
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | **Yes** | The article topic/title |
| `style` | string | No | Content style: `brief`, `standard`, `comprehensive` |
| `cultural_focus` | string | No | Cultural sensitivity level: `low`, `medium`, `high` |
| `min_quality_score` | float | No | Minimum acceptable quality (0.0-1.0) |
| `include_sources` | boolean | No | Include research citations |
| `max_word_count` | integer | No | Maximum article length |
| `region_focus` | string | No | Geographic focus area |

**Response**
```json
{
  "id": "art_abc123def456",
  "status": "completed",
  "article": {
    "title": "Traditional Nepali Momos: Cultural Heritage and Regional Variations",
    "content": "Momos hold a special place in Nepalese cuisine...",
    "word_count": 1247,
    "quality_score": 0.87,
    "cultural_authenticity": 0.92,
    "sources": [...],
    "metadata": {
      "author_agent": "Enhanced Author v2.1",
      "reviewer": "Dr. Spicy",
      "chair_decision": "ACCEPTED",
      "generation_time": 45.2,
      "revision_count": 1
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "processing_time": 45.2
}
```

#### Get Article Status
Check the status of an article generation request.

```http
GET /v1/articles/{article_id}/status
```

**Response**
```json
{
  "id": "art_abc123def456",
  "status": "processing",
  "progress": {
    "current_step": "reviewer_analysis",
    "completion_percentage": 65,
    "estimated_time_remaining": 23.5
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### List Articles
Retrieve a list of generated articles.

```http
GET /v1/articles?limit=10&offset=0&region=Nepal&min_score=0.8
```

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Number of articles to return (1-100) |
| `offset` | integer | Number of articles to skip |
| `region` | string | Filter by geographic region |
| `min_score` | float | Minimum quality score filter |
| `topic_category` | string | Category filter: `traditional`, `modern`, `fusion` |

**Response**
```json
{
  "articles": [
    {
      "id": "art_abc123",
      "title": "Traditional Nepali Momos",
      "quality_score": 0.87,
      "region": "Nepal",
      "created_at": "2024-01-15T10:30:00Z",
      "word_count": 1247
    }
  ],
  "total": 156,
  "has_more": true
}
```

### Quality Metrics

#### Get Quality Analytics
Retrieve quality metrics and performance data.

```http
GET /v1/quality/analytics?period=30d
```

**Response**
```json
{
  "period": "30d",
  "metrics": {
    "average_quality_score": 0.83,
    "cultural_authenticity_avg": 0.89,
    "total_articles_generated": 43,
    "acceptance_rate": 0.74,
    "revision_rate": 0.26
  },
  "trends": {
    "quality_improvement": 0.05,
    "efficiency_gain": 0.12,
    "cultural_accuracy_trend": "improving"
  },
  "top_regions": [
    {"region": "Nepal", "count": 15, "avg_score": 0.91},
    {"region": "Tibet", "count": 12, "avg_score": 0.88},
    {"region": "Bhutan", "count": 8, "avg_score": 0.85}
  ]
}
```

### Regional Content

#### Get Regional Information
Retrieve information about momo traditions in specific regions.

```http
GET /v1/regions/{region_name}
```

**Response**
```json
{
  "region": "Nepal",
  "cultural_context": {
    "primary_languages": ["Nepali", "Newari"],
    "traditional_styles": ["jhol momo", "kothey momo", "sadeko momo"],
    "cultural_significance": "Festival food, family gatherings",
    "historical_roots": "Tibetan influence via trade routes"
  },
  "articles_available": 23,
  "average_quality_score": 0.89,
  "expert_reviewers": ["Dr. Spicy", "Chef Karma Lama"]
}
```

### Configuration

#### Update Generation Settings
Customize AI behavior for your use case.

```http
PUT /v1/config/generation
```

**Request Body**
```json
{
  "default_style": "comprehensive",
  "cultural_sensitivity": "high",
  "quality_threshold": 0.80,
  "auto_approve_score": 0.85,
  "max_revisions": 3,
  "regional_preferences": {
    "Nepal": {"cultural_weight": 0.9},
    "Tibet": {"historical_focus": true}
  }
}
```

## Webhooks

Subscribe to events in the content generation process.

### Event Types

- `article.generation.started` - Article generation begins
- `article.review.completed` - Review process finishes  
- `article.published` - Article accepted and published
- `article.rejected` - Article rejected after review
- `quality.threshold.exceeded` - High-quality content generated

### Webhook Configuration

```http
POST /v1/webhooks
```

**Request Body**
```json
{
  "url": "https://your-app.com/webhooks/momopedia",
  "events": ["article.published", "article.rejected"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload Example

```json
{
  "event": "article.published",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "article_id": "art_abc123def456",
    "title": "Traditional Nepali Momos",
    "quality_score": 0.87,
    "region": "Nepal"
  }
}
```

## Rate Limits

| Plan | Requests/Hour | Concurrent Generations |
|------|---------------|----------------------|
| Free | 10 | 1 |
| Pro | 100 | 3 |
| Enterprise | 1000 | 10 |

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1705320600
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The topic parameter is required",
    "details": {
      "field": "topic",
      "constraint": "required"
    }
  },
  "request_id": "req_abc123def456"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | API key is invalid or expired |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `VALIDATION_ERROR` | Request parameters are invalid |
| `QUALITY_THRESHOLD_NOT_MET` | Generated content below minimum quality |
| `TOPIC_NOT_SUPPORTED` | Topic outside momo domain |
| `CULTURAL_SENSITIVITY_VIOLATION` | Content violates cultural guidelines |

## SDK Libraries

### Python SDK

```bash
pip install momopedia-sdk
```

```python
from momopedia_sdk import MomoPediaClient, GenerationConfig

client = MomoPediaClient(api_key="YOUR_API_KEY")

# Custom generation configuration
config = GenerationConfig(
    style="comprehensive",
    cultural_focus="high",
    min_quality_score=0.8,
    include_sources=True
)

# Generate article
article = client.generate_article(
    topic="Sikkimese Momo Innovations",
    config=config
)

# Async support
async with MomoPediaAsyncClient(api_key="YOUR_API_KEY") as client:
    article = await client.generate_article("Bhutanese Ema Momos")
```

### JavaScript/Node.js SDK

```bash
npm install momopedia-sdk
```

```javascript
const { MomoPediaClient } = require('momopedia-sdk');

const client = new MomoPediaClient({
  apiKey: 'YOUR_API_KEY'
});

// Generate article
const article = await client.generateArticle({
  topic: 'Korean-Style Mandu Variations',
  style: 'comprehensive',
  culturalFocus: 'high'
});

console.log(`Generated: ${article.title}`);
console.log(`Quality Score: ${article.qualityScore}`);
```

### Go SDK

```bash
go get github.com/momopedia/go-sdk
```

```go
package main

import (
    "context"
    "fmt"
    "github.com/momopedia/go-sdk"
)

func main() {
    client := momopedia.NewClient("YOUR_API_KEY")
    
    article, err := client.GenerateArticle(context.Background(), &momopedia.GenerationRequest{
        Topic: "Japanese Gyoza: From Momo to Modern Dumpling",
        Style: "comprehensive",
        CulturalFocus: "high",
    })
    
    if err != nil {
        panic(err)
    }
    
    fmt.Printf("Generated: %s\n", article.Title)
}
```

## Advanced Usage

### Batch Processing

Generate multiple articles in a single request:

```http
POST /v1/articles/batch
```

```json
{
  "requests": [
    {
      "topic": "Ladakhi High-Altitude Momos",
      "style": "comprehensive"
    },
    {
      "topic": "Modern Vegan Momo Innovations", 
      "style": "standard"
    }
  ],
  "callback_url": "https://your-app.com/batch-complete"
}
```

### Custom Reviewer Assignment

Request specific regional expert reviewers:

```json
{
  "topic": "Traditional Sherpa Momos",
  "preferred_reviewer": "himalayan_expert",
  "cultural_validation": "required"
}
```

### Quality Monitoring

Set up quality alerts and monitoring:

```http
POST /v1/quality/alerts
```

```json
{
  "conditions": {
    "quality_score_below": 0.7,
    "cultural_authenticity_below": 0.8
  },
  "notification_url": "https://your-app.com/quality-alerts"
}
```

## Changelog

### v1.2.0 (Latest)
- Added batch processing endpoints
- Enhanced cultural validation
- Improved quality metrics
- Regional expert reviewer assignment

### v1.1.0
- Webhook support
- Quality analytics API
- Rate limiting improvements
- SDK libraries released

### v1.0.0
- Initial API release
- Core article generation
- Basic quality metrics

## Support

- **Documentation**: [https://docs.momopedia.org](https://docs.momopedia.org)
- **Support Email**: api-support@momopedia.org
- **Discord Community**: [MomoPedia Developers](https://discord.gg/momopedia)
- **GitHub Issues**: [Report bugs or request features](https://github.com/nabin/MomoPedia/issues)

---

**Happy Coding! 🥟✨**

*For more examples and tutorials, visit our [Developer Portal](https://developers.momopedia.org)*