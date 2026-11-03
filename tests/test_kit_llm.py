# -*- coding: utf-8 -*-
"""kit/llm/score.py 시험 - 임시 폴더에 지어낸 답만 쓴다 (실데이터 없음 · matplotlib 없이 돈다)."""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit", "llm")
sys.path.insert(0, KIT)
import score  # noqa: E402

TRUTH = score.read_json(os.path.join(KIT, "synthetic", "truth.json"))
FACTS = score.read_json(os.path.join(KIT, "synthetic", "facts_lite.json"))
INTERVIEW = score.read_json(os.path.join(KIT, "synthetic", "interview_lite.json"))
EVIDENCE, ANSWER_IDS = score.known_ids(FACTS, INTERVIEW)
LAST_LINES = ("결과: OK", "결과: 확인 필요", "결과: 점검 실패")


def perfect_answers():
    """truth.json 에서 만든 만점 답 (칸 이름 → 값)"""
    k2 = TRUTH["kit2"]
    ans = {
        "k2.a.code": k2["a"]["code"], "k2.a.shape": k2["a"]["shape"],
        "k2.b.code": k2["b"]["code"], "k2.b.shape": k2["b"]["shape"],
        "k2.ping": score.ping_token(), "k2.attach": "붙여넣기", "k2.question": "선택화면",
        "k2.korean": "좋음", "k2.opencode": "1.0.0", "k2.b.config": "modalities", "peeked": "아니오",
    }
    for img_id, c in k2["ctx"].items():
        ans["k2.ctx.%s.tag" % img_id] = c["tag"]
        ans["k2.ctx.%s.facts" % img_id] = ", ".join(c["facts"])
    for cid, c in TRUTH["kit3"].items():
        for qid, q in c["questions"].items():
            t = q["truth"]
            ans["%s.%s" % (cid, qid)] = ", ".join(t) if isinstance(t, list) else str(t)
    return ans


def good_deck():
    s = lambda text, kind, refs, **kw: dict({"text": text, "kind": kind, "refs": refs}, **kw)  # noqa: E731
    return {
        "format": 1,
        "meta": {"type": "anomaly", "audience": "팀장", "title": "PRD_B 두께 상승", "date": "2026-10-01",
                 "host": "opencode", "data_class": "synthetic"},
        "slides": [
            {"id": "s1", "section": "요약", "title": s("PRD_B 두께가 9/16 부터 1.2 nm 올랐다", "사실", ["f003"])},
            {"id": "s2", "section": "현상", "title": s("PRD_B 만 9/16 부터 1.2 nm 올랐다", "사실", ["f003", "img2"]),
             "bullets": [s("PRD_A 는 변화가 없다", "사실", ["f002"]),
                         s("PRD_B 조건 쪽 원인이다", "해석", ["f003", "f002"], reasoning="한 제품만 움직였다")]},
            {"id": "s3", "section": "의견", "title": s("EQ-03 PM 조건을 다시 보자", "의견", ["a04"])},
            {"id": "s4", "section": "한계 · 다음", "title": s("PM 기록은 아직 다 보지 못했다", "미확인", [])},
        ],
        "open_items": [{"slot": "s3.title", "why": "확신 정도를 다시 묻기"}],
    }


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="kit_llm_")
        self.addCleanup(shutil.rmtree, self.dir, True)

    def write(self, name, obj):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            if isinstance(obj, str):
                f.write(obj)
            else:
                json.dump(obj, f, ensure_ascii=False)

    def put_decks(self, n=5, deck=None):
        for i in range(1, n + 1):
            self.write("deck_%d.json" % i, deck or good_deck())

    def run_score(self, *flags):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = score.main(["--results", self.dir] + list(flags))
            except SystemExit as e:                                 # argparse 사용법 오류
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def assert_last(self, out, expected):
        last = out.strip().splitlines()[-1]
        self.assertIn(last, LAST_LINES)
        self.assertEqual(last, expected)


