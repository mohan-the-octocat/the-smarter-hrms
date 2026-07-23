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

"""Unit tests for MAS agents and tools structure matching OpenAPI specification."""

import pytest
from app.agent import app, root_agent, hr_policy_agent, hrms_agent, itms_agent
from app.tools import (
    list_okf_concepts,
    read_okf_concept,
    query_hr_policy,
    workweek_mcp_toolset,
    serviceimmediately_mcp_toolset,
)


def test_agent_structure():
    """Verify that root agent has all three specialist sub-agents attached as tools."""
    assert root_agent.name == "orchestrator_agent"
    tool_names = [tool.name for tool in root_agent.tools]
    assert "hr_policy_specialist" in tool_names
    assert "hrms_specialist" in tool_names
    assert "itms_specialist" in tool_names



def test_sub_agent_tools_count():
    """Verify sub-agents are equipped with McpToolsets and OKF tools."""
    assert len(hr_policy_agent.tools) == 3
    assert len(hrms_agent.tools) == 1
    assert len(itms_agent.tools) == 1


def test_okf_list_concepts():
    """Test listing concepts from OKF bundle."""
    res = list_okf_concepts()
    assert "concepts" in res
    assert len(res["concepts"]) > 100


def test_okf_read_concept():
    """Test reading a specific concept file from OKF bundle."""
    res = read_okf_concept("19-sick-time-hospitalization-leave-singapore/19.1-eligibility-and-scope")
    assert "Eligibility" in res or "Sick" in res or "Altostrat" in res


def test_hr_policy_query():
    """Test HR policy keyword query tool against OKF bundle."""
    res = query_hr_policy("sick leave hospitalization")
    assert "sick" in res.lower() or "leave" in res.lower()
