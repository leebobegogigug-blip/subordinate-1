#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score.py - M0 KIT-2 · KIT-3 채점기 (표준 라이브러리만 · Python 3.8+)

  python kit/llm/score.py prepare [--out 폴더]   작업 폴더를 만든다 (기본 ~/subordinate-m0 · 저장소 밖)
  python kit/llm/score.py --dir "작업폴더/results"  그 답을 채점한다
  python kit/llm/score.py --ping                  도구 호출 확인 토큰을 찍는다 (작업 폴더의 ping.py 와 같은 값)

[작업 폴더] 시험받는 모델은 작업 폴더에서만 돈다. 그 폴더에는 입력 그림 · facts_lite · interview_lite ·
  프롬프트 (경로는 작업 폴더 기준) · 빈 results/ · ping.py · 칸 이름만 든 answers_template.json 만 복사한다.
  정답 (truth.json) · 이 채점기 · README (문턱) 는 복사하지 않는다 - 모델이 정답 · 채점 규칙을 읽지 못하게.

[읽는 것] 답 폴더의
  answers.json     answers_template.json 을 복사해 채운 것 (칸 이름: 값)
  answers*.txt     모델의 답 블록을 그대로 붙여 넣은 글 (한 줄에 '칸 이름: 값' · 나머지 줄은 무시)
  deck_1.json …    KIT-2 ㅁ 에서 모델이 쓴 deck-lite (deck_1 – deck_5)
  같은 칸이 여러 번 나오면 나중 것이 이긴다 (answers.json › answers*.txt 이름 순).

[출력] 답 원문은 찍지 않는다 - 맞음 · 틀림과 알아본 값 (보기 이름 · 숫자 · 날짜) 만 보인다.
  마지막 줄은 결과: OK · 결과: 확인 필요 · 결과: 점검 실패 (RULES.md › S-03)
  종료 코드 0 OK · 1 점검 실패 (빨강) · 2 사용법 오류 · 3 확인 필요 (노랑 · 보류 · 빈 칸)

[판정] 문턱은 synthetic/truth.json 의 thresholds (결과를 보기 전에 적음 · README › 판정 문턱).
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import math
import os
import platform
import re
import sys
import unicodedata
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTH = os.path.join(HERE, "synthetic")
ROOT = os.path.dirname(os.path.dirname(HERE))
PROMPTS = os.path.join(HERE, "prompts")
WORK_DEFAULT = os.path.join(os.path.expanduser("~"), "subordinate-m0")
RESULTS_FALLBACK = os.path.join(ROOT, "kit", "results", "llm")
PING_SEED = b"subordinate-1 m0 kit2 ping"
DECK_COUNT = 5

GREEN, YELLOW, RED, HOLD = "초록", "노랑", "빨강", "보류"

DECK_TYPES = ("anomaly", "experiment", "periodic")
SECTIONS = ("요약", "현상", "현상 범위", "분석", "의견", "한계 · 다음", "부록")
KINDS = ("사실", "해석", "의견", "미확인")
META_KEYS = ("type", "audience", "title", "date", "host", "data_class")
SLIDE_KEYS = ("id", "section", "title", "bullets", "notes")
SENTENCE_KEYS = ("text", "kind", "refs", "reasoning")

USER_CHOICES = {
    "k2.attach": {"붙여넣기": ["붙여넣기", "paste", "끌어놓기", "드래그", "drag"],
                  "읽기도구": ["read", "읽기", "read도구", "읽기도구", "파일읽기"],
                  "둘다": ["둘다", "both", "모두"], "안됨": ["안됨", "실패", "없음", "no"]},
    "k2.question": {"선택화면": ["선택화면", "선택", "ui", "화면", "버튼"],
                    "글목록": ["글목록", "번호목록", "목록", "text", "글"],
                    "안함": ["안함", "안했음", "없음", "no", "실패"]},
    "k2.korean": {"좋음": ["좋음", "good"], "보통": ["보통", "ok"], "나쁨": ["나쁨", "bad"]},
    "peeked": {"예": ["예", "yes", "y", "1", "열었음"], "아니오": ["아니오", "아니요", "no", "n", "0", "안열었음"]},
}
USER_KEYS = ("k2.attach", "k2.question", "k2.korean", "k2.opencode", "k2.b.config", "peeked")


# ── 공통 ──────────────────────────────────────────────────────────────────

