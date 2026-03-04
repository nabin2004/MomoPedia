# 🤝 Contributing to MomoPedia

**Welcome to the MomoPedia community!** We're excited that you're interested in contributing to the world's first AI-powered momo encyclopedia. Whether you're a developer, cultural expert, food enthusiast, or momo lover, there are many ways to get involved.

---

## 🌟 Ways to Contribute

### For Developers
- **Code Contributions**: Enhance AI agents, add features, fix bugs
- **API Development**: Expand the REST API and SDK libraries  
- **Infrastructure**: Improve deployment, monitoring, and scalability
- **Testing**: Add comprehensive test coverage and quality assurance
- **Documentation**: Improve guides, tutorials, and code comments

### For Cultural Experts
- **Content Review**: Validate cultural accuracy and authenticity
- **Regional Expertise**: Provide insights on specific momo traditions
- **Language Support**: Help with translations and localization
- **Cultural Guidelines**: Develop sensitivity guidelines and best practices

### For Food Enthusiasts  
- **Recipe Validation**: Verify traditional preparation methods
- **Regional Variations**: Document local momo styles and customs
- **Historical Research**: Contribute to the cultural heritage documentation
- **Community Outreach**: Help spread awareness about momo culture

### For Everyone
- **Bug Reports**: Identify and report issues
- **Feature Requests**: Suggest improvements and new capabilities
- **Community Support**: Help other users and contributors
- **Feedback**: Share your experience and suggestions

## 🚀 Quick Start

### 1. Set Up Your Development Environment

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/MomoPedia.git
cd MomoPedia

# Set up the upstream remote
git remote add upstream https://github.com/nabin/MomoPedia.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run the Development Setup

```bash
# Start the application
python main.py

# Run tests
pytest

# Run linting
flake8 src/
black src/
isort src/

# Start development server (for API development)
uvicorn momopedia.api:app --reload --port 8000

# Build documentation locally
cd docs && bundle install && bundle exec jekyll serve
```

### 3. Make Your First Contribution

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest`
4. Commit: `git commit -m "Add feature: your feature description"`
5. Push: `git push origin feature/your-feature-name`
6. Create a Pull Request on GitHub

## 🎯 Development Guidelines

### Code Style

We follow Python best practices with these tools:

- **Formatter**: Black (line length: 88)
- **Import Sorting**: isort
- **Linting**: flake8
- **Type Checking**: mypy
- **Pre-commit Hooks**: Automated formatting and checking

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear commit history:

```
feat: add new cultural validation system
fix: resolve quality score calculation bug
docs: update API documentation
test: add tests for reviewer agent
refactor: improve agent architecture
chore: update dependencies
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `build`: Build system changes
- `ci`: CI/CD changes

### Branch Naming

```
feature/ai-agent-improvements
fix/quality-score-bug
docs/api-documentation
test/reviewer-coverage
refactor/monitoring-system
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── agents/            # AI agent tests  
│   ├── quality/           # Quality system tests
│   └── utils/             # Utility function tests
├── integration/           # Integration tests
│   ├── workflow/          # End-to-end workflow tests
│   └── api/               # API endpoint tests
├── fixtures/              # Test data and fixtures
└── conftest.py           # Pytest configuration
```

### Writing Tests

```python
# Example unit test
import pytest
from momopedia.agents import EnhancedAuthorAgent
from momopedia.state import MomoState

class TestAuthorAgent:
    @pytest.fixture
    def author_agent(self):
        return EnhancedAuthorAgent(
            cultural_sensitivity_level="high",
            min_word_count=500
        )
    
    @pytest.fixture
    def sample_state(self):
        return MomoState(
            topic="Traditional Nepali Momos",
            messages=[],
            iteration=0
        )
    
    def test_content_generation(self, author_agent, sample_state):
        """Test that author generates culturally sensitive content."""
        result = author_agent.generate_content(sample_state)
        
        assert result["article"]["title"]
        assert len(result["article"]["content"]) >= 500
        assert result["quality_metrics"]["cultural_accuracy"] >= 0.8
        
    def test_cultural_validation(self, author_agent):
        """Test cultural sensitivity validation."""
        content = "Traditional momos from Nepal..."
        score = author_agent.assess_cultural_accuracy(content, region="Nepal")
        
        assert 0.0 <= score <= 1.0
        
    @pytest.mark.asyncio
    async def test_async_generation(self, author_agent, sample_state):
        """Test asynchronous content generation."""
        result = await author_agent.generate_async(sample_state)
        assert result is not None
```

### Integration Tests

