#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trace_numbers.py - M0 KIT-6 G2 확인기: 장표의 숫자가 facts_lite 의 숫자에 묶이는가 (표준 라이브러리만 · Python 3.8+)

  python kit/baseline/trace_numbers.py 덱.pptx [--facts facts_lite.json] [--interview interview_lite.json] [--notes]

[읽는 것] .pptx 의 슬라이드 XML 글자 (a:t) - 표 · 묶음 도형 안 글자 포함. --notes 를 주면 발표자 노트도 읽는다.
  슬라이드 번호 · 날짜 자리 (sldNum · dt 자리표시자, slidenum · datetime 필드) 는 건너뛴다.
  차트 · 그림 안의 숫자는 읽지 못한다 (장표 글자만 본다). 파일은 읽기만 하고 아무것도 쓰지 않는다.

[숫자로 치는 것]
  정수 · 소수 (천 단위 쉼표 허용) · 퍼센트 (38%) · 시그마 (1.5σ) · 날짜
  날짜: 2026-10-01 · 2026/10/01 · 2026.10.01 · 2026-10 (연월) · 10/01 (월/일) · 09-30 (월-일, 두 자리씩) · 10월 1일 · 10월 · 2026년
  숫자로 안 치는 것: 이름에 붙은 숫자 (EQ-03 · f001 · img3 · P-02 · G2 처럼 영문자 바로 뒤의 숫자).
  부호는 무시하고 크기만 본다 (+1.2 와 -1.2 는 같은 숫자로 본다).

[맞추는 규칙] 기준 숫자 = facts_lite 의 value · n 과 text 안에 적힌 숫자 · 날짜.
  --interview 를 주면 interview_lite 의 answer 에 적힌 숫자 · 날짜도 기준에 더한다 (사용자 진술의 숫자, 예: 추가 측정 10 lot).
  1. 소수 자릿수: 장표 숫자의 자릿수가 기준 숫자의 자릿수 이하이면, 장표 숫자의 마지막 자리 반 칸 안이면 맞다
     (기준 2.57 ≈ 장표 2.6 · 기준 100.2 ≈ 장표 100). 반올림 · 반내림은 가리지 않는다.
  2. 장표 숫자의 자릿수가 기준보다 많으면 (기준 1.2 · 장표 1.25) 값이 정확히 같아야 한다 - 없던 정밀도는 지어낸 것으로 본다.
  3. 퍼센트: 38% 는 38 과 0.38 둘 다 후보 (42% ≈ 0.42). 단위 없는 0 초과 1 이하 소수는 x100 도 후보 (0.38 ≈ 38%).
  4. 날짜: (월, 일) 이 기준 날짜에 있어야 하고, 연도가 있으면 기준 연도에도 있어야 한다. 연월 · 월 · 연도도 같다.
  5. 장표가 계산해 낸 숫자 (차이 · 합 · 비) 는 안 맞는 것으로 센다. 사람이 보고 채점표에 따로 적는다.
  6. 이 규칙은 느슨한 편이다: 정수 1 은 기준 1.2 와 맞는다. 맞았다는 것은 '같은 숫자가 있다' 일 뿐 '맞게 썼다' 가 아니다.

[출력] 슬라이드마다 찾음 · 맞음 · 안 맞음 개수와 안 맞는 숫자 (합성 자료의 숫자라 찍는다). 그 밖의 장표 글자는 찍지 않는다.
  마지막 줄은 결과: OK (G2 비율 80% 이상이고 안 맞는 숫자 0) · 결과: 확인 필요 (그 밖 · 숫자가 하나도 없는 경우 포함)
  · 결과: 점검 실패 (파일을 읽지 못함). 종료 코드 0 · 3 · 1, 사용법 오류는 2.
