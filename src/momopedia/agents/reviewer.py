"""
Enhanced Reviewer Agent (Dr. Spicy) with advanced quality assessment and monitoring
"""

import json
from typing import Dict, Any, List, Union
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from momopedia.state import MomoState 
from momopedia.prompts.personas import REVIEWER_PROMPT
from momopedia.llm import get_llm
from momopedia.config.settings import get_config
from momopedia.monitoring.system_monitor import agent_monitor, get_logger, get_metrics_collector
from momopedia.utils.content_quality import validate_content

logger = get_logger()
metrics_collector = get_metrics_collector()
config = get_config()

class DetailedReviewResult(BaseModel):
    """Enhanced review result with detailed scoring"""
    decision: str = Field(description="'revise', 'approve', or 'reject'")
    feedback: Union[str, List[str]] = Field(description="Detailed feedback for improvements")
    cultural_score: float = Field(description="Cultural authenticity score (0-1)", default=0.0)
    accuracy_score: float = Field(description="Factual accuracy score (0-1)", default=0.0)
    quality_score: float = Field(description="Writing quality score (0-1)", default=0.0)
    citation_score: float = Field(description="Citation quality score (0-1)", default=0.0)
    overall_score: float = Field(description="Overall article score (0-1)", default=0.0)
    confidence: float = Field(description="Reviewer confidence in assessment (0-1)", default=0.0)
    revision_priority: str = Field(description="Priority level for revisions", default="medium")
    
