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

"""Test script for cross-agent prompt orchestration across Policy, WorkWeek, and ServiceImmediately."""

import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from app.agent import app, root_agent


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="app")
    session = await runner.session_service.create_session(
        app_name="app", user_id="test_user"
    )

    prompt = (
        "I just read the remote work policy and saw I'm eligible for a home office monitor. "
        "Can you verify my remote status for employee EMP-22 in WorkWeek and order a monitor for me in ServiceImmediately?"
    )

    print(f"\n--- Testing Cross-Agent Prompt ---\nUser: {prompt}\n")

    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    events = []
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=user_msg,
    ):
        events.append(event)
        if hasattr(event, "author") and event.author:
            if hasattr(event, "content") and event.content:
                parts = getattr(event.content, "parts", [])
                text_parts = [p.text for p in parts if hasattr(p, "text") and p.text]
                if text_parts:
                    print(f"[{event.author}]: {' '.join(text_parts)}")

    print("\n--- Summary of Events ---")
    print(f"Total events generated: {len(events)}")


if __name__ == "__main__":
    asyncio.run(main())