"""
import argparse
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
FACTS_DEFAULT = os.path.join(os.path.dirname(HERE), "llm", "synthetic", "facts_lite.json")
G2_TARGET = 0.80

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PR = "http://schemas.openxmlformats.org/package/2006/relationships"

# ── 숫자 찾기 ────────────────────────────────────────────────────────────
ID_RE = re.compile(r"[A-Za-z]+[-_]?\d+[A-Za-z0-9_]*")           # EQ-03 · f001 · img3 · G2 : 이름이므로 지운다
DATE_PATTERNS = (
    ("ymd", re.compile(r"(?<![\d.\-/])(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})(?![\d])")),
    ("ym", re.compile(r"(?<![\d.\-/])(\d{4})-(\d{2})(?![\d\-])")),
    ("md_ko", re.compile(r"(?<!\d)(\d{1,2})\s*월\s*(\d{1,2})\s*일")),
    ("md_slash", re.compile(r"(?<![\d.\-/])(\d{1,2})/(\d{1,2})(?![\d/])")),
    ("md_dash", re.compile(r"(?<![\d\-.])(\d{2})-(\d{2})(?![\d\-])")),
    ("m_ko", re.compile(r"(?<!\d)(\d{1,2})\s*월")),
    ("y_ko", re.compile(r"(?<!\d)(\d{4})\s*년")),
)
NUM_RE = re.compile(
    r"(?<![A-Za-z0-9_.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s*(%|σ|시그마|sigma)?",
    re.IGNORECASE)


class Token(NamedTuple):
    kind: str          # num · pct · sigma · date
    raw: str           # 찍을 글자 (숫자 · 날짜 모양만)
    value: Optional[Decimal]
    decimals: int
    date: Optional[Tuple[Optional[int], Optional[int], Optional[int]]]   # (연, 월, 일)


def _valid_md(m: int, d: int) -> bool:
    return 1 <= m <= 12 and 1 <= d <= 31


def extract_tokens(text: str) -> List[Token]:
    """글 한 덩어리에서 숫자 토큰을 뽑는다. 이름(EQ-03 …)은 먼저 지운다."""
    out = []  # type: List[Token]
    work = text
    # 날짜 먼저 (찾은 자리는 공백으로 가려 숫자로 다시 세지 않는다)
    for kind, rx in DATE_PATTERNS:
        def repl(mo, kind=kind):
            g = [int(x) for x in mo.groups()]
            if kind == "ymd":
                y, m, d = g
                if not _valid_md(m, d):
                    return mo.group(0)
                out.append(Token("date", mo.group(0).strip(), None, 0, (y, m, d)))
            elif kind == "ym":
                y, m = g
                if not 1 <= m <= 12:
                    return mo.group(0)
                out.append(Token("date", mo.group(0).strip(), None, 0, (y, m, None)))
            elif kind in ("md_ko", "md_slash", "md_dash"):
                m, d = g
                if not _valid_md(m, d):
                    return mo.group(0)
                out.append(Token("date", mo.group(0).strip(), None, 0, (None, m, d)))
            elif kind == "m_ko":
                if not 1 <= g[0] <= 12:
                    return mo.group(0)
                out.append(Token("date", mo.group(0).strip(), None, 0, (None, g[0], None)))
            else:   # y_ko
                out.append(Token("date", mo.group(0).strip(), None, 0, (g[0], None, None)))
            return " " * len(mo.group(0))
        work = rx.sub(repl, work)
    work = ID_RE.sub(lambda mo: " " * len(mo.group(0)), work)
    for mo in NUM_RE.finditer(work):
        whole = mo.group(1).replace(",", "")
        frac = mo.group(2) or ""
        unit = (mo.group(3) or "").lower()
        try:
            val = Decimal(whole + frac)
        except InvalidOperation:
            continue
        decimals = max(len(frac) - 1, 0)
        kind = "num"
        raw = mo.group(1) + frac
        if unit == "%":
            kind, raw = "pct", raw + "%"
        elif unit:
            kind, raw = "sigma", raw + "σ"
        out.append(Token(kind, raw, val, decimals, None))
    return out


# ── 기준 숫자 (facts_lite) ────────────────────────────────────────────────
class Reference(NamedTuple):
    numbers: List[Tuple[Decimal, int]]            # (값, 자릿수)
    dates: Set[Tuple[int, int]]                   # (월, 일)
    months: Set[int]
    years: Set[int]
    year_months: Set[Tuple[int, int]]


def _read_json(path: str):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f, parse_float=Decimal, parse_int=Decimal)


def load_reference(path: str, interview: Optional[str] = None) -> Reference:
    data = _read_json(path)
    nums = []  # type: List[Tuple[Decimal, int]]
    dates, months, years, yms = set(), set(), set(), set()
    texts = []  # type: List[str]
    for fact in data.get("facts", []):
        for key in ("value", "n"):
            v = fact.get(key)
            if isinstance(v, Decimal):
                nums.append((v, max(-v.as_tuple().exponent, 0)))
        texts.append(str(fact.get("text", "")))
    if interview:
        for ans in _read_json(interview).get("answers", []):
            texts.append(str(ans.get("answer", "")))
    for text in texts:
        for t in extract_tokens(text):
            if t.kind == "date":
                y, m, d = t.date
                if y is not None:
                    years.add(y)
                if m is not None:
                    months.add(m)
                if m is not None and d is not None:
                    dates.add((m, d))
                if y is not None and m is not None:
                    yms.add((y, m))
            else:
                nums.append((t.value, t.decimals))
    return Reference(nums, dates, months, years, yms)


def _near(slide_val: Decimal, slide_dec: int, ref_val: Decimal, ref_dec: int) -> bool:
    if slide_dec > ref_dec:
        return slide_val == ref_val
    half = Decimal(5) / (Decimal(10) ** (slide_dec + 1))
    return abs(slide_val - ref_val) <= half


def matches(tok: Token, ref: Reference) -> bool:
    if tok.kind == "date":
        y, m, d = tok.date
        if y is not None and y not in ref.years:
            return False
        if m is not None and d is not None:
            return (m, d) in ref.dates
        if m is not None and y is not None:
            return (y, m) in ref.year_months
        if m is not None:
            return m in ref.months
        return y is not None
    cands = [(tok.value, tok.decimals)]
    if tok.kind == "pct":
        cands.append((tok.value / 100, tok.decimals + 2))
    elif tok.kind == "num" and Decimal(0) < tok.value <= Decimal(1):
        cands.append((tok.value * 100, max(tok.decimals - 2, 0)))
    for sv, sd in cands:
        for rv, rd in ref.numbers:
            if _near(sv, sd, rv, rd):
                return True
    return False


# ── pptx 읽기 ────────────────────────────────────────────────────────────
def _q(ns: str, tag: str) -> str:
    return "{%s}%s" % (ns, tag)


def paragraph_texts(xml_bytes: bytes) -> List[str]:
    """XML 에서 문단별 글자를 모은다. 슬라이드 번호 · 날짜 자리는 뺀다."""
    root = ET.fromstring(xml_bytes)
    skip_ids = set()   # 건너뛸 도형 안의 문단 (id() 로 표시)
    for sp in root.iter(_q(NS_P, "sp")):
        for ph in sp.iter(_q(NS_P, "ph")):
            if ph.get("type") in ("sldNum", "dt"):
                for p in sp.iter(_q(NS_A, "p")):
                    skip_ids.add(id(p))
    out = []
    for p in root.iter(_q(NS_A, "p")):
        if id(p) in skip_ids:
            continue
        parts = []
        for el in p.iter():
            if el.tag == _q(NS_A, "fld"):
                if (el.get("type") or "").lower().startswith(("slidenum", "datetime")):
                    for t in el.iter(_q(NS_A, "t")):
                        t.text = ""
        for t in p.iter(_q(NS_A, "t")):
            parts.append(t.text or "")
        out.append("".join(parts))
    return out


def _rels(zf: zipfile.ZipFile, name: str) -> Dict[str, Tuple[str, str]]:
    """관계 파일 → {rId: (종류, 목표)}"""
    try:
        root = ET.fromstring(zf.read(name))
    except KeyError:
        return {}
    res = {}
    for r in root.iter(_q(NS_PR, "Relationship")):
        res[r.get("Id")] = (r.get("Type") or "", r.get("Target") or "")
    return res


def _join(base_dir: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return os.path.normpath(base_dir + "/" + target).replace("\\", "/")


def slide_parts(zf: zipfile.ZipFile) -> List[str]:
    """슬라이드 파일을 발표 순서로. 순서를 못 읽으면 번호 순."""
    names = zf.namelist()
    try:
        pres = ET.fromstring(zf.read("ppt/presentation.xml"))
        rels = _rels(zf, "ppt/_rels/presentation.xml.rels")
        ordered = []
        for sld in pres.iter(_q(NS_P, "sldId")):
            rid = sld.get(_q(NS_R, "id"))
            if rid in rels:
                path = _join("ppt", rels[rid][1])
                if path in names:
                    ordered.append(path)
        if ordered:
            return ordered
    except (KeyError, ET.ParseError):
        pass
    found = [n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)]
    return sorted(found, key=lambda n: int(re.findall(r"\d+", n)[-1]))


def notes_part(zf: zipfile.ZipFile, slide_path: str) -> Optional[str]:
    base = os.path.basename(slide_path)
    rels = _rels(zf, "ppt/slides/_rels/%s.rels" % base)
    for typ, target in rels.values():
        if typ.endswith("/notesSlide"):
            path = _join("ppt/slides", target)
            if path in zf.namelist():
                return path
    return None


def read_deck(path: str, with_notes: bool) -> List[List[str]]:
    """슬라이드마다 문단 글자 목록"""
    slides = []
    with zipfile.ZipFile(path, "r") as zf:
        for sp in slide_parts(zf):
            paras = paragraph_texts(zf.read(sp))
            if with_notes:
                np_ = notes_part(zf, sp)
                if np_:
                    paras += paragraph_texts(zf.read(np_))
            slides.append(paras)
    return slides


# ── 실행 ────────────────────────────────────────────────────────────────
def analyse(slides: List[List[str]], ref: Reference):
    rows = []
    for paras in slides:
        found, bad = 0, []
        for text in paras:
            for tok in extract_tokens(text):
                found += 1
                if not matches(tok, ref):
                    bad.append(tok.raw)
        rows.append((found, bad))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="장표 숫자가 facts_lite 의 숫자에 묶이는지 본다 (읽기만 함)")
    ap.add_argument("pptx", help="확인할 .pptx")
    ap.add_argument("--facts", default=FACTS_DEFAULT, help="facts_lite.json (기본: kit/llm/synthetic)")
    ap.add_argument("--interview", default=None, help="interview_lite.json (답에 적힌 숫자도 기준에 더함)")
    ap.add_argument("--notes", action="store_true", help="발표자 노트도 읽는다")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="replace")           # type: ignore[attr-defined]
    except AttributeError:
        pass
    try:
        ref = load_reference(args.facts, args.interview)
    except (OSError, ValueError) as e:
        print("기준 파일을 읽지 못했습니다 (%s)" % type(e).__name__)
        print("결과: 점검 실패")
        return 1
    try:
        slides = read_deck(args.pptx, args.notes)
    except (OSError, zipfile.BadZipFile, ET.ParseError, KeyError) as e:
        print("pptx 를 읽지 못했습니다 (%s)" % type(e).__name__)
        print("결과: 점검 실패")
        return 1
    rows = analyse(slides, ref)
    total = sum(f for f, _ in rows)
    unmatched = sum(len(b) for _, b in rows)
    matched = total - unmatched
    for i, (found, bad) in enumerate(rows, 1):
        line = "슬라이드 %d: 찾음 %d · 맞음 %d · 안 맞음 %d" % (i, found, found - len(bad), len(bad))
        if bad:
            line += " (안 맞는 숫자: %s)" % ", ".join(bad)
        print(line)
    print("합계: 슬라이드 %d · 찾음 %d · 맞음 %d · 안 맞음(지어낸 것 후보) %d" % (len(rows), total, matched, unmatched))
    if total == 0:
        print("G2 비율: 계산 못 함 (숫자가 하나도 없음)")
        print("결과: 확인 필요")
        return 3
    share = matched / float(total)
    print("G2 비율: %.0f%% (문턱 %.0f%%) · 안 맞는 숫자 %d 개" % (share * 100, G2_TARGET * 100, unmatched))
    if share >= G2_TARGET and unmatched == 0:
        print("결과: OK")
        return 0
    print("결과: 확인 필요")
    return 3


if __name__ == "__main__":
    sys.exit(main())
