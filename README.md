# **Deep Memory Research Agent**

A sophisticated **two-part AI system** that creates intelligent memory networks and performs deep research analysis through strategic memory exploration.

---

## **Project Architecture**

This project consists of **two main components** that work together to create an intelligent memory-aware research system:

### **Section 1: Memory Populator Pipeline**

**Location**: `backend/final_mem0_populator.py`

The **memory populator** creates synthetic medical conversations using a sophisticated **CAMEL agent dialogue system**. Think of it as a **doctor-patient conversation simulator** that generates unique, realistic medical consultations and stores them as structured memories.

**Key Features:**

- **Multi-agent conversation system** using CAMEL framework
- **Doctor-patient role-playing** with Dr. Sarah Chen as the attending physician
- **Synthetic patient generation** with unique medical conditions, demographics, and histories
- **Intelligent memory extraction** that converts conversations into structured medical facts
- **Mem0 storage integration** for persistent memory management

**How it works:**

1. **Patient Generation**: Creates unique patients with realistic medical conditions using structured LLM output
2. **Conversation Simulation**: Uses CAMEL RolePlaying society to generate authentic doctor-patient dialogues
3. **Memory Extraction**: Converts conversations into structured medical facts starting with patient names
4. **Mem0 Storage**: Stores extracted facts with metadata for future research and retrieval

---

### **Section 2: Deep Memory Research Engine**

**Location**: `backend/main.py` (orchestrator)

The **main research engine** takes user questions and performs **memory-aware deep research** through a sophisticated **5-phase pipeline**:

#### **Phase 1: Metadata Analysis**

- Analyzes the **entire mem0 database** to understand content patterns, coverage, and structure
- Generates **strategic metadata** about available information domains
- Creates **research optimization recommendations** based on database characteristics

#### **Phase 2: Strategic Planning**

- Takes user input and combines it with **database metadata**
- Uses **ReWOO planning methodology** to create multi-phase research strategies
- Generates **memory-aware research plans** that optimize for available data

#### **Phase 3: Strategic Deep Research**

- Implements **recursive memory exploration** using the strategic plan as guidance
- **Iterative search loops** with intelligent query refinement
- **Memory archaeology approach** that discovers connected information through relationship analysis
- **Strategic decision making** at each iteration to determine next search directions

#### **Phase 4: Meta-Analysis Engine**

- **Comprehensive analysis** of research methodology, data quality, and findings
- **Cross-validation** of results across multiple search iterations
- **Research quality assessment** and methodology evaluation

#### **Phase 5: Memory Writing (Optional)**

- Extracts **key research insights** from the analysis
- **Writes discoveries back** to mem0 for future research enhancement
- Creates **self-improving memory networks**

---

## **Technical Architecture**

### **Core Technologies**

- **CAMEL AI**: Multi-agent conversation framework for synthetic data generation
- **Mem0**: Persistent memory storage and retrieval system
- **Google Gemini**: Primary LLM for analysis and decision making
- **Rich**: Terminal interface and progress visualization
- **FastAPI**: Web server for frontend integration

### **Key Components**

| Component                  | Purpose               | Key Features                                                 |
| -------------------------- | --------------------- | ------------------------------------------------------------ |
| `final_mem0_populator.py`  | Memory population     | CAMEL agents, synthetic conversations, memory extraction     |
| `main.py`                  | Research orchestrator | 5-phase pipeline, progress tracking, artifact management     |
| `strategic_react_agent.py` | Memory exploration    | Iterative search, relationship analysis, strategic decisions |
| `rewoo_planner.py`         | Strategic planning    | ReWOO methodology, memory-aware planning                     |
| `meta_analysis_engine.py`  | Quality analysis      | Methodology evaluation, cross-validation, reporting          |
| `metadata_generator.py`    | Database analysis     | Content analysis, optimization recommendations               |

---

## **Installation & Setup**

### **Prerequisites**

```bash
# Python 3.8+
pip install -r backend/requirements.txt
```

### **Environment Configuration**

Create a `.env` file with:

```env
# Required API Keys
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_API_KEY=your_gemini_api_key  
MEM0_API_KEY=your_mem0_api_key

# Optional Configuration
USER_ID=doctor_memory
MAX_MEMORIES=100
```

### **Dependencies**

```bash
# Core AI frameworks
camel-ai
mem0ai

# LLM and API support
google-generativeai
python-dotenv

# Interface and data processing
rich
fastapi
uvicorn
```

---

## **Usage Guide**

### **Step 1: Populate Memory Database**

```bash
cd backend
python final_mem0_populator.py
```

This will:

- Generate **10 unique synthetic patients** with realistic medical conditions
- Create **doctor-patient conversations** using CAMEL multi-agent system
- Extract and store **structured medical memories** in mem0
- Display **progress and statistics** during population

**Sample Output:**

```
Patient: Elena Blackthorne (34y, female)
Condition: Type 1 Diabetes
Creating conversation...
Stored 7 medical facts
```

### **Step 2: Run Deep Research**

```bash
cd backend
python main.py
```

**Interactive Research Session:**

