"""
Strategic Research Agent that explores mem0 memory networks using strategic plans.
Implements memory archaeology approach with guided iterative exploration.
"""

import os

from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Import utils for path setup

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from mem0.client.main import MemoryClient
from rich import print as rprint
from memory_id_tracker import search_with_id_capture, inject_memory_context

from config.prompts import (
    MEMORY_ANALYST_SYSTEM_PROMPT,
    MEMORY_ARCHAEOLOGIST_SYSTEM_PROMPT,
    SEARCH_TERM_EXTRACTION_PROMPT,
    SEARCH_TERM_EXTRACTION_SYSTEM,
    STRATEGIC_DECISION_PROMPT,
    STRATEGIC_MEMORY_ANALYSIS_PROMPT,
)

# Config
USER_ID = "doctor_memory"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MEM0_API_KEY or not GEMINI_API_KEY:
    print("Missing API keys!")
    exit(1)


class StrategicResearchAgent:
    def __init__(self):
        self.mem0 = MemoryClient(api_key=MEM0_API_KEY)
        self.progress_emitter = None

        # Strategic research model setup
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO,
            api_key=GEMINI_API_KEY,
            model_config_dict={"temperature": 0.2, "max_tokens": 100000},
        )

    def set_progress_emitter(self, emitter):
        """Set progress emitter for streaming updates"""
        self.progress_emitter = emitter

    def emit_progress(self, phase: str, status: str, data=None):
        """Emit progress update if emitter is set"""
        if self.progress_emitter:
            self.progress_emitter(phase, status, data)

    def search_and_think(self, query, iteration_num=1):
        """Memory traversal + relationship analysis cycle with ID tracking"""
        rprint(f"Searching: '{query}'")

        try:
            # Use memory ID tracker for search with ID capture
            results, memory_context = search_with_id_capture(
                query=query,
                user_id=USER_ID,
                limit=5  # Small limit for strategic research
            )
        except Exception as e:
            rprint(f"Error with ID tracker, falling back to direct search: {e}")
            # Fallback to direct mem0 search
            results = self.mem0.search(
                query=query,
                user_id=USER_ID,
                limit=5,
                threshold=0.5
            )
            memory_context = ""

        rprint(f"Found {len(results)} connected memories")

        if not results:
            rprint("No connected memories found for this exploration")
            return [], "No results found"

        # Display memory relationship summary
        rprint("Memory Connections Discovered:")
        memory_connections = []
        for i, result in enumerate(results, 1):
            memory = result.get("memory", "")
            metadata = result.get("metadata") or {}
            patient = metadata.get("patient_name", "Unknown")
            score = result.get("score", 0)
            rprint(f"   {i}. [{patient}] Connection Strength: {score:.3f}")
            rprint(f"      Memory Fragment: {memory[:100]}...")
            
            memory_connections.append({
                "patient": patient,
                "score": score,
                "fragment": memory[:100]
            })

        # Emit progress for streaming
        self.emit_progress("research", "progress", {
            "message": f"Iteration {iteration_num}: Found {len(results)} memories for '{query}'",
            "current_iteration": iteration_num,
            "search_term": query,
            "memories_found": len(results),
            "memory_connections": memory_connections
        })

        # Use the memory context from tracker if available, otherwise format manually
        if memory_context:
            context = memory_context
        else:
            # Fallback: Format for agent with memory IDs for citations
            context = ""
            for i, result in enumerate(results, 1):
                memory = result.get("memory", "")
                metadata = result.get("metadata") or {}
                patient = metadata.get("patient_name", "Unknown")
                memory_id = result.get("id", f"unknown_{i}")
                context += f"{i}. [ID:{memory_id}] [{patient}] {memory}\n"

        return results, context

    def execute_with_strategic_plan(
        self,
        question: str,
        strategic_plan: str,
        metadata_context: str = None,
        max_iterations: int = 5,
    ) -> tuple:
        """
        Execute research using strategic plan as guidance for iterative research.

        Args:
            question: The research question
            strategic_plan: Strategic research plan from ReWOO planner as guidance
            metadata_context: Database metadata context for enhanced decision making
            max_iterations: Maximum number of research iterations

        Returns:
            tuple: (final_answer, raw_results_list)
        """
        rprint(f"Starting research: {question}")

        # Execute strategic iterative research with plan guidance
        final_answer = self.strategic_research_loop(
            question, strategic_plan, metadata_context, max_iterations
        )

        # Return empty raw_results - strategic research doesn't track raw results currently
        return final_answer, []

    def strategic_research_loop(
        self,
        question: str,
        strategic_plan: str,
        metadata_context: str = None,
        max_iterations: int = 5,
    ) -> str:
        """
        Execute iterative research guided by strategic plan
        """
        rprint("Strategic research loop started")

        all_context = ""

        # Create enhanced decision agent that uses strategic plan
        enhanced_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="StrategicResearcher",
                content=MEMORY_ARCHAEOLOGIST_SYSTEM_PROMPT.format(
                    strategic_plan=strategic_plan
                ),
            ),
            model=self.model,
        )

        # Start with plan-guided initial search
        current_search = self.extract_initial_search_from_plan(strategic_plan, question)

        for iteration in range(1, max_iterations + 1):
            rprint(f"\nIteration {iteration}/{max_iterations}")

            # Search with current terms
            results, context = self.search_and_think(current_search, iteration)

            # Add to accumulated context
            if context != "No results found":
                all_context += (
                    f"\nStrategic Search {iteration} - '{current_search}':\n{context}\n"
                )

            # Get strategic decision from enhanced agent
            if iteration < max_iterations:
                decision_prompt = STRATEGIC_DECISION_PROMPT.format(
                    question=question,
                    strategic_plan=strategic_plan,
                    all_context=all_context,
                    iteration=iteration,
                )
                
                # Inject memory context with IDs into the decision prompt
                try:
                    enhanced_prompt = inject_memory_context(decision_prompt, "")
                except Exception as e:
                    rprint(f"Warning: Could not inject memory context: {e}")
                    enhanced_prompt = decision_prompt

                response = enhanced_agent.step(
                    BaseMessage.make_user_message(
                        role_name="User", content=enhanced_prompt
                    )
                )

                decision = response.msg.content
                rprint("\nStrategic Decision:")
                rprint(f"   {decision}")

                # Parse decision
                if "ENOUGH_INFO: YES" in decision:
                    rprint("Strategic research complete - enough information gathered!")
                    break

                # Extract next search
                next_search = None
                for line in decision.split("\n"):
                    if "NEXT_SEARCH:" in line:
                        next_search = line.split("NEXT_SEARCH:")[1].strip()
                        break

                if next_search:
                    current_search = next_search
                else:
                    rprint("No next search found, stopping strategic research")
                    break

        # Generate final strategic answer with full context
        rprint("Generating final report...")
        if all_context.strip():
            final_answer = self.answer_strategic_question(
                question, all_context, strategic_plan, metadata_context
            )
        else:
            final_answer = "I couldn't find relevant information in the database to answer your question using the strategic approach."

        return final_answer

    def extract_initial_search_from_plan(
        self, strategic_plan: str, question: str
    ) -> str:
        """Extract the best initial search term from strategic plan using LLM"""

        prompt = SEARCH_TERM_EXTRACTION_PROMPT.format(
            question=question, strategic_plan=strategic_plan
        )

        agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="SearchTermExtractor", content=SEARCH_TERM_EXTRACTION_SYSTEM
            ),
            model=self.model,
        )

        response = agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )

        extracted_term = response.msg.content.strip()
        rprint(f"LLM extracted initial search term: '{extracted_term}'")
        return extracted_term

    def answer_strategic_question(
        self,
        question: str,
        all_context: str,
        strategic_plan: str,
        metadata_context: str = None,
    ) -> str:
        """Generate final answer using complete strategic context"""

        context_section = f"""STRATEGIC RESEARCH QUESTION: {question}

STRATEGIC RESEARCH PLAN EXECUTED:
{strategic_plan}

ALL STRATEGIC RESEARCH FINDINGS:
{all_context}"""

        if metadata_context:
            context_section += f"""

DATABASE METADATA CONTEXT:
{metadata_context}

This metadata provided crucial context about:
- Database structure and content patterns
- Available fields and coverage levels
- Search optimization opportunities
- Data quality and limitations
"""

        prompt = STRATEGIC_MEMORY_ANALYSIS_PROMPT.format(
            context_section=context_section
        )
        
        # Inject memory context with IDs into the final answer prompt
        try:
            enhanced_prompt = inject_memory_context(prompt, "")
        except Exception as e:
            rprint(f"Warning: Could not inject memory context into final answer: {e}")
            enhanced_prompt = prompt

        agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="MemoryAnalyst", content=MEMORY_ANALYST_SYSTEM_PROMPT
            ),
            model=self.model,
        )

        response = agent.step(
            BaseMessage.make_user_message(role_name="User", content=enhanced_prompt)
        )
        return response.msg.content


def main():
    """Strategic research testing"""
    print("Strategic Memory Research Agent")
    print("Ask questions and I'll use strategic research to find answers")
    print("Type 'exit' to quit\n")

    agent = StrategicResearchAgent()

    while True:
        try:
            question = input("\nYour question: ").strip()

            if question.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not question:
                continue

            # Requires strategic plan - this is just for testing
            # In production, this comes from strategic_planner.py
            mock_plan = '{"research_intent": "Test strategic research", "phases": []}'

            # Do strategic research
            answer, raw_results = agent.execute_with_strategic_plan(question, mock_plan)

            print("\nFINAL ANSWER:")
            print(answer)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()