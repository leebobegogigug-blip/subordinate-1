#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_env.py - M0 사내 PC 확인 키트 (KIT-1 · KIT-4 · KIT-5). M0 가 끝나면 kit/ 째로 지우는 버리는 코드다.

  python check_env.py env                          KIT-1  Python · pip · 패키지 import · PowerPoint COM · LibreOffice
  python check_env.py template 파일.pptx [파일2]    KIT-4  레이아웃 · 자리표시자 목록 · 지문 (두 판이면 차이)
  python check_env.py office [--template 파일] [--com]
                                                   KIT-5  시험 PPTX 를 만든다 (열어 보는 것은 사람)

[규칙]
  - 가져오기는 표준 라이브러리만 쓴다. python-pptx 는 필요한 함수 안에서 불러온다 (Python 3.8+).
  - 결과는 kit/results/ 에 JSON 으로 쓴다 (git 이 무시하는 폴더). 기존 파일은 덮어쓰지 않는다.
  - 화면과 JSON 에 사용자 폴더 경로는 %USERPROFILE% (Windows 밖에서는 ~) 로 바꿔 적는다.
  - 레이아웃 · 마스터 이름과 파일 이름은 화면에 찍지 않는다 (회사 이름이 들어 있을 수 있다).
    --show-names 를 주면 이름을 결과 JSON 파일에만 적는다.
  - 마지막 줄은 결과: OK · 결과: 확인 필요 · 결과: 점검 실패 중 하나다.
    종료 코드 0 OK · 1 점검 실패 · 2 사용법 오류(결과 줄 없음) · 3 사람 확인 필요.
"""
import argparse
import hashlib
import io
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import time
import zlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

KIT_VERSION = 1
KIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../kit
RESULTS_DIR = os.path.join(KIT_DIR, "results")
PINS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements-probe.txt")

OK, FAIL, USAGE, HUMAN = 0, 1, 2, 3
RESULT_LINES = {OK: "결과: OK", HUMAN: "결과: 확인 필요", FAIL: "결과: 점검 실패"}

MIN_PYTHON = (3, 8)
PIP_TIMEOUT_SEC = 60
ERROR_TEXT_MAX = 200
GEOMETRY_STEP_EMU = 36000          # 지문의 위치 · 크기는 0.1 cm 단위로 둥글린다
PPTX_MAIN_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"

# (pip 이름, import 이름, 필수 여부) - "win-opt" 는 Windows 에서만 보고 필수는 아니다 (렌더 검사용 선택 기능 · RULES.md › W-02)
PROBE_PACKAGES = [
    ("python-pptx", "pptx", True),
    ("pandas", "pandas", True),
    ("openpyxl", "openpyxl", True),
    ("matplotlib", "matplotlib", True),
    ("scipy", "scipy", True),
    ("pywin32", "win32com.client", "win-opt"),
]
# 참고로만 보이는 의존 (없어도 점검 실패가 아니다)
INFO_PACKAGES = [("lxml", "lxml"), ("Pillow", "PIL"), ("numpy", "numpy")]

TITLE_TYPES = ("TITLE", "CENTER_TITLE", "VERTICAL_TITLE")
BODY_TYPES = ("BODY", "OBJECT", "VERTICAL_BODY", "VERTICAL_OBJECT")
PICTURE_TYPES = ("PICTURE",)

LIBREOFFICE_DIRS = (
    r"C:\Program Files\LibreOffice\program",
    r"C:\Program Files (x86)\LibreOffice\program",
    "/usr/bin", "/usr/local/bin", "/opt/libreoffice/program",
    "/Applications/LibreOffice.app/Contents/MacOS",
)

# 시험 글 - 지어낸 문장이다. 일부러 길게 써서 넘침을 일으킨다.
PROBE_TITLE = ("반도체 공정 변동 원인 분석 결과 및 개선 방안에 대한 종합 보고 - "
               "한글이 긴 제목에서 줄바꿈과 글자 넘침이 어떻게 보이는지 확인하는 시험 문장입니다")
PROBE_BULLETS = [
    "첫째 항목은 일부러 길게 쓴 한글 문장으로, 한 줄에 다 들어가지 않고 두세 줄로 넘어가는지 확인합니다.",
    "둘째 항목도 길게 씁니다. 글머리 기호와 들여쓰기가 있어도 오른쪽 끝에서 잘리지 않아야 합니다.",
    "셋째 항목은 숫자와 단위를 섞습니다. 평균 12.34 nm, 표준편차 0.56 nm, 표본 수 n=128 입니다.",
    "넷째 항목은 괄호와 따옴표를 섞습니다. (가) 조건 A, (나) 조건 B, \"비교군\" 대비 차이를 봅니다.",
    "다섯째 항목은 영문과 한글을 섞습니다. Lot ID 와 Wafer ID 를 함께 적고 SPC 한계선을 표시합니다.",
    "여섯째 항목은 더 길게 씁니다. 본문 상자의 아래쪽 끝을 넘어 글자가 장표 밖으로 흘러나가는지 봅니다.",
    "일곱째 항목은 짧습니다.",
    "여덟째 항목은 마지막입니다. 이 줄까지 장표 안에 보이면 이 본문 상자는 이 분량을 견딥니다.",
]
PROBE_NOTE = "시험용 발표자 노트입니다. 한글 노트가 저장되고 다시 열리는지 확인합니다."


# ───────────────────────── 콘솔 · 경로 가리기 ─────────────────────────

def setup_console() -> None:
    """콘솔 출력을 UTF-8 로 맞춘다 (Python 3.8 은 reconfigure 가 있다). 실패해도 조용히 넘어간다."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            buf = getattr(stream, "buffer", None)
            if buf is not None:
                setattr(sys, name, io.TextIOWrapper(buf, encoding="utf-8", errors="replace",
                                                    line_buffering=True))


