"""
Enhanced Author Agent with advanced monitoring, quality control, and content generation
"""

import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from momopedia.state import MomoState, ArticleSchema
from momopedia.prompts.personas import AUTHOR_PROMPT
from momopedia.tools.web_research import search_momo_facts
from momopedia.llm import get_llm
from momopedia.config.settings import get_config
from momopedia.monitoring.system_monitor import agent_monitor, get_logger, get_metrics_collector
from momopedia.utils.content_quality import validate_content, enhance_content

logger = get_logger()
metrics_collector = get_metrics_collector()
config = get_config()

class EnhancedAuthorAgent:
    """Enhanced Author Agent with comprehensive content generation capabilities"""
    
    def __init__(self):
        self.llm = get_llm()
        self.tools = [search_momo_facts]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.structured_llm = self.llm_with_tools.with_structured_output(ArticleSchema)
        
        logger.log_agent_activity("Author", "agent_initialized", {
            "tools_count": len(self.tools),
            "config": {
                "research_depth": config.author.research_depth,
                "min_word_count": config.author.min_word_count,
                "max_word_count": config.author.max_word_count,
                "cultural_sensitivity": config.author.cultural_sensitivity_check
            }
        })
    
    @agent_monitor("Author")
    def generate_content(self, state: MomoState) -> Dict[str, Any]:
        """Generate comprehensive momo article content"""
        try:
            # Extract topic from messages or state
            topic = self._extract_topic(state)
            
            logger.log_agent_activity("Author", "content_generation_start", {
                "topic": topic,
                "iteration": state.get("iteration", 0),
                "has_feedback": bool(state.get("feedback"))
            })
            
            # Prepare messages with context
            messages = self._prepare_messages(state, topic)
            
            # Generate initial content
            response = self.structured_llm.invoke(messages)
            
            # Validate and enhance content
            enhanced_response = self._process_response(response, topic, state)
            
            # Calculate quality metrics
            quality_score = self._calculate_quality_score(enhanced_response, topic)
            
            # Record metrics
            metrics_collector.record_content_event(
                "article_created",
                topic=topic,
                word_count=len(enhanced_response.get('content', '').split()),
                citations=len(enhanced_response.get('citations', [])),
                quality_score=quality_score.overall
            )
            
            logger.log_agent_activity("Author", "content_generation_complete", {
                "topic": topic,
                "quality_score": quality_score.overall,
                "word_count": len(enhanced_response.get('content', '').split()),
                "citations": len(enhanced_response.get('citations', []))
            })
            
            return {
                "article": enhanced_response,
                "messages": [f"Author generated comprehensive article: '{enhanced_response.get('title', topic)}'"],
                "next_step": "reviewer",
                "iteration": state.get("iteration", 0) + 1,
                "quality_score": quality_score.overall,
                "content_metrics": {
                    "word_count": len(enhanced_response.get('content', '').split()),
                    "citations": len(enhanced_response.get('citations', [])),
                    "quality_breakdown": quality_score.to_dict()
                }
            }
            
        except Exception as e:
            logger.log_error(e, {
                "agent": "Author",
                "operation": "generate_content",
                "topic": topic,
                "iteration": state.get("iteration", 0)
            })
            
            # Return error state
            return {
                "messages": [f"Author agent encountered error: {str(e)}"],
                "next_step": "chair",  # Send to chair for error handling
                "error": True,
                "error_message": str(e)
            }
    
    def _extract_topic(self, state: MomoState) -> str:
        """Extract topic from state messages or use default"""
        # Try to extract from messages
        for message in state.get("messages", []):
            if isinstance(message, dict) and "topic" in str(message).lower():
                return str(message)
            elif isinstance(message, str) and any(word in message.lower() for word in ["momo", "dumpling"]):
                return message
        
        # Check if there's a topic field in state
        if hasattr(state, 'topic'):
            return state.topic
        
        # Default topic
        return "Traditional Momo Varieties and Cultural Significance"
    
    def _prepare_messages(self, state: MomoState, topic: str) -> List[BaseMessage]:
        """Prepare enhanced messages for content generation"""
        messages = [SystemMessage(content=AUTHOR_PROMPT)]
        
        # Add topic-specific instructions
        topic_instruction = self._create_topic_instruction(topic, state)
        messages.append(HumanMessage(content=topic_instruction))
        
        # Add previous messages with context
        for message in state.get("messages", []):
            if isinstance(message, str):
                messages.append(HumanMessage(content=message))
            elif isinstance(message, dict) and "content" in message:
                messages.append(HumanMessage(content=message["content"]))
        
        # Add feedback incorporation if this is a revision
        if state.get("feedback") and state.get("iteration", 0) > 0:
            feedback_instruction = self._create_feedback_instruction(state["feedback"])
            messages.append(HumanMessage(content=feedback_instruction))
        
        return messages
    
    def _create_topic_instruction(self, topic: str, state: MomoState) -> str:
        """Create comprehensive topic-specific instruction"""
        instruction = f"""
        Please write a comprehensive, culturally authentic article about: {topic}

        Requirements:
        - Word count: {config.author.min_word_count}-{config.author.max_word_count} words
        - Include at least {config.author.citation_requirements} reliable citations
        - Research depth: {config.author.research_depth}
        - Cultural sensitivity: {'Required' if config.author.cultural_sensitivity_check else 'Recommended'}
        
        Structure your article with these sections:
        1. Introduction - Cultural context and significance
        2. Historical Origins - When, where, and how momos developed
        3. Traditional Preparation - Authentic methods and techniques
        4. Regional Variations - Different styles across cultures
        5. Ingredients - Traditional and modern variations
        6. Cultural Significance - Role in festivals, daily life, traditions
        7. Modern Adaptations - How momos have evolved
        
        Ensure your content is:
        ✓ Culturally respectful and accurate
        ✓ Well-researched with proper citations
        ✓ Engaging and accessible to general readers
        ✓ Comprehensive but concise
        ✓ Rich in cultural context and historical detail
        
        Use the web search tool to gather authentic information about regional variations, 
        traditional recipes, and cultural practices.
        
        Return your response in the required JSON format with title, content, and citations.
        """
        
        return instruction.strip()
    
    def _create_feedback_instruction(self, feedback: List[str]) -> str:
        """Create instruction for incorporating reviewer feedback"""
        feedback_text = "\n".join(f"- {f}" for f in feedback)
        
        instruction = f"""
        IMPORTANT: This is a REVISION based on reviewer feedback. Please address the following concerns:

        Reviewer Feedback:
        {feedback_text}

        Please revise your article to specifically address each point above while maintaining 
        the overall quality and cultural authenticity. Make sure your revised content directly 
        responds to the feedback provided.
        """
        
        return instruction
    
    def _process_response(self, response: Dict[str, Any], topic: str, state: MomoState) -> Dict[str, Any]:
        """Process and enhance the LLM response"""
        # Ensure response has the expected structure
        if not isinstance(response, dict):
            logger.logger.warning(f"Unexpected response type: {type(response)}")
            response = {"title": topic, "content": str(response), "citations": []}
        
        # Extract and clean content
        title = response.get('title', topic)
        content = response.get('content', '')
        citations = response.get('citations', [])
        
        # Enhance content quality
        if content:
            enhanced_content, suggestions = enhance_content(
                content, 
                {"region": self._detect_region(topic), "topic": topic}
            )
            
            # Log enhancement suggestions
            if suggestions:
                logger.log_agent_activity("Author", "content_enhancement", {
                    "topic": topic,
                    "suggestions_count": len(suggestions),
                    "suggestions": suggestions
                })
        else:
            enhanced_content = content
        
        # Ensure minimum citations
        if len(citations) < config.author.citation_requirements:
            logger.logger.warning(f"Insufficient citations: {len(citations)} < {config.author.citation_requirements}")
        
        return {
            "title": title,
            "content": enhanced_content,
            "citations": citations,
            "version": float(state.get("iteration", 0) + 1)
        }
    
    def _detect_region(self, topic: str) -> str:
        """Detect geographic region from topic"""
        topic_lower = topic.lower()
        
        regions = {
            'nepal': ['nepal', 'nepali', 'kathmandu', 'himalaya'],
            'tibet': ['tibet', 'tibetan', 'lhasa'],
            'india': ['india', 'indian', 'darjeeling', 'sikkim'],
            'china': ['china', 'chinese', 'dim sum'],
            'mongolia': ['mongolia', 'mongolian']
        }
        
        for region, keywords in regions.items():
            if any(keyword in topic_lower for keyword in keywords):
                return region
        
        return 'general'
    
    def _calculate_quality_score(self, content_dict: Dict[str, Any], topic: str) -> Any:
        """Calculate comprehensive quality score for generated content"""
        content = content_dict.get('content', '')
        metadata = {
            'region': self._detect_region(topic),
            'topic': topic,
            'citations': len(content_dict.get('citations', []))
        }
        
        return validate_content(content, metadata)

# Create global agent instance
author_agent = EnhancedAuthorAgent()

@agent_monitor("Author")
def author_node(state: MomoState) -> Dict[str, Any]:
    """Main author node function - enhanced version"""
    return author_agent.generate_content(state)