import os
import google.auth
from google.auth.transport.requests import Request
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# Fetch Application Default Credentials (ADC)
_credentials, default_project_id = google.auth.default()
_request = Request()
if not _credentials.valid:
    _credentials.refresh(_request)

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", default_project_id)

def _adc_auth_header_provider(context=None) -> dict[str, str]:
    """Generates OAuth2 Bearer token for BigQuery MCP Server authorization."""
    if not _credentials.valid:
        _credentials.refresh(_request)
    return {
        "Authorization": f"Bearer {_credentials.token}",
        "x-goog-user-project": project_id
    }

# BigQuery MCP Toolset with strict read-only filter
bigquery_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        tool_filter=[
            "get_dataset_info",
            "list_table_ids",
            "get_table_info",
            "execute_sql_readonly"  # Strict read-only query execution
        ]
    ),
    header_provider=_adc_auth_header_provider
)

system_instruction = f"""
You are an expert Enterprise Data Analyst with direct access to Google BigQuery via Model Context Protocol (MCP).
Dataset: bigquery-public-data.new_york_citibike (Citi Bike trips and stations in NYC area).

Autonomous Reasoning Plan:
1. Dataset Exploration: Use list_table_ids and get_table_info to inspect table structures, primary keys, and data types.
2. Zero Prior Assumptions: Never guess column names or categorical values. Query distinct values when filtering dimensions.
3. Multi-table SQL Formulation: Write clean BigQuery SQL to answer business optimization questions.
4. Dry-Run Verification: Verify queries using execute_sql_readonly under project '{project_id}'.
5. Business Decision Synthesis: Summarize findings into clear strategic recommendations.
"""

root_agent = LlmAgent(
    name="data_agent",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    instruction=system_instruction,
    description="Enterprise Analytics Agent connected to BigQuery MCP Server for autonomous SQL reasoning.",
    tools=[bigquery_toolset]
)