class TestPing(Sandbox):
    def test_ping_prints_token_and_ok(self):
        code, out, _ = self.run_score("--ping")
        self.assertEqual(code, 0)
        self.assertIn("토큰: %s" % score.ping_token(), out)
        self.assert_last(out, "결과: OK")

    def test_ping_token_is_not_literal_in_source(self):
        with open(os.path.join(KIT, "score.py"), encoding="utf-8") as f:
            self.assertNotIn(score.ping_token(), f.read())

    def test_ping_as_subprocess(self):
        res = subprocess.run([sys.executable, os.path.join(KIT, "score.py"), "--ping"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)
        self.assertIn(score.ping_token().encode("ascii"), res.stdout)


class TestWhole(Sandbox):
    def test_perfect_answers_ok(self):
        self.write("answers.json", perfect_answers())
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 0, out)
        self.assertIn("KIT-2 초록 · KIT-3 초록", out)
        self.assert_last(out, "결과: OK")

    def test_text_answers_with_noise(self):
        lines = ["모델이 쓴 머리말입니다.", "```"]
        lines += ["%s: %s" % (k, v) for k, v in perfect_answers().items()]
        lines += ["```", "c01.q1:"]                                  # 빈 값은 앞의 답을 지우지 않는다
        self.write("answers.txt", "\n".join(lines))
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 0, out)

    def test_mostly_wrong_kit3_fails(self):
        ans = perfect_answers()
        for cid, c in TRUTH["kit3"].items():
            for qid, q in c["questions"].items():
                ans["%s.%s" % (cid, qid)] = "모름"
        self.write("answers.json", ans)
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 1)
        self.assertIn("KIT-3 빨강", out)
        self.assert_last(out, "결과: 점검 실패")

    def test_image_not_delivered_is_red(self):
        ans = perfect_answers()
        ans["k2.a.code"] = "그림 없음"
        ans["k2.b.code"] = "ABC-123"
        self.write("answers.json", ans)
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 1)
        self.assertIn("KIT-2 빨강", out)

    def test_one_delivery_is_enough(self):
        ans = perfect_answers()
        ans["k2.a.code"] = "그림 없음"
        self.write("answers.json", ans)
        self.put_decks()
        self.assertEqual(self.run_score()[0], 0)

    def test_wrong_ping_is_red(self):
        ans = perfect_answers()
        ans["k2.ping"] = "PING-000000"
        self.write("answers.json", ans)
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 1)

    def test_missing_answers_need_check(self):
        ans = perfect_answers()
        del ans["c05.q3"]
        self.write("answers.json", ans)
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 3)
        self.assertIn("KIT-3 보류", out)
        self.assert_last(out, "결과: 확인 필요")

    def test_three_of_five_decks_is_yellow(self):
        self.write("answers.json", perfect_answers())
        self.put_decks(3)
        self.write("deck_4.json", "```json\n{}\n```")
        self.write("deck_5.json", {"format": 1})
        code, out, _ = self.run_score()
        self.assertEqual(code, 3)
        self.assertIn("KIT-2 노랑", out)

    def test_two_of_five_decks_is_red(self):
        self.write("answers.json", perfect_answers())
        self.put_decks(2)
        code, out, _ = self.run_score()
        self.assertEqual(code, 1)
        self.assertIn("deck_3.json  파일 없음", out)

    def test_peeked_needs_check(self):
        ans = perfect_answers()
        ans["peeked"] = "예"
        self.write("answers.json", ans)
        self.put_decks()
        code, out, _ = self.run_score()
        self.assertEqual(code, 3)

    def test_raw_answer_text_not_echoed(self):
        ans = perfect_answers()
        ans["c02.q1"] = "SECRETWORD 가 보입니다"
        self.write("answers.json", ans)
        self.put_decks()
        _, out, _ = self.run_score()
        self.assertNotIn("SECRETWORD", out)


K2_RE = re.compile(r"^K2 [GYR-] [ABX-] [OX-] [OTX?] ([0-5]|-)$")
K3_RE = re.compile(r"^K3 [GYR-] (\d+|-) (\d+|-) [01]$")
LETTER = {"초록": "G", "노랑": "Y", "빨강": "R", "보류": "-"}


def main_totals():
    cat = num = 0
    for c in TRUTH["kit3"].values():
        if c["group"] != "main":
            continue
        for q in c["questions"].values():
            if q["type"] == "choice":
                cat += 1
            else:
                num += 1
    return cat, num


