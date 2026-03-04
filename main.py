"""
MomoPedia Enhanced Execution Script
Production-grade execution with comprehensive monitoring, error handling, and reporting
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from momopedia.state import MomoState
from momopedia.main import run_workflow, get_workflow_metrics
from momopedia.config.settings import get_config, update_config
from momopedia.monitoring.system_monitor import get_logger, generate_monitoring_report
from momopedia.llm import validate_llm_configuration

def main():
    """Enhanced main execution function"""
    print("🥟 Welcome to MomoPedia - AI-Powered Momo Encyclopedia System")
    print("=" * 60)
    
    # Initialize logging and configuration
    logger = get_logger()
    config = get_config()
    
    print(f"Environment: {config.environment}")
    print(f"Debug Mode: {config.debug}")
    print(f"Publication Standards: {config.chair.publication_standards}")
    print()
    
    # Validate system configuration
    print("🔧 Validating system configuration...")
    validation_result = validate_llm_configuration()
    
    if not validation_result["valid"]:
        print("❌ Configuration validation failed:")
        for error in validation_result["errors"]:
            print(f"  - {error}")
        return 1
    
    if validation_result["warnings"]:
        print("⚠️ Configuration warnings:")
        for warning in validation_result["warnings"]:
            print(f"  - {warning}")
    
    print("✅ System configuration validated successfully!")
    print()
    
    # Define example topics for demonstration
    example_topics = [
        "Traditional Nepali Momos: Cultural Heritage and Regional Variations",
        "Tibetan Momo Traditions in the Himalayas",
        "Darjeeling Hill Station Momos: A Fusion of Cultures",
        "Modern Momo Innovations and Contemporary Adaptations"
    ]
    
    print("📝 Available example topics:")
    for i, topic in enumerate(example_topics, 1):
        print(f"  {i}. {topic}")
    print("  5. Custom topic")
    print()
    
    # Get user input
    try:
        choice = input("Select a topic (1-5) or press Enter for default: ").strip()
        
        if choice == "" or choice == "1":
            selected_topic = example_topics[0]
        elif choice == "2":
            selected_topic = example_topics[1] 
        elif choice == "3":
            selected_topic = example_topics[2]
        elif choice == "4":
            selected_topic = example_topics[3]
        elif choice == "5":
            selected_topic = input("Enter your custom topic: ").strip()
            if not selected_topic:
                selected_topic = example_topics[0]
        else:
            selected_topic = example_topics[0]
            
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye!")
        return 0
    
    print(f"\n🎯 Selected Topic: {selected_topic}")
    print("=" * 60)
    print()
    
    # Prepare initial state
    initial_state = MomoState(
        topic=selected_topic,
        messages=[f"Generate a comprehensive, culturally authentic article about: {selected_topic}"],
        iteration=0,
        next_step="author"
    )
    
    # Log workflow start
    logger.log_agent_activity("System", "workflow_start", {
        "topic": selected_topic,
        "timestamp": datetime.now().isoformat(),
        "config_environment": config.environment
    })
    
    print("🚀 Starting AI Editorial Workflow...")
    print("   📝 Author Agent: Researching and writing content...")
    
    try:
        # Execute the enhanced workflow
        final_state = run_workflow(initial_state)
        
        # Display results
        display_results(final_state, selected_topic)
        
        # Generate and save reports
        save_reports(final_state, selected_topic)
        
        # Show metrics summary
        show_metrics_summary()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Critical error during execution: {str(e)}")
        logger.log_error(e, {"operation": "main_execution", "topic": selected_topic})
        return 1

def display_results(final_state: dict, topic: str):
    """Display comprehensive workflow results"""
    print("\n" + "=" * 60)
    print("📊 WORKFLOW RESULTS")
    print("=" * 60)
    
    # Basic info
    chair_decision = final_state.get("chair_decision", "UNKNOWN")
    publication_ready = final_state.get("publication_ready", False)
    final_score = final_state.get("final_score", 0.0)
    total_iterations = final_state.get("iteration", 0)
    
    # Status indicators
    status_emoji = "✅" if chair_decision == "ACCEPTED" else "❌"
    quality_stars = "⭐" * min(5, max(1, int(final_score * 5)))
    
    print(f"{status_emoji} Final Decision: {chair_decision}")
    print(f"🎯 Publication Ready: {'YES' if publication_ready else 'NO'}")
    print(f"🏆 Final Quality Score: {final_score:.2f}/1.0 {quality_stars}")
    print(f"🔄 Total Iterations: {total_iterations}")
    print()
    
    # Article information
    article = final_state.get("article", {})
    if article:
        title = article.get("title", "Untitled")
        content = article.get("content", "")
        citations = article.get("citations", [])
        
        print(f"📰 Article Title: {title}")
        print(f"📏 Content Length: {len(content.split())} words")
        print(f"📚 Citations: {len(citations)}")
        print()
    
    # Quality breakdown
    review_scores = final_state.get("review_scores", {})
    if review_scores:
        print("📈 Quality Breakdown:")
        print(f"   🌍 Cultural Authenticity: {review_scores.get('cultural', 0):.2f}/1.0")
        print(f"   📖 Factual Accuracy: {review_scores.get('accuracy', 0):.2f}/1.0") 
        print(f"   ✍️  Writing Quality: {review_scores.get('quality', 0):.2f}/1.0")
        print(f"   📎 Citation Quality: {review_scores.get('citation', 0):.2f}/1.0")
        print()
    
    # Editorial memo
    editorial_memo = final_state.get("editorial_memo", "")
    if editorial_memo:
        print("📝 Editorial Memo:")
        print(f"   {editorial_memo[:200]}{'...' if len(editorial_memo) > 200 else ''}")
        print()
    
    # Messages history
    messages = final_state.get("messages", [])
    if messages:
        print("💬 Workflow Messages:")
        for i, message in enumerate(messages[-3:], 1):  # Show last 3 messages
            print(f"   {i}. {message}")
        print()
    
    # Error information
    if final_state.get("error", False):
        error_message = final_state.get("error_message", "Unknown error")
        print(f"⚠️ Error Occurred: {error_message}")
        print()

def save_reports(final_state: dict, topic: str):
    """Save comprehensive reports to files"""
    print("💾 Saving reports...")
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed workflow results
    results_file = reports_dir / f"workflow_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(final_state, f, indent=2, default=str)
    
    print(f"   ✅ Workflow results saved to: {results_file}")
    
    # Save article content if available  
    article = final_state.get("article", {})
    if article and article.get("content"):
        article_file = reports_dir / f"article_{timestamp}.md"
        
        with open(article_file, 'w') as f:
            f.write(f"# {article.get('title', 'Untitled Article')}\n\n")
            f.write(f"*Generated by MomoPedia AI Editorial System*\n\n")
            f.write(f"**Topic:** {topic}\n\n")
            f.write(f"**Final Score:** {final_state.get('final_score', 0):.2f}/1.0\n\n")
            f.write(f"**Status:** {final_state.get('chair_decision', 'Unknown')}\n\n")
            f.write("---\n\n")
            f.write(article.get("content", ""))
            
            citations = article.get("citations", [])
            if citations:
                f.write("\n\n## Sources\n\n")
                for i, citation in enumerate(citations, 1):
                    f.write(f"{i}. {citation}\n")
        
        print(f"   ✅ Article content saved to: {article_file}")
    
    # Save monitoring report
    monitoring_report = generate_monitoring_report()
    monitoring_file = reports_dir / f"monitoring_report_{timestamp}.txt"
    
    with open(monitoring_file, 'w') as f:
        f.write(monitoring_report)
    
    print(f"   ✅ Monitoring report saved to: {monitoring_file}")

def show_metrics_summary():
    """Display workflow metrics summary"""
    print("📊 SYSTEM METRICS SUMMARY")
    print("=" * 60)
    
    try:
        metrics = get_workflow_metrics()
        
        # Agent performance
        print("🤖 Agent Performance:")
        for agent_name, agent_data in metrics.get('agents', {}).items():
            success_rate = agent_data.get('success_rate', 0) * 100
            avg_time = agent_data.get('average_response_time', 0)
            avg_quality = agent_data.get('average_quality', 0)
            
            print(f"   {agent_name}:")
            print(f"      Success Rate: {success_rate:.1f}%")
            print(f"      Avg Response Time: {avg_time:.2f}s")
            print(f"      Avg Quality: {avg_quality:.2f}")
        
        # Content metrics
        content_metrics = metrics.get('content', {})
        if content_metrics:
            print("\n📝 Content Metrics:")
            total_articles = content_metrics.get('total_articles', 0)
            approved_articles = content_metrics.get('approved_articles', 0)
            approval_rate = (approved_articles / total_articles * 100) if total_articles > 0 else 0
            
            print(f"   Total Articles: {total_articles}")
            print(f"   Approved: {approved_articles}")
            print(f"   Approval Rate: {approval_rate:.1f}%")
        
        print()
        
    except Exception as e:
        print(f"⚠️ Could not retrieve metrics: {str(e)}")

if __name__ == "__main__":
    """Main entry point"""
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