def ping_token() -> str:
    """도구 호출 확인 토큰. 소스에 글자 그대로 두지 않는다 - 모델이 실행하지 않고 읽어서 답하지 못하게."""
    return "PING-" + hashlib.sha256(PING_SEED).hexdigest()[:6].upper()


PING_PY = """# -*- coding: utf-8 -*-
\"\"\"KIT-2 ㄴ 도구 호출 확인 - 실행하면 토큰을 찍는다.\"\"\"
import hashlib
import platform

print("KIT-2 도구 호출 확인")
print("토큰: PING-" + hashlib.sha256(%r).hexdigest()[:6].upper())
print("Python " + platform.python_version())
""" % PING_SEED


# ── 작업 폴더 만들기 (prepare) ────────────────────────────────────────────

def _inside(path: str, root: str) -> bool:
    path, root = os.path.normcase(os.path.realpath(path)), os.path.normcase(os.path.realpath(root))
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _write_new(path: str, data: bytes):
    """새 파일로만 쓴다 - 같은 이름이 있으면 FileExistsError (덮어쓰지 않는다)"""
    with open(path, "xb") as f:
        f.write(data)


def prepare(out: str) -> List[str]:
    """작업 폴더를 만들고 쓴 파일 (작업 폴더 기준 경로) 목록을 돌려준다. 못 하면 ValueError."""
    out = os.path.abspath(out)
    if _inside(out, ROOT):
        raise ValueError("작업 폴더는 저장소 밖이어야 합니다 - 저장소 안이면 모델이 정답 · 채점기를 읽을 수 있습니다")
    if os.path.exists(out) and (not os.path.isdir(out) or os.listdir(out)):
        raise ValueError("작업 폴더가 이미 있고 비어 있지 않습니다 - 덮어쓰지 않습니다. 다른 --out 을 주거나 지운 뒤 하십시오")
    images = sorted(n for n in os.listdir(SYNTH) if n.endswith(".png"))
    copies = [(os.path.join(SYNTH, n), "inputs/" + n) for n in images]
    copies += [(os.path.join(SYNTH, n), "inputs/" + n) for n in ("facts_lite.json", "interview_lite.json")]
    for n in sorted(os.listdir(PROMPTS)):
        if n.endswith(".md"):
            copies.append((os.path.join(PROMPTS, n), "prompts/" + n))
    blobs = []
    for src, rel in copies:
        with open(src, "rb") as f:
            data = f.read()
        if rel.startswith("prompts/") and b"kit/" in data:
            raise ValueError("프롬프트에 저장소 경로가 남아 있습니다 - %s" % rel)
        blobs.append((rel, data))
    tpl = read_json(os.path.join(HERE, "answers_template.json"))
    names = dict((k, "") for k in tpl if not k.startswith("_"))
    blobs.append(("answers_template.json", (json.dumps(names, ensure_ascii=False, indent=1) + "\n").encode("utf-8")))
    blobs.append(("ping.py", PING_PY.encode("utf-8")))
    for sub in ("", "inputs", "prompts", "results"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for rel, data in blobs:
        _write_new(os.path.join(out, *rel.split("/")), data)
    return [rel for rel, _ in blobs]


def default_results() -> str:
    """--dir 이 없을 때: 기본 작업 폴더의 results › 저장소의 kit/results/llm 순"""
    first = os.path.join(WORK_DEFAULT, "results")
    return first if os.path.isdir(first) else RESULTS_FALLBACK


def norm(text: str) -> str:
    """보기 비교용: NFKC · 소문자 · 공백과 구두점 제거 (한글 · 영숫자 · % 만 남는다)"""
    t = unicodedata.normalize("NFKC", str(text)).lower()
    return "".join(ch for ch in t if ch.isalnum() or ch == "%")


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def judge(k: int, n: int, target: float, floor: float) -> str:
    """초록 = 점 >= target 그리고 하한 >= floor · 빨강 = 상한 < target · 노랑 = 나머지"""
    if n <= 0:
        return HOLD
    lo, hi = wilson(k, n)
    if k / n >= target and lo >= floor:
        return GREEN
    if hi < target:
        return RED
    return YELLOW


def rate_text(k: int, n: int) -> str:
    if n <= 0:
        return "0/0"
    lo, hi = wilson(k, n)
    return "%d/%d = %d%% (95%% 구간 %d–%d%%)" % (k, n, round(100 * k / n), round(100 * lo), round(100 * hi))


def pad(text: str, width: int) -> str:
    """한글 폭 (2칸) 을 셈에 넣어 오른쪽을 채운다 - 줄 맞춤용"""
    used = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
    return text + " " * max(1, width - used)


def read_json(path: str):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def read_text_any(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


# ── 답 읽기 ───────────────────────────────────────────────────────────────

LINE_RE = re.compile(r"^\s*(?:[-*>]\s*)?`?([A-Za-z][A-Za-z0-9_.]*)`?\s*[:=：]\s*(.*?)\s*$")


def parse_answer_text(text: str) -> Dict[str, str]:
    """'칸 이름: 값' 줄만 읽는다. 값이 빈 줄 · 코드 울타리 · 그 밖의 글은 건너뛴다."""
    out = {}
    for line in text.splitlines():
        if line.strip().startswith("```"):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        value = m.group(2).strip().strip("`").strip()
        if value:
            out[m.group(1).lower()] = value
    return out


def load_answers(results: str) -> Tuple[Dict[str, str], List[str]]:
    """(답 칸 → 값, 읽은 파일 이름 목록). answers.json 이 JSON 이 아니면 ValueError."""
    answers, used = {}, []
    path = os.path.join(results, "answers.json")
    if os.path.isfile(path):
        try:
            data = read_json(path)
        except ValueError as e:
            raise ValueError("answers.json 을 JSON 으로 읽지 못했습니다 (%d줄)" % getattr(e, "lineno", 0))
        if not isinstance(data, dict):
            raise ValueError("answers.json 의 맨 바깥은 {…} 이어야 합니다")
        for k, v in data.items():
            if k.startswith("_") or v is None:
                continue
            if isinstance(v, list):
                v = ", ".join(str(x) for x in v)
            v = str(v).strip()
            if v:
                answers[k.lower()] = v
        used.append("answers.json")
    for p in sorted(glob.glob(os.path.join(results, "answers*.txt"))):
        answers.update(parse_answer_text(read_text_any(p)))
        used.append(os.path.basename(p))
    return answers, used


# ── 값 알아보기 ───────────────────────────────────────────────────────────

NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")
DATE_RE = re.compile(
    r"(?P<y>\d{4})\s*[-./년]\s*(?P<m>\d{1,2})\s*[-./월]\s*(?P<d>\d{1,2})"
    r"|(?P<m2>\d{1,2})\s*월\s*(?P<d2>\d{1,2})\s*일?"
    r"|(?P<m3>\d{1,2})\s*[-/.]\s*(?P<d3>\d{1,2})")


def parse_number(text: str) -> Optional[float]:
    t = unicodedata.normalize("NFKC", text).replace("−", "-").replace(",", "")
    m = NUM_RE.search(t)
    return float(m.group(0)) if m else None


def parse_dates(text: str, year: int) -> List[dt.date]:
    out = []
    for m in DATE_RE.finditer(unicodedata.normalize("NFKC", text)):
        try:
            if m.group("y"):
                out.append(dt.date(int(m.group("y")), int(m.group("m")), int(m.group("d"))))
            elif m.group("m2"):
                out.append(dt.date(year, int(m.group("m2")), int(m.group("d2"))))
            else:
                out.append(dt.date(year, int(m.group("m3")), int(m.group("d3"))))
        except ValueError:
            continue
    return out


def match_choice(text: str, options: List[str], synonyms: Dict[str, List[str]]) -> Optional[str]:
    """답을 보기 하나로 알아본다. 같은 글 → 그 보기 · 아니면 답 안에 든 가장 긴 보기 글 (하나일 때만)."""
    a = norm(text)
    if not a:
        return None
    names = []
    for opt in options:
        for s in [opt] + list(synonyms.get(opt, [])):
            ns = norm(s)
            if ns:
                names.append((ns, opt))
    for ns, opt in names:
        if a == ns:
            return opt
    hits = [(len(ns), opt) for ns, opt in names if ns in a]
    if not hits:
        return None
    best = max(h[0] for h in hits)
    top = set(opt for ln, opt in hits if ln == best)
    return top.pop() if len(top) == 1 else None


def score_question(q: dict, text: Optional[str]) -> Tuple[Optional[bool], str]:
    """(맞음 여부 · None 이면 답 없음, 알아본 값 설명)"""
    if text is None or not str(text).strip():
        return None, "답 없음"
    kind = q["type"]
    if kind == "choice":
        got = match_choice(text, q["options"], q.get("synonyms", {}))
        if got is None:
            return False, "알아볼 수 없음"
        return got == q["truth"], "고른 것 %s" % got
    if kind == "number":
        v = parse_number(text)
        if v is None:
            return False, "숫자 없음"
        ok = q["lo"] <= v <= q["hi"]
        band = "%g" % q["lo"] if q["lo"] == q["hi"] else "%g–%g" % (q["lo"], q["hi"])
        return ok, "읽은 값 %g · 정답 구간 %s%s" % (v, band, q.get("unit", ""))
    year = int(str(q["truth"] if kind == "date" else q["truth"][0])[:4])
    got_dates = parse_dates(text, year)
    tol = int(q.get("tol_days", 0))
    if kind == "date":
        if not got_dates:
            return False, "날짜 없음"
        truth = dt.date.fromisoformat(q["truth"])
        diff = (got_dates[0] - truth).days
        return abs(diff) <= tol, "읽은 날짜 %s · 차이 %+d일 (허용 ±%d)" % (got_dates[0].isoformat(), diff, tol)
    if kind == "dates":
        truths = [dt.date.fromisoformat(s) for s in q["truth"]]
        if len(got_dates) != len(truths):
            return False, "날짜 %d개 (정답 %d개)" % (len(got_dates), len(truths))
        left = list(got_dates)
        for t in truths:
            near = [g for g in left if abs((g - t).days) <= tol]
            if not near:
                return False, "날짜 %d개 중 허용 ±%d일 밖이 있음" % (len(truths), tol)
            left.remove(min(near, key=lambda g: abs((g - t).days)))
        return True, "날짜 %d개 모두 ±%d일 안" % (len(truths), tol)
    raise ValueError("모르는 문제 종류: %s" % kind)


# ── deck-lite 검사 (PLAN 부록 A 의 작은 부분 · V-01 · V-02 · V-05 미리 보기) ─────────

def known_ids(facts_lite: dict, interview: dict) -> Tuple[set, set]:
    """(사실 · 그림 id, 인터뷰 답 id)"""
    evidence = set(f["id"] for f in facts_lite.get("facts", []))
    evidence |= set(i["id"] for i in facts_lite.get("images", []))
    answers = set(a["id"] for a in interview.get("answers", []))
    return evidence, answers


def _is_text(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _check_sentence(s, where: str, struct: List[str]) -> bool:
    if not isinstance(s, dict):
        struct.append("%s 가 {…} 가 아님" % where)
        return False
    ok = True
    for k in s:
        if k not in SENTENCE_KEYS:
            struct.append("%s.%s 는 없는 칸" % (where, k))
            ok = False
    if not _is_text(s.get("text")):
        struct.append("%s.text 가 비었거나 글이 아님" % where)
        ok = False
    if s.get("kind") not in KINDS:
        struct.append("%s.kind 가 보기 밖" % where)
        ok = False
    refs = s.get("refs")
    if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
        struct.append("%s.refs 가 글 목록이 아님" % where)
        ok = False
    if "reasoning" in s and not isinstance(s["reasoning"], str):
        struct.append("%s.reasoning 이 글이 아님" % where)
        ok = False
    return ok


def _grammar_sentence(s: dict, where: str, evidence: set, answers: set, gram: List[str]):
    refs = s["refs"]
    kind = s["kind"]
    for r in refs:
        if r not in evidence and r not in answers:
            gram.append("%s.refs 에 없는 근거 %s" % (where, r))
    ev = [r for r in refs if r in evidence]
    an = [r for r in refs if r in answers]
    if kind == "사실" and not ev:
        gram.append("%s 사실인데 사실 · 그림 근거가 없음" % where)
    if kind == "해석":
        if len(set(ev)) < 2:
            gram.append("%s 해석인데 사실 · 그림 근거가 둘 미만" % where)
        if not _is_text(s.get("reasoning")):
            gram.append("%s 해석인데 reasoning 이 없음" % where)
    if kind == "의견" and not an:
        gram.append("%s 의견인데 인터뷰 답 id 가 없음 (V-02)" % where)


def validate_deck(obj, evidence: set, answers: set) -> Tuple[List[str], List[str]]:
    """(구조 오류, 근거 규칙 오류). 구조가 깨지면 근거 규칙은 보지 않는다."""
    struct, gram = [], []
    if not isinstance(obj, dict):
        return ["맨 바깥이 {…} 가 아님"], []
    for k in obj:
        if k not in ("format", "meta", "slides", "open_items"):
            struct.append("%s 는 없는 칸" % k)
    if obj.get("format") != 1:
        struct.append("format 이 1 이 아님")
    meta = obj.get("meta")
    if not isinstance(meta, dict):
        struct.append("meta 가 {…} 가 아님")
    else:
        for k in meta:
            if k not in META_KEYS:
                struct.append("meta.%s 는 없는 칸" % k)
        for k in META_KEYS:
            if not _is_text(meta.get(k)):
                struct.append("meta.%s 가 비었거나 글이 아님" % k)
        if _is_text(meta.get("type")) and meta["type"] not in DECK_TYPES:
            struct.append("meta.type 이 보기 밖")
        if _is_text(meta.get("date")) and not re.match(r"^\d{4}-\d{2}-\d{2}$", meta["date"]):
            struct.append("meta.date 가 YYYY-MM-DD 가 아님")
        if _is_text(meta.get("data_class")) and meta["data_class"] != "synthetic":
            struct.append("meta.data_class 가 synthetic 이 아님")
    slides = obj.get("slides")
    sentences = []
    if not isinstance(slides, list) or not (3 <= len(slides) <= 12):
        struct.append("slides 가 3–12장 목록이 아님")
        slides = slides if isinstance(slides, list) else []
    seen_ids = set()
    sections = []
    for i, sl in enumerate(slides):
        where = "slides[%d]" % i
        if not isinstance(sl, dict):
            struct.append("%s 가 {…} 가 아님" % where)
            continue
        for k in sl:
            if k not in SLIDE_KEYS:
                struct.append("%s.%s 는 없는 칸" % (where, k))
        sid = sl.get("id")
        if not _is_text(sid):
            struct.append("%s.id 가 비었음" % where)
        elif sid in seen_ids:
            struct.append("%s.id 가 겹침" % where)
        else:
            seen_ids.add(sid)
        section = norm(sl.get("section", "")) if isinstance(sl.get("section"), str) else ""
        if section not in [norm(s) for s in SECTIONS]:
            struct.append("%s.section 이 보기 밖" % where)
        else:
            sections.append([norm(s) for s in SECTIONS].index(section))
        if _check_sentence(sl.get("title"), where + ".title", struct):
            sentences.append((sl["title"], where + ".title"))
        bullets = sl.get("bullets", [])
        if not isinstance(bullets, list):
            struct.append("%s.bullets 가 목록이 아님" % where)
            bullets = []
        for j, b in enumerate(bullets):
            if _check_sentence(b, "%s.bullets[%d]" % (where, j), struct):
                sentences.append((b, "%s.bullets[%d]" % (where, j)))
        if "notes" in sl and not isinstance(sl["notes"], str):
            struct.append("%s.notes 가 글이 아님" % where)
    items = obj.get("open_items")
    if not isinstance(items, list):
        struct.append("open_items 가 목록이 아님")
    else:
        for j, it in enumerate(items):
            if not (isinstance(it, dict) and set(it) == {"slot", "why"} and _is_text(it.get("slot"))
                    and _is_text(it.get("why"))):
                struct.append("open_items[%d] 가 {slot, why} 가 아님" % j)
    if struct:
        return struct, []
    for s, where in sentences:
        _grammar_sentence(s, where, evidence, answers, gram)
    if any(b < a for a, b in zip(sections, sections[1:])):
        gram.append("절 순서가 요약 › 현상 › 분석 › 의견 › 한계 · 다음 이 아님 (P-05)")
    must = [norm("현상"), norm("한계 · 다음")]
    have = set([norm(SECTIONS[i]) for i in sections])
    for m in must:
        if m not in have:
            gram.append("%s 절이 없음" % [s for s in SECTIONS if norm(s) == m][0])
    return struct, gram


def check_deck_file(path: str, evidence: set, answers: set) -> Tuple[List[str], List[str]]:
    try:
        obj = json.loads(read_text_any(path))
    except ValueError as e:
        return ["JSON 으로 읽지 못함 (%d줄)" % getattr(e, "lineno", 0)], []
    return validate_deck(obj, evidence, answers)


# ── 채점 ──────────────────────────────────────────────────────────────────

def norm_code(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKC", text).upper() if ch.isalnum())


def user_choice(key: str, value: Optional[str]) -> str:
    if key == "k2.opencode":
        return value if value and re.match(r"^v?\d+\.\d+(\.\d+)?$", value.strip()) else ("적음" if value else "적지 않음")
    if not value:
        return "적지 않음"
    if key == "k2.b.config":
        return match_choice(value, ["modalities", "modalities+attachment", "오류"],
                            {"modalities+attachment": ["attachment"], "오류": ["error", "설정오류"]}) or "알아볼 수 없음"
    opts = USER_CHOICES[key]
    return match_choice(value, list(opts), opts) or "알아볼 수 없음"


VERDICT_LETTER = {GREEN: "G", YELLOW: "Y", RED: "R", HOLD: "-"}
QUESTION_LETTER = {"선택화면": "O", "글목록": "T", "안함": "X"}


def score_kit2(truth: dict, ans: Dict[str, str], results: str, lines: List[str],
               facts: Optional[dict] = None) -> str:
    k2 = truth["kit2"]
    th = truth["thresholds"]
    lines.append("[KIT-2] opencode + 사내 LLM")
    delivered, runs_answered = False, 0
    delivered_by = {}
    for key, label in (("a", "그림 A (설정 그대로)"), ("b", "그림 B (modalities 추가)")):
        code = ans.get("k2.%s.code" % key)
        shape = ans.get("k2.%s.shape" % key)
        if not code:
            lines.append("  %s답 없음" % pad(label, 26))
            continue
        runs_answered += 1
        ok = norm_code(code) == norm_code(k2[key]["code"])
        delivered = delivered or ok
        delivered_by[key] = ok
        shape_ok = None if not shape else match_choice(shape, ["별", "삼각형", "원", "사각형"], {
            "별": ["star"], "삼각형": ["triangle", "세모"], "원": ["circle", "동그라미"], "사각형": ["square", "네모"]})
        shape_txt = "모양 답 없음" if not shape else ("모양 맞음" if shape_ok == k2[key]["shape"] else "모양 틀림")
        lines.append("  %s코드 %s · %s" % (pad(label, 26), "맞음 (그림이 닿았다)" if ok else "틀림", shape_txt))
    for key, label in (("k2.attach", "그림 넣는 법"), ("k2.b.config", "B 의 설정"), ("k2.opencode", "opencode 판"),
                       ("k2.question", "question 도구"), ("k2.korean", "한국어 문장")):
        lines.append("  %s%s" % (pad(label, 26), user_choice(key, ans.get(key))))
    ping = ans.get("k2.ping")
    ping_ok = bool(ping) and norm_code(ping) == norm_code(ping_token())
    lines.append("  %s%s" % (pad("도구 호출 (--ping)", 26), "답 없음" if not ping else ("맞음" if ping_ok else "틀림")))

    tags_ok, links_ok, tag_answered = 0, 0, 0
    owner = {}
    for img_id, c in k2["ctx"].items():
        for f in c["facts"]:
            owner[f] = img_id
    for img_id, c in k2["ctx"].items():
        tag = ans.get("k2.ctx.%s.tag" % img_id)
        if tag:
            tag_answered += 1
            tags_ok += norm_code(tag) == norm_code(c["tag"])
        cited = set(x.lower() for x in re.findall(r"[fF]\d{3}", ans.get("k2.ctx.%s.facts" % img_id, "")))
        if cited & set(c["facts"]) and not any(owner.get(f, img_id) != img_id for f in cited):
            links_ok += 1
    if tag_answered:
        lines.append("  %s태그 %d/5 · 사실 연결 %d/5" % (pad("맥락 (그림 5장 + facts)", 26), tags_ok, links_ok))
    else:
        lines.append("  %s답 없음" % pad("맥락 (그림 5장 + facts)", 26))

    evidence, answer_ids = known_ids(read_json(os.path.join(SYNTH, "facts_lite.json")),
                                     read_json(os.path.join(SYNTH, "interview_lite.json")))
    found, s_pass, g_pass, detail = 0, 0, 0, []
    for i in range(1, DECK_COUNT + 1):
        path = os.path.join(results, "deck_%d.json" % i)
        if not os.path.isfile(path):
            detail.append("    deck_%d.json  파일 없음" % i)
            continue
        found += 1
        struct, gram = check_deck_file(path, evidence, answer_ids)
        if not struct:
            s_pass += 1
            if not gram:
                g_pass += 1
        errs = struct or gram
        if errs:
            more = " 외 %d건" % (len(errs) - 2) if len(errs) > 2 else ""
            detail.append("    deck_%d.json  %s - %s%s" % (i, "구조" if struct else "근거 규칙", " · ".join(errs[:2]), more))
    if found:
        lines.append("  %s%s" % (pad("deck-lite 구조 통과", 26), rate_text(s_pass, DECK_COUNT)))
        lines.append("  %s%s" % (pad("deck-lite 근거 규칙 통과", 26), rate_text(g_pass, DECK_COUNT)))
        lines.extend(detail)
    else:
        lines.append("  %sdeck_1.json – deck_5.json 없음" % pad("deck-lite", 26))

    t = th["deck_structure"]
    deck_j = judge(s_pass, DECK_COUNT, t["target"], t["floor"]) if found else HOLD
    holds = []
    if not delivered and runs_answered < 2:
        holds.append("그림 A · B 를 다 돌리지 않음")
    if not ping:
        holds.append("--ping 답 없음")
    if deck_j == HOLD:
        holds.append("deck 파일 없음")
    if (runs_answered == 2 and not delivered) or (ping and not ping_ok) or deck_j == RED:
        verdict = RED
    elif holds:
        verdict = HOLD
    elif delivered and ping_ok and deck_j == GREEN:
        verdict = GREEN
    else:
        verdict = YELLOW
    if tag_answered and tags_ok < th["context_tags_min"]:
        lines.append("  참고: 맥락 태그 %d/5 - 그림은 한 장씩 보이는 쪽으로 (리스크 2)" % tags_ok)
    lines.append("  판정: %s%s" % (verdict, " (%s)" % " · ".join(holds) if verdict == HOLD else ""))
    if facts is not None:
        if delivered_by.get("a"):
            image = "A"
        elif delivered_by.get("b"):
            image = "B"
        else:
            image = "X" if runs_answered == 2 else "-"
        question = QUESTION_LETTER.get(user_choice("k2.question", ans.get("k2.question")), "?")
        facts.update({"verdict": VERDICT_LETTER[verdict], "image": image,
                      "tool": "-" if not ping else ("O" if ping_ok else "X"),
                      "question": question, "deck": str(s_pass) if found else "-"})
    return verdict


def score_kit3(truth: dict, ans: Dict[str, str], lines: List[str], facts: Optional[dict] = None) -> str:
    th = truth["thresholds"]
    charts = truth["kit3"]
    lines.append("[KIT-3] 그림 판독")
    cat_k = cat_n = num_k = num_n = 0
    missing = 0
    results = {}
    for cid, c in charts.items():
        parts = []
        for qid, q in c["questions"].items():
            ok, why = score_question(q, ans.get(("%s.%s" % (cid, qid)).lower()))
            results["%s.%s" % (cid, qid)] = ok
            parts.append("%s %s" % (qid, "답 없음" if ok is None else ("맞음" if ok else "틀림 (%s)" % why)))
            if c["group"] != "main":
                continue
            if ok is None:
                missing += 1
            elif q["type"] == "choice":
                cat_n += 1
                cat_k += ok
            else:
                num_n += 1
                num_k += ok
        lines.append("  %s%s%s" % (pad(cid, 6), pad(c["kind"], 28), " · ".join(parts)))
    tc, tn = th["kit3_categorical"], th["kit3_numeric"]
    lines.append("  " + pad("범주 답 맞음", 26) + "%s · 문턱 %d%% · 바닥 %d%%" % (rate_text(cat_k, cat_n), tc["target"] * 100, tc["floor"] * 100))
    lines.append("  " + pad("숫자 답 구간 안", 26) + "%s · 문턱 %d%% · 바닥 %d%%" % (rate_text(num_k, num_n), tn["target"] * 100, tn["floor"] * 100))
    for cid, c in charts.items():
        if c["group"] == "main":
            continue
        label = "축소 비교" if c["group"] == "downscale" else "잘라 보이기"
        mine = [results["%s.%s" % (cid, q)] for q in c["compare_with"]]
        base = [results[ref] for ref in c["compare_with"].values()]
        base_id = list(c["compare_with"].values())[0].split(".")[0]

        def frac(xs):
            return "답 없음" if all(x is None for x in xs) else "%d/%d" % (sum(1 for x in xs if x), len(xs))
        lines.append("  %s%s %s · %s %s" % (pad(label, 26), base_id, frac(base), cid, frac(mine)))
    if missing:
        verdict = HOLD
    else:
        js = [judge(cat_k, cat_n, tc["target"], tc["floor"]), judge(num_k, num_n, tn["target"], tn["floor"])]
        verdict = RED if RED in js else (GREEN if js == [GREEN, GREEN] else YELLOW)
    lines.append("  판정: %s%s" % (verdict, " (본 시험 답 없음 %d칸)" % missing if missing else ""))
    if facts is not None:
        answered = cat_n + num_n > 0
        facts.update({"verdict": VERDICT_LETTER[verdict],
                      "categorical": str(cat_k) if answered else "-",
                      "numeric": str(num_k) if answered else "-"})
    return verdict


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="M0 KIT-2 · KIT-3 채점기 (kit/llm/README.md)")
    ap.add_argument("command", nargs="?", choices=["prepare"], help="prepare = 작업 폴더를 만든다")
    ap.add_argument("--out", default=WORK_DEFAULT, help="prepare 의 작업 폴더 (기본 ~/subordinate-m0)")
    ap.add_argument("--ping", action="store_true", help="도구 호출 확인 토큰을 찍는다")
    ap.add_argument("--dir", "--results", dest="results", default=None,
                    help="답 폴더 (기본 ~/subordinate-m0/results · 없으면 kit/results/llm)")
    args = ap.parse_args(argv)                                     # 사용법 오류는 argparse 가 종료 코드 2 로 끝낸다
    try:
        sys.stdout.reconfigure(errors="replace")                   # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    if args.ping:
        print("KIT-2 도구 호출 확인")
        print("토큰: %s" % ping_token())
        print("Python %s" % platform.python_version())
        print("결과: OK")
        return 0
    if args.command == "prepare":
        try:
            written = prepare(args.out)
        except (OSError, ValueError) as e:
            print("사용법 오류: %s" % e, file=sys.stderr)
            return 2
        print("작업 폴더를 만들었습니다: %s" % os.path.abspath(args.out))
        print("  inputs/ %d · prompts/ %d · results/ (빈 폴더) · ping.py · answers_template.json"
              % (sum(1 for r in written if r.startswith("inputs/")), sum(1 for r in written if r.startswith("prompts/"))))
        print("다음: 이 폴더에서 opencode 를 엽니다 (README › KIT-2)")
        print("결과: OK")
        return 0
    if args.results is None:
        args.results = default_results()
    if not os.path.isdir(args.results):
        print("사용법 오류: 답 폴더가 없습니다 - --dir 로 작업 폴더의 results 를 주십시오 (README › 채점)", file=sys.stderr)
        return 2
    try:
        truth = read_json(os.path.join(SYNTH, "truth.json"))
        ans, used = load_answers(args.results)
    except (OSError, ValueError) as e:
        print("사용법 오류: %s" % e, file=sys.stderr)
        return 2
    decks = [n for n in ("deck_%d.json" % i for i in range(1, DECK_COUNT + 1))
             if os.path.isfile(os.path.join(args.results, n))]
    if not used and not decks:
        print("사용법 오류: 답 파일이 없습니다 - answers.json · answers*.txt · deck_*.json (README › 답 남기기)",
              file=sys.stderr)
        return 2
    lines = ["Subordinate–1 M0 · KIT-2 · KIT-3 채점",
             "읽은 파일: %s" % " · ".join(used + decks), ""]
    f2, f3 = {}, {}
    v2 = score_kit2(truth, ans, args.results, lines, f2)
    lines.append("")
    v3 = score_kit3(truth, ans, lines, f3)
    peek = user_choice("peeked", ans.get("peeked"))
    peeked = "1" if peek == "예" else "0"
    lines.append("")
    lines.append("정답 파일을 연 일: %s" % peek)
    print("\n".join(lines))
    print("")
    print("KIT-2 %s · KIT-3 %s" % (v2, v3))
    if peek == "예":
        print("정답 파일을 열었다면 그 시험은 무효입니다 - 새 세션에서 다시 하십시오.")
    # 사용자가 손으로 옮겨 적을 두 줄 (ASCII) - 마지막 '결과:' 줄 바로 앞
    print("보낼 줄: K2 %s %s %s %s %s" % (f2["verdict"], f2["image"], f2["tool"], f2["question"], f2["deck"]))
    print("보낼 줄: K3 %s %s %s %s" % (f3["verdict"], f3["categorical"], f3["numeric"], peeked))
    if peek == "예":
        print("결과: 확인 필요")
        return 3
    if RED in (v2, v3):
        print("결과: 점검 실패")
        return 1
    if v2 == GREEN and v3 == GREEN:
        print("결과: OK")
        return 0
    print("결과: 확인 필요")
    return 3


if __name__ == "__main__":
    sys.exit(main())
