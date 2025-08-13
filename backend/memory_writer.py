"""
Memory Writer - Converts research reports into actionable memories for mem0 storage
Simple module that extracts key insights and stores them as structured memories
"""

import os
import json
from dotenv import load_dotenv
from mem0.client.main import MemoryClient
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Load environment variables
load_dotenv()

# Configuration - same as final_mem0_populator.py
USER_ID = "doctor_memory"  # Same as final_mem0_populator.py and main.py


class MemoryWriter:
    def __init__(self):
        # Use same pattern as final_mem0_populator.py
        self.mem0 = MemoryClient()  # No API key needed here, uses env var
        
        # Simple model for memory extraction - adjusted for better JSON generation
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type="gemini-2.5-flash",  # Same as populator
            api_key=os.getenv("GOOGLE_API_KEY"),  # Same env var as populator
            model_config_dict={"temperature": 0.2, "max_tokens": 100000},  # Higher temp for better JSON generation
        )
    
    def extract_actionable_memories(self, research_report: str, analysis_report: str, question: str) -> list:
        """Extract actionable memories from research and analysis reports"""
        
        prompt = f"""RESEARCH QUESTION: {question}

RESEARCH REPORT:
{research_report}

ANALYSIS REPORT:
{analysis_report}

Extract key insights from the research reports above and format as JSON array.

**INSIGHT CATEGORIES TO EXTRACT:**
- **Key Findings**: Main discoveries from the research
- **Data Patterns**: Important patterns or trends identified  
- **Methodology Insights**: Research approach effectiveness
- **Limitations**: Gaps or constraints discovered
- **Process Learning**: Lessons about research methodology
- **Future Directions**: Recommendations for improvement

**JSON STRUCTURE REQUIRED:**
[
  {{"memory": "[specific insight from research report]", "topic": "[category_name]"}},
  {{"memory": "[specific insight from analysis report]", "topic": "[category_name]"}},
  {{"memory": "[another specific finding]", "topic": "[category_name]"}}
]

**REQUIREMENTS:**
- Extract 4-8 insights directly from the provided reports
- Each "memory" field must contain specific findings from the actual content
- Each "topic" field should be: findings, patterns, methodology, limitations, process_learning, or recommendations
- Use exact phrases and details from the reports, not generic statements
- Return ONLY the JSON array, no other text or formatting"""

        system_message = BaseMessage.make_assistant_message(
            role_name="MemoryExtractor",
            content="You extract insights from research reports and return them as a JSON array. Analyze the provided research content and extract specific findings, not generic statements. Return only valid JSON - no explanations, markdown, or code blocks."
        )
        
        agent = ChatAgent(system_message=system_message, model=self.model)
        response = agent.step(BaseMessage.make_user_message("User", prompt))
        
        try:
            response_content = response.msg.content.strip()
            rprint(f"[debug] LLM response length: {len(response_content)}")
            rprint(f"[debug] LLM response preview: {response_content[:200]}...")
            
            memory_data = json.loads(response_content)
            rprint(f"[debug] Successfully parsed {len(memory_data)} memories")
            return memory_data
        except json.JSONDecodeError as e:
            rprint(f"Memory extraction failed: {e}")
            rprint(f"[debug] Raw response: {response.msg.content}")
            
            # Fallback: Create simple memories from the analysis
            fallback_memories = [
                {"memory": "Research session completed successfully", "topic": "session_status"},
                {"memory": f"Research question: {question[:100]}...", "topic": "research_question"},
                {"memory": "Analysis artifacts generated", "topic": "artifacts"},
                {"memory": "Memory extraction encountered JSON parsing error", "topic": "technical_issue"}
            ]
            rprint(f"[debug] Using {len(fallback_memories)} fallback memories")
            return fallback_memories
    
    def store_memories(self, memories: list, session_id: str, question: str) -> int:
        """Store extracted memories in mem0 - same pattern as populator"""
        
        stored_count = 0
        
        for i, memory_entry in enumerate(memories):
            memory_text = memory_entry.get("memory", "")
            topic = memory_entry.get("topic", "research")
            
            if memory_text.strip():  # Check for non-empty content
                try:
                    # Use same pattern as final_mem0_populator.py
                    self.mem0.add(
                        messages=[{"role": "assistant", "content": memory_text}],
                        user_id=USER_ID,
                        metadata={
                            "session_id": session_id,
                            "research_question": question,
                            "topic": topic,
                            "memory_type": "research_insight",
                            "summary_fact": True  # Same as populator for consistency
                        }
                    )
                    stored_count += 1
                    # Simplified logging for production use
                    rprint(f"   + Stored insight {i+1}")
                except Exception as e:
                    rprint(f"   - Failed to store memory {i+1}: {e}")
        
        return stored_count
    
    def process_research_session(self, research_report: str, analysis_report: str, question: str, session_id: str) -> int:
        """Main function to process a research session and store memories"""
        
        # Extract memories from reports
        memories = self.extract_actionable_memories(research_report, analysis_report, question)
        
        if not memories:
            rprint("No memories extracted")
            return 0
        
        # Store memories - simple loop
        rprint(f"Extracting and storing {len(memories)} research insights...")
        stored_count = self.store_memories(memories, session_id, question)
        
        return stored_count


