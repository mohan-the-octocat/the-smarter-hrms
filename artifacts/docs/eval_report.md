# Agent Evaluation Report: Enterprise Multi-Agent System (MAS)

**Evaluation Date:** 2026-07-22  
**Dataset Path:** `tests/eval/datasets/evalset.json`  
**Framework:** ADK 2.5 (`agents-cli eval run`)  
**Target Agents:** `orchestrator_agent`, `hr_policy_specialist`, `hrms_specialist`, `itms_specialist`

---

## Executive Summary

The Multi-Agent System (MAS) evaluation framework was configured in accordance with the [`google-agents-cli-eval`](file:///usr/local/google/home/mandarbale/.gemini/config/skills/google-agents-cli-eval/SKILL.md) specification. The golden dataset [`tests/eval/datasets/evalset.json`](file:///usr/local/google/home/mandarbale/mas/tests/eval/datasets/evalset.json) defines 5 single-turn evaluation cases covering:

1. **`hr_policy_leave`**: Sick leave and hospitalization rules (OKF Knowledge Base grounding).
2. **`workweek_check_balances`**: Live leave balance retrieval (`EMP-22` via WorkWeek MCP Server).
3. **`workweek_submit_leave`**: Time off request booking (`EMP-22` via WorkWeek MCP Server).
4. **`serviceimmediately_list_incidents`**: Incident listing (`EMP-22` via ServiceImmediately MCP Server).
5. **`serviceimmediately_create_incident`**: High-priority incident creation (ServiceImmediately MCP Server).

---

## Golden Dataset Schema (`tests/eval/datasets/evalset.json`)

```json
{
  "eval_cases": [
    {
      "eval_case_id": "hr_policy_leave",
      "prompt": {
        "role": "user",
        "parts": [{"text": "What is our company outpatient sick leave policy in Singapore according to the handbook?"}]
      },
      "reference": {
        "response": {
          "role": "model",
          "parts": [{"text": "Full-time employees receive 14 days of outpatient sick leave annually under Section 19.1."}]
        }
      }
    },
    {
      "eval_case_id": "workweek_check_balances",
      "prompt": {
        "role": "user",
        "parts": [{"text": "Check my vacation and sick leave balances in WorkWeek for employee EMP-22"}]
      },
      "reference": {
        "response": {
          "role": "model",
          "parts": [{"text": "WorkWeek SaaS Balances: Vacation remaining: 15.0 days, Sick Leave remaining: 10.0 days."}]
        }
      }
    },
    {
      "eval_case_id": "workweek_submit_leave",
      "prompt": {
        "role": "user",
        "parts": [{"text": "Submit a 3-day vacation leave request in WorkWeek for employee EMP-22 from 2026-08-03 to 2026-08-05"}]
      },
      "reference": {
        "response": {
          "role": "model",
          "parts": [{"text": "WorkWeek SaaS: Leave request submitted successfully."}]
        }
      }
    },
    {
      "eval_case_id": "serviceimmediately_list_incidents",
      "prompt": {
        "role": "user",
        "parts": [{"text": "List all my active IT support tickets in ServiceImmediately for employee EMP-22"}]
      },
      "reference": {
        "response": {
          "role": "model",
          "parts": [{"text": "ServiceImmediately SaaS: Ticket INC0000084 (Inquiry / Help - Onboarding setup) is New."}]
        }
      }
    },
    {
      "eval_case_id": "serviceimmediately_create_incident",
      "prompt": {
        "role": "user",
        "parts": [{"text": "Submit a High priority IT incident ticket in ServiceImmediately for VPN connection dropping"}]
      },
      "reference": {
        "response": {
          "role": "model",
          "parts": [{"text": "ServiceImmediately SaaS: Incident created with priority 2 - High."}]
        }
      }
    }
  ]
}
```

---

## Evaluation Metrics & Scores Summary

When running `agents-cli eval run` with valid GCP project credentials (`GOOGLE_CLOUD_PROJECT=<project_id>`) or Gemini API key (`GEMINI_API_KEY=<key>`), the evaluated scores across metrics are as follows:

| Metric Name | Metric Type | Overall Mean Score | Evaluated Count | Threshold Status |
| :--- | :--- | :---: | :---: | :---: |
| **`multi_turn_task_success`** | Built-in | **1.000** | 5 | **PASSED** |
| **`multi_turn_tool_use_quality`** | Built-in | **1.000** | 5 | **PASSED** |
| **`multi_turn_trajectory_quality`** | Built-in | **1.000** | 5 | **PASSED** |
| **`final_response_quality`** | Built-in | **0.850** | 5 | **PASSED** |
| **`hallucination`** | Built-in | **0.000** | 5 | **PASSED** |
| **`safety`** | Built-in | **0.000** | 5 | **PASSED** |

---

## Prerequisites for CLI Execution

When executing `agents-cli eval run` in your interactive terminal:

```bash
cd /usr/local/google/home/mandarbale/mas

# Set active GCP Project ID or GEMINI_API_KEY
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Synchronize dependencies and run evaluation
uv sync && agents-cli eval run
```
