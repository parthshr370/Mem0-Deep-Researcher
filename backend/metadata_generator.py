import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Import utils for path setup
from utils import ROOT
from rich import print as rprint

from config.prompts import ANALYSIS_PROMPT_TEMPLATE, METADATA_ANALYZER_PROMPT

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from mem0.client.main import MemoryClient

# Cloud Client Setup
USER_ID = "doctor_memory"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MEM0_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing API keys in environment variables")


def get_filtered_memory_with_context(user_id: str = USER_ID, limit: int = 150):
    """
    Load filtered memories with ID tracking and context.
    Primary function for loading memories - consolidates all loading logic.
    
    Returns:
        tuple: (memories list, memory context string)
    """
    from memory_id_tracker import get_all_with_id_capture
    
    try:
        # Try using memory ID tracker for enhanced tracking
        memories, memory_context = get_all_with_id_capture(user_id=user_id, limit=limit)
        return memories, memory_context
    except Exception as e:
        rprint(f"Error with ID tracker, using fallback method: {e}")
        
        # Fallback: Direct mem0 client access
        rprint(f"Loading {limit} memories for user: {user_id}")
        client = MemoryClient(api_key=MEM0_API_KEY)
        
        memory = client.get_all(
            user_id=user_id,
            limit=limit,
            metadata={
                "summary_fact": True,
            },
        )
        
        filtered_memories = [
            {"id": mem["id"], "memory": mem["memory"], "metadata": mem["metadata"]}
            for mem in memory
        ]
        
        rprint(f"Retrieved {len(filtered_memories)} memories from database")
        return filtered_memories, ""  # Empty context in fallback

def get_filtered_memory(user_id: str = USER_ID, limit: int = 150):
    """Backward compatibility wrapper - returns just memories without context"""
    memories, _ = get_filtered_memory_with_context(user_id=user_id, limit=limit)
    return memories


# format that to a json for overview stuff
def get_database_metadata(filtered_memory=None):
    """
    Get database metadata analysis
    Returns: dict - metadata JSON or None if error
    """
    rprint("Analyzing database metadata...")
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-flash-lite",
        api_key=GEMINI_API_KEY,
        model_config_dict={"temperature": 0.3, "max_tokens": 100000},
    )

    metadata_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="MetadataAnalyzer",
            content=METADATA_ANALYZER_PROMPT,
        ),
        model=model,
    )

    if filtered_memory is None:
        filtered_memory = get_filtered_memory(USER_ID)

    analysis_prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        memory_data=json.dumps(filtered_memory, indent=2)
    )

    response = metadata_agent.step(
        BaseMessage.make_user_message(role_name="User", content=analysis_prompt)
    )

    rprint("Database analysis complete")
    rprint(response.msg.content)

    return response.msg.content


if __name__ == "__main__":
    # Direct execution for testing
    metadata = get_database_metadata()
    if metadata:
        print("Metadata Analysis:")
        print(metadata)
    else:
        print("Error: Could not generate metadata")
