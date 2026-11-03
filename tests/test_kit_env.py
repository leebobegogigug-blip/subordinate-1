# -*- coding: utf-8 -*-
"""kit/env/check_env.py 시험 - 임시 폴더에 지어낸 자료만 쓴다 (회사 자료 없음, 이진 고정 자료 없음)."""
import contextlib
import io
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit", "env"))
import check_env  # noqa: E402

try:
    import pptx  # noqa: F401
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False

NEEDS_PPTX = unittest.skipUnless(HAS_PPTX, "python-pptx 가 없으면 건너뜀 — CI 는 설치해서 돌린다")
COMPANY_LAYOUT = "AcmeCompanyLayout"       # 지어낸 '회사 이름이 든 레이아웃 이름'


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="kit_env_")
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.results = os.path.join(self.dir, "results")

    def run_main(self, *argv):
        """(종료 코드, 화면 출력) - 결과 파일은 임시 폴더로 보낸다."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = check_env.main(list(argv) + ["--results-dir", self.results])
        return code, buf.getvalue()

    def result_json(self):
        names = sorted(n for n in os.listdir(self.results) if n.endswith(".json"))
        with open(os.path.join(self.results, names[-1]), encoding="utf-8") as f:
            return json.load(f)


class PureParts(Sandbox):
    def test_png_signature_and_ihdr(self):
        data = check_env.make_png(40, 24)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        length, tag = struct.unpack(">I4s", data[8:16])
        self.assertEqual((length, tag), (13, b"IHDR"))
        width, height, depth, ctype = struct.unpack(">IIBB", data[16:26])
        self.assertEqual((width, height, depth, ctype), (40, 24, 8, 2))
        self.assertEqual(data[-12:-8], struct.pack(">I", 0))
        self.assertEqual(data[-8:-4], b"IEND")
        # IDAT 를 풀면 (1 + 3*폭) * 높이 바이트
        pos, idat = 8, b""
        while pos < len(data):
            n, t = struct.unpack(">I4s", data[pos:pos + 8])
            if t == b"IDAT":
                idat += data[pos + 8:pos + 8 + n]
            crc = struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0]
            self.assertEqual(crc, zlib.crc32(data[pos + 4:pos + 8 + n]) & 0xFFFFFFFF)
            pos += 12 + n
        self.assertEqual(len(zlib.decompress(idat)), (1 + 3 * 40) * 24)

    def test_mask_home_windows_style(self):
        home = "C:\\Users\\kim"
        tok = "%USERPROFILE%"
        self.assertEqual(check_env.mask_text("C:\\Users\\kim\\a\\b.pptx", [home], tok), "%USERPROFILE%\\a\\b.pptx")
        self.assertEqual(check_env.mask_text("c:/users/KIM/x", [home], tok), "%USERPROFILE%/x")
        self.assertEqual(check_env.mask_text("C:\\Users\\kim2\\x", [home], tok), "C:\\Users\\kim2\\x")
        self.assertEqual(check_env.mask_text("D:\\work\\x", [home], tok), "D:\\work\\x")

    def test_mask_home_posix_and_nested(self):
        masked = check_env.mask_obj({"a": ["/home/lee/x", {"b": "see /home/lee"}], "n": 3}, ["/home/lee"], "~")
        self.assertEqual(masked, {"a": ["~/x", {"b": "see ~"}], "n": 3})

    def test_mask_ignores_tiny_roots(self):
        self.assertEqual(check_env.mask_text("/usr/bin", ["/"], "~"), "/usr/bin")

    def test_unique_path_never_overwrites(self):
        first = check_env.write_new_file(self.results, "probe_x", ".json", b"1")
        second = check_env.write_new_file(self.results, "probe_x", ".json", b"2")
        third = check_env.write_new_file(self.results, "probe_x", ".json", b"3")
        self.assertEqual(len({first, second, third}), 3)
        with open(first, "rb") as f:
            self.assertEqual(f.read(), b"1")
        self.assertTrue(second.endswith("probe_x_2.json"))

    def test_rewrite_main_content_type(self):
        xml = ('<?xml version="1.0"?><Types xmlns="x"><Default Extension="xml" ContentType="application/xml"/>'
               '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.'
               'presentationml.template.main+xml"/><Override PartName="/ppt/slides/slide1.xml" ContentType="a/b"/></Types>')
        new, kind = check_env.rewrite_main_content_type(xml.encode("utf-8"))
        self.assertEqual(kind, "template")
        self.assertIn(b"presentationml.presentation.main+xml", new)
        self.assertNotIn(b"template.main", new)
        self.assertIn(b'ContentType="a/b"', new)          # 다른 항목은 그대로
        again, kind2 = check_env.rewrite_main_content_type(new)
        self.assertIsNone(kind2)
        self.assertEqual(again, new)

    def test_rewrite_attribute_order_and_macro(self):
        xml = (b"<Types><Override ContentType='application/vnd.ms-powerpoint.presentation.macroEnabled.main+xml' "
               b"PartName='/ppt/presentation.xml'/></Types>")
        new, kind = check_env.rewrite_main_content_type(xml)
        self.assertEqual(kind, "macro")
        self.assertIn(b"presentationml.presentation.main+xml", new)

    def test_classify(self):
        self.assertTrue(check_env.usable_layout(["TITLE", "BODY", "DATE"]))
        self.assertTrue(check_env.usable_layout(["CENTER_TITLE", "PICTURE"]))
        self.assertFalse(check_env.usable_layout(["TITLE", "DATE"]))
        self.assertFalse(check_env.usable_layout(["BODY", "OBJECT"]))

    def test_diff_layouts_synthetic(self):
        def lay(label, s, g=None):
            return {"label": label, "structure": s, "geometry": g or s + "g"}
        a = [lay("L01", "x"), lay("L02", "y"), lay("L03", "z"), lay("L04", "q")]
        b = [lay("L01", "x"), lay("L02", "z"), lay("L03", "y", "y-moved"), lay("L04", "w"), lay("L05", "n")]
        d = check_env.diff_layouts(a, b)
        self.assertEqual(d["same"], [["L01", "L01"], ["L03", "L02"]])        # 순서가 바뀌어도 구조로 맞춘다
        self.assertEqual(d["geometry_only"], [["L02", "L03"]])
        self.assertEqual(d["changed"], [["L04", "L04"]])
        self.assertEqual(d["added"], ["L05"])
        self.assertEqual(d["removed"], [])
        self.assertEqual(check_env.diff_layouts(a, a)["same"], [[x["label"], x["label"]] for x in a])

    def test_parse_pins(self):
        text = "# 설명\npython-pptx==1.0.2  # 끝 주석\npywin32==311; sys_platform == \"win32\"\nfoo>=1\n"
        pins = check_env.parse_pins(text)
        self.assertEqual(pins["python-pptx"], "1.0.2")
        self.assertEqual("pywin32" in pins, sys.platform.startswith("win"))
        self.assertNotIn("foo", pins)

    def test_probe_file_lists_every_package(self):
        # 시험 목록은 판을 고정하지 않는다 (사내 Python 에 맞는 판을 pip 가 고른다). 이름은 빠짐없이 있어야 한다.
        path = os.path.join(os.path.dirname(check_env.__file__), "requirements-probe.txt")
        with open(path, encoding="utf-8") as fh:
            names = [re.split(r"[ ;=<>!~\[]", ln.strip(), 1)[0].lower()
                     for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]
        for pip_name, _mod, _req in check_env.PROBE_PACKAGES:
            self.assertIn(pip_name.lower(), names)

    def test_pywin32_is_optional(self):
        flags = {name: req for name, _mod, req in check_env.PROBE_PACKAGES}
        self.assertFalse(check_env.required_here(flags["pywin32"]))
        self.assertTrue(check_env.windows_only(flags["pywin32"]))


class Commands(Sandbox):
    def test_usage_errors_return_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check_env.main([]), 2)
            self.assertEqual(check_env.main(["nothing"]), 2)
            self.assertEqual(check_env.main(["template"]), 2)
        code, out = self.run_main("template", os.path.join(self.dir, "없는파일.pptx"))
        self.assertEqual(code, 2)
        self.assertNotIn("결과:", out)
        code, _out = self.run_main("office", "--template", os.path.join(self.dir, "없는파일.pptx"))
        self.assertEqual(code, 2)

    def test_env_exit_code_matches_last_line(self):
        code, out = self.run_main("env")
        self.assertEqual(out.rstrip("\n").splitlines()[-1], check_env.RESULT_LINES[code])
        self.assertIn(code, (0, 1))
        record = self.result_json()
        self.assertEqual(record["kit"], "KIT-1")
        self.assertEqual(record["result"], check_env.RESULT_LINES[code])

    def test_env_ok_and_fail_paths(self):
        fake_pip = {"ok": True, "version": "9.9", "error": None}
        with mock.patch.object(check_env, "check_pip", return_value=fake_pip):
            with mock.patch.object(check_env, "PROBE_PACKAGES", [("json", "json", True)]):
                code, out = self.run_main("env")
            self.assertEqual((code, out.splitlines()[-1]), (0, "결과: OK"))
            with mock.patch.object(check_env, "PROBE_PACKAGES", [("nopkg", "no_such_module_zz", True)]):
                code, out = self.run_main("env")
            self.assertEqual((code, out.splitlines()[-1]), (1, "결과: 점검 실패"))
            self.assertIn("nopkg", out)
        with mock.patch.object(check_env, "check_pip", return_value={"ok": False, "version": None, "error": "x"}):
            with mock.patch.object(check_env, "PROBE_PACKAGES", [("json", "json", True)]):
                code, _out = self.run_main("env")
        self.assertEqual(code, 1)

    def test_env_result_has_no_home_path(self):
        self.run_main("env")
        path = os.path.join(self.results, sorted(os.listdir(self.results))[-1])
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        for home in check_env.home_dirs():
            if len(home) > 3:
                self.assertNotIn(home, raw)


@NEEDS_PPTX
class WithPptx(Sandbox):
    def make_pptx(self, name, mutate=None, template=False):
        from pptx import Presentation
        prs = Presentation()
        if mutate:
            mutate(prs)
        path = os.path.join(self.dir, name)
        buf = io.BytesIO()
        prs.save(buf)
        if template:
            with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as zin, zipfile.ZipFile(path, "w") as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename == "[Content_Types].xml":
                        data = data.replace(b"presentationml.presentation.main+xml", b"presentationml.template.main+xml")
                    zout.writestr(item, data)
        else:
            with open(path, "wb") as f:
                f.write(buf.getvalue())
        return path

    @staticmethod
    def rename_layout(prs):
        prs.slide_layouts[2].name = COMPANY_LAYOUT

    @staticmethod
    def drop_title_placeholder(prs):
        ph = prs.slide_layouts[3].placeholders[0]
        ph._element.getparent().remove(ph._element)

    @staticmethod
    def move_placeholder(prs):
        ph = prs.slide_layouts[1].placeholders[1]
        ph.left = ph.left + 720000

    def test_potx_opens_after_rewrite(self):
        path = self.make_pptx("acme_template.potx", template=True)
        prs, kind = check_env.open_presentation(path)
        self.assertEqual(kind, "template")
        self.assertEqual(len(prs.slide_layouts), 11)
        # 원본은 건드리지 않는다
        with zipfile.ZipFile(path) as z:
            self.assertIn(b"template.main", z.read("[Content_Types].xml"))
        plain = self.make_pptx("plain.pptx")
        self.assertIsNone(check_env.open_presentation(plain)[1])

    def test_fingerprint_stable_and_detects_difference(self):
        a1 = check_env.inspect_presentation(check_env.open_presentation(self.make_pptx("a1.pptx"))[0], False)
        a2 = check_env.inspect_presentation(check_env.open_presentation(self.make_pptx("a2.pptx"))[0], False)
        self.assertEqual(a1["deck_structure_fingerprint"], a2["deck_structure_fingerprint"])
        self.assertEqual(a1["deck_geometry_fingerprint"], a2["deck_geometry_fingerprint"])
        renamed = check_env.inspect_presentation(
            check_env.open_presentation(self.make_pptx("r.pptx", self.rename_layout))[0], False)
        self.assertEqual(a1["deck_structure_fingerprint"], renamed["deck_structure_fingerprint"])   # 이름은 지문에 안 든다
        dropped = check_env.inspect_presentation(
            check_env.open_presentation(self.make_pptx("d.pptx", self.drop_title_placeholder))[0], False)
        self.assertNotEqual(a1["deck_structure_fingerprint"], dropped["deck_structure_fingerprint"])
        diff = check_env.diff_layouts(a1["layouts"], dropped["layouts"])
        self.assertEqual(diff["changed"], [["L04", "L04"]])
        moved = check_env.inspect_presentation(
            check_env.open_presentation(self.make_pptx("m.pptx", self.move_placeholder))[0], False)
        self.assertEqual(a1["deck_structure_fingerprint"], moved["deck_structure_fingerprint"])
        self.assertNotEqual(a1["deck_geometry_fingerprint"], moved["deck_geometry_fingerprint"])
        self.assertEqual(check_env.diff_layouts(a1["layouts"], moved["layouts"])["geometry_only"], [["L02", "L02"]])

    def test_template_console_has_no_names(self):
        a = self.make_pptx("acme_secret_a.pptx", self.rename_layout)
        b = self.make_pptx("acme_secret_b.potx", self.drop_title_placeholder, template=True)
        code, out = self.run_main("template", a, b)
        self.assertEqual((code, out.splitlines()[-1]), (0, "결과: OK"))
        self.assertNotIn(COMPANY_LAYOUT.lower(), out.lower())
        self.assertNotIn("acme", out.lower())
        self.assertIn("L01", out)
        self.assertIn("구조 바뀜", out)
        with open(os.path.join(self.results, os.listdir(self.results)[0]), encoding="utf-8") as f:
            self.assertNotIn(COMPANY_LAYOUT, f.read())

    def test_show_names_goes_to_file_only(self):
        a = self.make_pptx("acme_secret_a.pptx", self.rename_layout)
        code, out = self.run_main("template", a, "--show-names")
        self.assertEqual(code, 0)
        self.assertNotIn(COMPANY_LAYOUT, out)
        self.assertIn(COMPANY_LAYOUT, json.dumps(self.result_json(), ensure_ascii=False))

    def test_template_open_failure_is_exit_1(self):
        bad = os.path.join(self.dir, "broken.pptx")
        with open(bad, "wb") as f:
            f.write(b"not a zip")
        code, out = self.run_main("template", bad)
        self.assertEqual((code, out.splitlines()[-1]), (1, "결과: 점검 실패"))

    def test_template_without_usable_layout_needs_human(self):
        def strip_bodies(prs):
            for layout in prs.slide_layouts:
                for ph in list(layout.placeholders):
                    if ph.placeholder_format.type is not None and ph.placeholder_format.type.name in check_env.BODY_TYPES + ("PICTURE",):
                        ph._element.getparent().remove(ph._element)
        code, out = self.run_main("template", self.make_pptx("nobody.pptx", strip_bodies))
        self.assertEqual((code, out.splitlines()[-1]), (3, "결과: 확인 필요"))

    def test_office_builds_probe_and_never_overwrites(self):
        from pptx import Presentation
        with mock.patch.object(check_env, "timestamp", return_value="20000101_000000"):
            code1, out1 = self.run_main("office")
            code2, _out2 = self.run_main("office")
        self.assertEqual((code1, out1.splitlines()[-1]), (3, "결과: 확인 필요"))
        self.assertEqual(code2, 3)
        decks = sorted(n for n in os.listdir(self.results) if n.endswith(".pptx"))
        self.assertEqual(decks, ["probe_20000101_000000.pptx", "probe_20000101_000000_2.pptx"])
        prs = Presentation(os.path.join(self.results, decks[0]))
        self.assertEqual(len(prs.slides), 4)
        for slide in prs.slides:
            self.assertTrue(slide.has_notes_slide)
            self.assertTrue(slide.notes_slide.notes_text_frame.text)
        self.assertTrue(any(s.shape_type == 13 for s in prs.slides[2].shapes))     # 그림
        self.assertTrue(any(s.has_table for s in prs.slides[3].shapes))            # 표
        table = [s for s in prs.slides[3].shapes if s.has_table][0].table
        self.assertEqual((len(table.rows), len(table.columns)), (4, 3))
        self.assertGreater(len(prs.slides[0].shapes.title.text), 40)

    def test_office_with_template_uses_title_body_layout(self):
        from pptx import Presentation
        tpl = self.make_pptx("acme_tpl.potx", self.rename_layout, template=True)
        code, out = self.run_main("office", "--template", tpl)
        self.assertEqual((code, out.splitlines()[-1]), (3, "결과: 확인 필요"))
        self.assertNotIn("acme", out.lower())
        self.assertNotIn(COMPANY_LAYOUT, out)
        deck = [n for n in os.listdir(self.results) if n.endswith("_template.pptx")]
        self.assertEqual(len(deck), 1)
        prs = Presentation(os.path.join(self.results, deck[0]))
        self.assertEqual(len(prs.slides), 3)
        self.assertTrue(all(s.has_notes_slide for s in prs.slides))

    def test_office_com_off_windows_does_not_fail(self):
        if sys.platform.startswith("win"):
            self.skipTest("Windows 에서는 실제 PowerPoint 를 부르므로 건너뜀")
        code, out = self.run_main("office", "--com")
        self.assertEqual(code, 3)
        self.assertIn("시도하지 못함", out)


if __name__ == "__main__":
    unittest.main()