class TestSendLines(Sandbox):
    def send(self, out):
        lines = out.rstrip("\n").splitlines()
        self.assertIn(lines[-1], LAST_LINES)
        self.assertTrue(lines[-3].startswith("보낼 줄: K2 "), lines[-3])
        self.assertTrue(lines[-2].startswith("보낼 줄: K3 "), lines[-2])
        self.assertEqual(sum(1 for l in lines if l.startswith("보낼 줄:")), 2)
        k2, k3 = lines[-3][len("보낼 줄: "):], lines[-2][len("보낼 줄: "):]
        k2.encode("ascii"), k3.encode("ascii")
        self.assertRegex(k2, K2_RE)
        self.assertRegex(k3, K3_RE)
        return k2.split(), k3.split()

    def verdicts(self, out):
        m = re.search(r"KIT-2 (\S+) · KIT-3 (\S+)", out)
        return LETTER[m.group(1)], LETTER[m.group(2)]

    def test_totals_come_from_truth(self):
        self.assertEqual(main_totals(), (17, 9))                 # truth.json 이 바뀌면 이 시험이 알려 준다

    def test_perfect(self):
        self.write("answers.json", perfect_answers())
        self.put_decks()
        code, out, _ = self.run_score()
        k2, k3 = self.send(out)
        cat, num = main_totals()
        self.assertEqual(k2, ["K2", "G", "A", "O", "O", "5"])
        self.assertEqual(k3, ["K3", "G", str(cat), str(num), "0"])
        self.assertEqual((k2[1], k3[1]), self.verdicts(out))
        self.assertEqual(code, 0)

    def test_counts_never_exceed_truth_totals(self):
        ans = perfect_answers()
        ans["c02.q1"] = "모름"
        ans["c01.q2"] = "99999"
        self.write("answers.json", ans)
        self.put_decks()
        _, out, _ = self.run_score()
        _, k3 = self.send(out)
        cat, num = main_totals()
        self.assertEqual((int(k3[2]), int(k3[3])), (cat - 1, num - 1))
        self.assertEqual(k3[1], self.verdicts(out)[1])

    def test_image_b_only_and_question_variants(self):
        for value, letter in (("글목록", "T"), ("안함", "X")):
            ans = perfect_answers()
            ans["k2.a.code"] = "ZZZ-000"
            ans["k2.question"] = value
            self.write("answers.json", ans)
            self.put_decks()
            _, out, _ = self.run_score()
            k2, _ = self.send(out)
            self.assertEqual((k2[2], k2[4]), ("B", letter))

    def test_image_not_delivered_is_x_and_red(self):
        ans = perfect_answers()
        ans["k2.a.code"] = "그림 없음"
        ans["k2.b.code"] = "ABC-123"
        self.write("answers.json", ans)
        self.put_decks()
        _, out, _ = self.run_score()
        k2, _ = self.send(out)
        self.assertEqual((k2[1], k2[2]), ("R", "X"))
        self.assertEqual(k2[1], self.verdicts(out)[0])

    def test_wrong_ping_is_tool_x(self):
        ans = perfect_answers()
        ans["k2.ping"] = "PING-000000"
        self.write("answers.json", ans)
        self.put_decks()
        _, out, _ = self.run_score()
        k2, _ = self.send(out)
        self.assertEqual((k2[1], k2[3]), ("R", "X"))

    def test_missing_fields_are_dash_or_question_mark(self):
        ans = perfect_answers()
        for k in ("k2.question", "k2.ping", "k2.a.code", "k2.b.code"):
            del ans[k]
        del ans["c05.q3"]
        self.write("answers.json", ans)
        _, out, _ = self.run_score()                              # deck 파일 없음
        k2, k3 = self.send(out)
        self.assertEqual(k2, ["K2", "-", "-", "-", "?", "-"])
        self.assertEqual(k3[1], "-")
        self.assertEqual(k3[1], self.verdicts(out)[1])

    def test_three_decks_yellow_and_pass_count(self):
        self.write("answers.json", perfect_answers())
        self.put_decks(3)
        self.write("deck_4.json", "```json\n{}\n```")
        self.write("deck_5.json", {"format": 1})
        _, out, _ = self.run_score()
        k2, _ = self.send(out)
        self.assertEqual((k2[1], k2[5]), ("Y", "3"))
        self.assertEqual(k2[1], self.verdicts(out)[0])

    def test_peeked_variants(self):
        for value, flag in (("예", "1"), ("yes", "1"), ("1", "1"), ("아니오", "0")):
            ans = perfect_answers()
            ans["peeked"] = value
            self.write("answers.json", ans)
            self.put_decks()
            code, out, _ = self.run_score()
            _, k3 = self.send(out)
            self.assertEqual(k3[4], flag, value)
            self.assertEqual(code, 3 if flag == "1" else 0)
            self.assert_last(out, "결과: 확인 필요" if flag == "1" else "결과: OK")

    def test_kit3_all_wrong_is_red_with_zero_counts(self):
        ans = perfect_answers()
        for cid, c in TRUTH["kit3"].items():
            for qid in c["questions"]:
                ans["%s.%s" % (cid, qid)] = "모름"
        self.write("answers.json", ans)
        self.put_decks()
        _, out, _ = self.run_score()
        _, k3 = self.send(out)
        self.assertEqual(k3[1:4], ["R", "0", "0"])