def say(text: str = "") -> None:
    print(text)


def home_dirs() -> List[str]:
    homes = []
    for value in (os.path.expanduser("~"), os.environ.get("USERPROFILE")):
        if value and value != "~" and value not in homes:
            homes.append(value)
    return homes


def mask_text(text: str, homes: Optional[Sequence[str]] = None, token: Optional[str] = None) -> str:
    """글 안의 사용자 폴더 경로를 %USERPROFILE% (Windows 밖에서는 ~) 로 바꾼다. 슬래시 방향 · 대소문자 무시."""
    if homes is None:
        homes = home_dirs()
    if token is None:
        token = "%USERPROFILE%" if os.name == "nt" else "~"
    for home in homes:
        home = home.rstrip("\\/")
        if len(home) <= 3:           # "C:" · "" 같은 뿌리는 가리지 않는다
            continue
        variants = {home, home.replace("\\", "/"), home.replace("/", "\\")}
        for variant in sorted(variants, key=len, reverse=True):
            pattern = re.compile(re.escape(variant) + r"(?![\w.\-])", re.IGNORECASE)
            text = pattern.sub(lambda _m: token, text)
    return text


def mask_obj(obj: Any, homes: Optional[Sequence[str]] = None, token: Optional[str] = None) -> Any:
    if isinstance(obj, str):
        return mask_text(obj, homes, token)
    if isinstance(obj, dict):
        return {k: mask_obj(v, homes, token) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [mask_obj(v, homes, token) for v in obj]
    return obj


def short_error(exc: BaseException) -> str:
    """예외를 한 줄로 줄이고 경로를 가린다. 길이를 자른다."""
    text = "%s: %s" % (type(exc).__name__, " ".join(str(exc).split()))
    text = mask_text(text)
    return text if len(text) <= ERROR_TEXT_MAX else text[:ERROR_TEXT_MAX] + "..."


def display_path(path: str) -> str:
    """사람에게 보일 경로 - 저장소 폴더 안이면 kit\\... 상대 경로, 아니면 가린 절대 경로."""
    try:
        rel = os.path.relpath(path, os.path.dirname(KIT_DIR))
        if not rel.startswith(".."):
            return rel
    except ValueError:
        pass
    return mask_text(path)


# ───────────────────────── 결과 파일 ─────────────────────────

def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def write_new_file(directory: str, stem: str, ext: str, data: bytes) -> str:
    """덮어쓰지 않고 새 파일을 쓴다. 같은 이름이 있으면 stem_2 · stem_3 ... 으로 간다."""
    os.makedirs(directory, exist_ok=True)
    n = 1
    while True:
        name = stem + ext if n == 1 else "%s_%d%s" % (stem, n, ext)
        path = os.path.join(directory, name)
        try:
            with open(path, "xb") as f:
                f.write(data)
            return path
        except FileExistsError:
            n += 1


def write_result(results_dir: str, sub: str, record: Dict[str, Any], stamp: Optional[str] = None) -> str:
    record = mask_obj(record)
    body = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    return write_new_file(results_dir, "%s_%s" % (sub, stamp or timestamp()), ".json", body)


def finish(code: int) -> int:
    say(RESULT_LINES[code])
    return code


def say_send_line(line: str) -> None:
    """사용자가 손으로 옮겨 적을 한 줄 (ASCII). 마지막 '결과:' 줄 바로 앞에 찍는다."""
    say("보낼 줄: " + line)


# ───────────────────────── PNG (표준 라이브러리) ─────────────────────────

def make_png(width: int = 160, height: int = 96) -> bytes:
    """합성 PNG (8비트 RGB). 그림 시험용 - Pillow 가 필요 없다."""
    def chunk(tag: bytes, payload: bytes) -> bytes:
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    rows = []
    for y in range(height):
        row = bytearray([0])                       # 필터 없음
        for x in range(width):
            checker = ((x // 16) + (y // 16)) % 2
            row += bytes((40 + (x * 180) // max(width - 1, 1),
                          60 + (y * 160) // max(height - 1, 1),
                          200 if checker else 120))
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))


# ───────────────────────── KIT-1: env ─────────────────────────

def parse_pins(text: str) -> Dict[str, str]:
    """requirements 글에서 name==version 을 뽑는다. 이 PC 에 해당하는 줄만 (sys_platform 표식)."""
    pins = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        spec, _, marker = line.partition(";")
        if "win32" in marker and not sys.platform.startswith("win"):
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s]+)$", spec.strip())
        if m:
            pins[m.group(1).lower().replace("_", "-")] = m.group(2)
    return pins