```python
# Example integration test
@pytest.mark.integration
class TestWorkflowIntegration:
    def test_full_article_generation_workflow(self):
        """Test complete article generation from start to finish."""
        initial_state = MomoState(
            topic="Bhutanese Ema Momos: Spice and Tradition",
            next_step="author"
        )
        
        final_state = run_workflow(initial_state)
        
        assert final_state["chair_decision"] in ["ACCEPTED", "REJECTED"]
        if final_state["chair_decision"] == "ACCEPTED":
            assert final_state["final_score"] >= 0.70
            assert final_state["article"]["title"]
            assert len(final_state["article"]["content"]) >= 500
```

### Test Coverage

We aim for:
- **Unit Tests**: 90%+ coverage for core components
- **Integration Tests**: All major workflows
- **Cultural Validation**: All regional configurations
- **API Tests**: All endpoints and error cases

```bash
# Run tests with coverage
pytest --cov=momopedia --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

## 📖 Documentation Standards

### Code Documentation

```python
class EnhancedAuthorAgent:
    """Enhanced AI agent for generating culturally sensitive momo content.
    
    This agent combines web research, cultural awareness, and quality
    self-assessment to produce authentic articles about momo traditions.
    
    Args:
        cultural_sensitivity_level: Level of cultural validation ("low", "medium", "high")
        min_word_count: Minimum word count for generated articles
        research_depth: Depth of web research ("basic", "standard", "comprehensive")
        
    Attributes:
        quality_metrics: Performance tracking for generated content
        cultural_validator: Cultural accuracy assessment component
        
    Example:
        >>> agent = EnhancedAuthorAgent(cultural_sensitivity_level="high")
        >>> state = MomoState(topic="Traditional Tibetan Momos")
        >>> result = agent.generate_content(state)
        >>> print(f"Quality Score: {result['quality_metrics']['overall_score']}")
    """
    
    def generate_content(self, state: MomoState) -> Dict[str, Any]:
        """Generate comprehensive momo article content.
        
        Performs web research, generates culturally sensitive content,
        and provides quality self-assessment metrics.
        
        Args:
            state: Current workflow state with topic and context
            
        Returns:
            Dict containing:
                - article: Generated article with title and content
                - quality_metrics: Self-assessment scores
                - sources: Research citations
                - cultural_notes: Cultural sensitivity observations
                
        Raises:
            ContentGenerationError: When content generation fails
            CulturalValidationError: When cultural standards not met
        """
```

### API Documentation

Use comprehensive docstrings and examples:

```python
@app.post("/api/articles/generate")
async def generate_article(
    request: ArticleGenerationRequest,
    api_key: str = Depends(verify_api_key)
) -> ArticleResponse:
    """Generate a new AI-powered momo article.
    
    Creates authentic, culturally sensitive content about momo traditions
    using our multi-agent AI system.
    
    Args:
        request: Article generation parameters including topic, style, and quality requirements
        api_key: Valid API key for authentication
        
    Returns:
        ArticleResponse: Generated article with quality metrics and metadata
        
    Raises:
        HTTPException: 400 for invalid parameters, 401 for auth errors, 422 for validation errors
        
    Example:
        ```python
        response = await client.post("/api/articles/generate", json={
            "topic": "Traditional Nepali Momos: Cultural Heritage",
            "style": "comprehensive",
            "cultural_focus": "high"
        })
        ```
    """
```

## 🎨 Cultural Sensitivity Guidelines

### Core Principles

1. **Respect and Authenticity**: Represent all cultures with dignity and accuracy
2. **Community Input**: Involve people from represented communities
3. **Source Verification**: Use reliable, culturally authoritative sources
4. **Inclusive Language**: Use terminology preferred by communities
5. **Context Awareness**: Understand historical and cultural context

### Cultural Review Process

1. **Research Phase**: Use authentic cultural sources
2. **Content Review**: Have cultural experts review content
3. **Community Feedback**: Share with community representatives
4. **Iterative Improvement**: Incorporate feedback and refine
5. **Ongoing Monitoring**: Continuously assess cultural accuracy

### Regional Expertise

We welcome experts from:
- **Nepal**: Traditional momo preparation and cultural significance
- **Tibet**: High-altitude variations and Buddhist context
- **Bhutan**: Ema datshi connections and festival traditions  
- **India**: Regional variations (Sikkim, Darjeeling, etc.)
- **Other regions**: Any area with momo traditions

### Cultural Validation Checklist

- [ ] Authentic terminology and pronunciation guides
- [ ] Accurate historical and cultural context
- [ ] Respectful representation of traditions
- [ ] Proper attribution to source communities
- [ ] Sensitivity to sacred or restricted knowledge
- [ ] Inclusive of diverse perspectives within cultures

## 🐛 Bug Reports

### Before Reporting

1. Check [existing issues](https://github.com/nabin/MomoPedia/issues)
2. Search [discussions](https://github.com/nabin/MomoPedia/discussions)
3. Try the latest version
4. Review documentation

### Bug Report Template

```markdown
**Bug Description**
Clear description of what went wrong.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What should have happened.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.2]
- MomoPedia Version: [e.g., 1.2.0]
- API Keys: [Configured/Not Configured]

