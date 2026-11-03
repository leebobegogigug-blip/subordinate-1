# -*- coding: utf-8 -*-
"""docs/SPEC-deck-md.md 의 기계로 잴 수 있는 규칙 (DM-01 – DM-14) 을 합성 예시와 반례에 대 본다.

제품 검사기가 아니다. 명세 · 예시 · 반례가 서로 어긋나지 않는지만 지킨다 (표준 라이브러리 · Python 3.8).
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "docs", "examples", "deck_synthetic.md")
COUNTER = os.path.join(ROOT, "docs", "examples", "deck_counterexamples.md")
FIXTURES = os.path.join(ROOT, "tests", "fixtures", "deck")

SECTIONS = ["요약", "현상", "현상 범위", "분석", "의견", "한계", "부록"]
REQUIRED = ["요약", "현상", "분석", "의견", "부록"]          # 한계 는 DM-11 이 따로 본다
PREFIX_RE = re.compile(r"^(\S+(?: \S+)?) › (.+)$")
FRONT_KEYS = ["title", "date", "deck_md", "type", "audience", "data_class", "sources"]
TYPES = ["이상 보고", "실험 결과", "정기 보고"]
TITLE_MAX = 40

ID = r"(?:f\d{3}|img\d+|a\d{2})"
ID_RE = re.compile(r"\b" + ID + r"\b")
TAG_RE = re.compile(r"\[(?:(해석|의견|추정) · )?(" + ID + r"(?: · " + ID + r")*)\]$")
FIG_RE = re.compile(r"^!\[(img\d+) · [^\]]+\]\(([^)\s]+)\)$")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
LIST_RE = re.compile(r"^- (" + ID + r") · (.+)$")


def load_sources():
    with open(os.path.join(FIXTURES, "facts_lite.json"), encoding="utf-8") as f:
        facts = json.load(f)
    with open(os.path.join(FIXTURES, "interview_lite.json"), encoding="utf-8") as f:
        interview = json.load(f)
    src = {}
    for x in facts["facts"]:
        nums = numbers(x["text"])
        nums.update(float(v) for v in (x["value"], x["n"]) if v is not None)
        src[x["id"]] = {"text": x["text"], "nums": nums}
    for x in facts["images"]:
        src[x["id"]] = {"text": x["what"], "file": x["file"], "nums": set()}
    for x in interview["answers"]:
        src[x["id"]] = {"text": x["answer"], "nums": numbers(x["answer"])}
    return src


def numbers(text):
    """줄 속 숫자 (부호 · 단위 뺀 값). 영문으로 시작하는 이름 (EQ-03 · f003 · k2_ctx_2) 과 그림 링크는 숫자가 아니다."""
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = WORD_RE.sub(" ", text)
    return {float(m) for m in NUM_RE.findall(text)}


class Slide(object):
    def __init__(self, heading):
        m = PREFIX_RE.match(heading)
        self.heading = heading
        self.section = m.group(1) if m else None   # 제목 머리의 절 이름
        self.title = m.group(2) if m else heading  # › 뒤의 주장
        self.lines = []      # (종류, 글) — 종류: bullet · evidence · figure · notes · other

    def body(self, kind=None):
        return [t for k, t in self.lines if kind is None or k == kind]


def parse(text):
    """(머리말 dict, 1단계 제목 수, 장 목록, 첫 장 앞 글 수)"""
    front, lines = {}, text.split("\n")
    if lines and lines[0] == "---":
        end = lines.index("---", 1)
        for raw in lines[1:end]:
            m = re.match(r"^(\w+):\s*(.*)$", raw)
            if m:
                front[m.group(1)] = m.group(2).strip()
            m = re.match(r"^  (\w+):\s*(.+)$", raw)
            if m:
                front["sources." + m.group(1)] = m.group(2).strip()
        lines = lines[end + 1:]
    level1, slides, stray, stack = 0, [], 0, []
    for raw in lines:
        line = raw.rstrip()
        m = re.match(r"^(:{3,})\s*(.*)$", line)
        if m:
            if m.group(2):
                stack.append(m.group(2))
            elif stack:
                stack.pop()
            continue
        if not line:
            continue
        if not stack and line.startswith("# "):
            level1 += 1
            continue
        if not stack and line.startswith("## "):
            slides.append(Slide(line[3:].strip()))
            continue
        if not slides:
            stray += 1
            continue
        if "notes" in stack:
            kind = "notes"
        elif line.startswith("!["):
            kind = "figure"
        elif line.startswith("근거:"):
            kind = "evidence"
        elif line.startswith("- "):
            kind = "bullet"
        else:
            kind = "other"
        slides[-1].lines.append((kind, line))
    return front, level1, slides, stray


def tag_of(line):
    """(꼬리표 종류, id 목록) — 꼬리표가 없으면 (None, [])"""
    m = TAG_RE.search(line)
    if not m:
        return None, []
    return (m.group(1) or "사실"), m.group(2).split(" · ")


def check(text, src, deck_path, full=True):
    """어긴 규칙 번호의 집합. full=False 면 장 하나짜리 조각 — 덱 전체 규칙 (DM-01 · 02 · 11 · 13 목록) 은 건너뛴다."""
    front, level1, slides, stray = parse(text)
    bad = set()
    content = [s for s in slides if s.section != "부록"]

    if full:
        # DM-01 머리말
        if any(k not in front for k in FRONT_KEYS) or "author" in front or front.get("deck_md") != "1" \
                or front.get("type") not in TYPES or front.get("data_class") not in ("synthetic", "real") \
                or not re.match(r"^\d{4}-\d{2}-\d{2}$", front.get("date", "")) \
                or "sources.facts" not in front or "sources.interview" not in front:
            bad.add("DM-01")
        # DM-02 필수 절 · 첫 장 앞에 글 없음 (머리 이름 · 순서는 아래에서 조각에도 본다)
        if stray or any(r not in [x.section for x in slides] for r in REQUIRED):
            bad.add("DM-02")
        # DM-11 한계 장 · [미확인] 줄
        limits = [s for s in slides if s.section == "한계"]
        if not limits or not any(b.startswith("- [미확인]") for s in limits for b in s.body("bullet")):
            bad.add("DM-11")

    # DM-02 1단계 제목 없음 · 모든 장 제목에 정해진 절 머리 · 순서
    order = [SECTIONS.index(x.section) if x.section in SECTIONS else -1 for x in slides]
    if level1 or -1 in order or order != sorted(order):
        bad.add("DM-02")

    figures = {}
    for s in content:
        # DM-03 제목 = 한 문장 주장
        t = s.title
        if not t or len(t) > TITLE_MAX or not re.search(r"다\.?$", t) or "[" in t:
            bad.add("DM-03")
        # DM-04 몸통 모양: 글머리 · 그림 하나 · 그림 다음 첫 줄은 근거 줄
        kinds = [k for k, _ in s.lines if k != "notes"]
        if "other" in kinds or kinds.count("figure") > 1 or kinds.count("evidence") != kinds.count("figure") \
                or ("figure" in kinds and kinds[kinds.index("figure") + 1:kinds.index("figure") + 2] != ["evidence"]):
            bad.add("DM-04")
        fig_file = None
        for line in s.body("figure"):
            m = FIG_RE.match(line)
            # DM-12 그림: img id · 받은 파일 이름 그대로 · 상대 경로 · 파일이 있다
            if not m or m.group(1) not in src or "://" in m.group(2) or m.group(2).startswith("/") \
                    or os.path.basename(m.group(2)) != src[m.group(1)].get("file") \
                    or not os.path.isfile(os.path.join(os.path.dirname(deck_path), m.group(2))):
                bad.add("DM-12")
            if m:
                figures[m.group(1)] = s
                fig_file = os.path.basename(m.group(2))
        # DM-05 근거 줄: 여섯 칸 · 그림 파일 이름 · 사실 꼬리표
        for line in s.body("evidence"):
            kind, ids = tag_of(line)
            fields = TAG_RE.sub("", line[len("근거:"):]).strip().split(" · ")
            if kind != "사실" or len(fields) != 6 or fields[0] != fig_file:
                bad.add("DM-05")
        backed = set()
        has_interp = False
        for kind_line, line in s.lines:
            if kind_line == "figure":
                continue
            kind, ids = tag_of(line)
            if kind_line == "bullet":
                # DM-06 꼬리표 문법 · DM-10 [미확인] 은 줄 머리에만
                unconf = line.startswith("- [미확인] ")
                if (kind is None and not unconf) or (kind == "해석" and len([i for i in ids if i[0] in "fi"]) < 2) \
                        or (kind == "추정" and not any(i.startswith("img") for i in ids)):
                    bad.add("DM-06")
                if "[미확인]" in line[len("- [미확인]"):] or (unconf and kind in ("해석", "의견", "추정")):
                    bad.add("DM-10")
                # DM-09 의견: 답 id · 요약 · 의견 절에만 · 의견 절의 글머리는 의견 · 미확인뿐
                if kind == "의견" and (not any(i.startswith("a") for i in ids) or s.section not in ("요약", "의견")):
                    bad.add("DM-09")
                if s.section == "의견" and kind != "의견" and not unconf:
                    bad.add("DM-09")
                has_interp = has_interp or kind == "해석"
            elif "[미확인]" in line:
                bad.add("DM-10")
            ids = ids or ID_RE.findall(line) if kind_line == "notes" else ids
            nums = numbers(TAG_RE.sub("", line))
            text_ids = [i for i in ids if not i.startswith("img")]
            for i in ids:
                if i not in src:
                    bad.add("DM-13")
            if not nums:
                continue
            if kind == "추정":
                continue
            if ids and not text_ids:
                bad.add("DM-08")          # 그림에서 읽은 숫자를 [추정] 없이 썼다
                continue
            pool = set()
            for i in text_ids:
                pool |= src.get(i, {}).get("nums", set())
            if not nums <= pool:
                bad.add("DM-07")          # 근거가 없거나, 인용한 근거에 그 숫자가 없다
            backed |= pool
        # DM-07 제목의 숫자는 이 장 몸통이 인용한 근거 (추정 빼고) 에 있어야 한다
        if not numbers(s.title) <= backed:
            bad.add("DM-07")
        # DM-14 해석은 노트에 '해석 근거:' 줄
        if has_interp and not any(n.startswith("해석 근거:") for n in s.body("notes")):
            bad.add("DM-14")

    if full:
        # DM-13 근거 목록 = 본문이 인용한 사실 · 답 id 그대로 · 원문과 같은 글. 그림 id 는 그림 줄로 풀린다.
        cited = set()
        for s in content:
            for k, line in s.lines:
                if k != "figure":
                    cited |= set(ID_RE.findall(line))
        listed = {}
        for s in [x for x in slides if x.section == "부록"]:
            for line in s.body("bullet"):
                m = LIST_RE.match(line)
                if m:
                    listed[m.group(1)] = m.group(2)
        if {i for i in cited if not i.startswith("img")} != set(listed) \
                or any(i not in src or src[i]["text"] != t for i, t in listed.items()) \
                or any(i not in figures for i in cited if i.startswith("img")):
            bad.add("DM-13")
    return bad


def counterexamples():
    """[(번호, 노린 규칙, 덱 조각 글, 머리말이 있어 덱 전체인가)]"""
    with open(COUNTER, encoding="utf-8") as f:
        text = f.read()
    out = []
    for m in re.finditer(r"^## 반례 (\d+) · (DM-\d\d)[^\n]*\n(.*?)(?=^## 반례 |\Z)", text, re.S | re.M):
        block = re.search(r"^```markdown\n(.*?)^```$", m.group(3), re.S | re.M)
        body = block.group(1) if block else ""
        out.append((m.group(1), m.group(2), body, body.startswith("---\n")))
    return out


class DeckExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = load_sources()
        with open(EXAMPLE, encoding="utf-8") as f:
            cls.text = f.read()
        cls.front, _, cls.slides, _ = parse(cls.text)

    def test_example_passes_every_rule(self):
        self.assertEqual(check(self.text, self.src, EXAMPLE), set())

    def test_section_order(self):
        seen = []
        for s in self.slides:
            if s.section not in seen:
                seen.append(s.section)
        self.assertEqual(seen, ["요약", "현상", "현상 범위", "분석", "의견", "한계", "부록"])
        self.assertIsNone(re.search(r"^# ", self.text, re.M))
        self.assertNotIn("author", self.front)

    def test_slide_count_and_titles(self):
        body = [s for s in self.slides if s.section != "부록"]
        self.assertTrue(6 <= len(body) <= 9, len(body))
        for s in self.slides:
            self.assertTrue(s.title.endswith("다"), s.title)
            self.assertLessEqual(len(s.title), TITLE_MAX, s.title)

    def test_every_number_has_a_source_on_its_line(self):
        for s in self.slides:
            for k, line in s.lines:
                if k != "figure" and numbers(TAG_RE.sub("", line)):
                    self.assertTrue(ID_RE.search(line), line)

    def test_limits_slide_present(self):
        limits = [s for s in self.slides if s.section == "한계"]
        self.assertTrue(limits)
        self.assertTrue(any(b.startswith("- [미확인]") for b in limits[0].body("bullet")))

    def test_figures_are_received_files(self):
        for s in self.slides:
            for line in s.body("figure"):
                m = FIG_RE.match(line)
                self.assertTrue(m, line)
                path = os.path.join(os.path.dirname(EXAMPLE), m.group(2))
                self.assertTrue(os.path.isfile(path), path)
                self.assertEqual(os.path.basename(path), self.src[m.group(1)]["file"])

    def test_numbers_parser(self):
        self.assertEqual(numbers("EQ-03 은 9/15 에 +1.2 nm [f003]"), {9.0, 15.0, 1.2})
        self.assertEqual(numbers("k2_ctx_2.png · n=25"), {25.0})


class CounterexampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = load_sources()
        cls.cases = counterexamples()

    def test_seven_counterexamples(self):
        self.assertEqual([c[1] for c in self.cases], ["DM-07", "DM-09", "DM-08", "DM-03", "DM-11", "DM-12", "DM-02"])

    def test_each_fails_exactly_its_rule(self):
        for no, rule, body, full in self.cases:
            with self.subTest(반례=no):
                self.assertTrue(body.strip())
                self.assertEqual(check(body, self.src, COUNTER, full=full), {rule})


if __name__ == "__main__":
    unittest.main()