class TestUsage(Sandbox):
    def test_empty_folder_is_usage_error(self):
        code, out, err = self.run_score()
        self.assertEqual(code, 2)
        self.assertIn("사용법 오류", err)

    def test_missing_folder_is_usage_error(self):
        code, _, _ = self.run_score("--results", os.path.join(self.dir, "없음"))
        self.assertEqual(code, 2)

    def test_bad_json_is_usage_error(self):
        self.write("answers.json", "{ 깨진")
        self.assertEqual(self.run_score()[0], 2)

    def test_unknown_flag_is_usage_error(self):
        self.assertEqual(self.run_score("--모름")[0], 2)


class TestQuestions(unittest.TestCase):
    def q(self, cid, qid):
        return TRUTH["kit3"][cid]["questions"][qid]

    def test_choice_synonyms_and_sentence(self):
        q = self.q("c02", "q2")
        self.assertTrue(score.score_question(q, "왼쪽 아래")[0])
        self.assertTrue(score.score_question(q, "왼쪽아래 입니다")[0])
        self.assertTrue(score.score_question(q, "lower left")[0])
        self.assertFalse(score.score_question(q, "오른쪽 아래")[0])
        self.assertFalse(score.score_question(q, "왼쪽")[0])

    def test_choice_band_labels(self):
        q = self.q("c02", "q3")
        self.assertTrue(score.score_question(q, q["truth"])[0])
        self.assertTrue(score.score_question(q, "50-100")[0])
        self.assertFalse(score.score_question(q, "20–50개")[0])

    def test_number_band_edges(self):
        q = self.q("c01", "q2")
        self.assertTrue(score.score_question(q, "약 %gσ" % q["lo"])[0])
        self.assertTrue(score.score_question(q, str(q["hi"]))[0])
        self.assertFalse(score.score_question(q, "%g" % (q["hi"] + 0.05))[0])
        self.assertFalse(score.score_question(q, "모름")[0])

    def test_exact_count(self):
        q = self.q("c08", "q1")
        self.assertTrue(score.score_question(q, "3개")[0])
        self.assertFalse(score.score_question(q, "4")[0])

    def test_date_tolerance(self):
        q = self.q("c01", "q1")                                      # 2026-10-01 ±3
        self.assertTrue(score.score_question(q, "2026-10-04")[0])
        self.assertTrue(score.score_question(q, "9월 28일")[0])
        self.assertFalse(score.score_question(q, "10/05")[0])

    def test_dates_set(self):
        q = self.q("c08", "q2")
        shifted = []
        for s in reversed(q["truth"]):                               # 순서를 바꾸고 하루씩 밀어도 맞음
            y, m, d = (int(x) for x in s.split("-"))
            shifted.append("%d.%d.%d" % (y, m, d + 1))
        self.assertTrue(score.score_question(q, ", ".join(shifted))[0])
        self.assertFalse(score.score_question(q, ", ".join(q["truth"][:2]))[0])
        self.assertIsNone(score.score_question(q, "")[0])

    def test_wilson_and_judge(self):
        lo, hi = score.wilson(4, 5)
        self.assertAlmostEqual(lo, 0.376, places=2)
        self.assertEqual(score.judge(4, 5, 0.8, 0.35), score.GREEN)
        self.assertEqual(score.judge(3, 5, 0.8, 0.35), score.YELLOW)
        self.assertEqual(score.judge(2, 5, 0.8, 0.35), score.RED)
        self.assertEqual(score.judge(0, 0, 0.8, 0.35), score.HOLD)


