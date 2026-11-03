// readme_pages.mjs — README 그림을 다시 그리는 개발 도구 (Node)
//
// 실행에는 필요 없다. docs/images/src/*.html 을 라이트 · 다크 두 테마로 열어
// docs/images/page/<이름>-dark.png · <이름>-light.png 로 찍는다 (배율 2 — 폭 880 이면 1760 픽셀).
//
//   node tools/readme_pages.mjs                전부 다시 그린다
//   node tools/readme_pages.mjs hero title     이름을 준 것만 (docs/images/src/<이름>.html)
//
// 필요한 것
//   · Node 18 이상 · playwright 패키지 (npm i -D playwright 또는 전역 설치) · Chromium (npx playwright install chromium)
//   · 글꼴 GNU Unifont (otf). 저장소에 넣지 않는다 — 이 PC 에서 찾아 쓴다.
//     찾는 자리: 환경 변수 UNIFONT_OTF → /usr/share/fonts/opentype/unifont/unifont.otf → /usr/share/fonts/truetype/unifont/unifont.ttf
//               → C:\Windows\Fonts\unifont.otf → ~/.fonts/unifont.otf. 다른 곳에 있으면 UNIFONT_OTF 에 파일 경로를 적는다.
//   · 출력 폴더를 바꾸려면 README_PAGES_OUT (시험 그림을 저장소 밖에 찍어 볼 때)
//
// 네트워크를 쓰지 않는다 (file:// 만 연다). 밑줄(_)로 시작하는 파일 (_base.css · _sprite.js) 은 공용 조각이라 그리지 않는다.
// 글이 칸을 넘치면 (data-fit 표시가 있는 곳) 그리지 않고 멈춘다 — 줄이거나 칸을 넓힌다.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SRC = path.join(ROOT, "docs", "images", "src");
const OUT = process.env.README_PAGES_OUT ? path.resolve(process.env.README_PAGES_OUT) : path.join(ROOT, "docs", "images", "page");
const THEMES = ["dark", "light"];
const SCALE = 2;

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch {
    try {
      return createRequire(import.meta.url)("playwright");   // 전역 설치 (NODE_PATH) 는 require 로만 보인다
    } catch {
      fail("playwright 를 찾지 못했습니다. npm i -D playwright (또는 전역 설치) 한 뒤 npx playwright install chromium 을 하세요.");
    }
  }
}

function fail(msg) {
  console.error("실패: " + msg);
  process.exit(1);
}

function findFont() {
  const home = os.homedir();
  if (process.env.UNIFONT_OTF && !fs.existsSync(process.env.UNIFONT_OTF)) {
    fail(`UNIFONT_OTF 의 글꼴 파일이 없습니다: ${process.env.UNIFONT_OTF}`);
  }
  const candidates = [
    process.env.UNIFONT_OTF,
    "/usr/share/fonts/opentype/unifont/unifont.otf",
    "/usr/share/fonts/truetype/unifont/unifont.ttf",
    "C:\\Windows\\Fonts\\unifont.otf",
    path.join(home, ".fonts", "unifont.otf"),
  ].filter(Boolean);
  for (const c of candidates) if (fs.existsSync(c)) return path.resolve(c);
  fail("GNU Unifont 글꼴을 찾지 못했습니다. UNIFONT_OTF 에 unifont.otf 경로를 적으세요 (https://unifoundry.com/unifont/).");
}

function pickNames() {
  const asked = process.argv.slice(2);
  const all = fs.readdirSync(SRC).filter((f) => f.endsWith(".html") && !f.startsWith("_")).map((f) => f.slice(0, -5)).sort();
  if (!asked.length) return all;
  for (const n of asked) if (!fs.existsSync(path.join(SRC, n + ".html"))) fail(`원본이 없습니다: docs/images/src/${n}.html`);
  return asked;
}

async function main() {
  const names = pickNames();
  if (!names.length) fail("그릴 원본이 없습니다 (docs/images/src/*.html).");
  const font = findFont();
  const { chromium } = await loadPlaywright();
  fs.mkdirSync(OUT, { recursive: true });
  const fontFace =
    `@font-face{font-family:"UnifontPage";src:url("${pathToFileURL(font).href}") format("opentype");font-display:block}`;

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 1600 }, deviceScaleFactor: SCALE });
  page.on("pageerror", (e) => fail(`페이지 오류: ${e.message}`));
  page.on("requestfailed", (r) => {
    if (!r.url().startsWith("data:")) fail(`불러오지 못했습니다: ${r.url()}`);
  });
  let bytes = 0;
  try {
    for (const name of names) {
      for (const theme of THEMES) {
        await page.goto(pathToFileURL(path.join(SRC, name + ".html")).href);
        await page.addStyleTag({ content: fontFace });
        await page.evaluate(async (t) => {
          document.documentElement.dataset.theme = t;
          await document.fonts.load('16px "UnifontPage"');
          await document.fonts.ready;
        }, theme);
        const cut = await page.evaluate(() =>
          [...document.querySelectorAll("[data-fit]")]
            .filter((e) => e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1)
            .map((e) => (e.textContent || "").trim().slice(0, 40)));
        if (cut.length) fail(`${name}-${theme}: 글이 칸을 넘칩니다 → ${JSON.stringify(cut)}`);
        const out = path.join(OUT, `${name}-${theme}.png`);
        await page.locator("#cap").screenshot({ path: out, type: "png", animations: "disabled" });
        const size = fs.statSync(out).size;
        bytes += size;
        console.log(`${path.relative(ROOT, out)} · ${(size / 1024).toFixed(0)} KB`);
      }
    }
  } finally {
    await browser.close();
  }
  console.log(`합계 ${(bytes / 1024).toFixed(0)} KB · 그림 ${names.length * THEMES.length}장`);
}

main().catch((e) => fail(e && e.stack ? e.stack : String(e)));
