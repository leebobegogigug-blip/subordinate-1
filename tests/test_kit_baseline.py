# -*- coding: utf-8 -*-
"""kit/baseline/trace_numbers.py 시험 - 임시 폴더에 zipfile 로 지어낸 pptx 를 만든다 (python-pptx 없이 돈다)."""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit", "baseline")
sys.path.insert(0, KIT)
import trace_numbers as tn  # noqa: E402

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
LAST_LINES = ("결과: OK", "결과: 확인 필요", "결과: 점검 실패")


def para(text):
    return "<a:p><a:r><a:t>%s</a:t></a:r></a:p>" % escape(text)


def slide_xml(paras, extra=""):
    body = "".join(para(t) for t in paras)
    return ('<?xml version="1.0" encoding="UTF-8"?><p:sld %s><p:cSld><p:spTree>'
            '<p:sp><p:txBody>%s</p:txBody></p:sp>%s</p:spTree></p:cSld></p:sld>' % (NS, body, extra))


def make_pptx(path, slides, notes=None, order=None):
    """slides: 문단 목록의 목록. notes: {슬라이드 번호(1부터): 문단 목록}. order: 발표 순서 (슬라이드 파일 번호)."""
    notes = notes or {}
    order = order or list(range(1, len(slides) + 1))
    with zipfile.ZipFile(path, "w") as zf:
        ids = "".join('<p:sldId id="%d" r:id="rId%d"/>' % (256 + n, n) for n in order)
        zf.writestr("ppt/presentation.xml",
                    '<?xml version="1.0"?><p:presentation %s><p:sldIdLst>%s</p:sldIdLst></p:presentation>' % (NS, ids))
        rels = "".join('<Relationship Id="rId%d" Type="%s/slide" Target="slides/slide%d.xml"/>' % (n, REL, n)
                       for n in range(1, len(slides) + 1))
        zf.writestr("ppt/_rels/presentation.xml.rels",
                    '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>' % rels)
        for i, paras in enumerate(slides, 1):
            zf.writestr("ppt/slides/slide%d.xml" % i, slide_xml(paras))
            if i in notes:
                zf.writestr("ppt/slides/_rels/slide%d.xml.rels" % i,
                            '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                            '<Relationship Id="rId1" Type="%s/notesSlide" Target="../notesSlides/notesSlide%d.xml"/></Relationships>' % (REL, i))
                zf.writestr("ppt/notesSlides/notesSlide%d.xml" % i, slide_xml(notes[i]))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="s1-baseline-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.ref = tn.load_reference(tn.FACTS_DEFAULT)

    def deck(self, slides, name="d.pptx", **kw):
        path = os.path.join(self.tmp, name)
        make_pptx(path, slides, **kw)
        return path

    def run_main(self, *argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = tn.main(list(argv))
        return code, buf.getvalue()

    def raws(self, text):
        return [t.raw for t in tn.extract_tokens(text)]


class ExtractTests(Base):
    def test_formats(self):
        self.assertEqual(self.raws("평균 100.2 nm"), ["100.2"])
        self.assertEqual(self.raws("불량 26 개 · 1,200 장"), ["26", "1,200"])
        self.assertEqual(self.raws("38% 와 2.5 %"), ["38%", "2.5%"])
        self.assertEqual(self.raws("이동 1.5σ · 2 시그마"), ["1.5σ", "2σ"])

    def test_dates(self):
        toks = tn.extract_tokens("2026-10-01 에 10/01 과 10월 3일 그리고 09-30")
        self.assertEqual([t.kind for t in toks], ["date"] * 4)
        self.assertEqual({t.date for t in toks},
                         {(2026, 10, 1), (None, 10, 1), (None, 10, 3), (None, 9, 30)})

    def test_identifiers_not_numbers(self):
        self.assertEqual(self.raws("EQ-03 은 f003 · img3 · PRD_B · P-02 · a01"), [])
        self.assertEqual(self.raws("EQ-03 은 2 lot"), ["2"])

    def test_korean_attached(self):
        self.assertEqual(self.raws("총26개"), ["26"])

    def test_range_not_sign(self):
        self.assertEqual(self.raws("100–103 nm"), ["100", "103"])


class MatchTests(Base):
    def ok(self, text):
        toks = tn.extract_tokens(text)
        self.assertEqual(len(toks), 1, text)
        return tn.matches(toks[0], self.ref)

    def test_exact(self):
        self.assertTrue(self.ok("100.2"))
        self.assertTrue(self.ok("103.0"))        # facts text 안의 USL
        self.assertTrue(self.ok("26"))

    def test_rounding(self):
        self.assertTrue(self.ok("100"))          # 100.2 의 반올림
        self.assertTrue(self.ok("0.2"))          # 0.16 의 반올림
        self.assertFalse(self.ok("100.7"))
        self.assertFalse(self.ok("1.25"))        # 기준 1.2 에 없던 정밀도

    def test_percent(self):
        self.assertTrue(self.ok("38%"))
        self.assertTrue(self.ok("0.38"))         # 38% = 0.38
        self.assertTrue(self.ok("81%"))
        self.assertFalse(self.ok("42%"))

    def test_percent_decimal_of_reference(self):
        # 기준 0.16 → 장표 16% 가 맞는 쪽 (0.16 = 16%)
        self.assertTrue(self.ok("16%"))

    def test_dates(self):
        self.assertTrue(self.ok("2026-09-16"))
        self.assertTrue(self.ok("9/15"))
        self.assertTrue(self.ok("9월 30일"))
        self.assertFalse(self.ok("2026-10-01"))
        self.assertFalse(self.ok("10/01"))
        self.assertFalse(self.ok("2025-09-16"))

    def test_sigma_unmatched(self):
        self.assertFalse(self.ok("2.57σ"))

    def test_derived_unmatched(self):
        self.assertFalse(self.ok("1.3"))         # 101.5 - 100.2 : 계산해 낸 숫자


class CliTests(Base):
    def test_ok(self):
        p = self.deck([["PRD_B 두께가 9/16 부터 +1.2 nm 올랐다", "USL 103.0 nm 초과 2 lot"], ["Residue 38%"]])
        code, out = self.run_main(p)
        self.assertEqual(code, 0)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: OK")
        self.assertIn("슬라이드 1: 찾음 4 · 맞음 4 · 안 맞음 0", out)

    def test_unmatched_counted_and_printed(self):
        p = self.deck([["평균 100.2 nm 이고 2.57σ 이동"], ["수율 97.3%", "26 개"]])
        code, out = self.run_main(p)
        self.assertEqual(code, 3)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: 확인 필요")
        self.assertIn("안 맞음 1 (안 맞는 숫자: 2.57σ)", out)
        self.assertIn("97.3%", out)
        self.assertIn("합계: 슬라이드 2 · 찾음 4 · 맞음 2 · 안 맞음(지어낸 것 후보) 2", out)
        self.assertIn("G2 비율: 50%", out)

    def test_share_ok_but_unmatched_is_check(self):
        # 5개 중 4개 맞음 (80%) 이어도 안 맞는 숫자가 있으면 확인 필요
        p = self.deck([["100.2 1.2 26 38% 999"]])
        code, out = self.run_main(p)
        self.assertEqual(code, 3)
        self.assertIn("G2 비율: 80%", out)

    def test_no_numbers(self):
        p = self.deck([["숫자 없는 장표"]])
        code, out = self.run_main(p)
        self.assertEqual(code, 3)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: 확인 필요")

    def test_unreadable(self):
        bad = os.path.join(self.tmp, "bad.pptx")
        with open(bad, "w") as f:
            f.write("not a zip")
        code, out = self.run_main(bad)
        self.assertEqual(code, 1)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: 점검 실패")
        code, out = self.run_main(os.path.join(self.tmp, "missing.pptx"))
        self.assertEqual(code, 1)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: 점검 실패")

    def test_interview_numbers(self):
        p = self.deck([["PRD_B 10 lot 추가 측정"]])
        code, out = self.run_main(p)
        self.assertEqual(code, 3)
        iv = os.path.join(os.path.dirname(tn.FACTS_DEFAULT), "interview_lite.json")
        code, out = self.run_main(p, "--interview", iv)
        self.assertEqual(code, 0)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: OK")

    def test_bad_facts(self):
        p = self.deck([["100.2"]])
        code, out = self.run_main(p, "--facts", os.path.join(self.tmp, "none.json"))
        self.assertEqual(code, 1)
        self.assertEqual(out.rstrip().splitlines()[-1], "결과: 점검 실패")

    def test_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                self.run_main()
        self.assertEqual(cm.exception.code, 2)

    def test_slide_order_follows_presentation(self):
        p = self.deck([["999"], ["100.2"]], order=[2, 1])
        slides = tn.read_deck(p, False)
        self.assertEqual(slides[0], ["100.2"])

    def test_notes_optional(self):
        p = self.deck([["100.2"]], notes={1: ["메모 7.77"]})
        _, out = self.run_main(p)
        self.assertIn("찾음 1", out)
        _, out = self.run_main(p, "--notes")
        self.assertIn("찾음 2", out)
        self.assertIn("7.77", out)

    def test_slide_number_field_skipped(self):
        fld = '<a:p><a:fld id="{1}" type="slidenum"><a:t>7</a:t></a:fld></a:p>'
        ph = ('<p:sp><p:nvSpPr><p:nvPr><p:ph type="sldNum"/></p:nvPr></p:nvSpPr>'
              '<p:txBody><a:p><a:r><a:t>8</a:t></a:r></a:p></p:txBody></p:sp>')
        xml = slide_xml(["100.2"], extra="<p:sp><p:txBody>%s</p:txBody></p:sp>%s" % (fld, ph))
        texts = [t for t in tn.paragraph_texts(xml.encode("utf-8")) if t.strip()]
        self.assertEqual(texts, ["100.2"])

    def test_no_slide_text_printed(self):
        secret = "비밀문장 알파 브라보 PRD_B 두께 100.2 nm 7.77"
        p = self.deck([[secret]])
        _, out = self.run_main(p)
        for word in ("비밀문장", "알파", "브라보", "PRD_B", "두께"):
            self.assertNotIn(word, out)
        self.assertIn("7.77", out)

    def test_read_only(self):
        p = self.deck([["100.2 7.77"]])
        with open(p, "rb") as f:
            before = f.read()
        before_files = sorted(os.listdir(self.tmp))
        self.run_main(p)
        with open(p, "rb") as f:
            self.assertEqual(f.read(), before)
        self.assertEqual(sorted(os.listdir(self.tmp)), before_files)

    def test_last_line_always_known(self):
        for slides in ([["100.2"]], [["7.77"]], [["없음"]]):
            _, out = self.run_main(self.deck(slides, name="x.pptx"))
            self.assertIn(out.rstrip().splitlines()[-1], LAST_LINES)


if __name__ == "__main__":
    unittest.main()
