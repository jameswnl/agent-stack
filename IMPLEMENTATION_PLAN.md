# LangGraph Chatbot with RAG + Research Workflows - Implementation Plan

## Context

Building a production-ready chatbot system that handles two primary use cases:
1. **Chatbot with RAG**: Answer questions using internal documentation (Markdown/Text files)
2. **Research Workflows**: Complex multi-step research including web search, log analysis, error diagnosis, and live system access via MCP

**Key Requirements:**
- TDD approach (Red → Green → Refactor)
- **Configurable, swappable LLM providers** (OpenAI, Anthropic, Ollama, Google, etc.)
- FAISS for vector store (in-memory, fast)
- Markdown/Text document ingestion
- Research capabilities: Web search, multi-step reasoning, source citation, log analysis, error diagnosis
- MCP integration for live system access
- **HTTP API server** (FastAPI) for service access
- Configuration-based provider selection
- **Multi-user support** with user isolation
- **Authentication & authorization** (JWT tokens, API keys)

**Project Location:** `~/ws/langgraph/`

---

## Architecture Overview

### Component Structure

```
langgraph/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── chatbot_agent.py          # Main agent with RAG + research
│   │   ├── graph.py                  # LangGraph state graph definition
│   │   └── state.py                  # Agent state management
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                   # Abstract provider interface
│   │   ├── openai_provider.py        # OpenAI implementation
│   │   ├── anthropic_provider.py     # Anthropic/Claude implementation
│   │   ├── ollama_provider.py        # Ollama local models
│   │   ├── google_provider.py        # Google Gemini
│   │   └── factory.py                # Provider factory/registry
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── rag_search.py             # RAG knowledge base search
│   │   ├── web_search.py             # Tavily/DuckDuckGo web search
│   │   ├── log_analyzer.py           # Log analysis tool
│   │   ├── error_diagnosis.py        # Error message diagnosis
│   │   └── mcp_tools.py              # MCP server integration
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── document_loader.py        # Load Markdown/Text files
│   │   ├── vector_store.py           # FAISS vector store management
│   │   └── embeddings.py             # Configurable embeddings
│   ├── research/
│   │   ├── __init__.py
│   │   ├── planner.py                # Research query planning
│   │   ├── synthesizer.py            # Multi-source synthesis
│   │   └── citation_tracker.py       # Source citation management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py                 # FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── chat.py               # Chat endpoints
│   │   │   ├── documents.py          # Document management
│   │   │   ├── users.py              # User management
│   │   │   └── health.py             # Health check
│   │   ├── models.py                 # Pydantic request/response models
│   │   ├── auth.py                   # Authentication utilities
│   │   ├── dependencies.py           # Dependency injection (current user, etc.)
│   │   └── middleware.py             # Auth middleware
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py                    # JWT token handling
│   │   ├── password.py               # Password hashing
│   │   └── models.py                 # User models
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py               # Database connection
│   │   ├── models.py                 # SQLAlchemy models
│   │   └── crud.py                   # CRUD operations
│   └── cli/
│       ├── __init__.py
│       └── chat.py                   # CLI interface for testing
├── tests/
│   ├── unit/
│   │   ├── test_rag_search.py
│   │   ├── test_web_search.py
│   │   ├── test_log_analyzer.py
│   │   ├── test_document_loader.py
│   │   ├── test_vector_store.py
│   │   └── test_agent.py
│   ├── integration/
│   │   ├── test_rag_pipeline.py
│   │   ├── test_research_workflow.py
│   │   └── test_mcp_integration.py
│   └── fixtures/
│       ├── sample_docs/              # Test markdown files
│       ├── sample_logs.txt           # Test log files
│       └── sample_errors.json        # Test error messages
├── docs/
│   └── knowledge_base/               # Actual docs for RAG
│       ├── getting_started.md
│       ├── troubleshooting.md
│       └── api_reference.md
├── config/
│   ├── config.yaml                   # Main configuration
│   ├── providers.yaml                # LLM provider configurations
│   └── mcp_servers.json              # MCP server configurations
├── data/
│   ├── faiss_index/                  # Shared vector store
│   ├── users/                        # User-specific data
│   │   └── {user_id}/
│   │       └── faiss_index/          # User-specific vector stores
│   └── chatbot.db                    # SQLite database for users/sessions
├── pyproject.toml                    # Dependencies
├── README.md
└── .env.example                      # Environment variables template
```

---

## Implementation Plan (TDD Approach)

### Phase 1: Project Setup & Infrastructure (Day 1)

**1.1 Initialize Project Structure**
- Create directory structure in `~/ws/langgraph/`
- Set up Python virtual environment
- Create `pyproject.toml` with dependencies:
  ```toml
  [tool.poetry]
  name = "langgraph-chatbot"
  version = "0.1.0"

  [tool.poetry.dependencies]
  python = "^3.11"
  langgraph = "^0.2.45"
  langchain = "^0.3.13"
  langchain-openai = "^0.2.12"
  langchain-anthropic = "^0.3.0"
  langchain-google-genai = "^2.0.8"
  langchain-community = "^0.3.13"
  faiss-cpu = "^1.9.0"
  python-dotenv = "^1.0.0"
  tavily-python = "^0.5.0"
  tiktoken = "^0.8.0"
  pyyaml = "^6.0.2"
  fastapi = "^0.115.6"
  uvicorn = "^0.34.0"
  pydantic = "^2.10.6"
  pydantic-settings = "^2.7.1"

  [tool.poetry.group.dev.dependencies]
  pytest = "^8.3.4"
  pytest-asyncio = "^0.24.0"
  pytest-cov = "^6.0.0"
  black = "^24.10.0"
  ruff = "^0.8.4"
  ```

- Create `.env.example`:
  ```env
  # LLM Provider API Keys
  OPENAI_API_KEY=your_key_here
  ANTHROPIC_API_KEY=your_key_here
  GOOGLE_API_KEY=your_key_here

  # Active provider (openai, anthropic, ollama, google)
  LLM_PROVIDER=openai

  # Research tools
  TAVILY_API_KEY=your_key_here

  # LangSmith observability
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=your_key_here
  LANGCHAIN_PROJECT=langgraph-chatbot

  # API Server
  API_HOST=0.0.0.0
  API_PORT=8000

  # Authentication
  JWT_SECRET_KEY=your_secret_key_here_change_in_production
  JWT_ALGORITHM=HS256
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
  JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

  # Database
  DATABASE_URL=sqlite:///./data/chatbot.db
  # For PostgreSQL: postgresql://user:password@localhost/dbname

  # Admin user (created on startup)
  ADMIN_EMAIL=admin@example.com
  ADMIN_PASSWORD=changeme
  ```

**1.2 Test Infrastructure Setup**
- Create `tests/conftest.py` with pytest fixtures:
  - Mock OpenAI client
  - Sample documents fixture
  - Sample log files fixture
  - FAISS vector store fixture

**1.3 Create Sample Test Data**
- `tests/fixtures/sample_docs/getting_started.md`
- `tests/fixtures/sample_logs.txt`
- `tests/fixtures/sample_errors.json`

---

### Phase 2: Provider Abstraction Layer (Day 1) - TDD