```
Deep Memory Research Pipeline
I'll help you research your mem0 memories comprehensively!

What would you like to research? > What are the most common symptoms across diabetic patients?

Research Question: What are the most common symptoms across diabetic patients?
Starting comprehensive research...

Phase 1: Database Analysis
Loaded 67 memories with ID tracking
Metadata analysis saved: artifacts/20250813_154201_metadata.json

Phase 2: Strategic Planning
Research plan saved: artifacts/20250813_154201_plan.json

Phase 3: Strategic Deep Research
Iteration 1/5
Searching: 'diabetes symptoms'
Found 12 connected memories
Strategic Decision: Continue with 'insulin management'

Phase 4: Meta-Analysis
Analysis report saved: artifacts/20250813_154201_analysis_report.md

Phase 5: Memory Writing
Do you want to store key insights as memories for future research? (y/n): y
Stored 5 research insights as memories
```

---

## **Web Interface (Optional)**

### **Backend Server**

```bash
uvicorn backend.server:app --reload --port 8000
```

### **Frontend Development**

```bash
cd frontend
npm install
npm run dev
```

Access the web interface at `http://localhost:3000`

---

## **Research Methodology**

### **Memory-Aware Research Approach**

The system uses a **novel "memory archaeology"** methodology:

1. **Strategic Metadata Analysis**: Understanding the knowledge landscape before searching
2. **Plan-Guided Exploration**: Using strategic plans to guide iterative memory traversal
3. **Relationship Discovery**: Finding connections between memories through iterative queries
4. **Evidence Synthesis**: Combining findings from multiple memory exploration paths
5. **Quality Meta-Analysis**: Evaluating research methodology and result reliability

### **Iterative Search Strategy**

- **Initial search** based on strategic plan analysis
- **Relationship exploration** through connected memory discovery
- **Strategic decision points** determining next search directions
- **Evidence accumulation** across multiple search iterations
- **Satisfaction criteria** for research completion

---

## **Output Artifacts**

Each research session generates comprehensive artifacts in `backend/artifacts/`:

| Artifact             | Description                                        |
| -------------------- | -------------------------------------------------- |
| `metadata.json`      | Database analysis and optimization recommendations |
| `plan.json`          | Strategic research plan with phases and approaches |
| `final_answer.md`    | Comprehensive research report with findings        |
| `raw_results.jsonl`  | Detailed search results and memory connections     |
| `analysis_report.md` | Meta-analysis of research quality and methodology  |

---

## **Advanced Configuration**

### **Memory Population Settings**

```python
# In final_mem0_populator.py
DOCTOR_MEMORY_ID = "doctor_memory"  # Memory namespace
for i in range(10):  # Number of patients to generate
    process_single_patient()
```

### **Research Pipeline Settings**

```python
# In main.py
orchestrator = DeepResearchOrchestrator(
    user_id="doctor_memory",  # Memory namespace
    max_memories=100          # Memory analysis limit
)
```

### **Search Strategy Configuration**

```python
# In strategic_react_agent.py
max_iterations = 5  # Maximum research iterations
search_limit = 5    # Memories per search iteration
```

---

## **Architecture Highlights**

### **Multi-Agent Conversation System**

- **CAMEL RolePlaying** framework for realistic doctor-patient dialogues
- **System message engineering** for consistent character behavior
- **Conversation flow management** with natural termination conditions

### **Memory-Aware Planning**

- **Database metadata integration** for search optimization
- **ReWOO planning methodology** for strategic research decomposition
- **Dynamic plan adaptation** based on discovered information

### **Iterative Research Engine**

- **Strategic decision making** at each research iteration
- **Memory relationship analysis** for connection discovery
- **Evidence synthesis** across multiple search paths

### **Comprehensive Analysis Pipeline**

- **Methodology evaluation** for research approach assessment
- **Data quality analysis** for result reliability
- **Cross-validation** across multiple evidence sources

---

## **Sample Research Prompts**

### **Medical Conditions & Treatment Analysis**
*"Analyze my approach to diabetes management across all diabetic patients over time. How have my medication choices, dosing strategies, and combination therapies evolved? Which patients showed the best HbA1c improvements and what specific treatment patterns led to those outcomes?"*

### **Diagnostic Patterns & Clinical Decision Making**
*"Examine cases where diagnosis was challenging or took multiple visits to establish. What initial symptoms or presentations led to extended diagnostic processes? How do I approach differential diagnosis when patients present with non-specific symptoms?"*

### **Patient Population Analysis**
*"Compare my treatment approaches between younger and older patients with similar conditions. How do I modify medication choices, dosing, and monitoring based on age-related factors?"*

### **Treatment Effectiveness & Outcomes**
*"Analyze patient responses to first-line treatments across common conditions in my practice. Which medications do patients tolerate best and show optimal therapeutic response?"*

---

## **Key Benefits**

1. **Intelligent Memory Networks**: Creates rich, interconnected knowledge bases through synthetic conversations
2. **Strategic Research Planning**: Uses database awareness to optimize research approaches
3. **Deep Memory Exploration**: Discovers hidden connections through iterative relationship analysis
4. **Research Quality Assurance**: Built-in meta-analysis for methodology and result validation
5. **Self-Improving System**: Optional memory writing creates expanding knowledge networks

---