def load_pins() -> Dict[str, str]:
    try:
        with open(PINS_FILE, "r", encoding="utf-8") as f:
            return parse_pins(f.read())
    except OSError:
        return {}


def installed_version(pip_name: str, module: Any) -> Optional[str]:
    version = getattr(module, "__version__", None)
    if version:
        return str(version)
    try:
        from importlib import metadata
        return metadata.version(pip_name)
    except Exception:                              # 메타데이터가 없거나 깨진 설치
        return None


def check_package(pip_name: str, module_name: str) -> Dict[str, Any]:
    import importlib
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:                       # ImportError · DLL 오류 등 모두 "안 불러와짐"
        return {"imported": False, "version": None, "error": short_error(exc)}
    return {"imported": True, "version": installed_version(pip_name, module), "error": None}


def check_pip() -> Dict[str, Any]:
    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "--version"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=PIP_TIMEOUT_SEC)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "version": None, "error": short_error(exc)}
    out = proc.stdout.decode("utf-8", "replace").strip()
    m = re.match(r"pip\s+(\S+)", out)
    if proc.returncode != 0 or not m:
        err = proc.stderr.decode("utf-8", "replace")
        return {"ok": False, "version": None, "error": mask_text(" ".join(err.split()))[:ERROR_TEXT_MAX]}
    return {"ok": True, "version": m.group(1), "error": None}


def check_powerpoint_com() -> Dict[str, Any]:
    """PowerPoint 를 실행하지 않고 레지스트리만 본다."""
    if not sys.platform.startswith("win"):
        return {"applicable": False, "registered": None, "progid": None}
    try:
        import winreg
    except ImportError:
        return {"applicable": False, "registered": None, "progid": None}
    result = {"applicable": True, "registered": False, "progid": None}
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application\CLSID"):
            result["registered"] = True
    except OSError:
        return result
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application\CurVer") as key:
            result["progid"] = str(winreg.QueryValue(key, None))     # 예: PowerPoint.Application.16
    except OSError:
        pass
    return result


def find_libreoffice() -> Dict[str, Any]:
    found = shutil.which("soffice") or shutil.which("soffice.exe")
    if not found:
        for folder in LIBREOFFICE_DIRS:
            for exe in ("soffice.exe", "soffice"):
                candidate = os.path.join(folder, exe)
                if os.path.isfile(candidate):
                    found = candidate
                    break
            if found:
                break
    return {"found": bool(found), "path": mask_text(found) if found else None}


def required_here(flag: Any) -> bool:
    if flag == "win":
        return sys.platform.startswith("win")
    if flag == "win-opt":
        return False
    return bool(flag)


def windows_only(flag: Any) -> bool:
    return flag in ("win", "win-opt")


def cmd_env(args: argparse.Namespace) -> int:
    say("[KIT-1] 사내 PC 환경 점검")
    problems = []
    py_ok = sys.version_info[:2] >= MIN_PYTHON
    py = {
        "version": platform.python_version(),
        "bits": struct.calcsize("P") * 8,
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
        "os": platform.platform(),
        "machine": platform.machine(),
    }
    say("Python %s (%d비트, %s)" % (py["version"], py["bits"], py["implementation"]))
    say("운영체제: %s" % py["os"])
    if not py_ok:
        problems.append("Python 3.8 이상이 필요합니다")
        say("  -> Python 이 3.8 보다 낮습니다")

    pip = check_pip()
    say("pip: %s" % (pip["version"] if pip["ok"] else "실패 (%s)" % pip["error"]))
    if not pip["ok"]:
        problems.append("pip 를 쓸 수 없습니다")

    pins = load_pins()
    packages = {}
    say("패키지 (필수 표시 *):")
    for pip_name, module_name, req in PROBE_PACKAGES:
        needed = required_here(req)
        if windows_only(req) and not sys.platform.startswith("win"):
            packages[pip_name] = {"required": False, "skipped": "Windows 가 아니라 건너뜀"}
            say("  %-12s 건너뜀 (Windows 에서만 씁니다)" % pip_name)
            continue
        info = check_package(pip_name, module_name)
        info["required"] = needed
        pin = pins.get(pip_name.lower())
        info["pinned"] = pin
        info["matches_pin"] = (info["version"] == pin) if (pin and info["version"]) else None
        packages[pip_name] = info
        if info["imported"]:
            note = ""
            if info["matches_pin"] is False:
                note = "  (고정 판 %s 와 다름)" % pin
            say("  %-12s %s 불러옴 %s%s" % (pip_name, info["version"] or "판 알 수 없음", "*" if needed else "", note))
        else:
            say("  %-12s 불러오지 못함 %s - %s" % (pip_name, "*" if needed else "", info["error"]))
            if needed:
                problems.append("%s 를 불러오지 못했습니다" % pip_name)
    extras = {}
    for pip_name, module_name in INFO_PACKAGES:
        extras[pip_name] = check_package(pip_name, module_name)
    say("참고: " + " · ".join("%s %s" % (n, (v["version"] or "있음") if v["imported"] else "없음")
                              for n, v in extras.items()))

    com = check_powerpoint_com()
    if com["applicable"]:
        say("PowerPoint COM 등록: %s%s" % ("있음" if com["registered"] else "없음",
                                           " (%s)" % com["progid"] if com["progid"] else ""))
    else:
        say("PowerPoint COM 등록: 해당 없음 (Windows 가 아닙니다)")
    office = find_libreoffice()
    say("LibreOffice: %s" % ("있음" if office["found"] else "없음"))

    code = FAIL if problems else OK
    failed_required = sum(1 for v in packages.values() if v.get("required") and not v.get("imported"))
    win32 = packages.get("pywin32", {})
    if problems:
        verdict = "R"
    elif sys.platform.startswith("win") and not win32.get("imported"):
        verdict = "Y"
    else:
        verdict = "G"
    send_line = "K1 %s %d.%d %d" % (verdict, sys.version_info[0], sys.version_info[1], failed_required)
    record = {"kit": "KIT-1", "subcommand": "env", "kit_version": KIT_VERSION, "time": timestamp(),
              "python": py, "python_ok": py_ok, "pip": pip, "packages": packages, "extras": extras,
              "powerpoint_com": com, "libreoffice": office, "problems": problems,
              "send_line": send_line, "result": RESULT_LINES[code]}
    path = write_result(args.results_dir, "env", record)
    say("결과 파일: %s" % display_path(path))
    for p in problems:
        say("문제: %s" % p)
    say_send_line(send_line)
    return finish(code)