#### Test 2.1: Base Provider Interface (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_providers.py
def test_provider_interface():
    """Test that all providers implement the base interface"""
    from src.providers.base import BaseLLMProvider
    from src.providers.openai_provider import OpenAIProvider

    provider = OpenAIProvider(api_key="test_key", model="gpt-4o")

    # Check interface methods exist
    assert hasattr(provider, 'get_chat_model')
    assert hasattr(provider, 'get_embeddings')
    assert callable(provider.get_chat_model)

def test_provider_factory():
    """Test provider factory creates correct provider"""
    from src.providers.factory import ProviderFactory

    factory = ProviderFactory()

    # Create OpenAI provider
    provider = factory.create_provider(
        provider_type="openai",
        config={"api_key": "test", "model": "gpt-4o"}
    )

    assert provider is not None
    assert provider.provider_name == "openai"

def test_provider_swapping():
    """Test switching between providers"""
    from src.providers.factory import ProviderFactory

    factory = ProviderFactory()

    # Start with OpenAI
    provider1 = factory.create_provider("openai", {"api_key": "test1"})
    assert provider1.provider_name == "openai"

    # Switch to Anthropic
    provider2 = factory.create_provider("anthropic", {"api_key": "test2"})
    assert provider2.provider_name == "anthropic"
```

**GREEN - Implementation:**
```python
# src/providers/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """Return configured chat model"""
        pass

    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """Return configured embeddings model"""
        pass

    @property
    def model_name(self) -> str:
        """Return the model name"""
        return self.config.get("model", "default")

# src/providers/openai_provider.py
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from .base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""

    def get_chat_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.config.get("model", "gpt-4o"),
            temperature=self.config.get("temperature", 0.0),
            api_key=self.config.get("api_key"),
        )

    def get_embeddings(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model=self.config.get("embedding_model", "text-embedding-3-small"),
            api_key=self.config.get("api_key"),
        )

# src/providers/anthropic_provider.py
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings  # Use OpenAI for embeddings
from .base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    """Anthropic/Claude provider implementation"""

    def get_chat_model(self) -> ChatAnthropic:
        return ChatAnthropic(
            model=self.config.get("model", "claude-3-5-sonnet-20241022"),
            temperature=self.config.get("temperature", 0.0),
            api_key=self.config.get("api_key"),
        )

    def get_embeddings(self) -> OpenAIEmbeddings:
        # Anthropic doesn't have embeddings, use OpenAI
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.config.get("openai_api_key"),
        )

# src/providers/factory.py
from typing import Dict, Any
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

class ProviderFactory:
    """Factory for creating LLM providers"""

    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        # Add more providers as needed
    }

    def create_provider(
        self,
        provider_type: str,
        config: Dict[str, Any]
    ) -> BaseLLMProvider:
        """Create a provider instance"""
        provider_class = self._providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_type}")
        return provider_class(config)

    def list_providers(self) -> list:
        """List available providers"""
        return list(self._providers.keys())
```

#### Test 2.2: Configuration Loading (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_config.py
def test_load_provider_config():
    """Test loading provider configuration from YAML"""
    from src.config import load_provider_config

    config = load_provider_config("config/providers.yaml")

    assert "default_provider" in config
    assert "providers" in config
    assert "openai" in config["providers"]

def test_get_active_provider():
    """Test getting active provider from config"""
    from src.config import get_active_provider

    provider_name, provider_config = get_active_provider()

    assert provider_name in ["openai", "anthropic", "ollama", "google"]
    assert "api_key" in provider_config or "base_url" in provider_config
```

**GREEN - Implementation:**
```python
# src/config.py
import os
import yaml
from typing import Dict, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def load_provider_config(config_path: str = "config/providers.yaml") -> Dict[str, Any]:
    """Load provider configuration from YAML"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_active_provider() -> Tuple[str, Dict[str, Any]]:
    """Get active provider from environment and config"""
    # Load config
    config = load_provider_config()

    # Get provider from environment or use default
    provider_name = os.getenv("LLM_PROVIDER", config["default_provider"])

    # Get provider config
    provider_config = config["providers"][provider_name].copy()

    # Override with environment variables
    if provider_name == "openai":
        provider_config["api_key"] = os.getenv("OPENAI_API_KEY")
    elif provider_name == "anthropic":
        provider_config["api_key"] = os.getenv("ANTHROPIC_API_KEY")
        provider_config["openai_api_key"] = os.getenv("OPENAI_API_KEY")  # For embeddings
    # Add more providers...

    return provider_name, provider_config
```

**Create config/providers.yaml:**
```yaml
# Default provider
default_provider: openai

# Provider configurations
providers:
  openai:
    model: gpt-4o
    temperature: 0.0
    embedding_model: text-embedding-3-small
    max_tokens: 4096

  anthropic:
    model: claude-3-5-sonnet-20241022
    temperature: 0.0
    max_tokens: 8192

  ollama:
    base_url: http://localhost:11434
    model: llama3.2
    temperature: 0.0
    embedding_model: nomic-embed-text

  google:
    model: gemini-2.0-flash-exp
    temperature: 0.0
```

---

### Phase 3: RAG Foundation (Day 1-2) - TDD

#### Test 2.1: Document Loader (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_document_loader.py
def test_load_markdown_file():
    loader = DocumentLoader()
    docs = loader.load_file("tests/fixtures/sample_docs/getting_started.md")

    assert len(docs) > 0
    assert docs[0].page_content != ""
    assert docs[0].metadata["source"] == "getting_started.md"

def test_load_directory():
    loader = DocumentLoader()
    docs = loader.load_directory("tests/fixtures/sample_docs/")

    assert len(docs) >= 1
    assert all(doc.metadata.get("source") for doc in docs)
```

**GREEN - Implementation:**
```python
# src/rag/document_loader.py
from pathlib import Path
from typing import List
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document

class DocumentLoader:
    def load_file(self, file_path: str) -> List[Document]:
        """Load a single markdown/text file"""
        # Implementation here

    def load_directory(self, dir_path: str) -> List[Document]:
        """Load all markdown/text files from directory"""
        # Implementation here
```

#### Test 2.2: Vector Store (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_vector_store.py
def test_create_vector_store(sample_documents):
    store = VectorStoreManager()
    vectorstore = store.create_from_documents(sample_documents)

    assert vectorstore is not None
    results = vectorstore.similarity_search("test query", k=3)
    assert len(results) <= 3

def test_persist_and_load_vector_store(sample_documents, tmp_path):
    store = VectorStoreManager()
    vectorstore = store.create_from_documents(sample_documents)

    # Persist
    store.persist(vectorstore, str(tmp_path / "faiss_index"))

    # Load
    loaded = store.load(str(tmp_path / "faiss_index"))
    results = loaded.similarity_search("test query", k=1)
    assert len(results) > 0
```

**GREEN - Implementation:**
```python
# src/rag/vector_store.py
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class VectorStoreManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def create_from_documents(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        # Implementation here

    def persist(self, vectorstore: FAISS, path: str) -> None:
        """Save vector store to disk"""
        # Implementation here

    def load(self, path: str) -> FAISS:
        """Load vector store from disk"""
        # Implementation here
```