**Additional Context**
- Error messages
- Screenshots
- Log files
- Configuration details

**Cultural Context (if applicable)**
- Region/culture being discussed
- Cultural accuracy issues
- Sensitivity concerns
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature.

**Problem/Motivation**
What problem does this solve?

**Proposed Solution**
How should this work?

**Cultural Considerations**
Any cultural sensitivity aspects?

**Alternative Solutions**
Other ways to solve this problem?

**Additional Context**
Mockups, examples, related issues.
```

## 🔍 Code Review Process

### Pull Request Guidelines

1. **Clear Description**: Explain what and why
2. **Small Changes**: Keep PRs focused and manageable
3. **Tests Included**: Add tests for new functionality
4. **Documentation**: Update docs for user-facing changes
5. **Cultural Review**: Include cultural experts for content changes

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Cultural sensitivity improvement

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Integration tests updated
- [ ] Cultural validation completed

## Cultural Impact
- [ ] No cultural content affected
- [ ] Cultural expert reviewed changes
- [ ] Community feedback incorporated
- [ ] Sensitivity guidelines followed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or marked as such)
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Maintainer reviews code quality and architecture
3. **Cultural Review**: Cultural expert reviews content changes
4. **Testing**: Manual testing in various environments
5. **Approval**: At least one maintainer approval required
6. **Merge**: Squash and merge with descriptive commit message

## 🏆 Recognition

We value all contributions and recognize them in various ways:

### Contributors Hall of Fame
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Annual contributor spotlight blog posts
- Community recognition in release notes

### Contribution Types
- **Code Contributors**: Development and technical improvements
- **Cultural Advisors**: Cultural accuracy and sensitivity guidance
- **Content Reviewers**: Article validation and quality assurance
- **Community Leaders**: Forum management and user support
- **Translators**: Internationalization and localization

### Special Recognition
- **Cultural Ambassador**: Outstanding cultural guidance
- **Quality Guardian**: Exceptional quality assurance
- **Innovation Leader**: Significant feature contributions
- **Community Hero**: Exceptional community support

## 🗓️ Development Workflow

### Release Cycle

- **Major Releases** (X.0.0): Every 3-4 months with significant features
- **Minor Releases** (X.Y.0): Monthly with new features and improvements  
- **Patch Releases** (X.Y.Z): As needed for bug fixes and security updates

### Development Branches

- **main**: Production-ready code
- **develop**: Integration branch for upcoming release
- **feature/***: Individual feature development
- **hotfix/***: Critical bug fixes
- **release/***: Release preparation

### Issue Labels

- `good first issue`: Great for newcomers
- `help wanted`: Community help appreciated
- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `cultural-sensitivity`: Cultural accuracy needed
- `documentation`: Documentation improvements
- `question`: Further information requested

## 📞 Getting Help

### Communication Channels

- **GitHub Discussions**: General questions and community chat
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time developer communication
- **Email**: cultural-experts@momopedia.org for cultural guidance

### Mentorship Program

New contributors can request mentorship:
- Assigned experienced contributor
- Guided first contribution
- Regular check-ins and support
- Cultural sensitivity training for content contributors

### Office Hours

Weekly virtual office hours for contributors:
- **Time**: Fridays 15:00 UTC
- **Platform**: Discord voice chat
- **Topics**: Development questions, cultural guidance, project direction

## 🎉 Thank You!

Every contribution, no matter how small, helps build MomoPedia into a more comprehensive and culturally accurate resource. We're grateful for your time, expertise, and passion for momo culture.

### First-time Contributors

Welcome! Don't be afraid to make your first contribution. We have a supportive community that will help you succeed. Start with issues labeled `good first issue` and don't hesitate to ask questions.

### Experienced Contributors  

Thank you for your ongoing support! Consider mentoring newcomers, reviewing PRs, or taking on leadership roles in areas that interest you.

---

**Ready to contribute?** 

1. 🍴 [Fork the repository](https://github.com/nabin/MomoPedia/fork)
2. 🌟 Star the project to show your support
3. 💬 Join our [Discord community](https://discord.gg/momopedia)
4. 📖 Check out [good first issues](https://github.com/nabin/MomoPedia/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

*Together, we're building the world's most comprehensive and culturally respectful momo encyclopedia! 🥟✨*