def write_memories_from_reports(research_report: str, analysis_report: str, question: str, session_id: str) -> int:
    """Convenience function to write memories from research reports"""
    
    writer = MemoryWriter()
    return writer.process_research_session(research_report, analysis_report, question, session_id)


if __name__ == "__main__":
    # Test the memory writer with realistic sample data
    rprint("[yellow]Testing Memory Writer with Sample Data[/yellow]")
    
    test_question = "What are the most effective diabetes treatments for elderly patients?"
    
    test_report = """# Research Report: Diabetes Treatment in Elderly Patients

## Key Findings
Based on analysis of patient memories, several patterns emerged:

1. **Metformin Effectiveness**: Elderly patients on metformin 500mg showed better glucose control
2. **Insulin Management**: Complex insulin regimens in patients over 75 require frequent monitoring
3. **Comorbidity Considerations**: Heart disease significantly impacts treatment choices
4. **Patient Compliance**: Simpler medication schedules improve adherence rates

## Patient Examples
- Elena Vance (67y): Type 2 diabetes managed with metformin and lifestyle changes
- Marcus Chen (72y): Insulin-dependent with excellent self-management
- Sarah Johnson (69y): Multiple medications requiring careful coordination

## Treatment Patterns
The data shows preference for conservative dosing in elderly patients, with emphasis on avoiding hypoglycemia. Most effective approaches combine medication with structured lifestyle counseling.

## Conclusions
Evidence suggests individualized treatment plans yield better outcomes than standard protocols for elderly diabetic patients."""

    test_analysis = """# Meta-Analysis Report

## Methodology Assessment
- **Data Quality**: High - consistent patient records with detailed medication histories
- **Sample Size**: 45 elderly diabetic patients analyzed
- **Coverage**: Good representation across age groups 65-85

## Research Quality Indicators
- **Evidence Strength**: Strong correlation between treatment complexity and adherence issues
- **Data Completeness**: 89% of records contained complete medication information  
- **Bias Assessment**: Selection bias toward complex cases noted

## Key Insights
1. **Pattern Recognition**: Clear preference for metformin as first-line therapy
2. **Risk Factors**: Age over 75 correlates with increased monitoring frequency
3. **Outcome Measures**: HbA1c improvements documented in 73% of cases
4. **Knowledge Gaps**: Limited data on very elderly patients (>85 years)

## Recommendations
Future research should focus on long-term outcomes and quality of life measures in this population."""

    test_session = "test_session_20250813"
    
    rprint(f"Question: {test_question}")
    rprint(f"Session: {test_session}")
    rprint()
    
    try:
        count = write_memories_from_reports(test_report, test_analysis, test_question, test_session)
        rprint(f"\n[green]Successfully stored {count} test memories![/green]")
        
        # Verify the memories were stored by searching for them
        rprint("\n[yellow]Verifying stored memories...[/yellow]")
        writer = MemoryWriter()
        
        # Search for our test memories
        test_memories = writer.mem0.search(
            query="diabetes elderly patients",
            user_id=USER_ID,
            limit=10
        )
        
        if test_memories:
            rprint(f"[green]Found {len(test_memories)} memories in database[/green]")
            rprint("[cyan]Sample stored memories:[/cyan]")
            for i, memory in enumerate(test_memories[:3], 1):
                memory_text = memory.get('memory', 'No content')[:100]
                rprint(f"  {i}. {memory_text}...")
        else:
            rprint("[red]No memories found - storage may have failed[/red]")
            
    except Exception as e:
        rprint(f"[red]Test failed with error: {e}[/red]")
        import traceback
        traceback.print_exc()