#### Test 2.3: RAG Search Tool (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_rag_search.py
def test_rag_search_tool(vectorstore_fixture):
    tool = RAGSearchTool(vectorstore_fixture)

    result = tool.invoke({"query": "How do I get started?"})

    assert result is not None
    assert "content" in result
    assert "sources" in result
    assert len(result["sources"]) > 0

def test_rag_search_with_relevance_threshold(vectorstore_fixture):
    tool = RAGSearchTool(vectorstore_fixture, relevance_threshold=0.7)

    result = tool.invoke({"query": "unrelated query xyz123"})

    # Should return fewer results due to threshold
    assert len(result["sources"]) >= 0
```

**GREEN - Implementation:**
```python
# src/tools/rag_search.py
from langchain_core.tools import tool
from typing import Dict, Any, List

@tool
def rag_search(query: str, k: int = 3) -> Dict[str, Any]:
    """Search the knowledge base for relevant information.

    Args:
        query: The search query
        k: Number of results to return

    Returns:
        Dict with 'content' (formatted results) and 'sources' (metadata)
    """
    # Implementation here
    pass

class RAGSearchTool:
    def __init__(self, vectorstore, relevance_threshold: float = 0.5):
        self.vectorstore = vectorstore
        self.relevance_threshold = relevance_threshold

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RAG search with relevance filtering"""
        # Implementation here
```

---

### Phase 3: Research Tools (Day 2-3) - TDD

#### Test 3.1: Web Search Tool (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_web_search.py
@pytest.mark.asyncio
async def test_web_search_tavily(mock_tavily_client):
    tool = WebSearchTool(provider="tavily")

    result = await tool.ainvoke({"query": "LangGraph documentation"})

    assert "results" in result
    assert len(result["results"]) > 0
    assert "url" in result["results"][0]
    assert "content" in result["results"][0]

def test_web_search_cites_sources():
    tool = WebSearchTool()
    result = tool.invoke({"query": "test query", "max_results": 3})

    assert "citations" in result
    assert len(result["citations"]) <= 3
```

**GREEN - Implementation:**
```python
# src/tools/web_search.py
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Dict, Any

class WebSearchTool:
    def __init__(self, provider: str = "tavily", max_results: int = 5):
        if provider == "tavily":
            self.search = TavilySearchResults(max_results=max_results)
        # Could add DuckDuckGo as fallback

    async def ainvoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search and format results with citations"""
        # Implementation here
```

#### Test 3.2: Log Analyzer Tool (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_log_analyzer.py
def test_analyze_log_file():
    analyzer = LogAnalyzerTool()

    result = analyzer.invoke({
        "log_content": "ERROR: Connection timeout\nINFO: Retry attempt 1\nERROR: Connection failed",
        "analysis_type": "errors"
    })

    assert "error_count" in result
    assert result["error_count"] == 2
    assert "patterns" in result

def test_extract_error_context():
    analyzer = LogAnalyzerTool()

    result = analyzer.invoke({
        "log_content": "...\nERROR: Database connection failed\n...",
        "context_lines": 2
    })

    assert "errors" in result
    assert len(result["errors"]) > 0
    assert "context" in result["errors"][0]
```

**GREEN - Implementation:**
```python
# src/tools/log_analyzer.py
import re
from typing import Dict, Any, List

class LogAnalyzerTool:
    def __init__(self):
        self.error_pattern = re.compile(r"ERROR|FATAL|CRITICAL", re.IGNORECASE)
        self.warn_pattern = re.compile(r"WARN|WARNING", re.IGNORECASE)

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze log content and extract errors, warnings, patterns"""
        # Implementation here

    def extract_errors_with_context(self, log_lines: List[str], context_lines: int = 3) -> List[Dict]:
        """Extract errors with surrounding context"""
        # Implementation here
```

#### Test 3.3: Error Diagnosis Tool (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_error_diagnosis.py
def test_diagnose_error_message():
    diagnoser = ErrorDiagnosisTool()

    result = diagnoser.invoke({
        "error_message": "ModuleNotFoundError: No module named 'langchain'",
        "context": {"language": "python", "environment": "production"}
    })

    assert "diagnosis" in result
    assert "possible_causes" in result
    assert "suggested_fixes" in result
    assert len(result["suggested_fixes"]) > 0

def test_categorize_error_type():
    diagnoser = ErrorDiagnosisTool()

    error_types = [
        ("FileNotFoundError", "io"),
        ("ConnectionRefusedError", "network"),
        ("MemoryError", "resource"),
    ]

    for error, expected_category in error_types:
        result = diagnoser.categorize_error(error)
        assert result["category"] == expected_category
```

**GREEN - Implementation:**
```python
# src/tools/error_diagnosis.py
from typing import Dict, Any, List

class ErrorDiagnosisTool:
    def __init__(self):
        self.error_patterns = {
            "import": r"(ModuleNotFoundError|ImportError)",
            "network": r"(ConnectionError|Timeout)",
            "io": r"(FileNotFoundError|PermissionError)",
            # More patterns...
        }

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose error message and suggest fixes"""
        # Implementation here

    def categorize_error(self, error_message: str) -> Dict[str, str]:
        """Categorize error type"""
        # Implementation here
```

#### Test 3.4: MCP Tools Integration (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_mcp_tools.py
@pytest.mark.asyncio
async def test_mcp_server_connection(mock_mcp_server):
    mcp_manager = MCPToolsManager()

    await mcp_manager.connect("test_server", "http://localhost:3000")

    assert mcp_manager.is_connected("test_server")
    tools = await mcp_manager.list_tools("test_server")
    assert len(tools) > 0

@pytest.mark.asyncio
async def test_mcp_tool_execution(mock_mcp_server):
    mcp_manager = MCPToolsManager()
    await mcp_manager.connect("test_server", "http://localhost:3000")

    result = await mcp_manager.execute_tool(
        server="test_server",
        tool_name="get_system_status",
        args={}
    )

    assert result is not None
    assert "status" in result
```

**GREEN - Implementation:**
```python
# src/tools/mcp_tools.py
from typing import Dict, Any, List, Optional
import httpx

class MCPToolsManager:
    """Manager for MCP (Model Context Protocol) server connections"""

    def __init__(self):
        self.connections: Dict[str, httpx.AsyncClient] = {}
        self.server_configs: Dict[str, Dict[str, Any]] = {}

    async def connect(self, server_name: str, url: str) -> None:
        """Connect to an MCP server"""
        # Implementation here

    def is_connected(self, server_name: str) -> bool:
        """Check if connected to server"""
        # Implementation here

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools from MCP server"""
        # Implementation here

    async def execute_tool(self, server: str, tool_name: str, args: Dict) -> Any:
        """Execute a tool on MCP server"""
        # Implementation here
```

---

### Phase 4: Research Orchestration (Day 3-4) - TDD

#### Test 4.1: Research Planner (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_planner.py
def test_create_research_plan():
    planner = ResearchPlanner()

    plan = planner.create_plan(
        query="Compare LangGraph and LangChain for production use",
        available_tools=["web_search", "rag_search"]
    )

    assert "steps" in plan
    assert len(plan["steps"]) > 0
    assert all("action" in step for step in plan["steps"])
    assert all("tool" in step for step in plan["steps"])

def test_multi_step_research_plan():
    planner = ResearchPlanner()

    plan = planner.create_plan(
        query="Debug error in production logs and suggest fix",
        available_tools=["mcp_access", "log_analyzer", "error_diagnosis"]
    )

    # Should have multiple steps
    assert len(plan["steps"]) >= 3
    # Should use appropriate tools
    tool_names = [step["tool"] for step in plan["steps"]]
    assert "log_analyzer" in tool_names
    assert "error_diagnosis" in tool_names
```

