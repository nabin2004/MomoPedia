"""
Enhanced MomoPedia main workflow with comprehensive monitoring and error handling
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any

from momopedia.state import MomoState
from momopedia.agents.author import author_node
from momopedia.agents.reviewer import reviewer_node  
from momopedia.agents.chair import chair_node
from momopedia.config.settings import get_config
from momopedia.monitoring.system_monitor import get_logger, get_metrics_collector, performance_monitor

logger = get_logger()
metrics_collector = get_metrics_collector()
config = get_config()

class EnhancedMomoPediaWorkflow:
    """Enhanced workflow with monitoring, error handling, and quality controls"""
    
    def __init__(self):
        self.workflow = StateGraph(MomoState)
        self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.log_agent_activity("Workflow", "workflow_initialized", {
            "max_iterations": config.author.max_iterations,
            "quality_threshold": config.reviewer.auto_approve_threshold,
            "publication_standards": config.chair.publication_standards
        })
    
    def _build_workflow(self):
        """Build the enhanced workflow graph"""
        
        # Add nodes with error handling wrappers
        self.workflow.add_node("author", self._wrap_agent_node(author_node, "Author"))
        self.workflow.add_node("reviewer", self._wrap_agent_node(reviewer_node, "Reviewer"))
        self.workflow.add_node("chair", self._wrap_agent_node(chair_node, "Chair"))
        self.workflow.add_node("error_handler", self._error_handler_node)
        
        # Set entry point
        self.workflow.set_entry_point("author")
        
        # Add edges
        self.workflow.add_edge("author", "reviewer")
        
        # Enhanced conditional routing after reviewer
        self.workflow.add_conditional_edges(
            "reviewer",
            self._enhanced_route_after_review,
            {
                "author": "author",
                "chair": "chair",
                "error": "error_handler"
            }
        )
        
        # Chair decision routing
        self.workflow.add_conditional_edges(
            "chair", 
            self._route_after_chair,
            {
                "end": END,
                "author": "author",
                "error": "error_handler"
            }
        )
        
        # Error handler always ends
        self.workflow.add_edge("error_handler", END)
    
    def _wrap_agent_node(self, agent_func, agent_name: str):
        """Wrap agent nodes with error handling and monitoring"""
        
        @performance_monitor(f"{agent_name.lower()}_workflow_node")
        def wrapped_agent_node(state: MomoState) -> Dict[str, Any]:
            try:
                logger.log_agent_activity("Workflow", f"{agent_name.lower()}_node_start", {
                    "iteration": state.get("iteration", 0),
                    "current_step": state.get("next_step", "unknown")
                })
                
                # Call the actual agent
                result = agent_func(state)
                
                # Validate result structure
                if not isinstance(result, dict):
                    raise ValueError(f"{agent_name} returned invalid result type: {type(result)}")
                
                # Ensure required fields
                if "next_step" not in result:
                    result["next_step"] = "chair"  # Default fallback
                
                if "messages" not in result:
                    result["messages"] = [f"{agent_name} completed processing"]
                
                logger.log_agent_activity("Workflow", f"{agent_name.lower()}_node_complete", {
                    "next_step": result["next_step"],
                    "has_error": result.get("error", False)
                })
                
                return result
                
            except Exception as e:
                logger.log_error(e, {
                    "agent": agent_name,
                    "operation": "workflow_node",
                    "iteration": state.get("iteration", 0)
                })
                
                # Return error state
                return {
                    "messages": [f"Error in {agent_name}: {str(e)}"],
                    "next_step": "error",
                    "error": True,
                    "error_agent": agent_name,
                    "error_message": str(e)
                }
        
        return wrapped_agent_node
    
    def _enhanced_route_after_review(self, state: MomoState) -> str:
        """Enhanced routing logic after reviewer assessment"""
        try:
            iteration = state.get("iteration", 0)
            next_step = state.get("next_step", "chair")
            error = state.get("error", False)
            
            # Handle errors
            if error:
                return "error"
            
            # Enforce maximum iterations
            if iteration >= config.author.max_iterations:
                logger.log_agent_activity("Workflow", "max_iterations_reached", {
                    "iteration": iteration,
                    "max_allowed": config.author.max_iterations
                })
                return "chair"  # Force to chair for final decision
            
            # Check for quality override conditions
            review_scores = state.get("review_scores", {})
            overall_score = review_scores.get("overall", 0.0)
            
            # Auto-approve high quality content
            if overall_score >= config.reviewer.auto_approve_threshold:
                logger.log_agent_activity("Workflow", "auto_approve_triggered", {
                    "score": overall_score,
                    "threshold": config.reviewer.auto_approve_threshold
                })
                return "chair"
            
            # Route based on reviewer decision
            if next_step == "author":
                return "author"
            elif next_step == "chair":
                return "chair"
            else:
                # Default to chair for unknown states
                return "chair"
                
        except Exception as e:
            logger.log_error(e, {"operation": "route_after_review"})
            return "error"
    
    def _route_after_chair(self, state: MomoState) -> str:
        """Route after chair decision"""
        try:
            error = state.get("error", False)
            chair_decision = state.get("chair_decision", "REJECTED")
            
            if error:
                return "error"
            
            # Check if chair wants another revision (rare case)
            if chair_decision == "OVERRIDE_REVISION":
                iteration = state.get("iteration", 0)
                if iteration < config.author.max_iterations + 2:  # Allow extra iterations for chair override
                    return "author"
            
            # Default end for all other cases
            return "end"
            
        except Exception as e:
            logger.log_error(e, {"operation": "route_after_chair"})
            return "error"
    
    def _error_handler_node(self, state: MomoState) -> Dict[str, Any]:
        """Handle workflow errors gracefully"""
        error_message = state.get("error_message", "Unknown error occurred")
        error_agent = state.get("error_agent", "Unknown")
        
        logger.log_agent_activity("Workflow", "error_handling", {
            "error_agent": error_agent,
            "error_message": error_message,
            "iteration": state.get("iteration", 0)
        })
        
        # Record error metrics
        metrics_collector.record_content_event("article_rejected", reason="system_error")
        
        return {
            "messages": [
                f"Workflow Error: {error_message}",
                f"Error occurred in: {error_agent}",
                "Article processing terminated due to system error."
            ],
            "chair_decision": "REJECTED",
            "error_recovery": True,
            "next_step": "end"
        }
    
    @performance_monitor("workflow_execution")
    def run(self, initial_state: MomoState) -> Dict[str, Any]:
        """Execute the workflow with comprehensive monitoring"""
        try:
            logger.log_agent_activity("Workflow", "execution_start", {
                "topic": initial_state.get("topic", "Unknown"),
                "config_environment": config.environment
            })
            
            # Validate initial state
            validated_state = self._validate_initial_state(initial_state)
            
            # Execute workflow
            final_state = self.app.invoke(validated_state)
            
            # Post-process results
            processed_results = self._post_process_results(final_state)
            
            logger.log_agent_activity("Workflow", "execution_complete", {
                "final_decision": processed_results.get("chair_decision", "Unknown"),
                "total_iterations": processed_results.get("iteration", 0),
                "success": not processed_results.get("error", False)
            })
            
            return processed_results
            
        except Exception as e:
            logger.log_error(e, {"operation": "workflow_execution"})
            
            return {
                "messages": [f"Critical workflow error: {str(e)}"],
                "chair_decision": "REJECTED",
                "error": True,
                "error_message": str(e),
                "next_step": "end"
            }
    
    def _validate_initial_state(self, state: MomoState) -> MomoState:
        """Validate and enhance initial state"""
        validated_state = dict(state)
        
        # Ensure required fields
        if "messages" not in validated_state:
            validated_state["messages"] = []
        
        if "iteration" not in validated_state:
            validated_state["iteration"] = 0
        
        if "next_step" not in validated_state:
            validated_state["next_step"] = "author"
        
        # Extract topic if provided
        topic = validated_state.get("topic")
        if topic:
            validated_state["messages"].append(f"Generate comprehensive article about: {topic}")
        
        return validated_state
    
    def _post_process_results(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process workflow results for better reporting"""
        
        # Generate execution summary
        execution_summary = {
            "workflow_completed": True,
            "total_messages": len(final_state.get("messages", [])),
            "final_iteration": final_state.get("iteration", 0),
            "publication_ready": final_state.get("publication_ready", False),
            "final_quality_score": final_state.get("final_score", 0.0)
        }
        
        # Add metrics summary
        metrics_summary = metrics_collector.get_metrics_summary()
        
        # Combine results
        enhanced_results = dict(final_state)
        enhanced_results["execution_summary"] = execution_summary
        enhanced_results["metrics_summary"] = metrics_summary
        enhanced_results["timestamp"] = logger.logger.handlers[0].stream.name if logger.logger.handlers else "unknown"
        
        return enhanced_results

# Create global workflow instance
enhanced_workflow = EnhancedMomoPediaWorkflow()

# Maintain backward compatibility
workflow = enhanced_workflow.workflow
app = enhanced_workflow.app

def run_workflow(initial_state: MomoState) -> Dict[str, Any]:
    """Run the enhanced workflow with monitoring"""
    return enhanced_workflow.run(initial_state)

def get_workflow_metrics() -> Dict[str, Any]:
    """Get comprehensive workflow metrics"""
    return metrics_collector.get_metrics_summary()

def reset_workflow_metrics():
    """Reset workflow metrics for new session"""
    global metrics_collector
    from momopedia.monitoring.system_monitor import MetricsCollector
    metrics_collector = MetricsCollector()