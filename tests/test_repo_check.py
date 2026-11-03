# -*- coding: utf-8 -*-
"""tools/repo_check.py 시험 - 임시 폴더에 지어낸 파일만 쓴다 (실데이터 없음)."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import repo_check  # noqa: E402

# 시험용 가짜 값은 실행할 때 조립한다 - 이 소스 자체가 검사에 걸리지 않게
FAKE_SK = "sk-" + "a1B2c3D4" * 4
FAKE_AWS = "AKIA" + "ABCDEFGH12345678"
FAKE_PW = "pw" + "x9" * 12
PRIVATE_IP = ".".join(["192", "168", "0", "7"])


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="repo_check_")
        self.addCleanup(shutil.rmtree, self.dir, True)

    def put(self, rel, content=b"x"):
        path = os.path.join(self.dir, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = content.encode("utf-8") if isinstance(content, str) else content
        with open(path, "wb") as f:
            f.write(data)

    def run_check(self, *flags):
        """(종료 코드, 출력 전체) - 임시 폴더는 git 저장소가 아니라 폴더 걷기로 돈다."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = repo_check.main(["--root", self.dir] + list(flags))
        return code, buf.getvalue()


class FindingTypes(Sandbox):
    def test_clean_repo_is_ok(self):
        self.put("README.md", "안녕하세요. 127.0.0.1 에서만 돕니다.\n")
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[-1], "결과: OK")

    def test_sk_key(self):
        self.put("a.txt", "key = %s\n" % FAKE_SK)
        _, out = self.run_check()
        self.assertIn("a.txt:1", out)
        self.assertIn("sk- 식 키", out)

    def test_aws_key(self):
        self.put("a.txt", "x\n%s\n" % FAKE_AWS)
        _, out = self.run_check()
        self.assertIn("a.txt:2", out)
        self.assertIn("AWS 키", out)

    def test_private_key_header(self):
        self.put("k.txt", "-----BEGIN " + "RSA PRIVATE KEY-----\n")
        _, out = self.run_check()
        self.assertIn("개인 키 머리말", out)

    def test_assignment_with_long_value(self):
        self.put("c.json", '{"api_key": "%s"}\n' % FAKE_PW)
        self.put("d.py", 'password = "%s"\n' % FAKE_PW)
        _, out = self.run_check()
        self.assertIn("c.json:1", out)
        self.assertIn("d.py:1", out)

    def test_short_value_and_reference_are_fine(self):
        self.put("c.json", '{"api_key": "{env:SUBORDINATE_LLM_KEY_NAME}", "token": "short"}\n')
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0, out)

    def test_private_ipv4_ranges(self):
        lines = ["10.1.2.3", "172.16.0.1", "172.31.255.1", PRIVATE_IP]  # repo-check: allow (지어낸 주소)
        self.put("n.md", "\n".join("서버 " + ip for ip in lines) + "\n")
        _, out = self.run_check()
        for no in (1, 2, 3, 4):
            self.assertIn("n.md:%d" % no, out)

    def test_loopback_and_public_ranges_are_fine(self):
        self.put("n.md", "127.0.0.1\n172.32.0.1\n8.8.8.8\n1.10.1.2.3\n")
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0, out)

    def test_ip_is_not_printed_in_full(self):
        self.put("n.md", PRIVATE_IP + "\n")
        _, out = self.run_check()
        self.assertNotIn(PRIVATE_IP, out)

    def test_data_files_outside_allowed_folders(self):
        names = ["a.pptx", "b.potx", "c.ppt", "d.xlsx", "e.xls", "f.csv", "g.png", "h.jpg", "i.JPEG", "sub/j.csv"]
        for n in names:
            self.put(n)
        _, out = self.run_check()
        for n in names:
            self.assertIn(n, out)
        self.assertEqual(out.count("[파일 종류]"), len(names))