**GREEN - Implementation:**
```python
# src/research/planner.py
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ResearchPlanner:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research planning assistant..."),
            ("user", "{query}")
        ])

    def create_plan(self, query: str, available_tools: List[str]) -> Dict[str, Any]:
        """Create a multi-step research plan"""
        # Implementation here
```

#### Test 4.2: Citation Tracker (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_citation_tracker.py
def test_track_source():
    tracker = CitationTracker()

    tracker.add_source(
        content="LangGraph is a framework...",
        metadata={"url": "https://example.com", "title": "LangGraph Guide"}
    )

    citations = tracker.get_citations()
    assert len(citations) == 1
    assert citations[0]["title"] == "LangGraph Guide"

def test_format_citations():
    tracker = CitationTracker()
    tracker.add_source("Content 1", {"url": "https://a.com", "title": "A"})
    tracker.add_source("Content 2", {"url": "https://b.com", "title": "B"})

    formatted = tracker.format_citations(style="markdown")

    assert "[1]" in formatted
    assert "[2]" in formatted
    assert "https://a.com" in formatted
```

**GREEN - Implementation:**
```python
# src/research/citation_tracker.py
from typing import Dict, Any, List

class CitationTracker:
    def __init__(self):
        self.sources: List[Dict[str, Any]] = []

    def add_source(self, content: str, metadata: Dict[str, Any]) -> int:
        """Add a source and return citation number"""
        # Implementation here

    def get_citations(self) -> List[Dict[str, Any]]:
        """Get all tracked citations"""
        # Implementation here

    def format_citations(self, style: str = "markdown") -> str:
        """Format citations in specified style"""
        # Implementation here
```

---

### Phase 5: Agent Graph (Day 4-5) - TDD

#### Test 5.1: Agent State (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_agent.py
def test_agent_state_initialization():
    state = AgentState(
        messages=[],
        user_query="Test query",
        research_plan=None
    )

    assert state.messages == []
    assert state.user_query == "Test query"
    assert state.research_plan is None

def test_agent_state_with_context():
    state = AgentState(
        messages=[{"role": "user", "content": "Hello"}],
        user_query="Follow-up question",
        context={"previous_results": ["result1"]}
    )

    assert len(state.messages) == 1
    assert "previous_results" in state.context
```

**GREEN - Implementation:**
```python
# src/agent/state.py
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """State for the chatbot agent"""
    messages: Annotated[List[Dict[str, Any]], add_messages]
    user_query: str
    research_plan: Optional[Dict[str, Any]]
    rag_results: Optional[List[Dict[str, Any]]]
    web_results: Optional[List[Dict[str, Any]]]
    citations: List[Dict[str, Any]]
    context: Dict[str, Any]
    next_action: Optional[str]
```

#### Test 5.2: Agent Graph (RED → GREEN)

**RED - Write failing test:**
```python
# tests/integration/test_agent_graph.py
@pytest.mark.asyncio
async def test_simple_rag_query(vectorstore_fixture):
    graph = create_chatbot_graph(vectorstore=vectorstore_fixture)

    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": "How do I get started?"}],
        "user_query": "How do I get started?",
    })

    assert "messages" in result
    assert len(result["messages"]) > 1
    assert result["messages"][-1]["role"] == "assistant"
    assert len(result["citations"]) > 0

@pytest.mark.asyncio
async def test_research_workflow(vectorstore_fixture, mock_web_search):
    graph = create_chatbot_graph(
        vectorstore=vectorstore_fixture,
        enable_web_search=True
    )

    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": "Research latest LangGraph features"}],
        "user_query": "Research latest LangGraph features",
    })

    # Should use both RAG and web search
    assert result.get("rag_results") is not None
    assert result.get("web_results") is not None
    assert len(result["citations"]) > 0
```

**GREEN - Implementation:**
```python
# src/agent/graph.py
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Dict, Any

def create_chatbot_graph(
    vectorstore,
    enable_web_search: bool = True,
    enable_mcp: bool = False
):
    """Create the main agent graph"""

    workflow = StateGraph(AgentState)

    # Define nodes
    workflow.add_node("classify_query", classify_query_node)
    workflow.add_node("rag_search", rag_search_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("synthesize", synthesize_node)
    workflow.add_node("respond", respond_node)

    # Define edges
    workflow.set_entry_point("classify_query")

    # Conditional routing
    workflow.add_conditional_edges(
        "classify_query",
        route_query,
        {
            "rag_only": "rag_search",
            "research": "web_search",
            "both": "rag_search"
        }
    )

    workflow.add_edge("rag_search", "synthesize")
    workflow.add_edge("web_search", "synthesize")
    workflow.add_edge("synthesize", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()

def classify_query_node(state: AgentState) -> AgentState:
    """Classify whether query needs RAG, web search, or both"""
    # Implementation here

def rag_search_node(state: AgentState) -> AgentState:
    """Execute RAG search"""
    # Implementation here

def web_search_node(state: AgentState) -> AgentState:
    """Execute web search"""
    # Implementation here

def synthesize_node(state: AgentState) -> AgentState:
    """Synthesize results from multiple sources"""
    # Implementation here

def respond_node(state: AgentState) -> AgentState:
    """Generate final response with citations"""
    # Implementation here
```

---

### Phase 6: Authentication & Multi-User Support (Day 5) - TDD

#### Test 6.1: User Authentication (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_auth.py
def test_create_access_token():
    """Test JWT token creation"""
    from src.auth.jwt import create_access_token

    token = create_access_token(data={"sub": "user@example.com"})

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_token():
    """Test JWT token verification"""
    from src.auth.jwt import create_access_token, verify_token

    token = create_access_token(data={"sub": "user@example.com"})
    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "user@example.com"

def test_password_hashing():
    """Test password hashing and verification"""
    from src.auth.password import hash_password, verify_password

    password = "testpassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False
```

**GREEN - Implementation:**
```python
# src/auth/jwt.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# src/auth/password.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

#### Test 6.2: User Database Models (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_db_models.py
def test_create_user():
    """Test user creation in database"""
    from src.db.crud import create_user
    from src.db.database import get_db

    db = next(get_db())

    user = create_user(
        db=db,
        email="test@example.com",
        password="testpass123",
        full_name="Test User"
    )

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password != "testpass123"
    assert user.is_active is True

def test_get_user_by_email():
    """Test retrieving user by email"""
    from src.db.crud import create_user, get_user_by_email
    from src.db.database import get_db

    db = next(get_db())

    # Create user
    create_user(db, "test@example.com", "pass123")

    # Retrieve user
    user = get_user_by_email(db, "test@example.com")

    assert user is not None
    assert user.email == "test@example.com"
```

**GREEN - Implementation:**
```python
# src/db/models.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")

