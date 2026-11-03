#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repo_check.py - 공개 저장소 위생 검사기 (표준 라이브러리만 · Python 3.8+)

  python tools/repo_check.py               검사하고 결과를 보인다. 걸린 것이 있어도 종료 코드 0 (고치는 중에 볼 때)
  python tools/repo_check.py --strict      걸린 것이 있으면 종료 코드 1 (CI 가 쓰는 차단 모드)
  python tools/repo_check.py --all-files   git 목록 대신 폴더 전체를 걷는다 (git 이 무시하는 파일도 본다)
  python tools/repo_check.py --root 경로   검사할 저장소 자리 (기본: 이 파일의 부모의 부모)

[검사하는 것] 이 저장소는 공개다 (RULES.md › W-12). 회사 자료가 새어 나가지 않게 세 가지를 본다.
  1. 비밀처럼 보이는 문자열 - sk- 식 키 · AKIA 키 · 개인 키 머리말 · 긴 값이 든 api_key / password / token 대입
  2. 사설 IPv4 주소 - 10.x.x.x · 172.16-31.x.x · 192.168.x.x (127.0.0.1 은 괜찮다)
  3. 허용 폴더 밖의 Office · 데이터 · 그림 파일 - pptx potx ppt xlsx xls csv png jpg jpeg
     허용 폴더: tests/fixtures/ (전부) · kit/**/synthetic/ (전부) · docs/images/ (그림만)

[출력] 비밀 값은 찍지 않는다. 파일:줄 과 가린 모양 (앞 두 글자 + 길이) 만 보인다.
  마지막 줄은 결과: OK · 결과: 확인 필요(기본 모드의 걸린 것) · 결과: 점검 실패(--strict 의 걸린 것)
  사용법 오류는 종료 코드 2 (결과 줄 없음).

[예외] 가짜 값이 일부러 들어가야 하는 줄 (시험 자료 등) 은 줄 안에 repo-check: allow 를 적으면
  그 줄의 글 검사(1 · 2)를 건너뛴다. 파일 종류 검사(3)에는 통하지 않는다 - 허용 폴더에 둔다.
