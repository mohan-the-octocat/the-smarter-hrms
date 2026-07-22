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

"""Multi-Agent System (MAS) ADK 2.0 application with Orchestrator and 3 Specialists (HR Policy, HRMS WorkWeek MCP, ITMS ServiceImmediately MCP)."""

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

# 1. HR Policy Specialist Agent (OKF Knowledge Base)
hr_policy_agent = Agent(
    name="hr_policy_specialist",
    description="Specialist agent that responds to HR policy, handbook guidelines, leave rules, expenses, conduct, and OKF knowledge base queries.",
    model=default_model,
    instruction=(
        "You are the HR Policy Specialist for Altostrat Singapore.\n"
        "Your role is to answer employee questions regarding company policies, leave rules, business expenses, "
        "workplace conduct, benefits, and Singapore employee guidelines based EXCLUSIVELY on the OKF Employee Policy Handbook.\n\n"
        "STRICT GROUNDING & ZERO-HALLUCINATION RULES:\n"
        "1. TOOL USAGE: Use `query_hr_policy`, `list_okf_concepts`, or `read_okf_concept` to retrieve policy documentation BEFORE answering.\n"
        "2. GROUNDING: Answer strictly and only from the retrieved text. Do NOT use external pre-trained knowledge or make assumptions.\n"
        "3. PROHIBITIONS: If a policy states an item (e.g. gift cards, cash equivalents, adult entertainment) is prohibited, state that it is NOT reimbursable/prohibited regardless of dollar amount.\n"
        "4. CITATION: Always cite the exact Handbook Section and Title (e.g. Section 19.1 Eligibility & Scope, Section 4.2 Expense Submission) in your response.\n"
        "5. REFUSAL RULE: If the tool returns 'NO_MATCH' or if the retrieved text does NOT contain the answer, explicitly state:\n"
        "   'I cannot find this information in the Altostrat Singapore Employee Policy Handbook.'"
    ),
    tools=[list_okf_concepts, read_okf_concept, query_hr_policy],
)

# 2. HRMS Specialist Agent (WorkWeek SaaS via Live MCP Streamable HTTP)
hrms_agent = Agent(
    name="hrms_specialist",
    description="Specialist agent connected to the live WorkWeek SaaS MCP Server via Streamable HTTP and X-MCP-Token header to manage profiles, leave balances, and time off requests.",
    model=default_model,
    instruction=(
        "You are the HRMS Specialist.\n"
        "You connect to the WorkWeek SaaS MCP server statelessly over Streamable HTTP using the `X-MCP-Token` header.\n\n"
        "Capabilities & Tools:\n"
        "- `get_employee_balances`: Fetch current vacation and sick leave balances for an employee.\n"
        "- `request_time_off`: Book vacation or sick leave.\n"
        "- `get_personal_info`: Fetch home address and phone details.\n"
        "- `update_personal_info`: Update address or phone number.\n"
        "- `cancel_leave_request`: Cancel pending/approved leave requests.\n"
        "- `get_current_employee_id`: Resolve authenticated user session ID.\n\n"
        "Always present clear, structured results returned directly from the WorkWeek MCP tools."
    ),
    tools=[workweek_mcp_toolset],
)

# 3. ITMS Specialist Agent (ServiceImmediately SaaS via Live MCP Streamable HTTP)
itms_agent = Agent(
    name="itms_specialist",
    description="Specialist agent connected to the live ServiceImmediately SaaS MCP Server via Streamable HTTP and X-MCP-Token header for incident tracking, ticket creation, comments, and status updates.",
    model=default_model,
    instruction=(
        "You are the ITMS Specialist.\n"
        "You connect to the ServiceImmediately SaaS MCP server statelessly over Streamable HTTP using the `X-MCP-Token` header.\n\n"
        "Capabilities & Tools:\n"
        "- `list_tickets`: List all incident tickets requested by a specific employee ID (e.g. 'EMP-22').\n"
        "- `create_ticket`: Submit a new incident ticket.\n"
        "- `add_ticket_comment`: Append a comment/note to a ticket's activity log.\n"
        "- `update_ticket_status`: Update ticket lifecycle status (e.g. 'New', 'In Progress', 'Resolved', 'Closed').\n\n"
        "Always confirm ticket numbers, status values, and details cleanly."
    ),
    tools=[serviceimmediately_mcp_toolset],
)

# Central Orchestrator Agent
root_agent = Agent(
    name="orchestrator_agent",
    model=default_model,
    instruction=(
        "You are the central Orchestrator for the enterprise Multi-Agent System (MAS).\n"
        "Your task is to analyze incoming user requests and delegate to the appropriate specialist sub-agent:\n"
        "- For HR policy Q&A, handbook rules, expenses, benefits, or OKF questions, delegate to 'hr_policy_specialist'.\n"
        "- For HRMS WorkWeek operations (employee profiles, leave balances, leave submission, profile updates for employees like 'EMP-22'), delegate to 'hrms_specialist'.\n"
        "- For ITMS ServiceImmediately IT support (incident listing, ticket creation, comments, status updates for employees like 'EMP-22'), delegate to 'itms_specialist'.\n"
        "Pass the sub-agent's response clearly back to the user."
    ),
    sub_agents=[hr_policy_agent, hrms_agent, itms_agent],
)

# ADK App Export
app = App(
    root_agent=root_agent,
    name="app",
)