# ───────────────────────── python-pptx 열기 (.potx 포함) ─────────────────────────

def import_pptx():
    """python-pptx 를 불러온다. 없으면 None."""
    try:
        import pptx
        return pptx
    except Exception:
        return None


def rewrite_main_content_type(xml: bytes) -> Tuple[bytes, Optional[str]]:
    """[Content_Types].xml 에서 /ppt/presentation.xml 의 형식을 일반 프레젠테이션으로 바꾼다.
    돌려주는 값: (새 내용, 바꾸기 전 형식의 짧은 이름). 바꿀 것이 없으면 (원본, None)."""
    text = xml.decode("utf-8")
    override = re.search(r"<Override\b[^>]*PartName=([\"'])/ppt/presentation\.xml\1[^>]*>", text)
    if not override:
        return xml, None
    tag = override.group(0)
    ct = re.search(r"ContentType=([\"'])([^\"']*)\1", tag)
    if not ct or ct.group(2) == PPTX_MAIN_TYPE:
        return xml, None
    old = ct.group(2)
    new_tag = tag.replace(ct.group(0), 'ContentType="%s"' % PPTX_MAIN_TYPE)
    kind = "template" if "template" in old else ("macro" if "macro" in old.lower() else "other")
    return text.replace(tag, new_tag, 1).encode("utf-8"), kind


def repackage_as_pptx(path: str) -> Tuple[bytes, Optional[str]]:
    """원본은 읽기만 한다. 형식을 고친 사본을 메모리에서 만든다 (디스크에 사본을 남기지 않는다)."""
    import zipfile
    out = io.BytesIO()
    kind = None
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data, kind = rewrite_main_content_type(data)
            zout.writestr(item, data)
    return out.getvalue(), kind


def open_presentation(path: str):
    """(Presentation, 바꾼 형식 이름 또는 None). 실패하면 예외."""
    from pptx import Presentation
    data, kind = repackage_as_pptx(path)
    return Presentation(io.BytesIO(data)), kind


# ───────────────────────── KIT-4: template ─────────────────────────

def ph_type_name(ph: Any) -> str:
    t = ph.placeholder_format.type
    if t is None:
        return "NONE"
    return getattr(t, "name", None) or str(t).split(" ")[0]


def classify(type_names: Sequence[str]) -> Dict[str, bool]:
    names = set(type_names)
    return {"title": bool(names & set(TITLE_TYPES)),
            "body": bool(names & set(BODY_TYPES)),
            "picture": bool(names & set(PICTURE_TYPES))}


def usable_layout(type_names: Sequence[str]) -> bool:
    """KIT-4 초록 조건: 제목 + (본문 또는 그림) 자리표시자."""
    c = classify(type_names)
    return c["title"] and (c["body"] or c["picture"])


def _digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, separators=(",", ":")).encode("utf-8")).hexdigest()


def layout_record(layout: Any, label: str, master_no: int, show_names: bool) -> Dict[str, Any]:
    phs = []
    for ph in layout.placeholders:
        try:
            geom = [ph.left, ph.top, ph.width, ph.height]
            geom = [int(round((v or 0) / GEOMETRY_STEP_EMU)) for v in geom]
        except Exception:                          # 위치를 물려받지 못한 깨진 자리표시자
            geom = [0, 0, 0, 0]
        phs.append((ph.placeholder_format.idx, ph_type_name(ph), geom))
    phs.sort(key=lambda x: (x[0], x[1]))
    structure = _digest([[idx, t] for idx, t, _g in phs])
    geometry = _digest([[idx, t] + g for idx, t, g in phs])
    total_shapes = len(layout.shapes)
    rec = {"label": label, "master": master_no,
           "placeholder_count": len(phs),
           "other_shape_count": total_shapes - len(phs),
           "placeholders": [{"idx": idx, "type": t} for idx, t, _g in phs],
           "structure": structure, "geometry": geometry,
           "usable": usable_layout([t for _i, t, _g in phs])}
    if show_names:
        rec["name"] = layout.name
    return rec