class EnhancedReviewerAgent:
    """Enhanced Dr. Spicy - The Most Discerning Momo Critic in the AI World"""
    
    def __init__(self):
        self.llm = get_llm()
        self.structured_reviewer = self.llm.with_structured_output(DetailedReviewResult)
        
        logger.log_agent_activity("Reviewer", "agent_initialized", {
            "strictness_level": config.reviewer.strictness_level,
            "weights": {
                "cultural": config.reviewer.cultural_accuracy_weight,
                "factual": config.reviewer.factual_accuracy_weight,
                "writing": config.reviewer.writing_quality_weight
            },
            "auto_approve_threshold": config.reviewer.auto_approve_threshold
        })
    
    @agent_monitor("Reviewer")
    def review_content(self, state: MomoState) -> Dict[str, Any]:
        """Comprehensive content review by Dr. Spicy"""
        try:
            article_content = state.get("article", {})
            iteration = state.get("iteration", 0)
            
            logger.log_agent_activity("Reviewer", "review_start", {
                "iteration": iteration,
                "article_title": article_content.get('title', 'Unknown'),
                "content_length": len(str(article_content.get('content', ''))),
                "strictness": config.reviewer.strictness_level
            })
            
            # Validate content structure
            if not article_content or not isinstance(article_content, dict):
                return self._handle_invalid_content(state)
            
            # Perform automated quality assessment
            quality_assessment = self._automated_quality_check(article_content)
            
            # Prepare messages for Dr. Spicy
            messages = self._prepare_review_messages(article_content, iteration, quality_assessment)
            
            # Get Dr. Spicy's review
            review_response = self.structured_reviewer.invoke(messages)
            
            # Process and enhance the review
            processed_review = self._process_review_response(
                review_response, 
                quality_assessment, 
                article_content,
                iteration
            )
            
            # Determine next step based on review
            next_step = self._determine_next_step(processed_review, iteration)
            
            # Record metrics
            self._record_review_metrics(processed_review, article_content, next_step)
            
            logger.log_agent_activity("Reviewer", "review_complete", {
                "decision": processed_review["decision"],
                "overall_score": processed_review["overall_score"],
                "next_step": next_step,
                "confidence": processed_review["confidence"]
            })
            
            return {
                "feedback": [processed_review["feedback"]] if isinstance(processed_review["feedback"], str) else processed_review["feedback"],
                "messages": [self._create_review_message(processed_review)],
                "next_step": next_step,
                "review_scores": {
                    "cultural": processed_review["cultural_score"],
                    "accuracy": processed_review["accuracy_score"],
                    "quality": processed_review["quality_score"],
                    "citation": processed_review["citation_score"],
                    "overall": processed_review["overall_score"]
                },
                "reviewer_confidence": processed_review["confidence"],
                "revision_priority": processed_review["revision_priority"]
            }
            
        except Exception as e:
            logger.log_error(e, {
                "agent": "Reviewer",
                "operation": "review_content",
                "iteration": state.get("iteration", 0)
            })
            
            return {
                "feedback": [f"Reviewer error: {str(e)}"],
                "messages": [f"Dr. Spicy encountered an error during review: {str(e)}"],
                "next_step": "chair",
                "error": True
            }
    
    def _handle_invalid_content(self, state: MomoState) -> Dict[str, Any]:
        """Handle cases where article content is invalid"""
        logger.logger.warning("Received invalid article content for review")
        
        return {
            "feedback": ["CRITICAL: No valid article content received for review. Author must generate proper content."],
            "messages": ["Dr. Spicy REJECTS: No article content provided!"],
            "next_step": "author",
            "review_scores": {"overall": 0.0},
            "reviewer_confidence": 1.0,
            "revision_priority": "critical"
        }
    
    def _automated_quality_check(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated quality assessment before AI review"""
        content = article.get('content', '')
        title = article.get('title', '')
        citations = article.get('citations', [])
        
        # Use our content quality validator
        quality_score = validate_content(content, {
            'title': title,
            'citations_count': len(citations)
        })
        
        return {
            "automated_scores": quality_score.to_dict(),
            "word_count": len(content.split()) if content else 0,
            "citation_count": len(citations),
            "has_title": bool(title),
            "content_length": len(content) if content else 0
        }
    
    def _prepare_review_messages(self, article: Dict[str, Any], iteration: int, quality_assessment: Dict[str, Any]) -> List[BaseMessage]:
        """Prepare comprehensive review messages for Dr. Spicy"""
        
        # Enhanced system prompt based on configuration
        enhanced_prompt = f"""
        {REVIEWER_PROMPT}
        
        ENHANCED REVIEW PARAMETERS:
        - Strictness Level: {config.reviewer.strictness_level.upper()}
        - Cultural Weight: {config.reviewer.cultural_accuracy_weight}
        - Factual Weight: {config.reviewer.factual_accuracy_weight} 
        - Writing Weight: {config.reviewer.writing_quality_weight}
        - Auto-Approve Threshold: {config.reviewer.auto_approve_threshold}
        
        ITERATION CONTEXT: This is revision #{iteration}
        
        AUTOMATED PRE-ASSESSMENT:
        - Word Count: {quality_assessment['word_count']}
        - Citations: {quality_assessment['citation_count']}
        - Automated Quality Score: {quality_assessment['automated_scores']['overall']:.2f}
        
        Focus your review on areas where the automated assessment shows weaknesses.
        Be extra strict on cultural authenticity and provide specific, actionable feedback.
        """
        
        messages = [SystemMessage(content=enhanced_prompt)]
        
        # Create detailed review request
        review_request = self._create_review_request(article, iteration, quality_assessment)
        messages.append(HumanMessage(content=review_request))
        
        return messages
    
    def _create_review_request(self, article: Dict[str, Any], iteration: int, quality_assessment: Dict[str, Any]) -> str:
        """Create detailed review request"""
        
        article_text = f"""
        ARTICLE FOR REVIEW:
        
        Title: {article.get('title', 'No title provided')}
        
        Content: {article.get('content', 'No content provided')}
        
        Citations: {json.dumps(article.get('citations', []), indent=2)}
        
        REVIEW CONTEXT:
        - This is revision #{iteration}
        - Word count: {quality_assessment['word_count']} words
        - Citation count: {quality_assessment['citation_count']}
        - Automated quality scores available for reference
        
        Dr. Spicy, please provide your expert review focusing on:
        
        1. CULTURAL AUTHENTICITY ({config.reviewer.cultural_accuracy_weight * 100}% weight):
           - Respect for cultural traditions
           - Accurate representation of regional practices
           - Appropriate terminology and context
           - Avoidance of cultural appropriation or stereotypes
        
        2. FACTUAL ACCURACY ({config.reviewer.factual_accuracy_weight * 100}% weight):
           - Historical accuracy of claims
           - Correctness of preparation methods
           - Accuracy of ingredient information
           - Reliability of sources and citations
        
        3. WRITING QUALITY ({config.reviewer.writing_quality_weight * 100}% weight):
           - Clarity and readability
           - Proper structure and flow
           - Engaging and informative content
           - Grammar and language usage
        
        Based on your {config.reviewer.strictness_level} standards, provide:
        - Overall decision (revise/approve/reject)
        - Detailed scores for each category (0.0-1.0)
        - Specific, actionable feedback
        - Your confidence in this assessment
        - Priority level for any needed revisions
        
        Remember: Only approve if the article meets world-class standards for a momo encyclopedia!
        """
        
        return article_text.strip()
    
    def _process_review_response(self, review: DetailedReviewResult, quality_assessment: Dict[str, Any], 
                               article: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Process and enhance the review response"""
        
        # Calculate weighted overall score
        weighted_score = (
            review.cultural_score * config.reviewer.cultural_accuracy_weight +
            review.accuracy_score * config.reviewer.factual_accuracy_weight +
            review.quality_score * config.reviewer.writing_quality_weight
        )
        
        # Override overall score with weighted calculation
        review.overall_score = weighted_score
        
        # Adjust decision based on thresholds and iteration
        final_decision = self._finalize_decision(review, iteration)
        
        # Enhance feedback based on specific scores
        enhanced_feedback = self._enhance_feedback(review, quality_assessment, iteration)
        
        return {
            "decision": final_decision,
            "feedback": enhanced_feedback,
            "cultural_score": review.cultural_score,
            "accuracy_score": review.accuracy_score,
            "quality_score": review.quality_score,
            "citation_score": review.citation_score,
            "overall_score": review.overall_score,
            "confidence": review.confidence,
            "revision_priority": review.revision_priority
        }
    
    def _finalize_decision(self, review: DetailedReviewResult, iteration: int) -> str:
        """Finalize decision based on scores, thresholds, and iteration count"""
        
        # Auto-approve if above threshold
        if review.overall_score >= config.reviewer.auto_approve_threshold:
            return "approve"
        
        # Force to chair if too many iterations
        if iteration >= config.reviewer.max_iterations:
            return "chair"  # Let chair make final decision
        
        # Reject if critically low scores
        if review.overall_score < 0.3:
            return "reject"
        
        # Default to revise
        return "revise"
    
    def _enhance_feedback(self, review: DetailedReviewResult, quality_assessment: Dict[str, Any], iteration: int) -> List[str]:
        """Enhance feedback with specific, actionable recommendations"""
        feedback_list = []
        
        # Convert single feedback to list
        if isinstance(review.feedback, str):
            feedback_list.append(review.feedback)
        else:
            feedback_list.extend(review.feedback)
        
        # Add specific recommendations based on scores
        if review.cultural_score < 0.7:
            feedback_list.append(
                "🌶️ CULTURAL AUTHENTICITY ISSUE: Add more specific cultural context, "
                "traditional preparation methods, and respectful terminology. "
                "Research authentic regional practices and avoid generalizations."
            )
        
        if review.accuracy_score < 0.7:
            feedback_list.append(
                "🌶️ FACTUAL ACCURACY CONCERN: Verify historical claims, ingredient lists, "
                "and preparation methods. Add more reliable sources and cross-check facts "
                "against authentic culinary sources."
            )
        
        if review.quality_score < 0.7:
            feedback_list.append(
                "🌶️ WRITING QUALITY NEEDS IMPROVEMENT: Enhance readability, improve structure, "
                "add more descriptive language about taste and texture, and ensure smooth flow "
                "between sections."
            )
        
        if review.citation_score < 0.6:
            feedback_list.append(
                f"🌶️ INSUFFICIENT CITATIONS: Current count ({quality_assessment['citation_count']}) "
                f"is below requirements ({config.author.citation_requirements}). Add more "
                f"reliable sources from cultural institutions, academic papers, or reputable "
                f"culinary websites."
            )
        
        # Add iteration-specific feedback
        if iteration > 1:
            feedback_list.append(
                f"🌶️ REVISION #{iteration}: This article has been through multiple revisions. "
                f"Focus on addressing previous feedback comprehensively. Quality must improve "
                f"significantly or this may be rejected."
            )
        
        return feedback_list
    
    def _determine_next_step(self, review: Dict[str, Any], iteration: int) -> str:
        """Determine the next step based on review results"""
        decision = review["decision"]
        
        if decision == "approve":
            return "chair"
        elif decision == "reject":
            return "chair"  # Let chair handle rejections
        elif decision == "revise":
            return "author"
        elif decision == "chair":
            return "chair"
        else:
            return "author"  # Default fallback
    
    def _record_review_metrics(self, review: Dict[str, Any], article: Dict[str, Any], next_step: str):
        """Record detailed metrics for the review process"""
        metrics_collector.record_agent_request(
            "Reviewer", 
            success=True,
            response_time=1.0,  # This would be calculated in the decorator
            quality_score=review["overall_score"]
        )
        
        # Record content-specific metrics
        if next_step == "chair" and review["decision"] == "approve":
            metrics_collector.record_content_event(
                "article_approved",
                citations=len(article.get('citations', [])),
                word_count=len(str(article.get('content', '')).split()),
                quality_score=review["overall_score"]
            )
    
    def _create_review_message(self, review: Dict[str, Any]) -> str:
        """Create a comprehensive review message"""
        decision = review["decision"].upper()
        score = review["overall_score"]
        confidence = review["confidence"]
        
        spice_level = "🌶️🌶️🌶️" if score < 0.5 else "🌶️🌶️" if score < 0.7 else "🌶️"
        
        message = (
            f"Dr. Spicy's Verdict: {decision} {spice_level}\n"
            f"Overall Score: {score:.2f}/1.0 (Confidence: {confidence:.0%})\n"
            f"Cultural: {review['cultural_score']:.2f} | "
            f"Accuracy: {review['accuracy_score']:.2f} | "
            f"Quality: {review['quality_score']:.2f}\n"
        )
        
        if review["decision"] == "approve":
            message += "🎉 APPROVED: This article meets Dr. Spicy's exacting standards!"
        elif review["decision"] == "reject":
            message += "❌ REJECTED: This article does not meet publication standards."
        else:
            message += f"📝 REVISION NEEDED: Priority level - {review['revision_priority'].upper()}"
        
        return message

# Create global agent instance
reviewer_agent = EnhancedReviewerAgent()

@agent_monitor("Reviewer")
def reviewer_node(state: MomoState) -> Dict[str, Any]:
    """Main reviewer node function - Dr. Spicy enhanced"""
    return reviewer_agent.review_content(state)