# src/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

# src/db/crud.py
from sqlalchemy.orm import Session
from typing import Optional
from .models import User, Conversation
from ..auth.password import hash_password

def create_user(db: Session, email: str, password: str, full_name: str = None) -> User:
    """Create a new user"""
    hashed_password = hash_password(password)
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()
```

#### Test 6.3: User Isolation - Vector Stores (RED → GREEN)

**RED - Write failing test:**
```python
# tests/unit/test_user_isolation.py
def test_user_specific_vector_store(tmp_path):
    """Test that each user has their own vector store"""
    from src.rag.vector_store import VectorStoreManager

    manager = VectorStoreManager()

    # User 1 vector store
    user1_path = tmp_path / "user_1"
    user1_vectorstore = manager.create_from_documents(sample_docs_user1)
    manager.persist(user1_vectorstore, str(user1_path))

    # User 2 vector store
    user2_path = tmp_path / "user_2"
    user2_vectorstore = manager.create_from_documents(sample_docs_user2)
    manager.persist(user2_vectorstore, str(user2_path))

    # Verify isolation
    user1_loaded = manager.load(str(user1_path))
    user2_loaded = manager.load(str(user2_path))

    results1 = user1_loaded.similarity_search("user1 content")
    results2 = user2_loaded.similarity_search("user2 content")

    # Results should be different
    assert results1 != results2
```

**GREEN - Implementation:**
```python
# src/rag/vector_store.py (updated)
from pathlib import Path

class VectorStoreManager:
    # ... existing code ...

    def get_user_vectorstore_path(self, user_id: int) -> str:
        """Get path for user-specific vector store"""
        path = Path(f"./data/users/{user_id}/faiss_index")
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    def load_user_vectorstore(self, user_id: int) -> Optional[FAISS]:
        """Load user-specific vector store"""
        path = self.get_user_vectorstore_path(user_id)
        try:
            return self.load(path)
        except:
            return None

    def save_user_vectorstore(self, user_id: int, vectorstore: FAISS) -> None:
        """Save user-specific vector store"""
        path = self.get_user_vectorstore_path(user_id)
        self.persist(vectorstore, path)
```

#### Test 6.4: Authentication Endpoints (RED → GREEN)

**RED - Write failing test:**
```python
# tests/integration/test_auth_api.py
from fastapi.testclient import TestClient