def inspect_presentation(prs: Any, show_names: bool) -> Dict[str, Any]:
    layouts = []
    masters = []
    for mi, master in enumerate(prs.slide_masters, 1):
        m = {"master": mi, "layout_count": len(master.slide_layouts)}
        if show_names:
            m["name"] = master.name
        masters.append(m)
        for layout in master.slide_layouts:
            layouts.append(layout_record(layout, "L%02d" % (len(layouts) + 1), mi, show_names))
    return {
        "slide_size_cm": [round(prs.slide_width / 360000.0, 2), round(prs.slide_height / 360000.0, 2)],
        "slide_count": len(prs.slides),
        "masters": masters,
        "layouts": layouts,
        "deck_structure_fingerprint": _digest([l["structure"] for l in layouts]),
        "deck_geometry_fingerprint": _digest([l["geometry"] for l in layouts]),
        "usable_layout_count": sum(1 for l in layouts if l["usable"]),
    }


def diff_layouts(a: List[Dict[str, Any]], b: List[Dict[str, Any]]) -> Dict[str, Any]:
    """두 판의 레이아웃을 구조 지문으로 맞춘다 (이름을 쓰지 않는다).
    같음 → 구조는 같고 위치 · 크기만 다름 → 남은 것을 순서대로 짝지어 '바뀜' → 나머지는 사라짐 · 추가."""
    status = {}      # a 순번 -> (종류, b 순번)
    used = set()
    for i, la in enumerate(a):
        for j, lb in enumerate(b):
            if j not in used and la["structure"] == lb["structure"] and la["geometry"] == lb["geometry"]:
                status[i] = ("same", j)
                used.add(j)
                break
    for i, la in enumerate(a):
        if i in status:
            continue
        for j, lb in enumerate(b):
            if j not in used and la["structure"] == lb["structure"]:
                status[i] = ("geometry", j)
                used.add(j)
                break
    left_a = [i for i in range(len(a)) if i not in status]
    left_b = [j for j in range(len(b)) if j not in used]
    for i, j in zip(left_a, left_b):
        status[i] = ("changed", j)
    for i in left_a[len(left_b):]:
        status[i] = ("removed", None)
    added = left_b[len(left_a):]
    out = {"same": [], "geometry_only": [], "changed": [], "removed": [], "added": []}
    for i in sorted(status):
        kind, j = status[i]
        if kind == "same":
            out["same"].append([a[i]["label"], b[j]["label"]])
        elif kind == "geometry":
            out["geometry_only"].append([a[i]["label"], b[j]["label"]])
        elif kind == "changed":
            out["changed"].append([a[i]["label"], b[j]["label"]])
        else:
            out["removed"].append(a[i]["label"])
    out["added"] = [b[j]["label"] for j in added]
    return out


def file_facts(path: str) -> Dict[str, Any]:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return {"extension": os.path.splitext(path)[1].lower(), "bytes": os.path.getsize(path),
            "sha256_12": h.hexdigest()[:12]}


def print_inspection(tag: str, info: Dict[str, Any]) -> None:
    say("[%s] 슬라이드 크기 %.2f x %.2f cm · 마스터 %d개 · 레이아웃 %d개 · 들어 있는 장 %d개"
        % (tag, info["slide_size_cm"][0], info["slide_size_cm"][1], len(info["masters"]),
           len(info["layouts"]), info["slide_count"]))
    for l in info["layouts"]:
        phs = " ".join("%s#%d" % (p["type"], p["idx"]) for p in l["placeholders"]) or "(없음)"
        say("  %s 마스터%d · 자리표시자 %d개 · 지문 %s%s · %s"
            % (l["label"], l["master"], l["placeholder_count"], l["structure"][:8],
               " · 제목+본문/그림" if l["usable"] else "", phs))
    say("[%s] 구조 지문 %s · 위치 지문 %s" % (tag, info["deck_structure_fingerprint"][:12],
                                           info["deck_geometry_fingerprint"][:12]))


