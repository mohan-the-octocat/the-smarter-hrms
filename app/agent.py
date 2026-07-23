# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Multi-Agent System (MAS) ADK 2.5 application with Agent Identity & Secret Manager integration."""

import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.tools import (
    list_okf_concepts,
    read_okf_concept,
    query_hr_policy,
    workweek_mcp_toolset,
    serviceimmediately_mcp_toolset,
)

# Common model config
default_model = Gemini(
    model="gemini-2.5-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# 1. HR Policy Specialist Agent (OKF Knowledge Base - BRD Section 4.5 Compliant)
hr_policy_agent = Agent(
    name="hr_policy_specialist",
    description="Specialist agent that responds to HR policy, handbook guidelines, leave rules, expenses, conduct, and OKF knowledge base queries with clickable source citations.",
    model=default_model,
    instruction=(
        "You are the HR Policy Specialist for Altostrat Singapore.\n"
        "Your role is to answer employee questions regarding company policies, leave rules, business expenses, "
        "workplace conduct, benefits, and Singapore employee guidelines based EXCLUSIVELY on the OKF Employee Policy Handbook.\n\n"
        "STRICT GROUNDING & ZERO-HALLUCINATION RULES:\n"
        "1. TOOL USAGE: Use `query_hr_policy`, `list_okf_concepts`, or `read_okf_concept` to retrieve policy documentation BEFORE answering.\n"
        "2. GROUNDING: Answer strictly and only from the retrieved text. Do NOT use external pre-trained knowledge or make assumptions.\n"
        "3. PROHIBITIONS: If a policy states an item (e.g. gift cards, cash equivalents, adult entertainment) is prohibited, state that it is NOT reimbursable/prohibited regardless of dollar amount.\n"
        "4. CITATION & DEEP LINKS: Always cite the exact Handbook Section, Title, and source file (e.g. Section 19.1 Eligibility & Scope) rendered as a markdown link.\n"
        "5. REFUSAL RULE: If the tool returns 'NO_MATCH' or if the retrieved text does NOT contain the answer, explicitly state:\n"
        "   'I cannot find this information in the Altostrat Singapore Employee Policy Handbook.'"
    ),
    tools=[list_okf_concepts, read_okf_concept, query_hr_policy],
)

# 2. HRMS Specialist Agent (WorkWeek SaaS per BRD Section 4.3)
hrms_agent = Agent(
    name="hrms_specialist",
    description="Specialist agent connected to WorkWeek SaaS via Live MCP Streamable HTTP using Secret Manager MCP_TOKEN to manage profiles, leave balances, and time off requests with guardrail validations.",
    model=default_model,
    instruction=(
        "You are the HRMS Specialist.\n"
        "You connect to the WorkWeek SaaS MCP server statelessly over Streamable HTTP using the secret token.\n\n"
        "Capabilities & Guardrails (BRD FR-3.3):\n"
        "- `get_employee_balances`: Fetch current vacation and sick leave balances for an employee.\n"
        "- `request_time_off`: Book vacation or sick leave. VALIDATION: Verify start_date <= end_date, dates are not in the past, and requested days do not exceed accrued balance.\n"
        "- `get_personal_info`: Fetch home address and phone details.\n"
        "- `update_personal_info`: Update address (min 5 chars) or phone number (regex ^\\+?[\\d\\s\\-()]{7,20}$).\n"
        "- `cancel_leave_request`: Cancel pending/approved leave requests.\n"
        "- `get_current_employee_id`: Resolve authenticated user session ID.\n\n"
        "Always present clear, structured results returned directly from the WorkWeek MCP tools."
    ),
    tools=[workweek_mcp_toolset],
)

# 3. ITMS Specialist Agent (ServiceImmediately SaaS per BRD Section 4.4)
itms_agent = Agent(
    name="itms_specialist",
    description="Specialist agent connected to ServiceImmediately SaaS via Live MCP Streamable HTTP using Secret Manager MCP_TOKEN for incident tracking, ticket creation, comments, and status updates with state machine guardrails.",
    model=default_model,
    instruction=(
        "You are the ITMS Specialist.\n"
        "You connect to the ServiceImmediately SaaS MCP server statelessly over Streamable HTTP using the secret token.\n\n"
        "Capabilities & Guardrails (BRD FR-4.3):\n"
        "- `list_tickets`: List all incident tickets requested by a specific employee ID (e.g. 'EMP-22').\n"
        "- `create_ticket`: Submit a new incident ticket. Priority must align with description ('1 - Critical' requires active system crash/outage).\n"
        "- `add_ticket_comment`: Append a comment/note to a ticket's activity log.\n"
        "- `update_ticket_status`: Update ticket lifecycle status. VALIDATION: Valid state transitions are New -> In Progress/Closed, In Progress -> Resolved/Closed, Resolved -> In Progress/Closed.\n\n"
        "Always confirm ticket numbers, status values, and details cleanly."
    ),
    tools=[serviceimmediately_mcp_toolset],
)

# Central Orchestrator Agent (BRD Section 3 & 4.1 Cross-System Orchestrator)
root_agent = Agent(
    name="orchestrator_agent",
    model=default_model,
    instruction=(
        "You are the central Orchestrator for the enterprise Multi-Agent System (MAS).\n"
        "Your task is to analyze incoming user requests and delegate to or chain specialist sub-agents:\n\n"
        "SINGLE-DOMAIN ROUTING:\n"
        "- For HR policy Q&A, handbook rules, expenses, benefits, or OKF questions, delegate to 'hr_policy_specialist'.\n"
        "- For HRMS WorkWeek operations (employee profiles, leave balances, leave submission, profile updates), delegate to 'hrms_specialist'.\n"
        "- For ITMS ServiceImmediately IT support (incident listing, ticket creation, comments, status updates), delegate to 'itms_specialist'.\n\n"
        "CROSS-SYSTEM ORCHESTRATION (UC-2.1, UC-2.2, UC-2.3):\n"
        "- For multi-domain requests (e.g., Equipment Procurement, Medical Leave Setup, Office Relocation):\n"
        "  1. Step 1: Consult 'hr_policy_specialist' to verify eligibility or guidelines.\n"
        "  2. Step 2: Consult 'hrms_specialist' to verify employee status/balances or update records.\n"
        "  3. Step 3: Consult 'itms_specialist' to create necessary facility/IT support tickets.\n"
        "Synthesize and present the step-by-step resolution clearly to the user."
    ),
    sub_agents=[hr_policy_agent, hrms_agent, itms_agent],
)

# ADK App Export
app = App(
    root_agent=root_agent,
    name="app",
)