def test_register_user():
    """Test user registration"""
    from src.api.server import app

    client = TestClient(app)
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "testpass123",
        "full_name": "New User"
    })

    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login():
    """Test user login"""
    from src.api.server import app

    client = TestClient(app)

    # Register user first
    client.post("/api/v1/auth/register", json={
        "email": "logintest@example.com",
        "password": "testpass123"
    })

    # Login
    response = client.post("/api/v1/auth/login", data={
        "username": "logintest@example.com",
        "password": "testpass123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint_requires_auth():
    """Test that protected endpoints require authentication"""
    from src.api.server import app

    client = TestClient(app)
    response = client.post("/api/v1/chat", json={
        "message": "Hello",
        "conversation_id": None
    })

    assert response.status_code == 401

def test_protected_endpoint_with_auth():
    """Test authenticated access to protected endpoint"""
    from src.api.server import app

    client = TestClient(app)

    # Register and get token
    reg_response = client.post("/api/v1/auth/register", json={
        "email": "authtest@example.com",
        "password": "testpass123"
    })
    token = reg_response.json()["access_token"]

    # Access protected endpoint
    response = client.post(
        "/api/v1/chat",
        json={"message": "Hello", "conversation_id": None},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
```

**GREEN - Implementation:**
```python
# src/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from ...db.database import get_db
from ...db.crud import create_user, get_user_by_email
from ...auth.jwt import create_access_token
from ...auth.password import verify_password

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool

@router.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create user
    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    # Get user
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

# src/api/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.crud import get_user_by_email
from ..auth.jwt import verify_token
from .routes.auth import oauth2_scheme

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Get user
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

---

### Phase 7: HTTP API Server (Day 6) - TDD

#### Test 7.1: FastAPI Server Setup (RED → GREEN)

**RED - Write failing test:**
```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient

def test_api_health_endpoint():
    """Test health check endpoint"""
    from src.api.server import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_providers_endpoint():
    """Test list providers endpoint"""
    from src.api.server import app

    client = TestClient(app)
    response = client.get("/api/v1/providers")

    assert response.status_code == 200
    assert "providers" in response.json()
    assert len(response.json()["providers"]) > 0
```

**GREEN - Implementation:**
```python
# src/api/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import chat, documents, health, auth
from ..config import load_provider_config
from ..rag.vector_store import VectorStoreManager
from ..db.database import init_db

logger = logging.getLogger(__name__)

# Global state
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown"""
    # Startup
    logger.info("Initializing application...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Initialize vector store manager
    store_manager = VectorStoreManager()
    app_state["store_manager"] = store_manager

    yield

    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="LangGraph Chatbot API",
    description="Multi-user RAG-enabled chatbot with research capabilities",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])

# Get app state
def get_app_state():
    return app_state

# src/api/routes/health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}

@router.get("/api/v1/providers")
async def list_providers():
    """List available LLM providers"""
    from src.providers.factory import ProviderFactory
    from src.config import get_active_provider

    factory = ProviderFactory()
    active_provider, _ = get_active_provider()

    return {
        "providers": factory.list_providers(),
        "active_provider": active_provider
    }
```

#### Test 7.2: Chat Endpoint with Authentication (RED → GREEN)

**RED - Write failing test:**
```python
# tests/integration/test_api.py
def test_chat_endpoint_requires_auth(vectorstore_fixture):
    """Test chat endpoint requires authentication"""
    from src.api.server import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "How do I get started?",
            "conversation_id": "test-123"
        }
    )

    assert response.status_code == 401

def test_chat_endpoint_with_auth(vectorstore_fixture, test_user_token):
    """Test chat endpoint with authenticated user"""
    from src.api.server import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "How do I get started?",
            "conversation_id": "test-123"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "citations" in data
    assert len(data["citations"]) > 0

def test_chat_streaming_endpoint(vectorstore_fixture):
    """Test streaming chat endpoint"""
    from src.api.server import app, app_state

    app_state["vectorstore"] = vectorstore_fixture

    client = TestClient(app)
    with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"message": "Test query"}
    ) as response:
        assert response.status_code == 200

        chunks = []
        for line in response.iter_lines():
            if line:
                chunks.append(line)

        assert len(chunks) > 0
```

**GREEN - Implementation:**
```python
# src/api/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    provider: Optional[str] = Field(None, description="Override default LLM provider")
    enable_web_search: bool = Field(True, description="Enable web search for research")

class Citation(BaseModel):
    source: str
    content: str
    url: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    citations: List[Citation]
    conversation_id: str
    provider_used: str

# src/api/routes/chat.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
from sqlalchemy.orm import Session
import json

from ..models import ChatRequest, ChatResponse
from ..server import get_app_state
from ..dependencies import get_current_active_user
from ...db.database import get_db
from ...db.models import User
from ...agent.graph import create_chatbot_graph
from ...providers.factory import ProviderFactory
from ...config import get_active_provider
from ...rag.vector_store import VectorStoreManager

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat endpoint with RAG and research capabilities (authenticated)"""
    app_state = get_app_state()
    store_manager = app_state.get("store_manager")

    if not store_manager:
        raise HTTPException(status_code=503, detail="Vector store manager not initialized")

    # Load user-specific vector store
    vectorstore = store_manager.load_user_vectorstore(current_user.id)

    if not vectorstore:
        raise HTTPException(
            status_code=404,
            detail="No documents indexed for this user. Please upload documents first."
        )

    # Get provider
    if request.provider:
        provider_name = request.provider
        from ...config import load_provider_config
        config = load_provider_config()
        provider_config = config["providers"][provider_name]
    else:
        provider_name, provider_config = get_active_provider()

    # Create agent graph
    graph = create_chatbot_graph(
        vectorstore=vectorstore,
        provider_name=provider_name,
        provider_config=provider_config,
        enable_web_search=request.enable_web_search
    )

    # Execute query
    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": request.message}],
        "user_query": request.message,
    })

    # Format response
    response_text = result["messages"][-1]["content"]
    citations = [
        {
            "source": c.get("source", ""),
            "content": c.get("content", ""),
            "url": c.get("url")
        }
        for c in result.get("citations", [])
    ]

    return ChatResponse(
        response=response_text,
        citations=citations,
        conversation_id=request.conversation_id or "default",
        provider_used=provider_name
    )

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    app_state = get_app_state()
    vectorstore = app_state.get("vectorstore")

    if not vectorstore:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events"""
        # Get provider
        provider_name, provider_config = get_active_provider()

        # Create graph
        graph = create_chatbot_graph(
            vectorstore=vectorstore,
            provider_name=provider_name,
            provider_config=provider_config
        )

        # Stream events
        async for event in graph.astream({
            "messages": [{"role": "user", "content": request.message}],
            "user_query": request.message,
        }):
            yield f"data: {json.dumps(event)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

#### Test 7.3: Document Management Endpoint with Authentication (RED → GREEN)

**RED - Write failing test:**
```python
# tests/integration/test_api.py
def test_index_documents_requires_auth(tmp_path):
    """Test document indexing requires authentication"""
    from src.api.server import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/index",
        json={"source_path": "docs/knowledge_base/"}
    )

    assert response.status_code == 401

def test_index_documents_with_auth(tmp_path, test_user_token):
    """Test document indexing with authenticated user"""
    from src.api.server import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/index",
        json={"source_path": "docs/knowledge_base/"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "document_count" in data
    assert data["document_count"] > 0

def test_user_document_isolation(test_user1_token, test_user2_token):
    """Test that users have isolated document stores"""
    from src.api.server import app

    client = TestClient(app)

    # User 1 indexes documents
    response1 = client.post(
        "/api/v1/documents/index",
        json={"source_path": "tests/fixtures/user1_docs/"},
        headers={"Authorization": f"Bearer {test_user1_token}"}
    )
    assert response1.status_code == 200

    # User 2 should not see User 1's documents in search
    response2 = client.post(
        "/api/v1/chat",
        json={"message": "user1 specific content"},
        headers={"Authorization": f"Bearer {test_user2_token}"}
    )
    # Should not find user1's content
    assert "user1 specific content" not in response2.json()["response"]
```

**GREEN - Implementation:**
```python
# src/api/routes/documents.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from ..server import get_app_state
from ..dependencies import get_current_active_user
from ...db.database import get_db
from ...db.models import User
from ...rag.document_loader import DocumentLoader

router = APIRouter()

class IndexRequest(BaseModel):
    source_path: str
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200

class IndexResponse(BaseModel):
    status: str
    document_count: int
    chunk_count: int
    user_id: int

@router.post("/documents/index", response_model=IndexResponse)
async def index_documents(
    request: IndexRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Index documents for the authenticated user"""
    app_state = get_app_state()
    store_manager = app_state.get("store_manager")

    if not store_manager:
        raise HTTPException(status_code=503, detail="Store manager not initialized")

    # Load documents
    loader = DocumentLoader()
    try:
        docs = loader.load_directory(request.source_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load documents: {str(e)}")

    if not docs:
        raise HTTPException(status_code=400, detail="No documents found in the specified path")

    # Create or update user-specific vector store
    existing_vectorstore = store_manager.load_user_vectorstore(current_user.id)

    if existing_vectorstore:
        # Merge with existing documents (simplified, would need proper merging logic)
        vectorstore = store_manager.create_from_documents(docs)
    else:
        vectorstore = store_manager.create_from_documents(docs)

    # Persist user-specific vector store
    store_manager.save_user_vectorstore(current_user.id, vectorstore)

    return IndexResponse(
        status="success",
        document_count=len(docs),
        chunk_count=len(docs),  # Simplified, would need actual chunk count
        user_id=current_user.id
    )
```

---

### Phase 8: CLI Interface (Day 7) - TDD

#### Test 8.1: CLI Chat Interface (RED → GREEN)

**RED - Write failing test:**
```python
# tests/integration/test_cli.py
def test_cli_single_query(capsys, vectorstore_fixture):
    cli = ChatCLI(vectorstore=vectorstore_fixture)

    cli.process_query("How do I get started?")

    captured = capsys.readouterr()
    assert "Assistant:" in captured.out
    assert len(captured.out) > 0

def test_cli_with_citations(capsys, vectorstore_fixture):
    cli = ChatCLI(vectorstore=vectorstore_fixture, show_citations=True)

    cli.process_query("Test query")

    captured = capsys.readouterr()
    assert "Sources:" in captured.out or "Citations:" in captured.out
```

**GREEN - Implementation:**
```python
# src/cli/chat.py
import asyncio
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

class ChatCLI:
    def __init__(
        self,
        vectorstore,
        show_citations: bool = True,
        enable_web_search: bool = True
    ):
        self.console = Console()
        self.graph = create_chatbot_graph(
            vectorstore=vectorstore,
            enable_web_search=enable_web_search
        )
        self.show_citations = show_citations

    def process_query(self, query: str) -> None:
        """Process a single query and display results"""
        # Implementation here

    async def run_interactive(self) -> None:
        """Run interactive chat loop"""
        # Implementation here

def main():
    """CLI entry point"""
    # Load vectorstore
    # Initialize ChatCLI
    # Run interactive loop
```

---

### Phase 9: Integration Tests (Day 7-8)

#### Test 8.1: End-to-End RAG Pipeline

```python
# tests/integration/test_rag_pipeline.py
@pytest.mark.asyncio
async def test_complete_rag_pipeline():
    """Test complete flow: document loading → embedding → search → response"""

    # 1. Load documents
    loader = DocumentLoader()
    docs = loader.load_directory("docs/knowledge_base/")

    # 2. Create vector store
    store_manager = VectorStoreManager()
    vectorstore = store_manager.create_from_documents(docs)

    # 3. Create agent
    graph = create_chatbot_graph(vectorstore=vectorstore)

    # 4. Query
    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": "How do I troubleshoot errors?"}],
        "user_query": "How do I troubleshoot errors?",
    })

    # Assertions
    assert result["messages"][-1]["role"] == "assistant"
    assert len(result["citations"]) > 0
    assert any("troubleshooting.md" in c.get("source", "") for c in result["citations"])
```

#### Test 8.2: Research Workflow End-to-End

#### Test 8.3: Provider Swapping End-to-End

```python
# tests/integration/test_provider_swapping.py
@pytest.mark.asyncio
async def test_switch_providers_at_runtime():
    """Test switching between providers without restarting"""

    from src.providers.factory import ProviderFactory
    from src.agent.graph import create_chatbot_graph

    factory = ProviderFactory()

    # Test with OpenAI
    provider1 = factory.create_provider("openai", {"api_key": "test1"})
    graph1 = create_chatbot_graph(
        vectorstore=vectorstore_fixture,
        provider_name="openai",
        provider_config={"api_key": "test1"}
    )

    # Test with Anthropic
    provider2 = factory.create_provider("anthropic", {"api_key": "test2"})
    graph2 = create_chatbot_graph(
        vectorstore=vectorstore_fixture,
        provider_name="anthropic",
        provider_config={"api_key": "test2"}
    )

    # Both should work independently
    assert graph1 is not None
    assert graph2 is not None

#### Test 8.4: API Server End-to-End

```python
# tests/integration/test_api_e2e.py
def test_complete_api_workflow():
    """Test complete workflow: index docs → chat → get response with citations"""

    from src.api.server import app, app_state
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # 1. Index documents
    index_response = client.post(
        "/api/v1/documents/index",
        json={"source_path": "tests/fixtures/sample_docs/"}
    )
    assert index_response.status_code == 200

    # 2. Chat query
    chat_response = client.post(
        "/api/v1/chat",
        json={"message": "How do I get started?"}
    )
    assert chat_response.status_code == 200

    data = chat_response.json()
    assert "response" in data
    assert len(data["citations"]) > 0

    # 3. Verify provider was used
    assert "provider_used" in data
    assert data["provider_used"] in ["openai", "anthropic", "ollama", "google"]
```

```python
# tests/integration/test_research_workflow.py
@pytest.mark.asyncio
async def test_multi_step_research():
    """Test complete research workflow with planning, execution, synthesis"""

    graph = create_chatbot_graph(
        vectorstore=vectorstore_fixture,
        enable_web_search=True
    )

    complex_query = """
    Analyze the error in the production logs,
    compare it with known issues in our docs,
    and suggest a fix based on recent solutions
    """

    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": complex_query}],
        "user_query": complex_query,
    })

    # Should have used multiple tools
    assert result.get("research_plan") is not None
    assert len(result["research_plan"]["steps"]) >= 3

    # Should have citations from multiple sources
    sources = set(c.get("type") for c in result["citations"])
    assert len(sources) > 1  # RAG + web + logs
```

---

### Phase 10: Documentation & Examples (Day 8)

**9.1 Create README.md**
- Project overview
- Installation instructions
- Quick start guide
- Example usage
- Configuration guide

**9.2 Create Usage Examples**
```python
# docs/examples/simple_rag.py
# Example: Simple RAG query

# docs/examples/research_workflow.py
# Example: Complex research query with citations

# docs/examples/log_analysis.py
# Example: Analyze production logs

# docs/examples/mcp_integration.py
# Example: Access live system via MCP
```

**9.3 Create Knowledge Base**

**9.4 API Documentation**
```python
# Add to docs/api_examples.md
# Example: Using the HTTP API

## Start the server
uvicorn src.api.server:app --reload --port 8000

## Index documents
curl -X POST http://localhost:8000/api/v1/documents/index \
  -H "Content-Type: application/json" \
  -d '{"source_path": "docs/knowledge_base/"}'

## Chat query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I get started?",
    "enable_web_search": true
  }'

## Switch provider at runtime
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare LangGraph and CrewAI",
    "provider": "anthropic"
  }'

## Streaming response
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Research AI agents"}'
```
- Add sample documentation to `docs/knowledge_base/`
- Create troubleshooting guide
- Create API reference

---

## Testing Strategy

### Unit Tests (80+ tests)
- Each tool tested independently
- Mock external dependencies (OpenAI, Tavily, MCP servers)
- Test edge cases and error handling

### Integration Tests (15+ tests)
- Full pipeline tests (document → embedding → search → response)
- Multi-tool workflows
- Real API calls (marked with `@pytest.mark.integration`)

### Test Coverage Target
- Minimum 80% code coverage
- 100% coverage for critical paths (RAG search, agent graph)

### TDD Cycle
1. **RED**: Write failing test
2. **GREEN**: Write minimal implementation to pass
3. **REFACTOR**: Improve code quality while tests pass
4. Repeat

---

## Configuration Management

### config/config.yaml
```yaml
# Main application config
app:
  name: "LangGraph Chatbot"
  version: "0.1.0"

# API server config
api:
  host: "0.0.0.0"
  port: 8000
  reload: true  # Development only
  log_level: "info"

embeddings:
  provider: "openai"  # Can be provider-specific
  model: "text-embedding-3-small"

vector_store:
  type: "faiss"
  persist_path: "./data/faiss_index"

rag:
  chunk_size: 1000
  chunk_overlap: 200
  top_k: 5
  relevance_threshold: 0.5

research:
  max_web_results: 5
  enable_web_search: true
  enable_mcp: true

mcp_servers:
  production:
    url: "http://localhost:3000"
    tools: ["get_logs", "get_metrics", "restart_service"]
```

### config/mcp_servers.json
```json
{
  "servers": {
    "production": {
      "url": "http://localhost:3000",
      "auth": {
        "type": "bearer",
        "token_env": "PROD_MCP_TOKEN"
      }
    }
  }
}
```

---

## Dependencies (pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.11"

# Core LangChain/LangGraph
langgraph = "^0.2.45"
langchain = "^0.3.13"
langchain-core = "^0.3.21"
langchain-community = "^0.3.13"

# LLM Providers
langchain-openai = "^0.2.12"
langchain-anthropic = "^0.3.0"
langchain-google-genai = "^2.0.8"
langchain-ollama = "^0.2.0"

# Vector store & embeddings
faiss-cpu = "^1.9.0"
tiktoken = "^0.8.0"

# API Server
fastapi = "^0.115.6"
uvicorn = {extras = ["standard"], version = "^0.34.0"}
pydantic = "^2.10.6"
pydantic-settings = "^2.7.1"

# Authentication & Database
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
sqlalchemy = "^2.0.36"
alembic = "^1.14.0"

# Tools & utilities
python-dotenv = "^1.0.0"
tavily-python = "^0.5.0"
pyyaml = "^6.0.2"
rich = "^13.9.4"
httpx = "^0.28.1"
unstructured = "^0.16.15"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.4"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
pytest-mock = "^3.14.0"
black = "^24.10.0"
ruff = "^0.8.4"
mypy = "^1.14.0"
httpx = "^0.28.1"  # For API testing
```

---

## Verification Steps

### 1. Unit Tests
```bash
cd ~/ws/langgraph
pytest tests/unit/ -v --cov=src --cov-report=html
```

### 2. Integration Tests
```bash
pytest tests/integration/ -v --log-cli-level=INFO
```

### 3. Start HTTP Server
```bash
# Development mode
uvicorn src.api.server:app --reload --port 8000

# Production mode
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# List providers
curl http://localhost:8000/api/v1/providers

# Index documents
curl -X POST http://localhost:8000/api/v1/documents/index \
  -H "Content-Type: application/json" \
  -d '{"source_path": "docs/knowledge_base/"}'

# Chat query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get started?", "provider": "openai"}'

# Switch to different provider
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Research AI frameworks", "provider": "anthropic"}'
```

### 5. Manual CLI Testing
```bash
# Interactive chat
python -m src.cli.chat

# Single query
python -m src.cli.chat --query "How do I get started?"

# Specify provider
python -m src.cli.chat --provider anthropic --query "Test"

# Enable debug mode
python -m src.cli.chat --debug
```

### 6. Test RAG Pipeline
```bash
# Load documents and create index
python scripts/index_documents.py --source docs/knowledge_base/

# Test search
python scripts/test_search.py --query "troubleshooting errors"
```

### 7. Test Research Workflow
```bash
# Complex research query
python -m src.cli.chat --query "Compare LangGraph and CrewAI with citations"
```

### 8. Test Provider Swapping
```bash
# Test switching between providers via API
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test OpenAI", "provider": "openai"}'

curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test Anthropic", "provider": "anthropic"}'

# Test via CLI
python -m src.cli.chat --provider openai --query "Test"
python -m src.cli.chat --provider anthropic --query "Test"
```

### 9. Test MCP Integration (if enabled)
```bash
# Start mock MCP server
python tests/fixtures/mock_mcp_server.py

# Test MCP tools
python scripts/test_mcp.py --server production --tool get_logs
```

---

## Critical Files to Implement

### Phase 1 (Setup)
1. `pyproject.toml`
2. `.env.example`
3. `config/config.yaml`
4. `config/providers.yaml`
5. `tests/conftest.py`

### Phase 2 (Provider Abstraction)
6. `src/providers/base.py`
7. `src/providers/openai_provider.py`
8. `src/providers/anthropic_provider.py`
9. `src/providers/factory.py`
10. `src/config.py`
11. `tests/unit/test_providers.py`
12. `tests/unit/test_config.py`

### Phase 3 (RAG Foundation)
13. `src/rag/document_loader.py`
14. `src/rag/vector_store.py`
15. `src/tools/rag_search.py`
16. `tests/unit/test_document_loader.py`
17. `tests/unit/test_vector_store.py`
18. `tests/unit/test_rag_search.py`

### Phase 4 (Research Tools)
19. `src/tools/web_search.py`
20. `src/tools/log_analyzer.py`
21. `src/tools/error_diagnosis.py`
22. `src/tools/mcp_tools.py`
23. `tests/unit/test_web_search.py`
24. `tests/unit/test_log_analyzer.py`

### Phase 5 (Agent Graph)
25. `src/agent/state.py`
26. `src/agent/graph.py`
27. `src/research/planner.py`
28. `src/research/citation_tracker.py`
29. `tests/integration/test_agent_graph.py`

### Phase 6 (Authentication & Multi-User)
30. `src/auth/jwt.py`
31. `src/auth/password.py`
32. `src/db/models.py`
33. `src/db/database.py`
34. `src/db/crud.py`
35. `tests/unit/test_auth.py`
36. `tests/unit/test_db_models.py`
37. `tests/unit/test_user_isolation.py`

### Phase 7 (HTTP API with Authentication)
38. `src/api/server.py`
39. `src/api/models.py`
40. `src/api/dependencies.py`
41. `src/api/routes/health.py`
42. `src/api/routes/auth.py`
43. `src/api/routes/chat.py`
44. `src/api/routes/documents.py`
45. `tests/integration/test_api.py`
46. `tests/integration/test_auth_api.py`

### Phase 8 (CLI)
47. `src/cli/chat.py`
48. `tests/integration/test_cli.py`

---

## Success Criteria

✅ All unit tests pass (100+ tests)
✅ All integration tests pass (25+ tests)
✅ Code coverage ≥ 80%
✅ Provider abstraction layer working - can swap between OpenAI, Anthropic, Ollama, Google
✅ **Authentication system working** - JWT tokens, password hashing, login/register
✅ **Multi-user support** - user isolation with separate vector stores
✅ **Protected endpoints** - all API endpoints require authentication
✅ HTTP API server running and responding correctly
✅ RAG pipeline works end-to-end
✅ Research workflow completes multi-step queries
✅ Citations tracked and displayed correctly
✅ API endpoints functional (chat, streaming, document indexing)
✅ **User-specific document indexing** - users can only access their own documents
✅ CLI interface functional
✅ Provider switching works at runtime via API and config
✅ MCP integration tested (if enabled)
✅ Documentation complete (API docs + authentication flow + examples)

---

## Timeline Summary

- **Day 1**: Setup + Provider abstraction layer + RAG foundation
- **Day 2**: RAG search tool + Web search tool
- **Day 3**: Log analyzer, error diagnosis, MCP tools
- **Day 4**: Research planner, citation tracker
- **Day 5**: Agent graph + Authentication & multi-user support
- **Day 6**: HTTP API server with protected endpoints
- **Day 7**: CLI interface + Provider swapping tests
- **Day 8**: Integration tests, documentation, API examples

**Total: 8 days** (assuming 6-8 hours/day focused development)

**Key Milestones:**
- **End of Day 1**: Can load documents and switch providers
- **End of Day 3**: All research tools working
- **End of Day 5**: Authentication system and user isolation working
- **End of Day 6**: Multi-user HTTP API server functional
- **End of Day 8**: Production-ready with full tests, auth, and docs

---

## Next Steps After Plan Approval

1. Create project structure in `~/ws/langgraph/`
2. Initialize Git repository
3. Set up virtual environment (Python 3.11+)
4. Install dependencies via `poetry install`
5. Create `.env` file from `.env.example`
6. Set up `config/providers.yaml` with provider configs
7. Begin Phase 1 with TDD approach
8. Commit after each GREEN phase
9. Document as we go

## Quick Start Commands After Implementation

```bash
# Setup
cd ~/ws/langgraph
poetry install
cp .env.example .env
# Edit .env with your API keys

# Index documents
python scripts/index_documents.py --source docs/knowledge_base/

# Start HTTP server
uvicorn src.api.server:app --reload --port 8000

# Or use CLI
python -m src.cli.chat --interactive

# Run tests
pytest tests/ -v --cov=src

# Switch provider at runtime (requires auth token)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Test", "provider": "anthropic"}'
```

## API Authentication Flow Example

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Login (if already registered)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepass123"
# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Index documents for the authenticated user
curl -X POST http://localhost:8000/api/v1/documents/index \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"source_path": "docs/my_docs/"}'
# Response: {"status": "success", "document_count": 10, "chunk_count": 10, "user_id": 1}

# 4. Chat with RAG (uses user-specific documents)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{
    "message": "What is in my documents?",
    "conversation_id": "conv-123",
    "enable_web_search": true
  }'
# Response: {"response": "...", "citations": [...], "conversation_id": "conv-123", "provider_used": "openai"}

# 5. Streaming chat
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"message": "Tell me more"}' \
  --no-buffer
# Response: Server-Sent Events stream
```