def cmd_template(args: argparse.Namespace) -> int:
    say("[KIT-4] 회사 템플릿 점검")
    paths = args.paths
    if len(paths) > 2:
        say("파일은 하나 또는 둘만 받습니다 (지금 판, 이전 판).")
        return USAGE
    for p in paths:
        if not os.path.isfile(p):
            say("파일을 찾을 수 없습니다. 경로를 큰따옴표로 감싸 다시 입력해 주세요.")
            return USAGE
    if import_pptx() is None:
        say("python-pptx 를 불러오지 못했습니다. 먼저 KIT-1 (env) 을 통과시켜 주세요.")
        return finish(FAIL)

    tags = ["A", "B"]
    infos = []
    files = []
    failures = []
    for tag, p in zip(tags, paths):
        try:
            prs, kind = open_presentation(p)
            info = inspect_presentation(prs, args.show_names)
            info["converted_from"] = kind
            infos.append(info)
            files.append(file_facts(p))
            say("%s 파일: 열기 성공 (%s, %d바이트)%s" % (
                tag, files[-1]["extension"], files[-1]["bytes"],
                " · 템플릿 형식을 일반 pptx 로 바꿔 읽음" if kind else ""))
            print_inspection(tag, info)
        except Exception as exc:                   # 깨진 파일 · 잠긴 파일 등. 메시지에 파일 이름이 있을 수 있어 종류만 적는다.
            failures.append({"tag": tag, "error_type": type(exc).__name__})
            infos.append(None)
            files.append(file_facts(p) if os.path.isfile(p) else {})
            say("%s 파일: 열기 실패 (%s)" % (tag, type(exc).__name__))

    diff = None
    if len(paths) == 2 and infos[0] and infos[1]:
        diff = diff_layouts(infos[0]["layouts"], infos[1]["layouts"])
        say("두 판 비교 (구조 지문 기준, 이름은 쓰지 않음)")
        say("  같음 %d · 위치/크기만 다름 %d · 구조 바뀜 %d · A 에만 있음 %d · B 에만 있음 %d"
            % (len(diff["same"]), len(diff["geometry_only"]), len(diff["changed"]),
               len(diff["removed"]), len(diff["added"])))
        for a_l, b_l in diff["geometry_only"]:
            say("  위치/크기만 다름: A %s ~ B %s" % (a_l, b_l))
        for a_l, b_l in diff["changed"]:
            say("  구조 바뀜: A %s -> B %s" % (a_l, b_l))
        for a_l in diff["removed"]:
            say("  A 에만 있음: %s" % a_l)
        for b_l in diff["added"]:
            say("  B 에만 있음: %s" % b_l)
        same_deck = infos[0]["deck_structure_fingerprint"] == infos[1]["deck_structure_fingerprint"]
        say("  전체 구조 지문: %s" % ("같음" if same_deck else "다름"))

    opened = [i for i in infos if i]
    if failures or not opened:
        code = FAIL
    elif all(i["usable_layout_count"] > 0 for i in opened):
        code = OK
    else:
        code = HUMAN
    if code != FAIL:
        say("제목+본문/그림 레이아웃: " + " · ".join(
            "%s %d개" % (t, i["usable_layout_count"]) for t, i in zip(tags, infos) if i))
    if args.show_names:
        say("이름은 화면에 찍지 않고 결과 파일에만 적었습니다.")
    verdict = {OK: "G", HUMAN: "Y", FAIL: "R"}[code]
    first = infos[0] if infos else None
    layout_n = str(len(first["layouts"])) if first else "-"
    usable_n = str(first["usable_layout_count"]) if first else "-"
    if len(paths) == 2 and diff is not None:
        diff_n = str(len(diff["changed"]) + len(diff["removed"]) + len(diff["added"]))
    else:
        diff_n = "-"
    send_line = "K4 %s %s %s %s" % (verdict, layout_n, usable_n, diff_n)
    record = {"kit": "KIT-4", "subcommand": "template", "kit_version": KIT_VERSION, "time": timestamp(),
              "show_names": bool(args.show_names), "files": files, "inspections": infos,
              "failures": failures, "diff": diff, "send_line": send_line, "result": RESULT_LINES[code]}
    path = write_result(args.results_dir, "template", record)
    say("결과 파일: %s" % display_path(path))
    say_send_line(send_line)
    return finish(code)


# ───────────────────────── KIT-5: office ─────────────────────────

def drop_all_slides(prs: Any) -> int:
    """템플릿에 들어 있던 장을 모두 뺀다 (시험 파일에 남지 않게)."""
    lst = prs.slides._sldIdLst
    n = len(lst)
    for sld_id in list(lst):
        prs.part.drop_rel(sld_id.rId)
        lst.remove(sld_id)
    return n


def _fill_table(shape: Any) -> None:
    table = shape.table
    for r in range(len(table.rows)):
        for c in range(len(table.columns)):
            table.cell(r, c).text = "제목 칸" if r == 0 else "행%d 열%d 값 %.2f" % (r, c + 1, r * 1.25 + c)


