# -*- coding: utf-8 -*-
"""스킬 묶음 (SKILL.md · opencode 에이전트 · 명령 · 모범 대화) 이 기획 · 명세와 어긋나지 않는지 본다.

- SKILL.md 는 호스트 이름 · 도구 이름 없이 쓰고, 절 머리 · 꼬리표 · id 모양은 docs/SPEC-deck-md.md 와 글자까지 같다.
- 질문 은행은 docs/PLAN.md 부록 B 와 같고, 예산은 틀 3 · 현상 3 · 분석 4 · 의견 2 = 12 다.
- 에이전트 권한은 셸 · 웹 · 하위 에이전트 · 선택 화면을 막고, 쓰기는 deck.md 이름 규칙에만 묻는다.
- 모범 대화는 예산 안이고, 답 id 는 tests/fixtures/deck/interview_lite.json 과 같다.

표준 라이브러리만 · Python 3.8 · 머리말은 손으로 읽는다 (yaml 없음).
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, "skills", "subordinate-1")
SKILL = os.path.join(SKILL_DIR, "SKILL.md")
AGENT = os.path.join(ROOT, "opencode", "agents", "subordinate-1.md")
COMMAND = os.path.join(ROOT, "opencode", "commands", "subordinate.md")
DIALOGUE = os.path.join(ROOT, "docs", "examples", "interview_synthetic.md")
DECK = os.path.join(ROOT, "docs", "examples", "deck_synthetic.md")
SPEC = os.path.join(ROOT, "docs", "SPEC-deck-md.md")
PLAN = os.path.join(ROOT, "docs", "PLAN.md")
FIXTURES = os.path.join(ROOT, "tests", "fixtures", "deck")

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
EMOJI_RE = re.compile(u"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")
HOST_RE = re.compile(r"opencode|claude", re.I)
# SKILL.md 에 쓰지 않는 호스트 도구 이름 (D2 — 동작으로 쓴다)
TOOL_WORDS = {"question", "skill", "read", "write", "edit", "bash", "glob", "grep", "task",
              "webfetch", "websearch", "todowrite", "patch"}
STAGES = ["틀", "현상", "분석", "의견"]
BUDGET = {"틀": 3, "현상": 3, "분석": 4, "의견": 2}
BANK_ROW_RE = re.compile(r"^\| (B\d+) \| (.+?) \| (.+?) \| (.+?) \|$", re.M)
QUESTION_RE = re.compile(r"^\[질문 (\d+)/12 · (\S+) (\d+)/(\d+)\]$", re.M)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if len(s) >= 2 and s[0] == s[-1] == '"':
        return re.sub(r'\\(.)', r"\1", s[1:-1])
    return s


def split_key(line):
    """'key: value' 를 (key, value) 로. key 는 따옴표를 칠 수 있다."""
    m = re.match(r"""^("(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^:]+):(?:\s+(.*))?$""", line)
    if not m:
        raise ValueError("머리말 줄을 읽지 못함: %r" % line)
    return unquote(m.group(1)), (m.group(2) or "").strip()


def frontmatter(text):
    """(머리말 dict, 본문). 들여쓰기 두 칸의 겹친 칸과 스칼라 값만 읽는다. 칸 순서를 지킨다 (규칙 순서)."""
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise ValueError("머리말 없음")
    end = lines.index("---", 1)
    root = []
    stack = [(-1, root)]
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, value = split_key(raw.strip())
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value:
            parent.append((key, unquote(value)))
        else:
            child = []
            parent.append((key, child))
            stack.append((indent, child))
    return root, "\n".join(lines[end + 1:])


def get(pairs, key, default=None):
    for k, v in pairs:
        if k == key:
            return v
    return default


def wildcard(pattern, text):
    """opencode 권한 무늬: * 는 아무 글자 0개 이상 · ? 는 한 글자 · 나머지는 그대로."""
    rx = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    return re.match("^" + rx + "$", text, re.S) is not None


def decide(rules, text):
    """규칙 목록 [(무늬, 동작)] 에서 마지막으로 맞은 규칙의 동작. 하나도 안 맞으면 None."""
    if isinstance(rules, str):
        return rules
    out = None
    for pattern, action in rules:
        if wildcard(pattern, text):
            out = action
    return out


