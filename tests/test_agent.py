import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from script_agent.agent import run
from script_agent.providers import GLMProvider, MockProvider, ProviderError, sample_script
from script_agent.tools import Tools


def request():
    return {"theme": "字幕编辑", "audience": "新手", "platform": "短视频平台", "target_seconds": 30, "style": "简洁"}


class SequenceProvider:
    mode, model, last_usage = "mock", "test-sequence", None

    def __init__(self, actions):
        self.actions = iter(actions)

    def respond(self, messages, schemas):
        name, args = next(self.actions)
        return {"role": "assistant", "content": None, "tool_calls": [{"id": str(len(messages)), "type": "function",
                "function": {"name": name, "arguments": json.dumps({"reason": "test", **args}, ensure_ascii=False)}}]}


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.tools = Tools(ROOT / "data", request())
        self.tools.search_materials("字幕", "test")
        self.tools.set_script(sample_script(), "test")

    def test_duration_is_sum_of_concurrent_visual_and_speech(self):
        result = self.tools.estimate_duration("test")
        self.assertEqual(result["total_seconds"], 11)
        self.assertTrue(result["passed"])

    def test_speech_cannot_be_hidden_by_short_hold(self):
        script = sample_script()
        script["shots"][1]["lines"] *= 10
        script["shots"][1]["hold_seconds"] = 0.1
        self.tools.set_script(script, "test")
        self.assertGreater(self.tools.estimate_duration("test")["shots"][1]["seconds"], 5)

    def test_unretrieved_fact_rejected(self):
        self.tools.retrieved.clear()
        self.assertFalse(self.tools.check_script("test")["passed"])

    def test_correct_citation_contains_original_and_version(self):
        result = self.tools.check_script("test")
        self.assertTrue(result["passed"])
        self.assertEqual(result["citations"][0]["quote"], "支持手动编辑字幕。")
        self.assertEqual(result["citations"][0]["source_id"], "P01")

    def test_approved_title_can_be_used_as_nonfactual_caption(self):
        self.tools.script["shots"][0]["lines"][0]["text"] = "字幕编辑小指南"
        self.assertTrue(self.tools.check_script("test")["passed"])

    def test_forged_claim_with_valid_id_rejected(self):
        self.tools.script["shots"][1]["lines"][0]["text"] = "效率提升80%。"
        result = self.tools.check_script("test")
        self.assertFalse(result["passed"])
        self.assertIn("unsupported_claim", [i["code"] for i in result["issues"]])

    def test_script_revision_invalidates_both_checks(self):
        self.tools.check_script("test")
        self.tools.estimate_duration("test")
        self.assertTrue(self.tools.finish("completed", "test")["ok"])
        script = sample_script(long=True)
        self.tools.set_script(script, "test")
        self.assertFalse(self.tools.finish("completed", "test")["ok"])
        self.assertIsNone(self.tools.check)
        self.assertIsNone(self.tools.duration)

    def test_hash_blocks_out_of_band_mutation(self):
        self.tools.check_script("test")
        self.tools.estimate_duration("test")
        self.tools.script["shots"][0]["hold_seconds"] = 50
        self.assertFalse(self.tools.finish("completed", "test")["ok"])

    def test_injected_failure_does_not_claim_success(self):
        self.tools.failures["check_script"] = 1
        self.assertFalse(self.tools.execute("check_script", {"reason": "test"})["ok"])
        self.assertIsNone(self.tools.check)

    def test_bad_numbers_and_shapes_are_rejected(self):
        for number in [0, -1, True, float("nan"), float("inf"), "5"]:
            with self.subTest(number=number):
                script = sample_script()
                script["shots"][0]["hold_seconds"] = number
                self.assertFalse(self.tools.execute("set_script", {"script": script, "reason": "test"})["ok"])

    def test_document_changes_affect_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            for file in ("materials.json", "brand_rules.json"):
                (Path(directory) / file).write_text((ROOT / "data" / file).read_text(encoding="utf-8"), encoding="utf-8")
            path = Path(directory) / "materials.json"
            catalog = json.loads(path.read_text(encoding="utf-8"))
            catalog["documents"][0]["facts"][0]["text"] = "仅支持调整字幕颜色。"
            path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
            changed = Tools(directory, request())
            changed.search_materials("字幕", "test")
            changed.set_script(sample_script(), "test")
            self.assertFalse(changed.check_script("test")["passed"])

    def test_unknown_tool_and_extra_arguments_rejected(self):
        self.assertFalse(self.tools.execute("publish", {})["ok"])
        self.assertFalse(self.tools.execute("estimate_duration", {"reason": "test", "target_seconds": 100})["ok"])

    def test_unchecked_extra_script_fields_rejected(self):
        script = sample_script()
        script["unverified_claim"] = "unsupported text"
        self.assertFalse(self.tools.execute("set_script", {"script": script, "reason": "test"})["ok"])


