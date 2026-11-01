from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from codex_usage.sessions import scan_sessions


def usage(i=100, o=10, c=40, r=5):
    return {"input_tokens": i, "output_tokens": o, "cached_input_tokens": c,
            "reasoning_output_tokens": r, "total_tokens": i + o}


def row(kind, payload, n=0):
    return {"type": kind, "timestamp": f"2026-10-25T01:00:{n:02d}Z", "payload": payload}


def meta(sid="s1", **extra):
    return row("session_meta", {"id": sid, "session_id": sid, "cwd": "C:\\project", **extra})


def start(tid="t1", n=1):
    return row("event_msg", {"type": "task_started", "turn_id": tid}, n)


def context(tid="t1", model="gpt-6-astra", effort="high", n=2):
    return row("turn_context", {"turn_id": tid, "model": model, "effort": effort}, n)


def record(rid="r1", sid="s1", tid="t1", values=None, n=3):
    return row("token_usage_record", {"response_id": rid, "thread_id": sid,
                                      "turn_id": tid, "usage": values or usage()}, n)


def snapshot(total=None, last=None, n=4, **extra):
    return row("event_msg", {"type": "token_count", "info": {"total_token_usage": total or usage(),
                           "last_token_usage": last}, **extra}, n)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        (self.home/"sessions").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, rows, suffix=""):
        path = self.home/"sessions"/name
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n" + suffix, encoding="utf-8")
        return path

    def scan(self):
        return scan_sessions(self.home, current_account_id="account-a")

    def test_modern_and_legacy_are_not_added_twice(self):
        self.write("a.jsonl", [meta(), start(), context(), record(), snapshot(last=usage()),
                              snapshot(last=usage(), n=5)])
        result = self.scan()
        self.assertEqual(result["turns"][0]["total_tokens"], 110)
        self.assertEqual(result["turns"][0]["input_tokens"], 100)
        self.assertEqual(result["turns"][0]["cached_input_tokens"], 40)
        self.assertEqual(result["turns"][0]["output_tokens"], 10)
        self.assertEqual(result["turns"][0]["request_count"], 1)

    def test_response_id_dedup_across_files_and_session_rollovers(self):
        rows = [meta(), start(), context(), record()]
        self.write("a.jsonl", rows)
        self.write("b.jsonl", rows + [record("r2", values=usage(50, 5, 10, 2), n=5)])
        result = self.scan()
        self.assertEqual(len(result["sessions"]), 1)
        self.assertEqual(result["sessions"][0]["total_tokens"], 165)
        self.assertEqual(result["coverage"]["duplicate_response_records"], 1)

    def test_legacy_deltas_sum_per_turn_without_subsets_double_counted(self):
        self.write("a.jsonl", [meta(), start(), context(), snapshot(last=usage()),
                              snapshot(total=usage(300, 30, 120, 15), last=usage(200, 20, 80, 10), n=6),
                              snapshot(total=usage(300, 30, 120, 15), last=usage(200, 20, 80, 10), n=7)])
        turn = self.scan()["turns"][0]
        self.assertEqual(turn["total_tokens"], 330)
        self.assertEqual(turn["cached_input_tokens"], 120)
        self.assertEqual(turn["reasoning_output_tokens"], 15)
        self.assertEqual(turn["accounting_method"], "cumulative_delta")
        self.assertEqual(turn["request_count"], 0)  # snapshot deltas are not request IDs

    def test_resume_baseline_does_not_charge_inherited_history(self):
        self.write("a.jsonl", [meta(), start(), context(),
                              snapshot(total=usage(10000, 1000, 4000, 500), last=usage())])
        result = self.scan()
        self.assertEqual(result["turns"][0]["total_tokens"], 110)
        self.assertEqual(result["coverage"]["baseline_snapshots_with_prior_usage"], 1)

    def test_counter_reset_uses_last_response_only(self):
        self.write("a.jsonl", [meta(), start(), context(), snapshot(last=usage()),
                              snapshot(total=usage(50, 5, 20, 2), last=usage(50, 5, 20, 2), n=6),
                              snapshot(total=usage(50, 5, 20, 2), last=usage(50, 5, 20, 2), n=7)])
        result = self.scan()
        self.assertEqual(result["turns"][0]["total_tokens"], 165)
        self.assertEqual(result["coverage"]["counter_resets_or_replays"], 1)

    def test_snapshot_without_last_or_baseline_not_invented(self):
        self.write("a.jsonl", [meta(), start(), context(), snapshot(total=usage(10000, 1000), last=None)])
        result = self.scan()
        self.assertEqual(result["turns"][0]["total_tokens"], 0)
        self.assertEqual(result["coverage"]["unallocated_initial_snapshots"], 1)

    def test_models_and_efforts_preserved_within_same_turn(self):
        self.write("a.jsonl", [meta(), start(), context(), record(),
                              context(model="gpt-6.1-sol", effort="ultra", n=5), record("r2", n=6)])
        turn = self.scan()["turns"][0]
        self.assertEqual(turn["model"], "mixed")
        self.assertEqual(turn["reasoning_effort"], "mixed")
        self.assertEqual(len(turn["model_segments"]), 2)
        self.assertEqual({x["model"] for x in turn["model_segments"]}, {"gpt-6-astra", "gpt-6.1-sol"})
        self.assertEqual(turn["total_tokens"], 220)

    def test_subagent_identity_is_not_overwritten_by_inherited_parent_meta(self):
        self.write("a.jsonl", [meta("parent"), start("old"), context("old"), record("parent-response", "parent", "old")])
        child = meta("child", creator_account_id="account-a")
        child["payload"]["session_id"] = "parent"
        self.write("b.jsonl", [child, meta("parent"), start("new"), context("new"), record("child-response", "child", "new")])
        result = self.scan()
        child_session = next(s for s in result["sessions"] if s["id"] == "child")
        self.assertEqual(child_session["total_tokens"], 110)
        self.assertEqual(child_session["creator_account_id"], "account-a")
        self.assertEqual(child_session["root_session_id"], "parent")

    def test_inclusive_rollup_requires_explicit_root_ids_and_never_changes_direct_totals(self):
        self.write("a.jsonl", [meta("parent"), start("main"), context("main"), record("r-parent", "parent", "main")])
        child = meta("child", thread_source="subagent")
        child["payload"]["session_id"] = "parent"
        response = record("r-child", "child", "child-turn", values=usage(200, 20))
        response["payload"]["root_turn_id"] = "main"
        self.write("b.jsonl", [child, start("child-turn"), context("child-turn"), response])
        # Same root session, but an unknown root turn must not be attributed by time.
        orphan = record("r-orphan", "child", "orphan-turn", values=usage(300, 30), n=8)
        self.write("c.jsonl", [child, start("orphan-turn", 6), context("orphan-turn", n=7), orphan])
        result = self.scan()
        main = next(t for t in result["turns"] if t["id"] == "main")
        parent = next(s for s in result["sessions"] if s["id"] == "parent")
        self.assertEqual(main["total_tokens"], 110)
        self.assertEqual(main["inclusive_tokens"]["total_tokens"], 330)
        self.assertEqual(main["child_turn_count"], 1)
        self.assertEqual(parent["inclusive_tokens"]["total_tokens"], 660)
        self.assertEqual(parent["child_session_count"], 1)
        self.assertEqual(sum(s["total_tokens"] for s in result["sessions"]), 660)
        self.assertEqual(result["coverage"]["subagent_turns_without_verified_root_turn"], 1)

    def test_legacy_fork_replay_is_not_double_counted(self):
        rows = [start("old"), context("old"), snapshot(last=usage())]
        self.write("a.jsonl", [meta("parent"), *rows])
        self.write("b.jsonl", [meta("child", forked_from_id="parent"), *rows,
                              start("new", 5), context("new", n=6),
                              snapshot(total=usage(150, 15, 60, 7), last=usage(50, 5, 20, 2), n=7)])
        result = self.scan()
        self.assertEqual(sum(s["total_tokens"] for s in result["sessions"]), 165)

    def test_mixed_legacy_turn_with_incomplete_modern_records_warns(self):
        self.write("a.jsonl", [meta(), start(), context(), record(), snapshot(last=usage()),
                              snapshot(total=usage(200, 20, 80, 10), last=usage(), n=6)])
        result = self.scan()
        self.assertEqual(result["coverage"]["modern_records_below_legacy_deltas"], 1)
        self.assertEqual(result["turns"][0]["total_tokens"], 110)

    def test_subagent_inherited_history_is_skipped_and_native_usage_retained(self):
        self.write("a.jsonl", [meta("parent"), start("old"), context("old"), record("old-r", "parent", "old")])
        child_meta = meta("child", parent_thread_id="parent", creator_account_id="account-a", subagent_history_start_ordinal=5)
        child_meta["payload"]["session_id"] = "parent"
        self.write("b.jsonl", [child_meta, meta("parent"), start("old"), context("old"), record("old-r", "parent", "old"),
                              start("new", 6), context("new", n=7), record("new-r", "child", "new", n=8)])
        result = self.scan()
        self.assertEqual(sum(s["total_tokens"] for s in result["sessions"]), 220)
        child = next(s for s in result["sessions"] if s["id"] == "child")
        self.assertEqual(child["total_tokens"], 110)
        self.assertEqual(child["root_session_id"], "parent")
        self.assertEqual(child["attribution"], "matched")
        self.assertEqual(len(result["turns"]), 2)

    def test_creator_attribution_is_explicit_and_unknown_stays_unknown(self):
        self.write("a.jsonl", [meta(creator_account_id="account-a"), start(), context(), record()])
        self.write("b.jsonl", [meta("s2", creator_account_id="account-b"), start(), context(), record("r2", "s2")])
        self.write("c.jsonl", [meta("s3"), start(), context(), record("r3", "s3")])
        by_id = {x["id"]: x for x in self.scan()["sessions"]}
        self.assertEqual(by_id["s1"]["attribution"], "matched")
        self.assertEqual(by_id["s1"]["attribution_basis"], "session_creator_account_id")
        self.assertEqual(by_id["s2"]["attribution"], "other")
        self.assertEqual(by_id["s3"]["attribution"], "unknown")

    def test_rate_limits_are_allowlisted_and_timestamped(self):
        rate = {"limit_id": "codex", "primary": {"used_percent": 25, "window_minutes": 300,
                 "resets_at": 2000000000, "secret": "DO-NOT-EXPORT"}, "secondary": None,
                 "credits": {"has_credits": False, "unlimited": False, "balance": "0", "api_key": "DO-NOT-EXPORT"},
                 "auth_token": "DO-NOT-EXPORT"}
        self.write("a.jsonl", [meta(creator_account_id="account-a"), start(), context(), snapshot(last=usage(), rate_limits=rate)])
        result = self.scan()
        limit = result["rate_limits"][0]
        self.assertEqual(limit["primary"]["window_minutes"], 300)
        self.assertEqual(limit["source"]["line"], 4)
        self.assertEqual(limit["attribution"], "matched")
        self.assertNotIn("DO-NOT-EXPORT", json.dumps(result))

    def test_message_content_and_auth_are_never_exported(self):
        self.write("a.jsonl", [meta(base_instructions="PRIVATE-PROMPT", auth="PRIVATE-SECRET"),
                              start(), row("response_item", {"type": "message", "role": "user", "content": "PRIVATE-PROMPT"}),
                              context(), record()], suffix='{"incomplete":')
        result = self.scan()
        self.assertNotIn("PRIVATE", json.dumps(result))
        self.assertEqual(result["coverage"]["malformed_lines"], 1)

    def test_sources_are_read_only(self):
        path = self.write("a.jsonl", [meta(), start(), context(), record()])
        before = path.read_bytes(), path.stat().st_mtime_ns
        self.scan()
        self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns))

    def test_symlink_file_is_not_read(self):
        target = self.home/"target.jsonl"
        target.write_text(json.dumps(meta()) + "\n", encoding="utf-8")
        try:
            (self.home/"sessions"/"linked.jsonl").symlink_to(target)
        except OSError:
            self.skipTest("symlink privilege unavailable")
        self.assertEqual(self.scan()["coverage"]["files_discovered"], 0)


if __name__ == "__main__":
    unittest.main()