def _set_notes(slide: Any, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


def _add_picture(slide: Any, prs: Any) -> None:
    width = int(prs.slide_width * 0.35)
    slide.shapes.add_picture(io.BytesIO(make_png()), int(prs.slide_width * 0.55),
                             int(prs.slide_height * 0.45), width=width)


def _add_table(slide: Any, prs: Any) -> Any:
    shape = slide.shapes.add_table(4, 3, int(prs.slide_width * 0.1), int(prs.slide_height * 0.45),
                                   int(prs.slide_width * 0.8), int(prs.slide_height * 0.3))
    _fill_table(shape)
    return shape


def build_default_deck() -> bytes:
    from pptx import Presentation
    prs = Presentation()
    s1 = prs.slides.add_slide(prs.slide_layouts[0])          # 제목 장
    s1.shapes.title.text = PROBE_TITLE
    s1.placeholders[1].text = "부제목도 한글로 길게 씁니다 - 가나다라마바사 아자차카타파하 " * 2
    _set_notes(s1, PROBE_NOTE + " (1장)")
    s2 = prs.slides.add_slide(prs.slide_layouts[1])          # 제목 + 본문
    s2.shapes.title.text = "긴 한글 본문 넘침 시험"
    tf = s2.placeholders[1].text_frame
    tf.text = PROBE_BULLETS[0]
    for line in PROBE_BULLETS[1:]:
        tf.add_paragraph().text = line
    _set_notes(s2, PROBE_NOTE + " (2장)")
    s3 = prs.slides.add_slide(prs.slide_layouts[5])          # 제목만 + 그림
    s3.shapes.title.text = "그림 시험"
    _add_picture(s3, prs)
    _set_notes(s3, PROBE_NOTE + " (3장)")
    s4 = prs.slides.add_slide(prs.slide_layouts[5])          # 제목만 + 표 4x3
    s4.shapes.title.text = "표 시험"
    _add_table(s4, prs)
    _set_notes(s4, PROBE_NOTE + " (4장)")
    out = io.BytesIO()
    prs.save(out)
    return out.getvalue()


def find_text_layout(prs: Any) -> Optional[Tuple[Any, int, int, str]]:
    """제목 + 본문 자리표시자가 있는 첫 레이아웃 -> (레이아웃, 제목 idx, 본문 idx, 'L03' 식 이름표)."""
    n = 0
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            n += 1
            title_idx = body_idx = None
            for ph in layout.placeholders:
                t = ph_type_name(ph)
                if title_idx is None and t in TITLE_TYPES:
                    title_idx = ph.placeholder_format.idx
                elif body_idx is None and t in BODY_TYPES:
                    body_idx = ph.placeholder_format.idx
            if title_idx is not None and body_idx is not None:
                return layout, title_idx, body_idx, "L%02d" % n
    return None


def build_template_deck(path: str) -> Tuple[Optional[bytes], Dict[str, Any]]:
    prs, kind = open_presentation(path)
    info = {"converted_from": kind, "removed_existing_slides": drop_all_slides(prs)}
    found = find_text_layout(prs)
    if not found:
        info["layout"] = None
        return None, info
    layout, title_idx, body_idx, label = found
    info["layout"] = label

    def new_slide(title: str) -> Any:
        slide = prs.slides.add_slide(layout)
        slide.placeholders[title_idx].text = title
        return slide

    s1 = new_slide(PROBE_TITLE)
    tf = s1.placeholders[body_idx].text_frame
    tf.text = PROBE_BULLETS[0]
    for line in PROBE_BULLETS[1:]:
        tf.add_paragraph().text = line
    _set_notes(s1, PROBE_NOTE + " (1장)")
    s2 = new_slide("그림 시험")
    s2.placeholders[body_idx].text_frame.text = "본문 칸 옆에 그림을 얹었습니다."
    _add_picture(s2, prs)
    _set_notes(s2, PROBE_NOTE + " (2장)")
    s3 = new_slide("표 시험")
    s3.placeholders[body_idx].text_frame.text = "본문 칸 아래에 표를 얹었습니다."
    _add_table(s3, prs)
    _set_notes(s3, PROBE_NOTE + " (3장)")
    out = io.BytesIO()
    prs.save(out)
    info["slides"] = 3
    return out.getvalue(), info


def try_com_open(path: str) -> Dict[str, Any]:
    """PowerPoint COM 으로 파일을 읽기 전용으로 연다 (창 없이). 이미 떠 있는 PowerPoint 는 닫지 않는다."""
    if not sys.platform.startswith("win"):
        return {"attempted": False, "reason": "Windows 가 아닙니다"}
    try:
        import win32com.client
    except Exception as exc:
        return {"attempted": False, "reason": "pywin32 를 불러오지 못했습니다 (%s)" % type(exc).__name__}
    started_here = False
    app = None
    try:
        try:
            app = win32com.client.GetActiveObject("PowerPoint.Application")
        except Exception:
            app = win32com.client.Dispatch("PowerPoint.Application")
            started_here = True
        pres = app.Presentations.Open(os.path.abspath(path), True, False, False)   # 읽기 전용 · 제목 있음 · 창 없음
        count = int(pres.Slides.Count)
        pres.Close()
        return {"attempted": True, "opened": True, "slides": count}
    except Exception as exc:
        hresult = None
        args = getattr(exc, "args", ())
        if args and isinstance(args[0], int):
            hresult = args[0]
        return {"attempted": True, "opened": False, "error_type": type(exc).__name__, "hresult": hresult}
    finally:
        if started_here and app is not None:
            try:
                app.Quit()
            except Exception:
                pass


def cmd_office(args: argparse.Namespace) -> int:
    say("[KIT-5] Office 열림 점검")
    if args.template and not os.path.isfile(args.template):
        say("템플릿 파일을 찾을 수 없습니다. 경로를 큰따옴표로 감싸 다시 입력해 주세요.")
        return USAGE
    if import_pptx() is None:
        say("python-pptx 를 불러오지 못했습니다. 먼저 KIT-1 (env) 을 통과시켜 주세요.")
        return finish(FAIL)

    stamp = timestamp()
    files = []
    problems = []
    try:
        path = write_new_file(args.results_dir, "probe_" + stamp, ".pptx", build_default_deck())
        files.append({"kind": "default", "name": os.path.basename(path), "slides": 4})
        say("시험 파일 1 (기본 템플릿, 4장): %s" % display_path(path))
    except Exception as exc:
        problems.append("기본 시험 파일을 만들지 못했습니다: " + short_error(exc))
        say(problems[-1])

    template_info = None
    if args.template:
        try:
            data, template_info = build_template_deck(args.template)
            if data is None:
                say("템플릿에 제목+본문 자리표시자가 있는 레이아웃이 없어 시험 파일 2 를 만들지 못했습니다.")
                problems.append("제목+본문 레이아웃 없음")
            else:
                tpath = write_new_file(args.results_dir, "probe_%s_template" % stamp, ".pptx", data)
                files.append({"kind": "template", "name": os.path.basename(tpath), "slides": 3})
                say("시험 파일 2 (회사 템플릿, 3장, 레이아웃 %s): %s" % (template_info["layout"], display_path(tpath)))
        except Exception as exc:
            problems.append("템플릿으로 시험 파일을 만들지 못했습니다 (%s)" % type(exc).__name__)
            say(problems[-1])

    com_results = []
    if args.com:
        for f in files:
            res = try_com_open(os.path.join(args.results_dir, f["name"]))
            res["file"] = f["kind"]
            com_results.append(res)
            if not res.get("attempted"):
                say("COM 열기 (%s): 시도하지 못함 - %s" % (f["kind"], res["reason"]))
            elif res["opened"]:
                say("COM 열기 (%s): 열림 (%d장)" % (f["kind"], res["slides"]))
            else:
                say("COM 열기 (%s): 실패 (%s, 코드 %s)" % (f["kind"], res["error_type"], res["hresult"]))
                problems.append("COM 으로 열지 못했습니다")
        say("COM 이 열었다고 해서 복구 대화상자가 없다는 뜻은 아닙니다. 손으로도 열어 주세요.")

    if files:
        say("")
        say("사람이 할 일 (kit\\env\\README.md 4단계):")
        say("  1. 위 파일을 PowerPoint 로 직접 엽니다 (더블클릭).")
        say("  2. '복구' 대화상자가 떴는지 봅니다.")
        say("  3. 각 장의 한글 제목 · 본문 · 표가 상자 밖으로 넘치는지 봅니다.")
        say("  4. 그림과 노트가 보이는지 봅니다. 그리고 README 의 표에 적습니다.")

    code = FAIL if problems else HUMAN
    if not files:
        code = FAIL
    send_line = "K5 ? ? ?" if files else "K5 - - -"
    record = {"kit": "KIT-5", "subcommand": "office", "kit_version": KIT_VERSION, "time": stamp,
              "files": files, "template_deck": template_info, "com": com_results if args.com else None,
              "problems": problems, "human_check": "PowerPoint 로 직접 열어 복구 대화상자 · 한글 넘침 확인",
              "send_line": send_line, "result": RESULT_LINES[code]}
    rpath = write_result(args.results_dir, "office", record, stamp)
    say("결과 파일: %s" % display_path(rpath))
    if files:
        say("손으로 열어 본 뒤 아래 줄의 ? 세 개를 바꿔 적어 주세요: 판정(G 초록 · Y 노랑 · R 빨강, README 판정 문턱) · "
            "복구 대화상자(없음 0 · 있음 1) · 넘치거나 잘린 장 수.")
    say_send_line(send_line)
    return finish(code)


# ───────────────────────── 입구 ─────────────────────────

def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--results-dir", default=RESULTS_DIR, help="결과 파일 폴더 (기본: kit/results)")
    parser = argparse.ArgumentParser(prog="check_env.py", description="M0 사내 PC 확인 키트 (KIT-1 · KIT-4 · KIT-5)")
    sub = parser.add_subparsers(dest="command", metavar="명령")
    sub.required = True
    sub.add_parser("env", parents=[common], help="KIT-1: Python · pip · 패키지 · COM · LibreOffice")
    p = sub.add_parser("template", parents=[common], help="KIT-4: 템플릿 레이아웃 · 자리표시자 · 지문")
    p.add_argument("paths", nargs="+", metavar="PATH", help=".pptx 또는 .potx (지금 판, 이전 판)")
    p.add_argument("--show-names", action="store_true", help="레이아웃 · 마스터 이름을 결과 파일에만 적는다")
    p = sub.add_parser("office", parents=[common], help="KIT-5: 시험 PPTX 만들기")
    p.add_argument("--template", metavar="PATH", help="회사 템플릿으로도 시험 파일을 만든다")
    p.add_argument("--com", action="store_true", help="Windows + pywin32: PowerPoint COM 으로 열어 본다")
    return parser


COMMANDS = {"env": cmd_env, "template": cmd_template, "office": cmd_office}


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:                      # argparse 는 사용법 오류에 2 로 끝낸다 (--help 는 0)
        return exc.code if isinstance(exc.code, int) else USAGE
    return COMMANDS[args.command](args)


if __name__ == "__main__":
    setup_console()
    sys.exit(main())