class AgentTests(unittest.TestCase):
    def execute(self, req=None, **kwargs):
        req = request() if req is None else req
        return run(req, MockProvider(req), ROOT / "data", **kwargs)

    def test_normal_offline_flow(self):
        result = self.execute()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["provider"], "mock")
        self.assertTrue(result["duration"]["passed"])
        self.assertTrue(result["rule_check"]["passed"])

    def test_missing_required_information(self):
        req = request()
        del req["target_seconds"]
        result = self.execute(req)
        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(result["model_calls"], 0)

    def test_no_material(self):
        req = request()
        req["theme"] = "全息投影"
        self.assertEqual(self.execute(req)["status"], "needs_input")

    def test_partial_script_retained_after_failure(self):
        result = self.execute(failures={"check_script": 1})
        self.assertEqual(result["status"], "failed")
        self.assertIsNotNone(result["script"])
        self.assertIsNone(result["rule_check"])

    def test_over_duration_repair_and_recheck(self):
        req = request()
        req["initial_draft"] = sample_script(long=True)
        result = self.execute(req)
        estimates = [s["observation"] for s in result["trace"] if s.get("tool") == "estimate_duration"]
        self.assertFalse(estimates[0]["passed"])
        self.assertTrue(estimates[-1]["passed"])
        self.assertEqual(result["status"], "completed")

    def test_limit_never_claims_completion(self):
        result = self.execute(max_calls=2)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["reason"], "tool_call_limit_reached")
        self.assertEqual(result["tool_calls"], 2)

    def test_premature_completion_is_blocked(self):
        provider = SequenceProvider([("finish", {"status": "completed"})])
        result = run(request(), provider, ROOT / "data", max_calls=1)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["trace"][0]["observation"]["error"], "completion_blocked")

    def test_model_error_is_recorded(self):
        provider = MockProvider(request())
        with patch.object(provider, "respond", side_effect=ProviderError("test unavailable")):
            result = run(request(), provider, ROOT / "data")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["trace"][0]["kind"], "model_error")

    def test_plain_text_cannot_bypass_tools_or_loop_bound(self):
        provider = MockProvider(request())
        with patch.object(provider, "respond", return_value={"role": "assistant", "content": "已完成"}):
            result = run(request(), provider, ROOT / "data", max_calls=3)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["model_calls"], 3)
        self.assertEqual(result["tool_calls"], 0)

    def test_invalid_input(self):
        req = request()
        req["target_seconds"] = True
        with self.assertRaises(ValueError):
            self.execute(req)


class TransportTests(unittest.TestCase):
    def test_rate_limit_retry_is_bounded_and_recorded(self):
        import io
        import urllib.error
        errors = [urllib.error.HTTPError("https://test.invalid", 429, "limited", {},
                  io.BytesIO(b'{"error":{"code":"1305"}}')) for _ in range(3)]
        with patch.dict("os.environ", {"GLM_API_KEY": "test-secret", "GLM_MIN_INTERVAL": "0"}), patch("time.sleep"), patch("urllib.request.urlopen", side_effect=errors) as send:
            provider = GLMProvider()
            with self.assertRaises(ProviderError):
                provider.respond([], [])
        self.assertEqual(send.call_count, 3)
        self.assertEqual([e["status"] for e in provider.last_transport_events], [429, 429, 429])
        self.assertEqual(provider.last_transport_events[-1]["provider_error_code"], "1305")

    def test_http_auth_error_not_retried_or_leaked(self):
        import io
        import urllib.error
        error = urllib.error.HTTPError("https://test.invalid", 401, "unauthorized", {}, io.BytesIO(b'test-secret'))
        with patch.dict("os.environ", {"GLM_API_KEY": "test-secret"}), patch("urllib.request.urlopen", side_effect=error) as send:
            with self.assertRaises(ProviderError) as caught:
                GLMProvider().respond([], [])
        self.assertEqual(send.call_count, 1)
        self.assertNotIn("test-secret", str(caught.exception))

    def test_credentials_and_internal_reasoning_not_in_message(self):
        import io
        body = {"choices": [{"message": {"content": None, "reasoning_content": "PRIVATE INTERNAL",
                 "tool_calls": [{"id": "x", "type": "function", "function": {"name": "finish", "arguments": "{}"}}]}}]}
        response = io.BytesIO(json.dumps(body).encode())
        with patch.dict("os.environ", {"GLM_API_KEY": "test-secret"}), patch("urllib.request.urlopen", return_value=response):
            message = GLMProvider().respond([], [])
        self.assertNotIn("PRIVATE", json.dumps(message))
        self.assertNotIn("test-secret", json.dumps(message))


if __name__ == "__main__":
    unittest.main(verbosity=2)
