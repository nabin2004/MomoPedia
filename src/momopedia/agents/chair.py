"""
Enhanced Editorial Chair Agent with advanced decision making and comprehensive reporting
"""

import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from momopedia.state import MomoState
from momopedia.prompts.personas import CHAIR_PROMPT
from momopedia.llm import get_llm
from momopedia.config.settings import get_config
from momopedia.monitoring.system_monitor import agent_monitor, get_logger, get_metrics_collector

logger = get_logger()
metrics_collector = get_metrics_collector()
config = get_config()

class ComprehensiveChairDecision(BaseModel):
    """Enhanced chair decision with detailed reasoning and metrics"""
    decision: str = Field(description="'ACCEPTED', 'REJECTED', or 'OVERRIDE_REVISION'")
    memo: str = Field(description="Detailed editorial memo explaining the decision")
    final_score: float = Field(description="Final quality score assigned by chair (0-1)", default=0.0)
    publication_ready: bool = Field(description="Whether article is ready for publication", default=False)
    revision_recommendations: List[str] = Field(description="Specific recommendations for future revisions", default=[])
    cultural_assessment: str = Field(description="Assessment of cultural authenticity", default="")
    editorial_notes: str = Field(description="Internal editorial notes", default="")
    confidence_level: str = Field(description="Chair's confidence in decision (low/medium/high)", default="medium")
    estimated_audience: str = Field(description="Target audience for this content", default="general")
    
