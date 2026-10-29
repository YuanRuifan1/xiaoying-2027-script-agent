"""GLM HTTPS adapter and explicitly synthetic offline policy."""
import copy
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


def load_env(path):
    if not Path(path).exists():
        return
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


class ProviderError(RuntimeError):
    pass


class GLMProvider:
    mode = "real"

    def __init__(self):
        self.key = os.getenv("GLM_API_KEY", "")
        if not self.key:
            raise ProviderError("GLM_API_KEY is missing; configure local .env or use --provider mock")
        base = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
        if not base.startswith("https://"):
            raise ProviderError("GLM_BASE_URL must use HTTPS")
        self.url = base + "/chat/completions"
        self.model = os.getenv("GLM_MODEL", "glm-4.7-flash")
        self.timeout = float(os.getenv("GLM_TIMEOUT", "60"))
        self.last_usage = None
        self.last_transport_events = []
        self.min_interval = float(os.getenv("GLM_MIN_INTERVAL", "5"))
        self.last_request_at = 0.0

    def respond(self, messages, schemas):
        self.last_transport_events = []
        payload = {"model": self.model, "messages": messages, "tools": schemas,
                   "tool_choice": "auto", "stream": False, "max_tokens": 4096}
        if self.model.startswith(("glm-4.5", "glm-4.6", "glm-4.7", "glm-5")):
            payload["thinking"] = {"type": "disabled"}
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.key})
        try:
            for attempt in range(3):
                delay = max(0, self.min_interval - (time.monotonic() - self.last_request_at))
                if delay:
                    time.sleep(delay)
                self.last_request_at = time.monotonic()
                try:
                    with urllib.request.urlopen(request, timeout=self.timeout) as response:
                        body = json.load(response)
                    self.last_transport_events.append({"attempt": attempt + 1, "status": 200})
                    break
                except urllib.error.HTTPError as error:
                    event = {"attempt": attempt + 1, "status": error.code}
                    try:
                        code = str(json.loads(error.read()).get("error", {}).get("code", ""))
                        if code.isdigit():
                            event["provider_error_code"] = code
                    except (ValueError, AttributeError):
                        pass
                    self.last_transport_events.append(event)
                    if error.code != 429 or attempt == 2:
                        raise
                    time.sleep(5 * (attempt + 1))
            self.last_usage = body.get("usage")
            raw = body["choices"][0]["message"]
            # Never retain reasoning_content, credentials or HTTP headers in Trace.
            return {"role": "assistant", "content": raw.get("content"),
                    **({"tool_calls": raw["tool_calls"]} if raw.get("tool_calls") else {})}
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"GLM HTTP {exc.code}; check account/model/quota; response body omitted") from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, IndexError) as exc:
            raise ProviderError(f"GLM transport or response error ({type(exc).__name__}); details omitted") from None


def sample_script(long=False):
    return {"title": "字幕编辑小指南", "shots": [
        {"visual": "标题卡", "hold_seconds": 3, "lines": [{"text": "想给画面加点表达？", "source_id": None, "fact_id": None}]},
        {"visual": "字幕编辑界面示意", "hold_seconds": 38 if long else 5,
         "lines": [{"text": "支持手动编辑字幕。", "source_id": "P01", "fact_id": "F01"}]},
        {"visual": "结束卡", "hold_seconds": 3, "lines": [{"text": "试试字幕编辑吧。", "source_id": None, "fact_id": None}]}
    ]}


class MockProvider:
    """A fixed offline policy. This is not model reasoning evidence."""
    mode = "mock"
    model = "offline-fixed-policy-v1"
    last_usage = None

    def __init__(self, request):
        self.request = request
        self.calls = 0

    def respond(self, messages, schemas):
        self.calls += 1
        events = []
        pending = {}
        for msg in messages:
            for call in msg.get("tool_calls", []):
                pending[call["id"]] = call["function"]["name"]
            if msg["role"] == "tool":
                events.append((pending.get(msg["tool_call_id"]), json.loads(msg["content"])))
        last_name, last = events[-1] if events else (None, {})
        reason = "离线固定策略，仅验证工程流程。"
        if last and not last.get("ok"):
            name, args = "finish", {"status": "failed", "reason": "离线策略观察到工具错误，保留已有结果并停止。"}
        elif not events:
            name, args = "search_materials", {"query": self.request["theme"], "reason": reason}
        elif last_name == "search_materials":
            if not last["count"]:
                name, args = "finish", {"status": "needs_input", "reason": "无匹配产品资料，请补充资料。"}
            else:
                if "initial_draft" in self.request:
                    name, args = "estimate_duration", {"reason": reason}
                else:
                    name, args = "set_script", {"script": sample_script(), "reason": reason}
        elif last_name == "set_script":
            name, args = "estimate_duration", {"reason": reason}
        elif last_name == "estimate_duration" and not last["passed"]:
            if any(n == "estimate_duration" and not r.get("passed") for n, r in events[:-1]):
                name, args = "finish", {"status": "incomplete", "reason": "压缩后仍超过目标时长。"}
            else:
                name, args = "set_script", {"script": sample_script(), "reason": "离线固定压缩策略。"}
        elif last_name == "estimate_duration":
            name, args = "check_script", {"reason": reason}
        elif last_name == "check_script":
            name, args = "finish", {"status": "completed" if last["passed"] else "incomplete", "reason": reason}
        else:
            name, args = "finish", {"status": "incomplete", "reason": reason}
        return {"role": "assistant", "content": None, "tool_calls": [
            {"id": f"mock-{self.calls}", "type": "function", "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}]}
