"""
Simple Memory ID Injection & Tracking System
- Captures memory IDs during search
- Injects them into every prompt
- Tracks all referenced memories in a file
- Uses LLM to add citations to final answer
"""

import os
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
from dotenv import load_dotenv
from mem0.client.main import MemoryClient
from rich import print as rprint

load_dotenv()


class MemoryIDTracker:
    """Simple tracker that captures and injects memory IDs"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.mem0_api_key = os.getenv("MEM0_API_KEY")
        self.client = MemoryClient(api_key=self.mem0_api_key)

        # File to track all memory-ID pairs for this session
        self.memory_file = f"/home/parthshr370/Downloads/DEEP_MEM/backend/artifacts/{session_id}_memory_references.json"
        self.memory_references = {}

    def search_and_capture(
        self, query: str, user_id: str, limit: int = 100
    ) -> Tuple[List[Dict], str]:
        """Search memories and capture IDs, return memories + prompt injection"""

        rprint(f"Searching memories for: {query[:50]}...")

        # Get memories with IDs
        memories = self.client.search(
            query=query, user_id=user_id, limit=limit, threshold=0.5
        )

        # Capture memory-ID pairs
        prompt_injection = "\n## MEMORY CONTEXT WITH IDs:\n"
        for i, mem in enumerate(memories, 1):
            memory_id = mem.get("id", f"unknown_{i}")
            memory_text = mem.get("memory", "")

            # Store the reference
            self.memory_references[memory_id] = {
                "memory": memory_text,
                "score": mem.get("score", 0.0),
                "metadata": mem.get("metadata", {}),
                "query_used": query,
            }

            # Add to prompt injection
            prompt_injection += f"[ID:{memory_id}] {memory_text}\n"

        # Save references to file
        self._save_references()

        rprint(f"Captured {len(memories)} memories with IDs")
        return memories, prompt_injection

    def get_all_and_capture(
        self, user_id: str, limit: int = 150
    ) -> Tuple[List[Dict], str]:
        """Get all memories and capture IDs for metadata analysis"""

        rprint("Getting all memories for metadata analysis...")

        memories = self.client.get_all(
            user_id=user_id, limit=limit, metadata={"summary_fact": True}
        )

        # Capture memory-ID pairs
        prompt_injection = "\n## ALL MEMORY CONTEXT WITH IDs:\n"
        for i, mem in enumerate(memories, 1):
            memory_id = mem.get("id", f"unknown_{i}")
            memory_text = mem.get("memory", "")

            # Store the reference
            self.memory_references[memory_id] = {
                "memory": memory_text,
                "metadata": mem.get("metadata", {}),
                "query_used": "metadata_analysis",
            }

            # Add to prompt injection
            prompt_injection += f"[ID:{memory_id}] {memory_text}\n"

        # Save references to file
        self._save_references()

        rprint(f"Captured {len(memories)} memories with IDs for metadata")
        return memories, prompt_injection

    def inject_into_prompt(self, base_prompt: str, memory_context: str) -> str:
        """Inject memory context with IDs into any prompt"""

        citation_instruction = """

## CITATION REQUIREMENTS:
When referencing any information from the memory context above, you MUST include the memory ID in square brackets like [ID:abc123].
This is critical for fact verification and source attribution.
        """

        return base_prompt + memory_context + citation_instruction

    def _save_references(self):
        """Save memory references to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

        with open(self.memory_file, "w") as f:
            json.dump(
                {
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "total_memories": len(self.memory_references),
                    "memory_references": self.memory_references,
                },
                f,
                indent=2,
            )

    def add_citations_to_final_answer(self, final_answer: str) -> str:
        """Use LLM to add proper citations to final answer based on tracked memories"""

        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType

        # Create citation prompt
        memory_list = ""
        for mem_id, mem_data in self.memory_references.items():
            memory_list += f"[ID:{mem_id}] {mem_data['memory']}\n"

        citation_prompt = f"""
You are a citation expert. Your job is to add proper memory ID citations to this research answer.

ORIGINAL ANSWER:
{final_answer}

AVAILABLE MEMORY REFERENCES:
{memory_list}

TASK:
1. Read the original answer carefully
2. For each factual claim or piece of information, find the corresponding memory reference
3. Add the memory ID citation in square brackets after the relevant information
4. Return the answer with proper citations added

CITATION FORMAT: Use [ID:memory_id] immediately after the information it supports.
EXAMPLE: "Diabetes affects 10% of adults [ID:abc123] and requires daily monitoring [ID:def456]."

Return ONLY the answer with citations added. Do not add any explanation or meta-commentary.
"""

        # Use LLM to add citations
        try:
            model = ModelFactory.create(
                model_platform=ModelPlatformType.GEMINI,
                model_type=ModelType.GEMINI_2_5_FLASH,
                api_key=os.getenv("GEMINI_API_KEY"),
                model_config_dict={"temperature": 0.1},
            )

            system_message = BaseMessage.make_assistant_message(
                role_name="CitationExpert",
                content="You add memory ID citations to research answers for proper source attribution.",
            )

            agent = ChatAgent(system_message=system_message, model=model)
            response = agent.step(
                BaseMessage.make_user_message("User", citation_prompt)
            )

            cited_answer = response.msg.content.strip()
            rprint("Added citations to final answer")
            return cited_answer

        except Exception as e:
            rprint(f"Error adding citations: {e}")
            return final_answer  # Return original if citation fails

    def get_memory_references_summary(self) -> Dict[str, Any]:
        """Get summary of all memory references used"""
        return {
            "total_memories_referenced": len(self.memory_references),
            "memory_file": self.memory_file,
            "session_id": self.session_id,
        }


# Global tracker instance (will be set by orchestrator)
current_tracker: MemoryIDTracker = None


def init_tracker(session_id: str):
    """Initialize the global tracker for a session"""
    global current_tracker
    current_tracker = MemoryIDTracker(session_id)
    rprint(f"Initialized Memory ID Tracker for session: {session_id}")


def search_with_id_capture(
    query: str, user_id: str, limit: int = 100
) -> Tuple[List[Dict], str]:
    """Search and capture - convenience function"""
    if not current_tracker:
        raise ValueError("Memory tracker not initialized!")
    return current_tracker.search_and_capture(query, user_id, limit)


def get_all_with_id_capture(user_id: str, limit: int = 150) -> Tuple[List[Dict], str]:
    """Get all and capture - convenience function"""
    if not current_tracker:
        raise ValueError("Memory tracker not initialized!")
    return current_tracker.get_all_and_capture(user_id, limit)


def inject_memory_context(base_prompt: str, memory_context: str) -> str:
    """Inject memory context into prompt - convenience function"""
    if not current_tracker:
        raise ValueError("Memory tracker not initialized!")
    return current_tracker.inject_into_prompt(base_prompt, memory_context)


def finalize_answer_with_citations(final_answer: str) -> str:
    """Add citations to final answer - convenience function"""
    if not current_tracker:
        raise ValueError("Memory tracker not initialized!")
    return current_tracker.add_citations_to_final_answer(final_answer)


def get_session_memory_summary() -> Dict[str, Any]:
    """Get memory usage summary - convenience function"""
    if not current_tracker:
        return {"error": "Memory tracker not initialized"}
    return current_tracker.get_memory_references_summary()