class EnhancedChairAgent:
    """Enhanced Editorial Chair with sophisticated decision making capabilities"""
    
    def __init__(self):
        self.llm = get_llm()
        self.structured_chair = self.llm.with_structured_output(ComprehensiveChairDecision)
        
        logger.log_agent_activity("Chair", "agent_initialized", {
            "publication_standards": config.chair.publication_standards,
            "override_threshold": config.chair.override_reviewer_threshold,
            "final_review_required": config.chair.final_review_required
        })
    
    @agent_monitor("Chair")
    def make_decision(self, state: MomoState) -> Dict[str, Any]:
        """Make final editorial decision with comprehensive analysis"""
        try:
            article = state.get("article", {})
            feedback = state.get("feedback", [])
            iteration = state.get("iteration", 0)
            review_scores = state.get("review_scores", {})
            
            logger.log_agent_activity("Chair", "decision_start", {
                "iteration": iteration,
                "article_title": article.get('title', 'Unknown'),
                "review_scores": review_scores,
                "feedback_count": len(feedback) if feedback else 0
            })
            
            # Validate inputs
            if not article:
                return self._handle_no_article(state)
            
            # Prepare comprehensive analysis
            analysis_context = self._prepare_analysis_context(state)
            
            # Create messages for chair decision
            messages = self._prepare_decision_messages(analysis_context, iteration)
            
            # Get chair's decision
            chair_response = self.structured_chair.invoke(messages)
            
            # Process and validate decision
            final_decision = self._process_chair_decision(chair_response, state, analysis_context)
            
            # Record final metrics
            self._record_final_metrics(final_decision, article, state)
            
            # Generate publication report if accepted
            publication_report = self._generate_publication_report(final_decision, article, state) if final_decision["decision"] == "ACCEPTED" else None
            
            logger.log_agent_activity("Chair", "decision_complete", {
                "final_decision": final_decision["decision"],
                "final_score": final_decision["final_score"],
                "publication_ready": final_decision["publication_ready"],
                "confidence": final_decision["confidence_level"]
            })
            
            return {
                "messages": [self._create_chair_message(final_decision)],
                "chair_decision": final_decision["decision"],
                "final_score": final_decision["final_score"],
                "publication_ready": final_decision["publication_ready"],
                "editorial_memo": final_decision["memo"],
                "publication_report": publication_report,
                "next_step": "end",
                "chair_analysis": {
                    "cultural_assessment": final_decision["cultural_assessment"],
                    "editorial_notes": final_decision["editorial_notes"],
                    "revision_recommendations": final_decision["revision_recommendations"],
                    "estimated_audience": final_decision["estimated_audience"]
                }
            }
            
        except Exception as e:
            logger.log_error(e, {
                "agent": "Chair",
                "operation": "make_decision",
                "iteration": state.get("iteration", 0)
            })
            
            return {
                "messages": [f"Editorial Chair encountered error: {str(e)}"],
                "chair_decision": "REJECTED",
                "error": True,
                "next_step": "end"
            }
    
    def _handle_no_article(self, state: MomoState) -> Dict[str, Any]:
        """Handle case where no article is provided"""
        logger.logger.error("Chair received no article content for review")
        
        return {
            "messages": ["EDITORIAL DECISION: REJECTED - No article content provided"],
            "chair_decision": "REJECTED",
            "editorial_memo": "Cannot make editorial decision without article content.",
            "next_step": "end"
        }
    
    def _prepare_analysis_context(self, state: MomoState) -> Dict[str, Any]:
        """Prepare comprehensive analysis context for decision making"""
        article = state.get("article", {})
        feedback = state.get("feedback", [])
        review_scores = state.get("review_scores", {})
        iteration = state.get("iteration", 0)
        
        content = article.get('content', '')
        word_count = len(content.split()) if content else 0
        citation_count = len(article.get('citations', []))
        
        # Calculate workflow statistics
        workflow_stats = {
            "total_iterations": iteration,
            "feedback_rounds": len(feedback) if feedback else 0,
            "final_reviewer_score": review_scores.get('overall', 0.0),
            "reviewer_confidence": state.get('reviewer_confidence', 0.0)
        }
        
        # Assess urgency and priority
        urgency_factors = {
            "high_iterations": iteration >= config.author.max_iterations,
            "low_quality": review_scores.get('overall', 0.0) < 0.5,
            "cultural_issues": review_scores.get('cultural', 0.0) < 0.6,
            "needs_override": review_scores.get('overall', 0.0) < config.chair.override_reviewer_threshold
        }
        
        return {
            "article_metrics": {
                "word_count": word_count,
                "citation_count": citation_count,
                "has_title": bool(article.get('title')),
                "content_length": len(content)
            },
            "review_assessment": review_scores,
            "workflow_stats": workflow_stats,
            "feedback_summary": feedback,
            "urgency_factors": urgency_factors,
            "publication_standards": config.chair.publication_standards
        }
    
    def _prepare_decision_messages(self, context: Dict[str, Any], iteration: int) -> List[BaseMessage]:
        """Prepare comprehensive messages for chair decision"""
        
        enhanced_prompt = f"""
        {CHAIR_PROMPT}
        
        ENHANCED EDITORIAL STANDARDS:
        - Publication Standard: {config.chair.publication_standards.upper()}
        - Override Threshold: {config.chair.override_reviewer_threshold}
        - Final Review Required: {config.chair.final_review_required}
        - Maximum Iterations: {config.author.max_iterations}
        
        DECISION FRAMEWORK:
        As Editorial Chair, you have the authority to:
        1. ACCEPT articles that meet world-class standards
        2. REJECT articles that cannot reach publication quality
        3. OVERRIDE_REVISION for articles needing minor improvements but acceptable overall
        
        Consider the complete editorial workflow, reviewer feedback quality, 
        and strategic publication decisions for MomoPedia's reputation.
        """
        
        messages = [SystemMessage(content=enhanced_prompt)]
        
        # Create detailed decision request
        decision_request = self._create_decision_request(context, iteration)
        messages.append(HumanMessage(content=decision_request))
        
        return messages
    
    def _create_decision_request(self, context: Dict[str, Any], iteration: int) -> str:
        """Create detailed decision request for the chair"""
        
        article_metrics = context["article_metrics"]
        review_scores = context["review_assessment"]
        workflow_stats = context["workflow_stats"]
        feedback = context["feedback_summary"]
        urgency = context["urgency_factors"]
        
        request = f"""
        EDITORIAL CHAIR DECISION REQUEST
        
        ARTICLE OVERVIEW:
        - Word Count: {article_metrics['word_count']} words
        - Citations: {article_metrics['citation_count']}
        - Content Length: {article_metrics['content_length']} characters
        - Has Title: {'Yes' if article_metrics['has_title'] else 'No'}
        
        REVIEWER ASSESSMENT (Dr. Spicy):
        - Overall Score: {review_scores.get('overall', 0):.2f}/1.0
        - Cultural Authenticity: {review_scores.get('cultural', 0):.2f}/1.0
        - Factual Accuracy: {review_scores.get('accuracy', 0):.2f}/1.0
        - Writing Quality: {review_scores.get('quality', 0):.2f}/1.0
        - Citation Quality: {review_scores.get('citation', 0):.2f}/1.0
        
        WORKFLOW STATISTICS:
        - Total Iterations: {workflow_stats['total_iterations']}
        - Feedback Rounds: {workflow_stats['feedback_rounds']}
        - Reviewer Confidence: {workflow_stats.get('reviewer_confidence', 0):.0%}
        
        FEEDBACK HISTORY:
        {json.dumps(feedback, indent=2) if feedback else "No feedback provided"}
        
        URGENCY FACTORS:
        - High Iterations: {'YES - Consider override' if urgency['high_iterations'] else 'No'}
        - Low Quality Score: {'YES - Quality concerns' if urgency['low_quality'] else 'No'}
        - Cultural Issues: {'YES - Cultural sensitivity needed' if urgency['cultural_issues'] else 'No'}
        - Needs Override: {'YES - Below override threshold' if urgency['needs_override'] else 'No'}
        
        EDITORIAL CONSIDERATIONS:
        1. Does this article meet {config.chair.publication_standards} publication standards?
        2. Are there cultural sensitivity issues that require attention?
        3. Is the content comprehensive and accurate for a momo encyclopedia?
        4. Would readers find this informative and culturally respectful?
        5. Does this enhance MomoPedia's reputation as a authoritative source?
        
        Based on your analysis, provide:
        - Final decision (ACCEPTED/REJECTED/OVERRIDE_REVISION)
        - Detailed editorial memo explaining your reasoning
        - Final quality score (0.0-1.0)
        - Cultural assessment and any concerns
        - Specific recommendations for future content
        - Your confidence level in this decision
        - Target audience for this content
        
        Remember: You have the final authority and responsibility for MomoPedia's content quality!
        """
        
        return request.strip()
    
    def _process_chair_decision(self, response: ComprehensiveChairDecision, 
                                state: MomoState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate the chair's decision"""
        
        # Validate decision type
        valid_decisions = ["ACCEPTED", "REJECTED", "OVERRIDE_REVISION"]
        if response.decision not in valid_decisions:
            logger.logger.warning(f"Invalid chair decision: {response.decision}, defaulting to REJECTED")
            response.decision = "REJECTED"
        
        # Adjust final score based on context if needed
        reviewer_score = context["review_assessment"].get('overall', 0.0)
        
        # Chair can override reviewer score but should justify significant differences
        if abs(response.final_score - reviewer_score) > 0.3:
            logger.log_agent_activity("Chair", "score_override", {
                "reviewer_score": reviewer_score,
                "chair_score": response.final_score,
                "difference": abs(response.final_score - reviewer_score)
            })
        
        # Set publication readiness based on decision
        response.publication_ready = response.decision == "ACCEPTED"
        
        # Add timestamp to editorial notes
        response.editorial_notes = (
            f"Decision made: {datetime.now().isoformat()}\n"
            f"Iteration: {state.get('iteration', 0)}\n"
            f"Reviewer score: {reviewer_score:.2f}\n"
            f"Chair override: {response.final_score:.2f}\n"
            f"{response.editorial_notes}"
        )
        
        return {
            "decision": response.decision,
            "memo": response.memo,
            "final_score": response.final_score,
            "publication_ready": response.publication_ready,
            "revision_recommendations": response.revision_recommendations,
            "cultural_assessment": response.cultural_assessment,
            "editorial_notes": response.editorial_notes,
            "confidence_level": response.confidence_level,
            "estimated_audience": response.estimated_audience
        }
    
    def _record_final_metrics(self, decision: Dict[str, Any], article: Dict[str, Any], state: MomoState):
        """Record final metrics for the editorial process"""
        
        # Record chair performance
        metrics_collector.record_agent_request(
            "Chair",
            success=True,
            response_time=1.0,  # Would be calculated by decorator
            quality_score=decision["final_score"]
        )
        
        # Record content outcome
        if decision["decision"] == "ACCEPTED":
            metrics_collector.record_content_event(
                "article_approved",
                revisions=state.get("iteration", 0),
                final_score=decision["final_score"],
                word_count=len(str(article.get('content', '')).split()),
                citations=len(article.get('citations', []))
            )
        else:
            metrics_collector.record_content_event(
                "article_rejected",
                revisions=state.get("iteration", 0),
                final_score=decision["final_score"],
                reason=decision["decision"]
            )
    
    def _generate_publication_report(self, decision: Dict[str, Any], article: Dict[str, Any], state: MomoState) -> Dict[str, Any]:
        """Generate comprehensive publication report for accepted articles"""
        
        return {
            "publication_status": "APPROVED",
            "article_id": f"momo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": article.get('title', 'Untitled'),
            "final_quality_score": decision["final_score"],
            "editorial_approval_date": datetime.now().isoformat(),
            "revision_history": {
                "total_iterations": state.get("iteration", 0),
                "feedback_rounds": len(state.get("feedback", [])),
                "final_reviewer_score": state.get("review_scores", {}).get("overall", 0.0)
            },
            "content_metrics": {
                "word_count": len(str(article.get('content', '')).split()),
                "citation_count": len(article.get('citations', [])),
                "estimated_reading_time": len(str(article.get('content', '')).split()) / 200  # 200 WPM average
            },
            "quality_assessment": {
                "cultural_authenticity": decision["cultural_assessment"],
                "target_audience": decision["estimated_audience"],
                "chair_confidence": decision["confidence_level"]
            },
            "publication_metadata": {
                "generated_by": "MomoPedia AI Editorial System",
                "chair_agent_version": "1.0.0",
                "editorial_standards": config.chair.publication_standards,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _create_chair_message(self, decision: Dict[str, Any]) -> str:
        """Create comprehensive chair message"""
        
        decision_emoji = {
            "ACCEPTED": "✅",
            "REJECTED": "❌", 
            "OVERRIDE_REVISION": "📝"
        }
        
        emoji = decision_emoji.get(decision["decision"], "📋")
        confidence_stars = "⭐" * {"low": 1, "medium": 2, "high": 3}.get(decision["confidence_level"], 2)
        
        message = f"""
        {emoji} EDITORIAL CHAIR FINAL DECISION: {decision['decision']} {confidence_stars}
        
        Final Quality Score: {decision['final_score']:.2f}/1.0
        Publication Ready: {'YES' if decision['publication_ready'] else 'NO'}
        Confidence Level: {decision['confidence_level'].upper()}
        Target Audience: {decision['estimated_audience'].title()}
        
        EDITORIAL MEMO:
        {decision['memo']}
        
        CULTURAL ASSESSMENT:
        {decision['cultural_assessment']}
        """
        
        if decision["revision_recommendations"]:
            message += f"\n\nFUTURE RECOMMENDATIONS:\n"
            for i, rec in enumerate(decision["revision_recommendations"], 1):
                message += f"{i}. {rec}\n"
        
        return message.strip()

# Create global agent instance
chair_agent = EnhancedChairAgent()

@agent_monitor("Chair")
def chair_node(state: MomoState) -> Dict[str, Any]:
    """Main chair node function - Enhanced Editorial Chair"""
    return chair_agent.make_decision(state)