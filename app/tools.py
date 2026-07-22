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

"""Tools for HR Policy (OKF), HRMS (WorkWeek MCP), and ITMS (ServiceImmediately MCP)."""

import json
import os
import re
from typing import Any, Dict, List, Optional
import httpx
import yaml

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# Base URLs & Credentials from environment / OpenAPI spec
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

MOCK_SAAS_BASE_URL = os.getenv("MOCK_SAAS_BASE_URL", "https://mock-saas.aishprabhat.demo.altostrat.com").rstrip("/")
mcp_token = os.getenv("MCP_TOKEN", os.getenv("WORKWEEK_MCP_TOKEN", "mcp_5XFozjRwWsNwIkOfv6O5mH3Aooztwb1V4pdJ1bo1J3E"))

# --- 1. Live MCP Toolsets ---
workweek_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{MOCK_SAAS_BASE_URL}/work-week/mcp/",
        headers={"X-MCP-Token": mcp_token}
    )
)

serviceimmediately_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{MOCK_SAAS_BASE_URL}/service-immediately/mcp/",
        headers={"X-MCP-Token": mcp_token}
    )
)


# --- 2. HR Policy Specialist OKF Tools ---
def list_okf_concepts() -> dict:
    """Lists all available HR policy concepts in the Altostrat Singapore OKF Knowledge Base."""
    base_dir = os.path.abspath(KNOWLEDGE_DIR)
    if not os.path.isdir(base_dir):
        return {"error": f"Knowledge directory not found at {base_dir}"}

    concepts = []
    for root, _, files in os.walk(base_dir):
        for f in sorted(files):
            if not f.endswith(".md") or f in ("index.md", "log.md"):
                continue
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, base_dir)
            concept_id = rel_path[:-3]

            title = f
            source = ""
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                m = FRONTMATTER_RE.match(content)
                if m:
                    data = yaml.safe_load(m.group(1)) or {}
                    title = data.get("title", f)
                    source = data.get("source", "")
            except Exception:
                pass

            concepts.append({
                "concept_id": concept_id,
                "title": title,
                "source": source,
            })

    concepts.sort(key=lambda x: x["concept_id"])
    return {"concepts": concepts}


def read_okf_concept(concept_id: str) -> str:
    """Reads the full policy text for a specified concept_id from the OKF Knowledge Base.

    Args:
        concept_id: The ID of the policy concept (e.g. '19-sick-time-hospitalization-leave-singapore/19.1-eligibility-and-scope').
    """
    base_dir = os.path.abspath(KNOWLEDGE_DIR)
    clean_id = concept_id.strip()
    if clean_id.startswith("/"):
        clean_id = clean_id[1:]
    if not clean_id.endswith(".md"):
        clean_id += ".md"

    filepath = os.path.abspath(os.path.join(base_dir, clean_id))
    if not filepath.startswith(base_dir):
        return "Error: Security violation (path traversal attempted)."

    if not os.path.exists(filepath):
        return f"Error: Concept '{concept_id}' not found in OKF knowledge bundle."

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception as e:
        return f"Error reading concept '{concept_id}': {e}"


def query_hr_policy(query: str) -> str:
    """Queries the HR Employee Handbook / OKF Knowledge Base by topic or keywords.

    Args:
        query: Search keywords or employee question regarding HR policies, leave, benefits, conduct, expenses, etc.
    """
    base_dir = os.path.abspath(KNOWLEDGE_DIR)
    query_lower = query.lower()

    synonym_map = {
        "pto": ["vacation", "sick", "leave", "paid time off"],
        "wfh": ["remote", "flexible", "telework"],
        "gift": ["gift cards", "commercial gifts", "entertainment"],
        "dinner": ["meal", "entertainment", "lodging"],
        "alcohol": ["drinking", "smoking", "substances"],
    }

    search_terms = set(re.findall(r"\w+", query_lower))
    for term in list(search_terms):
        if term in synonym_map:
            search_terms.update(synonym_map[term])

    matches = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.endswith(".md") or f in ("index.md", "log.md"):
                continue
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, base_dir)
            concept_id = rel_path[:-3]

            try:
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                content_lower = content.lower()

                score = 0
                for term in search_terms:
                    if len(term) <= 2:
                        continue
                    if term in concept_id.lower():
                        score += 5
                    if term in content_lower:
                        score += content_lower.count(term)

                if score > 0:
                    m = FRONTMATTER_RE.match(content)
                    title = concept_id
                    source = ""
                    if m:
                        data = yaml.safe_load(m.group(1)) or {}
                        title = data.get("title", concept_id)
                        source = data.get("source", "")
                    matches.append((score, concept_id, title, source, content))
            except Exception:
                continue

    if not matches:
        return f"NO_MATCH: No policy section found matching query '{query}' in the Altostrat Singapore Employee Policy Handbook."

    matches.sort(key=lambda x: x[0], reverse=True)
    top_matches = matches[:4]

    results = []
    for _, cid, title, source, body in top_matches:
        results.append(f"=== [Concept ID: {cid} | Title: {title} | Source: {source}] ===\n{body}")

    return "\n\n".join(results)
