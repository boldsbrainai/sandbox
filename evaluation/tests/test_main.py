"""Unit tests for evaluation.main scoring modes."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import evaluate_single_task


class FakeAgent:
    """Minimal async agent stub for task scoring tests."""

    def __init__(self, response_text, tool_metrics):
        self.response_text = response_text
        self.tool_metrics = tool_metrics

    async def run(self, prompt, tools=None):
        return self.response_text, self.tool_metrics


class FailingAgent:
    """Agent stub that raises during execution."""

    async def run(self, prompt, tools=None):
        raise RuntimeError("boom")


class TestEvaluateSingleTask(unittest.IsolatedAsyncioTestCase):
    """Verify response and tool-calling scoring are independent."""

    async def test_response_scoring_mode_uses_expected_pattern(self):
        task = {"prompt": "report version", "response": r"v1\.0\.0\.152"}
        agent = FakeAgent(
            "<response>v1.0.0.152</response>",
            {},
        )

        result = await evaluate_single_task(
            task,
            agent,
            [],
            0,
            scoring_mode="response",
        )

        self.assertEqual(result["score"], 1)
        self.assertEqual(result["expected"], r"v1\.0\.0\.152")

    async def test_tool_calling_scoring_mode_ignores_response_mismatch(self):
        task = {"prompt": "report version", "response": r"v1\\.0\\.0\\.999"}
        agent = FakeAgent(
            "<response>unexpected</response>",
            {
                "sandbox_get_context": {
                    "count": 1,
                    "durations": [0.05],
                    "calls": [],
                }
            },
        )

        result = await evaluate_single_task(
            task,
            agent,
            [],
            0,
            scoring_mode="tool-calling",
        )

        self.assertEqual(result["score"], 1)
        self.assertEqual(
            result["expected"],
            "At least one successful tool call",
        )
        self.assertEqual(result["num_tool_calls"], 1)

    async def test_tool_calling_scoring_mode_fails_without_tools(self):
        task = {"prompt": "report version", "response": r"v1\\.0\\.0\\.152"}
        agent = FakeAgent("<response>v1.0.0.152</response>", {})

        result = await evaluate_single_task(
            task,
            agent,
            [],
            0,
            scoring_mode="tool-calling",
        )

        self.assertEqual(result["score"], 0)
        self.assertEqual(result["num_tool_calls"], 0)

    async def test_tool_calling_scoring_mode_uses_tool_criterion_on_error(self):
        task = {"prompt": "report version", "response": r"v1\\.0\\.0\\.152"}

        result = await evaluate_single_task(
            task,
            FailingAgent(),
            [],
            0,
            scoring_mode="tool-calling",
        )

        self.assertEqual(
            result["expected"],
            "At least one successful tool call",
        )
        self.assertIn("TASK_EXECUTION_ERROR", result["actual"])
        self.assertEqual(result["score"], 0)


if __name__ == "__main__":
    unittest.main()