def spec_section(text, number):
    m = re.search(r"^## %d [^\n]*\n(.*?)(?=^## \d+ |\Z)" % number, text, re.S | re.M)
    return m.group(1) if m else ""


class SkillFileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(SKILL)
        cls.front, cls.body = frontmatter(cls.text)
        cls.spec = read(SPEC)

    def test_name_matches_folder(self):
        name = get(self.front, "name")
        self.assertEqual(name, os.path.basename(SKILL_DIR))
        self.assertTrue(NAME_RE.match(name) and len(name) <= 64)

    def test_description_length(self):
        desc = get(self.front, "description") or ""
        self.assertTrue(1 <= len(desc) <= 1024, len(desc))

    def test_host_neutral(self):
        self.assertIsNone(HOST_RE.search(self.text))
        words = {w.lower() for w in re.findall(r"[A-Za-z_]+", self.text)}
        self.assertEqual(words & TOOL_WORDS, set())

    def test_no_todo_or_emoji(self):
        self.assertNotIn("TODO", self.text)
        self.assertIsNone(EMOJI_RE.search(self.text))

    def test_section_heads_match_spec(self):
        rx = re.compile(r"머리 이름과 순서: ((?:`[^`]+` › )+`[^`]+`)")
        spec = rx.search(self.spec)
        skill = rx.search(self.text)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(skill)
        heads = re.findall(r"`([^`]+)`", spec.group(1))
        self.assertEqual(heads, re.findall(r"`([^`]+)`", skill.group(1)))
        self.assertEqual(heads, ["요약", "현상", "현상 범위", "분석", "의견", "한계", "부록"])

    def test_tag_table_matches_spec(self):
        row = re.compile(r"^\| (사실|해석|의견|추정|미확인) \| (.+?) \|", re.M)
        spec_rows = row.findall(spec_section(self.spec, 5))
        self.assertEqual(len(spec_rows), 5)
        m = re.search(r"^### 6\.4 [^\n]*\n(.*?)(?=^### )", self.text, re.S | re.M)
        self.assertIsNotNone(m)
        self.assertEqual(spec_rows, row.findall(m.group(1)))

    def test_id_shape_matches_spec(self):
        rx = re.compile(r"id 모양: .*?\(`a02`\)")
        spec = rx.search(self.spec)
        self.assertIsNotNone(spec)
        self.assertIn(spec.group(0), self.text)

    def test_line_shapes_match_spec(self):
        for shape in ["`근거: 파일 · 기간 · n · 거르기 · 집계 · 검정 [id …]`",
                      "`![imgN · 무엇을 보이나](상대 경로)`",
                      "`:::::: columns`", "`::: notes`", "`해석 근거:`", "`- [미확인] 없음`"]:
            self.assertIn(shape, self.spec)
            self.assertIn(shape, self.text)

    def test_front_keys_match_spec(self):
        keys = re.findall(r"^\| `([a-z_.]+)`(?: · `([a-z_.]+)`)? \|", spec_section(self.spec, 2), re.M)
        names = [k for pair in keys for k in pair if k]
        self.assertGreaterEqual(len(names), 9)
        for k in names:
            self.assertIn("`%s`" % k, self.text)
        self.assertIn("`author` 는 쓰지 않는다", self.text)

    def test_checklist_has_every_spec_item(self):
        spec_items = re.findall(r"^\d+\. ", spec_section(self.spec, 10), re.M)
        m = re.search(r"^### 7\.2 [^\n]*\n(.*?)(?=^### )", self.text, re.S | re.M)
        self.assertIsNotNone(m)
        self.assertEqual(len(spec_items), len(re.findall(r"^\d+\. ", m.group(1), re.M)))

    def test_one_file(self):
        self.assertEqual(sorted(os.listdir(SKILL_DIR)), ["SKILL.md"])


class QuestionBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = read(SKILL)
        cls.plan = read(PLAN)

    def test_bank_matches_plan(self):
        m = re.search(r"^### B 질문 은행[^\n]*\n(.*?)(?=^### )", self.plan, re.S | re.M)
        self.assertIsNotNone(m)
        plan_rows = BANK_ROW_RE.findall(m.group(1))
        self.assertEqual([r[0] for r in plan_rows], ["B%d" % i for i in range(1, 11)])
        self.assertEqual(plan_rows, BANK_ROW_RE.findall(self.skill))

    def test_budget(self):
        rows = dict(re.findall(r"^\| (틀|현상|분석|의견|합) \| (\d+) \|", self.skill, re.M))
        self.assertEqual({k: int(v) for k, v in rows.items() if k != "합"}, BUDGET)
        self.assertEqual(int(rows["합"]), 12)
        self.assertEqual(sum(BUDGET.values()), 12)
        self.assertIn("틀 3 · 현상 3 · 분석 4 · 의견 2 = 12", self.plan)
        self.assertIn("틀 3 · 현상 3 · 분석 4 · 의견 2", self.skill)

    def test_counting_rule_stated(self):
        self.assertIn("메시지 하나 = 한 질문", self.skill)
        self.assertIn("`[확인 · 제목 목록]` · `[확인 · 저장]`", self.skill)


def deck_names(skill_text):
    """SKILL.md 7.3 의 이름 규칙: deck.md 다음 deck-2.md … deck-N.md"""
    nums = [int(n) for n in re.findall(r"`deck-(\d+)\.md`", skill_text)]
    return ["deck.md"] + ["deck-%d.md" % i for i in range(min(nums), max(nums) + 1)]


class AgentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.front, cls.body = frontmatter(read(AGENT))
        cls.perm = get(cls.front, "permission")
        cls.skill = read(SKILL)

    def test_mode_and_model(self):
        self.assertEqual(get(self.front, "mode"), "primary")
        self.assertIsNone(get(self.front, "model"))
        self.assertTrue(get(self.front, "description"))

    def test_denied_tools(self):
        for key in ["bash", "webfetch", "websearch", "task", "question"]:
            self.assertEqual(get(self.perm, key), "deny", key)

    def test_skill_rules(self):
        rules = get(self.perm, "skill")
        self.assertEqual(rules[0], ("*", "deny"))
        self.assertEqual(decide(rules, "subordinate-1"), "allow")
        self.assertEqual(decide(rules, "other-skill"), "deny")

    def test_read_rules(self):
        rules = get(self.perm, "read")
        self.assertEqual(decide(rules, "D:/data/run.csv"), "allow")
        for path in [".env", "D:\\data\\.env", "/home/u/x/.env.local"]:
            self.assertEqual(decide(rules, path), "deny", path)

    def test_edit_rules_follow_name_rule(self):
        rules = get(self.perm, "edit")
        self.assertEqual(rules[0], ("*", "deny"))
        names = deck_names(self.skill)
        self.assertEqual((names[1], names[-1]), ("deck-2.md", "deck-99.md"))
        for name in names:
            for path in [name, "data/" + name, "/home/u/data/" + name,
                         "D:/data/" + name, "D:\\보고\\자료\\" + name]:
                self.assertEqual(decide(rules, path), "ask", path)
        for path in ["notes.md", "D:\\data\\deck.pptx", "deck-100.md", "deck.md.bak",
                     "D:/data/mydeck.md", "/home/u/.config/opencode/opencode.json", "SKILL.md"]:
            self.assertEqual(decide(rules, path), "deny", path)

    def test_external_directory_asks(self):
        self.assertEqual(get(self.perm, "external_directory"), "ask")

    def test_body_loads_skill_and_fails_closed(self):
        self.assertIn("`subordinate-1` 스킬을 불러온다", self.body)
        self.assertIn("흉내 내지 않는다", self.body)
        self.assertIn("멈춘다", self.body)


class CommandTest(unittest.TestCase):
    def test_command(self):
        front, body = frontmatter(read(COMMAND))
        self.assertEqual(get(front, "agent"), "subordinate-1")
        self.assertTrue(os.path.isfile(os.path.join(os.path.dirname(AGENT), "subordinate-1.md")))
        self.assertNotEqual(str(get(front, "subtask", "false")).lower(), "true")
        self.assertIn("$ARGUMENTS", body)
        self.assertTrue(get(front, "description"))


class DialogueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(DIALOGUE)
        with open(os.path.join(FIXTURES, "interview_lite.json"), encoding="utf-8") as f:
            cls.answers = {a["id"]: a["answer"] for a in json.load(f)["answers"]}
        with open(os.path.join(FIXTURES, "facts_lite.json"), encoding="utf-8") as f:
            facts = json.load(f)
        cls.fact_ids = {x["id"] for x in facts["facts"]}
        cls.image_ids = {x["id"] for x in facts["images"]}

    def test_marked_as_written_by_hand(self):
        head = self.text[:600]
        self.assertIn("실제 모델 실행 기록이 아니다", head)
        self.assertIn("지어낸 것", head)
        self.assertNotIn("kit/", self.text)
        self.assertIn("deck_synthetic.md", self.text)

    def test_budget(self):
        found = QUESTION_RE.findall(self.text)
        self.assertTrue(found)
        self.assertLessEqual(len(found), 12)
        self.assertEqual([int(q[0]) for q in found], list(range(1, len(found) + 1)))
        stage_order = [STAGES.index(q[1]) for q in found]
        self.assertEqual(stage_order, sorted(stage_order))
        for stage in STAGES:
            ks = [int(q[2]) for q in found if q[1] == stage]
            self.assertLessEqual(len(ks), BUDGET[stage], stage)
            self.assertEqual(ks, list(range(1, len(ks) + 1)), stage)
            self.assertTrue(all(int(q[3]) == BUDGET[stage] for q in found if q[1] == stage), stage)

    def test_question_shape(self):
        for m in re.finditer(r"^\[질문 [^\n]*\n(.*?)^```$", self.text, re.S | re.M):
            block = m.group(1)
            self.assertIn("모름 · 나중에", block)
            options = [o for o in re.findall(r"^\d+\. (.+)$", block, re.M) if "모름 · 나중에" not in o]
            self.assertLessEqual(len(options), 4, block)

    def test_confirmations_after_questions(self):
        last_q = max(m.start() for m in QUESTION_RE.finditer(self.text))
        at = []
        for mark in [r"\[확인 · 제목 목록\]", r"\[확인 · 저장\]"]:
            found = [m.start() for m in re.finditer("^" + mark + "$", self.text, re.M)]
            self.assertEqual(len(found), 1, mark)
            self.assertGreater(found[0], last_q)
            at.append(found[0])
        self.assertLess(at[0], at[1])

    def test_answer_ids_match_fixture(self):
        recorded = re.findall(r"^답 (a\d{2}) · (.+)$", self.text, re.M)
        self.assertEqual([r[0] for r in recorded], ["a%02d" % i for i in range(1, len(recorded) + 1)])
        for aid, text in recorded:
            self.assertEqual(self.answers.get(aid), text, aid)
        used = set(re.findall(r"\ba\d{2}\b", self.text))
        self.assertTrue(used <= set(self.answers), used - set(self.answers))
        self.assertEqual(used, set(self.answers))

    def test_fact_and_image_ids_exist(self):
        self.assertTrue(set(re.findall(r"\bf\d{3}\b", self.text)) <= self.fact_ids)
        self.assertTrue(set(re.findall(r"\bimg\d+\b", self.text)) <= self.image_ids)

    def test_title_list_is_example_deck(self):
        m = re.search(r"^\[확인 · 제목 목록\]\n(.*?)^```$", self.text, re.S | re.M)
        self.assertIsNotNone(m)
        shown = re.findall(r"^\d+\. (\S+(?: \S+)? › .+)$", m.group(1), re.M)
        deck = re.findall(r"^## (.+)$", read(DECK), re.M)
        self.assertEqual(shown, deck)


class BundleTextTest(unittest.TestCase):
    def test_no_todo_or_emoji(self):
        for path in [AGENT, COMMAND, DIALOGUE, SKILL]:
            text = read(path)
            self.assertNotIn("TODO", text, path)
            self.assertIsNone(EMOJI_RE.search(text), path)


if __name__ == "__main__":
    unittest.main()