"""
import argparse
import os
import re
import subprocess
import sys
from typing import Iterable, List, NamedTuple, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOW_MARK = "repo-check: allow"
SKIP_DIRS = (".git", "__pycache__", ".venv", "venv")      # 폴더 걷기에서 건너뛰는 폴더
MAX_TEXT_BYTES = 2 * 1024 * 1024                          # 이보다 큰 파일의 내용은 읽지 않는다
IMAGE_EXT = (".png", ".jpg", ".jpeg")
DATA_EXT = (".pptx", ".potx", ".ppt", ".xlsx", ".xls", ".csv") + IMAGE_EXT
# 허용 폴더: (폴더 접두사, 허용 확장자). kit/**/synthetic/ 은 allowed_by_folder 에서 따로 본다.
ALLOWED_FOLDERS = (
    ("tests/fixtures/", DATA_EXT),
    ("docs/images/", IMAGE_EXT),
)

SECRET_RES = (
    ("sk- 식 키", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("AWS 키", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("개인 키 머리말", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
)
# 이름에 api_key / password / secret / token 이 든 칸에 따옴표 친 긴 값(16자+, 공백 없음)을 대입하는 줄
ASSIGN_RE = re.compile(
    r"""(?ix)
    [\w-]*(?:api[_-]?key|password|passwd|secret|token)[\w-]*
    ["']?\s*[:=]\s*
    ["']([^"'\s]{16,})["']
    """
)
IPV4_RE = re.compile(r"(?<![\d.])(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?![\d]|\.\d)")


class Finding(NamedTuple):
    kind: str        # 비밀 · 사설 주소 · 파일 종류
    path: str        # 저장소 기준 경로 (/ 구분)
    line: int        # 0 이면 줄 없음 (파일 종류)
    msg: str


def mask(value: str) -> str:
    """비밀 값을 가린 모양: 앞 두 글자 + *** + 길이"""
    if len(value) <= 4:
        return "***"
    return "%s***(%d자)" % (value[:2], len(value))


def is_private_ipv4(a: int, b: int, c: int, d: int) -> bool:
    if max(a, b, c, d) > 255:
        return False
    return a == 10 or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168)


def scan_line(text: str) -> List[Tuple[str, str]]:
    """한 줄의 글 검사. (종류, 설명) 목록을 돌려준다. 설명에는 비밀 값 원문이 없다."""
    if ALLOW_MARK in text:
        return []
    out = []
    for label, rx in SECRET_RES:
        for m in rx.finditer(text):
            shown = label if label == "개인 키 머리말" else "%s %s" % (label, mask(m.group(0)))
            out.append(("비밀", shown))
    for m in ASSIGN_RE.finditer(text):
        value = m.group(1)
        if value.startswith("{env:") or value.startswith("{file:"):     # 참조는 비밀이 아니다 (W-04)
            continue
        out.append(("비밀", "이름 있는 칸에 긴 값 %s" % mask(value)))
    for m in IPV4_RE.finditer(text):
        a, b, c, d = (int(g) for g in m.groups())
        if is_private_ipv4(a, b, c, d):
            out.append(("사설 주소", "사설 IPv4 %d.x.x.x" % a))
    return out


def allowed_by_folder(rel: str, ext: str) -> bool:
    for prefix, exts in ALLOWED_FOLDERS:
        if rel.startswith(prefix) and ext in exts:
            return True
    parts = rel.split("/")
    # kit/**/synthetic/ - kit 아래 어디든 synthetic 폴더 안이면 전부 허용
    if parts[0] == "kit" and "synthetic" in parts[1:-1]:
        return True
    return False


def list_files(root: str, all_files: bool) -> List[str]:
    """검사할 파일의 저장소 기준 경로(/ 구분). git 저장소면 git 목록 (추적 + 무시되지 않은 새 파일), 아니면 걷기."""
    if not all_files and os.path.exists(os.path.join(root, ".git")):
        try:
            res = subprocess.run(
                ["git", "-C", root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
            names = [os.fsdecode(n) for n in res.stdout.split(b"\0") if n]
            return sorted(set(n for n in names if os.path.isfile(os.path.join(root, n))))
        except (OSError, subprocess.CalledProcessError):
            pass                                                   # git 이 없거나 실패하면 걷는다
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def read_text(path: str) -> Optional[str]:
    """글 파일이면 내용을, 아니면(바이너리 · 너무 큼 · 못 읽음) None 을 돌려준다."""
    try:
        if os.path.getsize(path) > MAX_TEXT_BYTES:
            return None
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        return None
    if b"\0" in raw[:8192]:
        return None
    return raw.decode("utf-8", errors="replace")


def check(root: str, all_files: bool = False) -> List[Finding]:
    findings = []
    for rel in list_files(root, all_files):
        ext = os.path.splitext(rel)[1].lower()
        if ext in DATA_EXT:
            if not allowed_by_folder(rel, ext):
                findings.append(Finding("파일 종류", rel, 0, "허용 폴더 밖의 %s 파일" % ext))
            continue                                               # 자료 파일의 내용은 읽지 않는다
        text = read_text(os.path.join(root, rel))
        if text is None:
            continue
        for no, line in enumerate(text.splitlines(), 1):
            for kind, msg in scan_line(line):
                findings.append(Finding(kind, rel, no, msg))
    return findings


def output_lines(findings: Iterable[Finding]) -> List[str]:
    return ["  - [%s] %s%s  %s" % (f.kind, f.path, ":%d" % f.line if f.line else "", f.msg) for f in findings]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="공개 저장소 위생 검사기 (RULES.md › W-12)")
    ap.add_argument("--strict", action="store_true", help="걸린 것이 있으면 종료 코드 1 (차단 모드)")
    ap.add_argument("--all-files", action="store_true", help="git 목록 대신 폴더 전체를 걷는다")
    ap.add_argument("--root", default=ROOT, help="검사할 저장소 자리")
    args = ap.parse_args(argv)                                     # 사용법 오류는 argparse 가 종료 코드 2 로 끝낸다
    if not os.path.isdir(args.root):
        print("사용법 오류: 폴더가 아닙니다 - %s" % args.root, file=sys.stderr)
        return 2
    try:
        sys.stdout.reconfigure(errors="replace")                   # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    findings = check(args.root, args.all_files)
    print("저장소 위생 검사 - %s" % os.path.abspath(args.root))
    if findings:
        print("")
        for line in output_lines(findings):
            print(line)
    print("")
    print("걸린 것 %d" % len(findings) + ("" if args.strict else " - 경고 모드 (--strict 로 차단)"))
    if not findings:
        print("결과: OK")
        return 0
    print("결과: 점검 실패" if args.strict else "결과: 확인 필요")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