class TestDeck(unittest.TestCase):
    def check(self, deck):
        return score.validate_deck(deck, EVIDENCE, ANSWER_IDS)

    def test_good_deck_passes(self):
        self.assertEqual(self.check(good_deck()), ([], []))

    def test_section_spacing_is_forgiven(self):
        d = good_deck()
        d["slides"][3]["section"] = "한계·다음"
        self.assertEqual(self.check(d), ([], []))

    def test_structure_errors(self):
        for mutate in (
            lambda d: d.update(format=2),
            lambda d: d["meta"].update(type="report"),
            lambda d: d["meta"].update(date="2026/10/01"),
            lambda d: d["meta"].pop("host"),
            lambda d: d["slides"][0]["title"].update(kind="주장"),
            lambda d: d["slides"][0].update(layout="title_only"),
            lambda d: d["slides"][1].update(id="s1"),
            lambda d: d.update(slides=d["slides"][:2]),
            lambda d: d.update(open_items=[{"slot": "s1"}]),
        ):
            d = good_deck()
            mutate(d)
            struct, gram = self.check(d)
            self.assertTrue(struct, d)
            self.assertEqual(gram, [])

    def test_missing_ref(self):
        d = good_deck()
        d["slides"][0]["title"]["refs"] = ["f099"]
        struct, gram = self.check(d)
        self.assertEqual(struct, [])
        self.assertTrue(any("없는 근거 f099" in g for g in gram))

    def test_opinion_without_answer_id(self):
        d = good_deck()
        d["slides"][2]["title"]["refs"] = ["f003"]
        _, gram = self.check(d)
        self.assertTrue(any("V-02" in g for g in gram))

    def test_interpretation_needs_two_facts_and_reasoning(self):
        d = good_deck()
        b = d["slides"][1]["bullets"][1]
        b["refs"] = ["f003"]
        del b["reasoning"]
        _, gram = self.check(d)
        self.assertEqual(len(gram), 2)

    def test_section_order_and_limits(self):
        d = good_deck()
        d["slides"].reverse()
        _, gram = self.check(d)
        self.assertTrue(any("P-05" in g for g in gram))
        d = good_deck()
        d["slides"][3]["section"] = "부록"
        _, gram = self.check(d)
        self.assertTrue(any("한계 · 다음 절이 없음" in g for g in gram))

    def test_fenced_file_is_structure_failure(self):
        tmp = tempfile.mkdtemp(prefix="kit_llm_")
        self.addCleanup(shutil.rmtree, tmp, True)
        path = os.path.join(tmp, "deck_1.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("```json\n" + json.dumps(good_deck(), ensure_ascii=False) + "\n```")
        struct, _ = score.check_deck_file(path, EVIDENCE, ANSWER_IDS)
        self.assertTrue(struct[0].startswith("JSON"))


class TestTruthFile(unittest.TestCase):
    def test_template_has_every_question(self):
        tpl = score.read_json(os.path.join(KIT, "answers_template.json"))
        for cid, c in TRUTH["kit3"].items():
            for qid in c["questions"]:
                self.assertIn("%s.%s" % (cid, qid), tpl)

    def test_every_image_exists(self):
        for name in TRUTH["images"]:
            self.assertTrue(os.path.isfile(os.path.join(KIT, "synthetic", name)), name)

    def test_prompt_per_chart(self):
        for cid, c in TRUTH["kit3"].items():
            path = os.path.join(KIT, "prompts", "k3_%s.md" % cid)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn(c["image"], text)
            for qid in c["questions"]:
                self.assertIn("%s.%s:" % (cid, qid), text)


class TestPrepare(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="kit_llm_work_")
        self.addCleanup(shutil.rmtree, self.base, True)
        self.work = os.path.join(self.base, "m0")

    def run_prepare(self, out):
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = score.main(["prepare", "--out", out])
        return code, buf.getvalue(), err.getvalue()

    def all_files(self):
        found = []
        for dirpath, _, names in os.walk(self.work):
            for n in names:
                found.append(os.path.relpath(os.path.join(dirpath, n), self.work).replace(os.sep, "/"))
        return sorted(found)

    def test_copies_only_what_the_model_needs(self):
        code, out, _ = self.run_prepare(self.work)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[-1], "결과: OK")
        files = self.all_files()
        for name in TRUTH["images"]:
            self.assertIn("inputs/" + name, files)
        for name in ("inputs/facts_lite.json", "inputs/interview_lite.json", "ping.py", "answers_template.json"):
            self.assertIn(name, files)
        self.assertTrue(os.path.isdir(os.path.join(self.work, "results")))
        self.assertEqual(os.listdir(os.path.join(self.work, "results")), [])
        prompts = sorted(n for n in os.listdir(os.path.join(KIT, "prompts")) if n.endswith(".md"))
        self.assertEqual([f[len("prompts/"):] for f in files if f.startswith("prompts/")], prompts)
        for f in files:                                              # 정답 · 채점기 · 문턱이 없다
            self.assertNotIn(os.path.basename(f), ("truth.json", "score.py", "README.md", "make_inputs.py"))

    def test_no_answers_or_rules_leak(self):
        self.run_prepare(self.work)
        secrets = [score.ping_token(), "thresholds", "tol_days", "\"kit3\"", "V-02 가"]
        for c in TRUTH["kit2"]["ctx"].values():
            secrets.append(c["tag"])
        secrets += [TRUTH["kit2"]["a"]["code"], TRUTH["kit2"]["b"]["code"]]
        for f in self.all_files():
            if f.endswith(".png"):
                continue
            with open(os.path.join(self.work, f), encoding="utf-8") as fh:
                text = fh.read()
            for word in secrets:
                self.assertNotIn(word, text, f)
        tpl = score.read_json(os.path.join(self.work, "answers_template.json"))
        self.assertTrue(all(v == "" and not k.startswith("_") for k, v in tpl.items()))

    def test_prompts_use_work_relative_paths(self):
        self.run_prepare(self.work)
        pdir = os.path.join(self.work, "prompts")
        for n in os.listdir(pdir):
            with open(os.path.join(pdir, n), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("kit/", text, n)
            for rel in re.findall(r"inputs/[A-Za-z0-9_]+\.(?:png|json)", text):
                self.assertTrue(os.path.isfile(os.path.join(self.work, *rel.split("/"))), rel)

    def test_ping_py_matches_score_ping(self):
        self.run_prepare(self.work)
        res = subprocess.run([sys.executable, "ping.py"], cwd=self.work,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(res.returncode, 0)
        self.assertIn(("토큰: " + score.ping_token()).encode("utf-8"), res.stdout)

    def test_refuses_non_empty_and_never_overwrites(self):
        os.makedirs(self.work)
        keep = os.path.join(self.work, "mine.txt")
        with open(keep, "w", encoding="utf-8") as fh:
            fh.write("내 파일")
        code, _, err = self.run_prepare(self.work)
        self.assertEqual(code, 2)
        self.assertIn("비어 있지 않습니다", err)
        self.assertEqual(os.listdir(self.work), ["mine.txt"])

    def test_empty_existing_folder_is_fine(self):
        os.makedirs(self.work)
        self.assertEqual(self.run_prepare(self.work)[0], 0)

    def test_refuses_inside_repo(self):
        code, _, err = self.run_prepare(os.path.join(KIT, "work_should_not_exist"))
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(os.path.join(KIT, "work_should_not_exist")))

    def test_scores_work_results_with_dir(self):
        self.run_prepare(self.work)
        results = os.path.join(self.work, "results")
        with open(os.path.join(results, "answers.json"), "w", encoding="utf-8") as fh:
            json.dump(perfect_answers(), fh, ensure_ascii=False)
        for i in range(1, 6):
            with open(os.path.join(results, "deck_%d.json" % i), "w", encoding="utf-8") as fh:
                json.dump(good_deck(), fh, ensure_ascii=False)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(score.main(["--dir", results]), 0)


if __name__ == "__main__":
    unittest.main()
