"""Deterministic business tools, conservative grounding, versioned checks."""
import copy
import hashlib
import json
import math
import re
from pathlib import Path


def fingerprint(script):
    raw = json.dumps(script, sort_keys=True, ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")


def validate_script(script):
    if not isinstance(script, dict) or not isinstance(script.get("title"), str) or not script["title"].strip():
        raise ValueError("script needs a nonempty title")
    if set(script) != {"title", "shots"}:
        raise ValueError("script fields must be exactly title and shots")
    shots = script.get("shots")
    if not isinstance(shots, list) or not 1 <= len(shots) <= 12:
        raise ValueError("script needs 1..12 shots")
    for shot in shots:
        if not isinstance(shot, dict) or not isinstance(shot.get("visual"), str):
            raise ValueError("each shot needs visual")
        if set(shot) != {"visual", "hold_seconds", "lines"}:
            raise ValueError("shot fields must be visual, hold_seconds and lines")
        positive(shot.get("hold_seconds"), "hold_seconds")
        parts = shot.get("lines")
        if not isinstance(parts, list) or not 1 <= len(parts) <= 10:
            raise ValueError("each shot needs 1..10 lines")
        for part in parts:
            if not isinstance(part, dict) or not isinstance(part.get("text"), str) or not part["text"].strip():
                raise ValueError("each line needs nonempty text")
            if set(part) != {"text", "source_id", "fact_id"}:
                raise ValueError("line fields must be text, source_id and fact_id")
            if not isinstance(part.get("source_id"), (str, type(None))) or not isinstance(part.get("fact_id"), (str, type(None))):
                raise ValueError("source_id/fact_id must be strings or null")


class Tools:
    def __init__(self, data_dir, request, failures=None):
        root = Path(data_dir)
        self.catalog = json.loads((root / "materials.json").read_text(encoding="utf-8"))
        self.rules = json.loads((root / "brand_rules.json").read_text(encoding="utf-8"))
        positive(self.rules["speech_units_per_second"], "speech rate")
        self.request = copy.deepcopy(request)
        positive(request["target_seconds"], "target_seconds")
        self.script = None
        self.retrieved = {}
        self.duration = None
        self.check = None
        self.failures = dict(failures or {})

    def execute(self, name, args):
        if name not in {"search_materials", "set_script", "estimate_duration", "check_script", "finish"}:
            return {"ok": False, "error": "unknown_tool"}
        if self.failures.get(name, 0) > 0:
            self.failures[name] -= 1
            return {"ok": False, "error": "injected_tool_failure", "retryable": True}
        try:
            if not isinstance(args, dict):
                raise ValueError("arguments must be an object")
            return getattr(self, name)(**args)
        except (ValueError, TypeError, KeyError) as exc:
            return {"ok": False, "error": "invalid_arguments", "detail": str(exc)}

    def search_materials(self, query, reason):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be nonempty")
        terms = re.findall(r"[a-zA-Z0-9]+|[\u4e00-\u9fff]+", query.lower())
        ranked = []
        for doc in self.catalog["documents"]:
            haystack = " ".join(doc["tags"]) + " " + " ".join(f["text"] for f in doc["facts"])
            score = sum(t in haystack.lower() for t in terms)
            if score:
                ranked.append((score, doc))
        docs = [copy.deepcopy(d) for _, d in sorted(ranked, key=lambda x: -x[0])[:3]]
        for doc in docs:
            self.retrieved[doc["id"]] = doc
        return {"ok": True, "documents": docs, "count": len(docs), "synthetic": True}

    def set_script(self, script, reason):
        validate_script(script)
        self.script = copy.deepcopy(script)
        self.duration = self.check = None
        return {"ok": True, "script_hash": fingerprint(script), "checks_invalidated": True}

    def estimate_duration(self, reason):
        if self.script is None:
            raise ValueError("set a script first")
        shots = []
        for i, shot in enumerate(self.script["shots"], 1):
            text = "".join(p["text"] for p in shot["lines"])
            # One Han character or one Latin word/number = one speech unit.
            units = len(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", text))
            spoken = units / self.rules["speech_units_per_second"]
            seconds = round(max(spoken, shot["hold_seconds"]), 2)
            shots.append({"shot": i, "speech_units": units, "speech_seconds": round(spoken, 2), "seconds": seconds})
        total = round(sum(s["seconds"] for s in shots), 2)
        self.duration = {"ok": True, "script_hash": fingerprint(self.script), "shots": shots,
                         "total_seconds": total, "target_seconds": self.request["target_seconds"],
                         "passed": total <= self.request["target_seconds"],
                         "excess_seconds": round(max(0, total - self.request["target_seconds"]), 2),
                         "method": f"sum(max(speech_units/{self.rules['speech_units_per_second']}, hold_seconds)); estimated only"}
        return copy.deepcopy(self.duration)

    def check_script(self, reason):
        if self.script is None:
            raise ValueError("set a script first")
        issues = []
        citations = []
        if self.script["title"] not in self.rules["titles"]:
            issues.append({"code": "unapproved_title", "location": "title"})
        for i, shot in enumerate(self.script["shots"], 1):
            if shot["visual"] not in self.rules["visuals"]:
                issues.append({"code": "unapproved_visual", "shot": i})
            for j, line in enumerate(shot["lines"], 1):
                source, fid, text = line.get("source_id"), line.get("fact_id"), line["text"]
                loc = {"shot": i, "line": j}
                if source is None and fid is None and text in self.rules["neutral_lines"] + self.rules["titles"]:
                    continue
                doc = self.retrieved.get(source, {})
                fact = next((f for f in doc.get("facts", []) if f["id"] == fid), None)
                if not fact or text != fact["text"]:
                    matches = [{"source_id": d["id"], "fact_id": f["id"]} for d in self.retrieved.values()
                               for f in d["facts"] if f["text"] == text]
                    issues.append({"code": "unsupported_claim" if source or fid or matches else "unapproved_copy", **loc, "text": text,
                                   "source_id": source, "fact_id": fid, "exact_text_matches": matches,
                                   "repair_hint": "使用匹配到的来源和事实ID；没有匹配时删除该句或改用已批准中性句。"})
                else:
                    citations.append({**loc, "source_id": source, "fact_id": fid, "quote": fact["text"], "version": doc["version"]})
        content = json.dumps(self.script, ensure_ascii=False)
        for term in self.rules["banned_terms"]:
            if term in content:
                issues.append({"code": "banned_term", "term": term})
        if not citations:
            issues.append({"code": "no_supported_product_fact"})
        self.check = {"ok": True, "script_hash": fingerprint(self.script), "passed": not issues,
                      "issues": issues, "citations": citations, "scope": "exact approved facts and controlled copy; not a general semantic verifier"}
        return copy.deepcopy(self.check)

    def finish(self, status, reason):
        if status not in {"completed", "needs_input", "incomplete", "failed"}:
            raise ValueError("invalid status")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be nonempty")
        if status == "completed":
            current = fingerprint(self.script) if self.script else None
            if not all(r and r.get("passed") and r.get("script_hash") == current for r in (self.duration, self.check)):
                required = [name for name, report in (("estimate_duration", self.duration), ("check_script", self.check))
                            if not report or report.get("script_hash") != current]
                return {"ok": False, "error": "completion_blocked", "detail": "latest script must pass duration and rules checks",
                        "missing_current_checks": required, "duration": self.duration, "rule_check": self.check}
        return {"ok": True, "terminal": True, "status": status, "reason": reason}
