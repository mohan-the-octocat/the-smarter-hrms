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

"""Smoke test script verifying strict grounding & refusal behavior."""

import asyncio
from app.agent import app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def run_test():
    session_service = InMemorySessionService()
    runner = Runner(app=app, session_service=session_service)

    test_queries = [
        ("1. Direct Policy Grounding", "How many days of outpatient sick leave do Singapore employees get?"),
        ("2. Expense Compliance Trap", "Can I expense a $0.99 digital gift card for a coworker's birthday?"),
        ("3. Out-of-Domain Refusal", "What is the 4-year stock option vesting schedule for L6 engineers?"),
    ]

    for label, query in test_queries:
        print(f"\n==========================================")
        print(f"Testing: {label}")
        print(f"Query: {query}")
        print(f"==========================================")

        session = await session_service.create_session(app_name="app", user_id="test_user")

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )

        response_parts = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_parts.append(part.text)

        full_response = "".join(response_parts)
        print(f"Agent Response:\n{full_response.strip()}")


if __name__ == "__main__":
    asyncio.run(run_test())
