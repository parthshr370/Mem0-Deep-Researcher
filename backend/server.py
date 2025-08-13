#!/usr/bin/env python3
"""
FastAPI server exposing the Deep Memory Research Pipeline for a simple frontend.

Endpoints:
- POST /api/research/run: Execute the pipeline synchronously for a question
- GET /api/health: Basic health check (env keys, artifacts dir)
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure local package modules (utils, main, etc.) are importable
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from utils import load_artifact
from main import DeepResearchOrchestrator


load_dotenv()

app = FastAPI(title="Deep Memory Research Backend", version="1.0")

# Allow local frontend by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    question: str
    user_id: Optional[str] = "doctor_memory"
    max_memories: Optional[int] = 100
    store_memories: Optional[bool] = False
    max_iterations: Optional[int] = 5


@app.get("/api/health")
def health() -> Dict[str, Any]:
    mem0 = os.getenv("MEM0_API_KEY")
    gemini = os.getenv("GEMINI_API_KEY")
    ok = bool(mem0 and gemini)
    return {
        "ok": ok,
        "has_MEM0_API_KEY": bool(mem0),
        "has_GEMINI_API_KEY": bool(gemini),
    }


@app.post("/api/research/run")
def run_research(req: RunRequest) -> Dict[str, Any]:
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    orchestrator = DeepResearchOrchestrator(
        user_id=req.user_id or "doctor_memory",
        max_memories=req.max_memories or 100,
    )

    # Capture pipeline logs to return to frontend for visual display
    import io
    import contextlib

    # Inject max_iterations by temporarily wrapping phase 3 call
    original_method = orchestrator.phase_3_strategic_deep_research
    def wrapped_phase_3(question: str, strategic_plan: str, metadata_context: str):
        return original_method(
            question,
            strategic_plan,
            metadata_context,
            max_iterations=req.max_iterations or 5,
        )
    orchestrator.phase_3_strategic_deep_research = wrapped_phase_3  # type: ignore

    buffer = io.StringIO()
    original_stdout = sys.stdout

    class Tee:
        def __init__(self, *streams):
            self.streams = streams
        def write(self, data):
            for s in self.streams:
                try:
                    s.write(data)
                except Exception:
                    pass
        def flush(self):
            for s in self.streams:
                try:
                    s.flush()
                except Exception:
                    pass

    tee = Tee(original_stdout, buffer)
    with contextlib.redirect_stdout(tee):
        result = orchestrator.run_complete_pipeline(req.question.strip())
    pipeline_logs = buffer.getvalue()
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Pipeline failed"))

    # Load selected artifacts for convenience
    artifacts = result.get("artifacts", {})
    response: Dict[str, Any] = {
        "success": True,
        "session_id": orchestrator.session_timestamp,
        "execution_time": result.get("execution_time"),
        "artifacts": artifacts,
        "final_answer": result.get("final_answer"),
        "logs": pipeline_logs,
    }

    # Try to parse metadata/plan when available
    metadata_path = artifacts.get("metadata")
    plan_path = artifacts.get("plan")
    analysis_path = artifacts.get("analysis_report")

    try:
        if metadata_path:
            response["metadata"] = load_artifact(metadata_path)
    except Exception:
        response["metadata"] = None

    try:
        if plan_path:
            response["plan"] = load_artifact(plan_path)
    except Exception:
        response["plan"] = None

    try:
        if analysis_path:
            response["analysis_report"] = load_artifact(analysis_path)
    except Exception:
        response["analysis_report"] = None

    # Optionally write memories back (Phase 5)
    if req.store_memories:
        try:
            stored = orchestrator.phase_5_memory_writing(req.question)
            response["memories_stored"] = stored
        except Exception as e:
            # Don't fail the request if optional memory write fails
            response["memories_stored_error"] = str(e)

    return response


@app.post("/api/research/stream")
def stream_research(req: RunRequest):
    """Stream research pipeline progress in real-time"""
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    def generate_progress():
        import threading
        import queue
        import time
        
        progress_queue = queue.Queue()
        
        class ProgressOrchestrator(DeepResearchOrchestrator):
            """Extends base orchestrator with progress reporting via queue"""
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.progress_queue = progress_queue
                
            def emit_progress(self, phase: str, status: str, data: Any = None):
                progress_data = {
                    "phase": phase,
                    "status": status,
                    "timestamp": time.time(),
                    "data": data
                }
                self.progress_queue.put(progress_data)
                
            def phase_1_metadata_analysis(self) -> str:
                """Override to add progress reporting"""
                self.emit_progress("metadata", "starting", {"message": "Loading memories from database"})
                
                # Load filtered memories
                filtered_memories = get_filtered_memory(
                    user_id=self.user_id, 
                    limit=self.max_memories
                )
                self.emit_progress("metadata", "progress", {
                    "message": f"Loaded {len(filtered_memories)} memories",
                    "count": len(filtered_memories)
                })
                
                self.emit_progress("metadata", "progress", {"message": "Analyzing database structure and patterns"})
                
                # Generate metadata analysis
                metadata_json = get_database_metadata(filtered_memory=filtered_memories)
                
                if not metadata_json:
                    raise ValueError("Failed to generate metadata analysis")
                    
                # Save metadata artifact
                metadata_path = save_artifact("metadata", metadata_json, ext="json")
                self.artifacts["metadata"] = metadata_path
                
                self.emit_progress("metadata", "completed", {
                    "message": "Database analysis complete",
                    "artifact_path": metadata_path,
                    "summary": json.loads(metadata_json).get("database_summary", {})
                })
                
                return metadata_json
                
            def phase_2_strategic_planning(self, question: str, metadata_json: str) -> str:
                self.emit_progress("planning", "starting", {"message": "Creating strategic research plan"})
                
                from rewoo_planner import ReWOOResearchPlanner
                planner = ReWOOResearchPlanner()
                
                research_plan = planner.create_research_plan(question, metadata_json)
                
                if "error" in research_plan.lower():
                    raise ValueError("Failed to create research plan")
                
                plan_path = save_artifact("plan", research_plan, ext="json")
                self.artifacts["plan"] = plan_path
                
                plan_data = json.loads(research_plan)
                self.emit_progress("planning", "completed", {
                    "message": "Strategic research plan created",
                    "artifact_path": plan_path,
                    "phases": plan_data.get("phases", []),
                    "strategy": plan_data.get("search_strategy", "")
                })
                
                return research_plan
                
            def phase_3_strategic_deep_research(self, question: str, strategic_plan: str, metadata_context: str, max_iterations: int = 5) -> tuple:
                self.emit_progress("research", "starting", {
                    "message": "Beginning strategic deep research",
                    "max_iterations": max_iterations
                })
                
                from strategic_react_agent import StrategicResearchAgent
                
                agent = StrategicResearchAgent()
                
                # Set up progress emission for the agent
                def emit_iteration_progress(iteration_num, search_term, memories_found, memory_connections):
                    self.emit_progress("research", "progress", {
                        "message": f"Iteration {iteration_num}: Searching '{search_term}'",
                        "current_iteration": iteration_num,
                        "search_term": search_term,
                        "memories_found": memories_found,
                        "memory_connections": memory_connections[:3] if memory_connections else []  # Show first 3 connections
                    })
                
                # Attach the emission method to the agent
                agent.emit_iteration_progress = emit_iteration_progress
                agent.set_progress_emitter(self.emit_progress)
                
                # Execute research with progress tracking
                final_answer, raw_results = agent.execute_with_strategic_plan(
                    question, strategic_plan, metadata_context, max_iterations=max_iterations
                )
                
                final_answer_path = save_artifact("final_answer", final_answer, ext="md")
                raw_results_path = save_jsonl_artifact("raw_results", raw_results)
                
                self.artifacts["final_answer"] = final_answer_path
                self.artifacts["raw_results"] = raw_results_path
                
                self.emit_progress("research", "completed", {
                    "message": "Research execution complete",
                    "final_answer": final_answer,
                    "artifact_paths": {
                        "final_answer": final_answer_path,
                        "raw_results": raw_results_path
                    },
                    "iterations_completed": len(raw_results),
                    "raw_results": raw_results
                })
                
                return final_answer, raw_results
                
            def phase_4_comprehensive_analysis(self, question: str, execution_time: float) -> str:
                self.emit_progress("analysis", "starting", {"message": "Performing comprehensive meta-analysis"})
                
                from meta_analysis_engine import AnalysisEngine
                analysis_engine = AnalysisEngine()
                
                analysis_report = analysis_engine.generate_comprehensive_report(
                    question=question,
                    artifacts_dict=self.artifacts,
                    execution_time=execution_time,
                    session_id=self.session_timestamp
                )
                
                analysis_path = save_artifact("analysis_report", analysis_report, ext="md")
                self.artifacts["analysis_report"] = analysis_path
                
                self.emit_progress("analysis", "completed", {
                    "message": "Meta-analysis complete",
                    "artifact_path": analysis_path
                })
                
                return analysis_report
        
        # Import required modules
        from utils import save_artifact, save_jsonl_artifact, get_timestamp, load_artifact
        from metadata_generator import get_database_metadata, get_filtered_memory
        
        def run_pipeline():
            try:
                orchestrator = ProgressOrchestrator(
                    user_id=req.user_id or "doctor_memory",
                    max_memories=req.max_memories or 100,
                )
                
                # Inject max_iterations
                original_method = orchestrator.phase_3_strategic_deep_research
                def wrapped_phase_3(question: str, strategic_plan: str, metadata_context: str):
                    return original_method(
                        question,
                        strategic_plan,
                        metadata_context,
                        max_iterations=req.max_iterations or 5,
                    )
                orchestrator.phase_3_strategic_deep_research = wrapped_phase_3
                
                result = orchestrator.run_complete_pipeline(req.question.strip())
                
                # Load all artifacts for final response
                final_response = {
                    "success": result.get("success"),
                    "session_id": result.get("session_id"),
                    "execution_time": result.get("execution_time"),
                    "artifacts": result.get("artifacts"),
                    "final_answer": result.get("final_answer"),
                }
                
                # Load and include artifact contents
                try:
                    if result.get("artifacts"):
                        # Load metadata if available
                        if "metadata" in result["artifacts"]:
                            metadata_content = load_artifact(result["artifacts"]["metadata"])
                            if metadata_content:
                                final_response["metadata"] = json.loads(metadata_content) if isinstance(metadata_content, str) else metadata_content
                        
                        # Load plan if available  
                        if "plan" in result["artifacts"]:
                            plan_content = load_artifact(result["artifacts"]["plan"])
                            if plan_content:
                                final_response["plan"] = json.loads(plan_content) if isinstance(plan_content, str) else plan_content
                        
                        # Load analysis report if available
                        if "analysis_report" in result["artifacts"]:
                            analysis_content = load_artifact(result["artifacts"]["analysis_report"])
                            if analysis_content:
                                final_response["analysis_report"] = analysis_content
                                
                        # Load raw results if available
                        if "raw_results" in result["artifacts"]:
                            raw_results_content = load_artifact(result["artifacts"]["raw_results"])
                            if raw_results_content:
                                final_response["raw_results"] = json.loads(raw_results_content) if isinstance(raw_results_content, str) else raw_results_content
                                
                except Exception as e:
                    # Log artifact loading errors but don't fail the whole response
                    print(f"Error loading artifacts: {e}")
                
                # Final completion message
                progress_queue.put({
                    "phase": "complete",
                    "status": "finished", 
                    "timestamp": time.time(),
                    "data": final_response
                })
                
            except Exception as e:
                progress_queue.put({
                    "phase": "error",
                    "status": "failed", 
                    "timestamp": time.time(),
                    "data": {"error": str(e)}
                })
        
        # Start pipeline in separate thread
        pipeline_thread = threading.Thread(target=run_pipeline)
        pipeline_thread.start()
        
        # Stream progress updates
        while True:
            try:
                progress = progress_queue.get(timeout=1)
                yield f"data: {json.dumps(progress)}\n\n"
                
                if progress["phase"] in ["complete", "error"]:
                    break
                    
            except queue.Empty:
                # Send heartbeat
                yield f"data: {json.dumps({'phase': 'heartbeat', 'status': 'alive', 'timestamp': time.time()})}\n\n"
                continue
        
        pipeline_thread.join()

    return StreamingResponse(
        generate_progress(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


# To run: uvicorn DEEP_RESEARCH_BACKEND.server:app --reload --port 8000