class AllowedFolders(Sandbox):
    def test_fixture_folders_are_allowed(self):
        for rel in ("tests/fixtures/a.csv", "tests/fixtures/deep/b.pptx", "kit/llm/synthetic/c.png",
                    "kit/synthetic/d.xlsx", "docs/images/e.png", "docs/images/f.jpeg"):
            self.put(rel)
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0, out)

    def test_docs_images_allows_pictures_only(self):
        self.put("docs/images/real.pptx")
        self.put("docs/images/data.csv")
        _, out = self.run_check()
        self.assertEqual(out.count("[파일 종류]"), 2)

    def test_lookalike_folders_are_not_allowed(self):
        for rel in ("tests/fixtures_old/a.csv", "kit/results/a.csv", "synthetic/a.csv", "kit/a.csv",
                    "docs/image/a.png"):
            self.put(rel)
        _, out = self.run_check()
        self.assertEqual(out.count("[파일 종류]"), 5)

    def test_text_scan_still_runs_inside_allowed_folders(self):
        self.put("tests/fixtures/notes.txt", "key %s\n" % FAKE_SK)
        _, out = self.run_check()
        self.assertIn("tests/fixtures/notes.txt:1", out)


class MaskingAndMarker(Sandbox):
    def test_secret_values_never_appear_in_output(self):
        self.put("a.txt", "%s\n%s\n" % (FAKE_SK, FAKE_AWS))
        self.put("b.json", '{"password": "%s"}\n' % FAKE_PW)
        _, out = self.run_check("--strict")
        for secret in (FAKE_SK, FAKE_AWS, FAKE_PW):
            self.assertNotIn(secret, out)
            self.assertNotIn(secret[4:], out)
        self.assertIn("sk***(%d자)" % len(FAKE_SK), out)

    def test_mask_short_values(self):
        self.assertEqual(repo_check.mask("abc"), "***")
        self.assertEqual(repo_check.mask("abcdef"), "ab***(6자)")

    def test_allow_marker_skips_that_line_only(self):
        self.put("t.py", "A = '%s'  # repo-check: allow\nB = '%s'\n" % (FAKE_SK, FAKE_SK))
        _, out = self.run_check()
        self.assertNotIn("t.py:1", out)
        self.assertIn("t.py:2", out)

    def test_allow_marker_does_not_excuse_file_kind(self):
        self.put("secret.csv", "a,b  # repo-check: allow\n")
        _, out = self.run_check()
        self.assertIn("secret.csv", out)


class ExitCodes(Sandbox):
    def test_default_mode_reports_but_exits_zero(self):
        self.put("a.csv")
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[-1], "결과: 확인 필요")

    def test_strict_mode_exits_one(self):
        self.put("a.csv")
        code, out = self.run_check("--strict")
        self.assertEqual(code, 1)
        self.assertEqual(out.strip().splitlines()[-1], "결과: 점검 실패")

    def test_usage_error_exits_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                repo_check.main(["--no-such-flag"])
        self.assertEqual(cm.exception.code, 2)

    def test_missing_root_exits_two(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = repo_check.main(["--root", os.path.join(self.dir, "없는폴더")])
        self.assertEqual(code, 2)

    def test_binary_and_large_text_are_not_scanned(self):
        self.put("blob.bin", b"\0\0" + FAKE_SK.encode("ascii"))
        self.put("big.txt", (FAKE_SK + "\n").encode("ascii") * (repo_check.MAX_TEXT_BYTES // 20))
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0, out)


@unittest.skipUnless(shutil.which("git"), "git 이 없음")
class GitMode(Sandbox):
    def git(self, *args):
        subprocess.run(["git", "-C", self.dir] + list(args), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def test_git_list_skips_ignored_and_all_files_does_not(self):
        self.git("init", "-q")
        self.put(".gitignore", "ignored.csv\n")
        self.put("ignored.csv")
        self.put("new.pptx")
        _, out = self.run_check()
        self.assertIn("new.pptx", out)
        self.assertNotIn("ignored.csv", out)
        _, out_all = self.run_check("--all-files")
        self.assertIn("ignored.csv", out_all)


if __name__ == "__main__":
    unittest.main()
