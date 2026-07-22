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

"""Live MCP connection test for WorkWeek and ServiceImmediately MCP servers."""

import asyncio
import os
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Read token from .env
mcp_token = os.getenv("MCP_TOKEN", "mcp_5XFozjRwWsNwIkOfv6O5mH3Aooztwb1V4pdJ1bo1J3E")
base_url = "https://mock-saas.aishprabhat.demo.altostrat.com"


async def test_workweek_mcp():
    print("\n--- Testing WorkWeek MCP Server ---")
    url = f"{base_url}/work-week/mcp/"
    headers = {"X-MCP-Token": mcp_token}

    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        async with streamable_http_client(url, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ WorkWeek MCP Session Initialized!")
                tools_res = await session.list_tools()
                print(f"Discovered Tools ({len(tools_res.tools)}):")
                for t in tools_res.tools:
                    print(f"  - {t.name}: {t.description}")

                # Call get_employee_balances for EMP-22
                print("\nCalling `get_employee_balances` for 'EMP-22'...")
                res = await session.call_tool("get_employee_balances", arguments={"employee_id": "EMP-22"})
                print(f"Result for EMP-22:\n{res}")


async def test_serviceimmediately_mcp():
    print("\n--- Testing ServiceImmediately MCP Server ---")
    url = f"{base_url}/service-immediately/mcp/"
    headers = {"X-MCP-Token": mcp_token}

    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        async with streamable_http_client(url, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ ServiceImmediately MCP Session Initialized!")
                tools_res = await session.list_tools()
                print(f"Discovered Tools ({len(tools_res.tools)}):")
                for t in tools_res.tools:
                    print(f"  - {t.name}: {t.description}")

                # Call list_tickets for EMP-22
                print("\nCalling `list_tickets` for 'EMP-22'...")
                res = await session.call_tool("list_tickets", arguments={"employee_id": "EMP-22"})
                print(f"Result for EMP-22:\n{res}")


async def main():
    try:
        await test_workweek_mcp()
    except Exception as e:
        print("WorkWeek MCP Error:", e)

    try:
        await test_serviceimmediately_mcp()
    except Exception as e:
        print("ServiceImmediately MCP Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
