#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_inputs.py - M0 KIT-2 · KIT-3 합성 입력 만들기 (개발 쪽 전용 · 사내 PC 에서는 돌리지 않는다)

  python kit/llm/make_inputs.py      kit/llm/synthetic/ 에 그림 · truth.json · facts_lite.json · interview_lite.json 을 쓴다

[의존] matplotlib · numpy (이 스크립트만). 사내 PC 에서 도는 score.py 는 표준 라이브러리만 쓴다.
[결정적] 씨앗 SEED 고정. 쓴 matplotlib · numpy 판을 truth.json 의 generator 에 적는다.
[합성] 이름 · 숫자는 모두 지어낸 것이다 (RULES.md › W-12). 제품 PRD_A · PRD_B, 설비 EQ-01–EQ-04.
[정답] 정답은 그린 데이터에서 계산하고, 구간 경계에 가까우면 멈춘다 (assert) - 애매한 문제를 내지 않으려는 것이다.
"""
import datetime as dt
import hashlib
import json
import os
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

SEED = 20261103
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "synthetic")

# works DESIGN.md 팔레트 (W-10 · 빨강 없음)
NAVY, NAVY2, NAVY4 = "#002341", "#1F507A", "#75A1C7"
LIME, LIME1 = "#6ABA23", "#45741B"
GRAY1, GRAY2, GRAY, GRAY4 = "#5C6166", "#81888D", "#A5AAAE", "#D4D6D8"
CODE_CHARS = "ACDEFHJKLMNPRTUVWXY34679"       # 헷갈리는 글자 (O 0 I 1 B 8 S 5 Z 2 G Q) 를 뺐다

rng = np.random.default_rng(SEED)


def save(fig, name, dpi=100):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, metadata={"Software": None})
    plt.close(fig)
    return name


def days(start, n):
    d0 = dt.date.fromisoformat(start)
    return [d0 + dt.timedelta(days=i) for i in range(n)]


def trunc_normal(n, sigma, clip):
    """잘린 정규 잡음 - 정상 점이 문턱선 근처에 오지 않게 한다."""
    out = rng.normal(0.0, sigma, n)
    return np.clip(out, -clip * sigma, clip * sigma)


def date_axis(ax, dates, step=7):
    idx = list(range(0, len(dates), step))
    ax.set_xticks([dates[i] for i in idx])
    ax.set_xticklabels([dates[i].strftime("%m-%d") for i in idx], rotation=0)


def random_code():
    pick = rng.choice(list(CODE_CHARS), 6)
    return "".join(pick[:3]) + "-" + "".join(pick[3:])


def band_ok(value, lo, hi, margin):
    """value 가 [lo, hi) 안에서 경계와 margin 비율 이상 떨어져 있는가"""
    width = hi - lo
    return lo + margin * width <= value <= hi - margin * width


# ── 웨이퍼 맵 ─────────────────────────────────────────────────────────────

def wafer_grid(n):
    """n×n 격자 · 원 안 다이 표시 · 반지름(0–1) · 각도(도, 수학 방향: 0 = 오른쪽, 90 = 위)"""
    c = (n - 1) / 2.0
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = xx - c, c - yy                     # 그림의 위쪽이 +y
    r = np.hypot(dx, dy) / (n / 2.0)
    ang = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
    inside = r <= 0.97
    return inside, r, ang


def draw_wafer(bad, inside, title, size_px, dpi=100, body_only=False):
    img = np.zeros(bad.shape, dtype=int)
    img[inside] = 1
    img[inside & bad] = 2
    cmap = ListedColormap(["#FFFFFF", GRAY4, NAVY])
    inch = size_px / dpi
    fig = plt.figure(figsize=(inch, inch), dpi=dpi)
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.86] if not body_only else [0, 0, 1, 1])
    ax.imshow(img, cmap=cmap, interpolation="nearest", vmin=0, vmax=2)
    n = bad.shape[0]
    circ = plt.Circle(((n - 1) / 2, (n - 1) / 2), n * 0.49, fill=False, color=GRAY1, lw=1.2)
    ax.add_patch(circ)
    ax.plot([(n - 1) / 2], [n * 0.985], marker="^", color=GRAY1, ms=max(6, size_px / 120))   # 노치 (아래)
    ax.set_axis_off()
    if not body_only:
        fig.suptitle(title, fontsize=max(11, size_px / 70), color=NAVY)
        fig.text(0.5, 0.012, "notch: bottom    gray = pass die    navy = fail die",
                 ha="center", fontsize=max(8, size_px / 100), color=GRAY1)
    return fig


# ── KIT-2 ─────────────────────────────────────────────────────────────────

def kit2_code_image(name, code, shape):
    fig = plt.figure(figsize=(9, 6), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 6)
    ax.set_axis_off()
    ax.text(0.4, 5.4, "KIT-2 image check", fontsize=14, color=GRAY1)
    ax.text(0.4, 3.0, code, fontsize=64, color=NAVY, family="DejaVu Sans Mono", weight="bold", va="center")
    cx, cy, s = 7.3, 1.4, 0.9
    if shape == "별":
        ax.scatter([cx], [cy], marker="*", s=9000, color=LIME)
    elif shape == "삼각형":
        ax.add_patch(plt.Polygon([[cx - s, cy - s * 0.8], [cx + s, cy - s * 0.8], [cx, cy + s]], color=LIME))
    elif shape == "원":
        ax.add_patch(plt.Circle((cx, cy), s * 0.85, color=LIME))
    else:
        ax.add_patch(plt.Rectangle((cx - s * 0.8, cy - s * 0.8), s * 1.6, s * 1.6, color=LIME))
    return save(fig, name)


def ctx_frame(img_id, tag):
    fig = plt.figure(figsize=(8, 5), dpi=100)
    ax = fig.add_axes([0.1, 0.13, 0.85, 0.68])
    fig.text(0.02, 0.93, img_id, fontsize=22, color=NAVY, weight="bold")
    fig.text(0.98, 0.93, "TAG " + tag, fontsize=16, color=LIME1, ha="right", weight="bold",
             family="DejaVu Sans Mono")
    return fig, ax


def make_kit2():
    shapes = {"a": "별", "b": "삼각형"}
    codes = {"a": random_code(), "b": random_code()}
    assert codes["a"] != codes["b"]
    k2 = {}
    for key in ("a", "b"):
        name = kit2_code_image("k2_%s.png" % key, codes[key], shapes[key])
        k2[key] = {"image": name, "code": codes[key], "shape": shapes[key]}

    tags = []
    while len(tags) < 5:
        t = "".join(rng.choice(list(CODE_CHARS), 3))
        if t not in tags:
            tags.append(t)

    facts, images = [], []

    def fact(fid, text, value=None, unit=None, n=None):
        facts.append({"id": fid, "text": text, "value": value, "unit": unit, "n": n})

    # img1 · PRD_A 두께 추세 (변화 없음)
    d = days("2026-09-01", 30)
    a = 100.2 + trunc_normal(30, 0.35, 2.0)
    fig, ax = ctx_frame("img1", tags[0])
    ax.plot(d, a, marker="o", ms=4, color=NAVY2, lw=1)
    ax.axhline(103.0, color=GRAY2, ls="--", lw=1)
    ax.axhline(97.0, color=GRAY2, ls="--", lw=1)
    ax.set_title("PRD_A thickness by lot (nm)", fontsize=11, color=GRAY1)
    date_axis(ax, d)
    save(fig, "k2_ctx_1.png")
    images.append({"id": "img1", "file": "k2_ctx_1.png", "what": "PRD_A 두께 lot 추세 (2026-09)"})
    fact("f001", "PRD_A 두께 평균 %.1f nm (2026-09-01–09-30)" % a.mean(), round(float(a.mean()), 1), "nm", 30)
    fact("f002", "PRD_A 두께에 변화점 후보 없음 (같은 기간)")

    # img2 · PRD_B 두께 추세 (9/16 부터 +1.3 nm · USL 초과 2 lot)
    b = 100.1 + trunc_normal(30, 0.35, 2.0)
    b[15:] += 1.3
    b[[19, 26]] = [103.5, 103.7]
    fig, ax = ctx_frame("img2", tags[1])
    ax.plot(d, b, marker="o", ms=4, color=NAVY2, lw=1)
    ax.axhline(103.0, color=GRAY2, ls="--", lw=1)
    ax.axhline(97.0, color=GRAY2, ls="--", lw=1)
    ax.text(d[0], 103.1, "USL 103.0", fontsize=8, color=GRAY1)
    ax.set_title("PRD_B thickness by lot (nm)", fontsize=11, color=GRAY1)
    date_axis(ax, d)
    save(fig, "k2_ctx_2.png")
    images.append({"id": "img2", "file": "k2_ctx_2.png", "what": "PRD_B 두께 lot 추세 (2026-09)"})
    shift = float(np.delete(b[15:], [4, 11]).mean() - b[:15].mean())
    fact("f003", "PRD_B 두께가 2026-09-16 부터 평균 +%.1f nm" % shift, round(shift, 1), "nm", 30)
    fact("f004", "PRD_B 2026-09-16 이후 USL (103.0 nm) 초과 2 lot", 2, "lot", 15)

    # img3 · 설비별 상자 그림
    groups = {"EQ-01": 100.4, "EQ-02": 100.5, "EQ-03": 101.6, "EQ-04": 100.3}
    vals = [m + trunc_normal(25, 0.3, 2.0) for m in groups.values()]
    fig, ax = ctx_frame("img3", tags[2])
    ax.boxplot(vals, tick_labels=list(groups), patch_artist=True,
               boxprops={"facecolor": NAVY4, "color": NAVY}, medianprops={"color": NAVY})
    ax.set_title("PRD_B thickness by tool (nm)", fontsize=11, color=GRAY1)
    save(fig, "k2_ctx_3.png")
    images.append({"id": "img3", "file": "k2_ctx_3.png", "what": "PRD_B 두께 설비별 상자 그림"})
    meds = [float(np.median(v)) for v in vals]
    fact("f005", "설비 중 EQ-03 의 PRD_B 두께 중앙값이 가장 높다 (%.1f nm)" % meds[2], round(meds[2], 1), "nm", 25)
    others = [meds[0], meds[1], meds[3]]
    fact("f006", "EQ-01 · EQ-02 · EQ-04 중앙값 차이 %.1f nm 안" % (max(others) - min(others) + 0.05),
         round(max(others) - min(others), 2), "nm", 75)

    # img4 · 웨이퍼 맵 (오른쪽 위 가장자리 군집)
    inside, r, ang = wafer_grid(28)
    bad = inside & (r > 0.72) & (ang > 25) & (ang < 70) & (rng.random(r.shape) < 0.75)
    bad |= inside & (rng.random(r.shape) < 0.01)
    fig, ax = ctx_frame("img4", tags[3])
    ax.remove()
    img = np.zeros(bad.shape, dtype=int)
    img[inside] = 1
    img[inside & bad] = 2
    ax = fig.add_axes([0.3, 0.05, 0.4, 0.78])
    ax.imshow(img, cmap=ListedColormap(["#FFFFFF", GRAY4, NAVY]), interpolation="nearest", vmin=0, vmax=2)
    ax.set_axis_off()
    save(fig, "k2_ctx_4.png")
    images.append({"id": "img4", "file": "k2_ctx_4.png", "what": "PRD_B 웨이퍼 맵 1장 (fail die)"})
    edge_bad = int((bad & (r > 0.72) & (ang > 25) & (ang < 70)).sum())
    fact("f007", "PRD_B 웨이퍼 맵의 불량 다이가 오른쪽 위 가장자리에 몰려 있다")
    fact("f008", "그 가장자리 군집의 불량 다이 %d 개 (웨이퍼 1장)" % edge_bad, edge_bad, "die", 1)

    # img5 · 불량 유형 파레토
    cats = ["Residue", "Particle", "Scratch", "Void", "Other"]
    cnt = np.array([76, 52, 34, 22, 16])
    fig, ax = ctx_frame("img5", tags[4])
    ax.bar(cats, cnt, color=NAVY2)
    ax2 = ax.twinx()
    ax2.plot(cats, np.cumsum(cnt) / cnt.sum() * 100, color=LIME1, marker="o")
    ax2.set_ylim(0, 105)
    ax.set_title("Defect type Pareto (count, cum %)", fontsize=11, color=GRAY1)
    save(fig, "k2_ctx_5.png")
    images.append({"id": "img5", "file": "k2_ctx_5.png", "what": "불량 유형 파레토"})
    share = cnt / cnt.sum() * 100
    fact("f009", "불량 유형 1 위는 Residue (%.0f%%)" % share[0], round(float(share[0]), 1), "%", int(cnt.sum()))
    fact("f010", "상위 3 유형이 전체의 %.0f%%" % share[:3].sum(), round(float(share[:3].sum()), 1), "%", int(cnt.sum()))
    fact("f011", "자료 기간 2026-09-01–09-30 · PRD_A 30 lot · PRD_B 30 lot", None, None, 60)
    fact("f012", "EQ-03 은 2026-09-15 에 정기 PM 을 했다 (설비 기록)")

    ctx = {}
    owners = {"img1": ["f001", "f002"], "img2": ["f003", "f004"], "img3": ["f005", "f006"],
              "img4": ["f007", "f008"], "img5": ["f009", "f010"]}
    for i, tag in enumerate(tags):
        img_id = "img%d" % (i + 1)
        ctx[img_id] = {"image": "k2_ctx_%d.png" % (i + 1), "tag": tag, "facts": owners[img_id]}

    facts_lite = {
        "format": 1,
        "_안내": "M0 KIT-2 시험용 합성 사실 목록이다. 이름 · 숫자는 모두 지어낸 것이다.",
        "facts": facts,
        "images": images,
    }
    interview = {
        "format": 1,
        "_안내": "M0 KIT-2 시험용 합성 인터뷰 답이다 (사용자 진술이라고 가정). 의견 문장은 이 id 로만 근거를 단다.",
        "answers": [
            {"id": "a01", "question": "이 보고는 무엇을 위한 것입니까?", "answer": "이상 보고 · 독자는 팀장"},
            {"id": "a02", "question": "무엇 때문이라고 보십니까?", "answer": "EQ-03 의 9/15 PM 뒤 공정 조건이 바뀐 것 같다"},
            {"id": "a03", "question": "이 결론을 얼마나 확신하십니까?", "answer": "유력 - PM 기록을 아직 다 보지 못했다"},
            {"id": "a04", "question": "이 보고로 무엇을 요청합니까?", "answer": "EQ-03 PM 조건 재확인 · PRD_B 10 lot 추가 측정"},
        ],
    }
    return k2, ctx, facts_lite, interview


# ── KIT-3 ─────────────────────────────────────────────────────────────────

WAFER_LOC = {
    "가장자리": ["edge", "외곽", "에지", "테두리", "가장자리군집"],
    "중심": ["center", "centre", "가운데", "중앙", "중심부", "센터"],
    "고리": ["ring", "donut", "도넛", "링", "고리모양", "환형"],
    "고르게 퍼짐": ["random", "uniform", "랜덤", "무작위", "고르게", "퍼짐", "흩어짐"],
}
DIRS = {
    "위": ["top", "up", "북", "12시"], "오른쪽 위": ["top right", "upper right", "우상", "우상단", "1시", "2시"],
    "오른쪽": ["right", "우", "3시"], "오른쪽 아래": ["bottom right", "lower right", "우하", "우하단", "4시", "5시"],
    "아래": ["bottom", "down", "남", "6시"], "왼쪽 아래": ["bottom left", "lower left", "좌하", "좌하단", "7시", "8시"],
    "왼쪽": ["left", "좌", "9시"], "왼쪽 위": ["top left", "upper left", "좌상", "좌상단", "10시", "11시"],
}


def choice(truth, options, synonyms=None):
    opts = list(options)
    assert truth in opts
    return {"type": "choice", "truth": truth, "options": opts,
            "synonyms": {k: v for k, v in (synonyms or {}).items() if k in opts}}


def number(truth, lo, hi, unit=""):
    assert lo <= truth <= hi
    return {"type": "number", "truth": truth, "lo": lo, "hi": hi, "unit": unit}


def pick_band(value, bands):
    for label, lo, hi in bands:
        if lo <= value < hi:
            return label, lo, hi
    raise AssertionError(value)


def count_band_question(count, bands, margin=0.15):
    label, lo, hi = pick_band(count, bands)
    hi_eff = hi if hi != float("inf") else lo * 3
    assert band_ok(count, lo, hi_eff, margin), (count, label)
    syn = {b[0]: [b[0].replace("개", "").replace(" ", "")] for b in bands}
    return choice(label, [b[0] for b in bands], syn)


def chart_frame(w=11, h=6.5):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.08, 0.12, 0.78, 0.78])
    ax.grid(True, color=GRAY4, lw=0.6)
    return fig, ax


def make_c01():
    """추세 · 평균 이동 · 스펙선 · USL 초과 점"""
    n, k = 60, 30
    d = days("2026-09-01", n)
    sigma = 1.0
    y = 100.0 + trunc_normal(n, sigma, 1.8)
    y[k:] += 2.5
    above = [36, 44, 53]
    y[above] = [105.7, 106.1, 105.8]
    usl, lsl = 105.0, 95.0
    others = np.delete(np.arange(n), above)
    assert y[others].max() < usl - 0.6
    fig, ax = chart_frame()
    ax.plot(d, y, marker="o", ms=4, color=NAVY2, lw=1, label="PRD_B thickness")
    ax.axhline(usl, color=GRAY1, ls="--", lw=1.2, label="USL 105.0 / LSL 95.0")
    ax.axhline(lsl, color=GRAY1, ls="--", lw=1.2)
    ax.axhline(100.0, color=GRAY, ls=":", lw=1.2, label="Target 100.0")
    ax.set_ylim(93.5, 107.5)
    ax.set_ylabel("Thickness (nm)")
    ax.set_title("PRD_B film thickness by lot · daily (synthetic)", color=NAVY)
    date_axis(ax, d)
    ax.set_xlabel("Date (2026, MM-DD)")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "c01.png")
    pre_sd = float(np.std(y[:k], ddof=1))
    post = np.delete(y[k:], [i - k for i in above])
    size = float((post.mean() - y[:k].mean()) / pre_sd)
    return {
        "image": "c01.png", "group": "main", "kind": "추세 · 평균 이동",
        "questions": {
            "q1": {"type": "date", "truth": d[k].isoformat(), "tol_days": 3},
            "q2": number(round(size, 2), round(size - 1.0, 2), round(size + 1.0, 2), "σ"),
            "q3": number(3, 3, 3, "점"),
        },
    }


def make_c02():
    inside, r, ang = wafer_grid(32)
    bad = inside & (r > 0.7) & (ang > 190) & (ang < 260) & (rng.random(r.shape) < 0.85)
    bad |= inside & (rng.random(r.shape) < 0.012)
    draw = draw_wafer(bad, inside, "Wafer map · lot W2611 · wafer 07 (synthetic)", 1000)
    save(draw, "c02.png")
    count = int(bad.sum())
    bands = [("20개 미만", 0, 20), ("20–50개", 20, 50), ("50–100개", 50, 100), ("100개 이상", 100, float("inf"))]
    return {
        "image": "c02.png", "group": "main", "kind": "웨이퍼 맵 · 가장자리 군집",
        "count": count, "dies": int(inside.sum()),
        "questions": {
            "q1": choice("가장자리", list(WAFER_LOC), WAFER_LOC),
            "q2": choice("왼쪽 아래", list(DIRS), DIRS),
            "q3": count_band_question(count, bands),
        },
    }


def make_c03():
    inside, r, ang = wafer_grid(32)
    bad = inside & (r < 0.3) & (rng.random(r.shape) < 0.4)
    bad |= inside & (rng.random(r.shape) < 0.01)
    save(draw_wafer(bad, inside, "Wafer map · lot W2614 · wafer 12 (synthetic)", 1000), "c03.png")
    count = int(bad.sum())
    bands = [("20개 미만", 0, 20), ("20–50개", 20, 50), ("50–100개", 50, 100), ("100개 이상", 100, float("inf"))]
    return {
        "image": "c03.png", "group": "main", "kind": "웨이퍼 맵 · 중심 군집",
        "count": count, "dies": int(inside.sum()),
        "questions": {
            "q1": choice("중심", list(WAFER_LOC), WAFER_LOC),
            "q2": count_band_question(count, bands),
        },
    }


def make_dense():
    inside, r, ang = wafer_grid(200)
    bad = inside & (r > 0.55) & (r < 0.65) & (rng.random(r.shape) < 0.12)
    bad |= inside & (rng.random(r.shape) < 0.004)
    title = "Wafer map · lot W2620 · wafer 03 · dense (synthetic)"
    save(draw_wafer(bad, inside, title, 1000), "c04.png")
    save(draw_wafer(bad, inside, title, 3600), "c04L.png")
    count = int(bad.sum())
    bands = [("100개 미만", 0, 100), ("100–300개", 100, 300), ("300–1000개", 300, 1000),
             ("1000개 이상", 1000, float("inf"))]
    qs = {"q1": choice("고리", list(WAFER_LOC), WAFER_LOC), "q2": count_band_question(count, bands)}
    base = {"kind": "웨이퍼 맵 · 작은 점 · 고리", "count": count, "dies": int(inside.sum()), "questions": qs}
    c04 = dict(base, image="c04.png", group="main")
    c04l = dict(base, image="c04L.png", group="downscale",
                compare_with={"q1": "c04.q1", "q2": "c04.q2"})
    return c04, c04l


def make_c05():
    spec = [("EQ-01", 50.0, 3.0), ("EQ-02", 51.0, 1.1), ("EQ-03", 54.0, 1.1), ("EQ-04", 49.5, 1.0)]
    vals = [m + trunc_normal(40, s, 2.2) for _, m, s in spec]
    fig, ax = chart_frame()
    ax.boxplot(vals, tick_labels=[s[0] for s in spec], patch_artist=True, widths=0.5,
               boxprops={"facecolor": NAVY4, "color": NAVY}, medianprops={"color": NAVY, "lw": 2},
               whiskerprops={"color": NAVY}, capprops={"color": NAVY})
    ax.set_ylabel("CD (nm)")
    ax.set_xlabel("Tool")
    ax.set_title("PRD_A CD by tool · 40 wafers each (synthetic)", color=NAVY)
    save(fig, "c05.png")
    med = [float(np.median(v)) for v in vals]
    iqr = [float(np.percentile(v, 75) - np.percentile(v, 25)) for v in vals]
    names = [s[0] for s in spec]
    assert med.index(max(med)) == 2 and iqr.index(max(iqr)) == 0
    assert sorted(iqr)[-1] > 1.8 * sorted(iqr)[-2]
    syn = {nm: [nm.replace("-", ""), nm[-1]] for nm in names}
    return {
        "image": "c05.png", "group": "main", "kind": "상자 그림 · 설비 넷",
        "questions": {
            "q1": choice("EQ-03", names, syn),
            "q2": choice("EQ-01", names, syn),
            "q3": number(round(med[3], 2), round(med[3] - 1.0, 2), round(med[3] + 1.0, 2), "nm"),
        },
    }


def make_c06():
    n = 45
    x = rng.uniform(300, 600, n)
    y = 260 - 0.2 * x + rng.normal(0, 13, n)
    r = float(np.corrcoef(x, y)[0, 1])
    assert -0.82 < r < -0.68, r
    fig, ax = chart_frame()
    ax.scatter(x, y, color=NAVY2, s=28)
    ax.set_xlabel("RF power (W)")
    ax.set_ylabel("Etch rate (nm/min)")
    ax.set_title("Etch rate vs RF power · 45 runs (synthetic)", color=NAVY)
    save(fig, "c06.png")
    sign = {"양": ["양의상관", "양수", "+", "positive", "정", "정비례"],
            "음": ["음의상관", "음수", "-", "negative", "부", "반비례", "역"],
            "없음": ["무상관", "none", "상관없음"]}
    bands = {"0.3 미만": ["0.3미만", "<0.3"], "0.3–0.6": ["0.3-0.6"], "0.6–0.9": ["0.6-0.9"], "0.9 이상": ["0.9이상", ">0.9"]}
    return {
        "image": "c06.png", "group": "main", "kind": "산점도 · 상관", "r": round(r, 3),
        "questions": {"q1": choice("음", list(sign), sign), "q2": choice("0.6–0.9", list(bands), bands)},
    }


def make_c07():
    a = rng.normal(48.0, 1.2, 300)
    b = rng.normal(56.0, 0.9, 330)
    v = np.concatenate([a, b])
    bins = np.arange(42, 61, 0.5)
    h, edges = np.histogram(v, bins=bins)
    mid = (edges[:-1] + edges[1:]) / 2
    left_peak = h[mid < 52].max()
    right_peak = h[mid >= 52].max()
    assert right_peak > 1.2 * left_peak
    left_mode = float(mid[mid < 52][h[mid < 52].argmax()])
    fig, ax = chart_frame()
    ax.hist(v, bins=bins, color=NAVY2, edgecolor="#FFFFFF")
    ax.set_xlabel("Sheet resistance (ohm/sq)")
    ax.set_ylabel("Count")
    ax.set_title("PRD_B sheet resistance · 630 sites (synthetic)", color=NAVY)
    save(fig, "c07.png")
    modes = {"1": ["1개", "하나", "단봉", "one"], "2": ["2개", "둘", "쌍봉", "두개", "two"], "3 이상": ["3개이상", "3", "셋", "three"]}
    side = {"왼쪽": ["left", "좌", "작은쪽", "낮은쪽"], "오른쪽": ["right", "우", "큰쪽", "높은쪽"]}
    return {
        "image": "c07.png", "group": "main", "kind": "히스토그램 · 두 봉우리",
        "questions": {
            "q1": choice("2", list(modes), modes),
            "q2": choice("오른쪽", list(side), side),
            "q3": number(round(left_mode, 2), round(left_mode - 1.5, 2), round(left_mode + 1.5, 2), "ohm/sq"),
        },
    }


def outlier_series():
    n = 50
    d = days("2026-09-07", n)
    y = 20.0 + trunc_normal(n, 0.5, 2.0)
    idx = [11, 27, 41]
    y[idx] = [22.6, 17.4, 22.8]
    return d, y, idx


def make_c08():
    d, y, idx = outlier_series()

    def plot(body_only):
        fig, ax = chart_frame()
        ax.plot(d, y, marker="o", ms=4, color=NAVY2, lw=1)
        ax.axhline(20.0, color=GRAY, ls=":", lw=1.2)
        ax.axhline(21.5, color=GRAY1, ls="--", lw=1)
        ax.axhline(18.5, color=GRAY1, ls="--", lw=1)
        ax.set_ylim(16.5, 23.5)
        if body_only:
            ax.set_position([0, 0, 1, 1])
            ax.set_axis_off()
            return fig
        ax.set_ylabel("Overlay X (nm)")
        ax.set_title("PRD_A overlay X by lot · CL 20.0 · UCL 21.5 · LCL 18.5 (synthetic)", color=NAVY)
        date_axis(ax, d)
        ax.set_xlabel("Date (2026, MM-DD)")
        return fig

    save(plot(False), "c08.png")
    fig = plot(True)
    fig.set_size_inches(9, 4.5)
    save(fig, "c08C.png")
    direction = {"위만": ["위쪽만", "위", "above", "up"], "아래만": ["아래쪽만", "아래", "below", "down"],
                 "둘 다": ["둘다", "위아래", "양쪽", "both", "위와아래", "위아래모두"]}
    c08 = {
        "image": "c08.png", "group": "main", "kind": "추세 · 이상점 셋",
        "questions": {
            "q1": number(3, 3, 3, "점"),
            "q2": {"type": "dates", "truth": [d[i].isoformat() for i in idx], "tol_days": 2},
            "q3": choice("둘 다", list(direction), direction),
        },
    }
    c08c = {
        "image": "c08C.png", "group": "crop", "kind": "이상점 셋 · 본문만 (축 없음)",
        "compare_with": {"q1": "c08.q1", "q2": "c08.q3"},
        "questions": {"q1": number(3, 3, 3, "점"), "q2": choice("둘 다", list(direction), direction)},
    }
    return c08, c08c


def make_c09():
    cats = ["Particle", "Scratch", "Residue", "Void", "Bridge", "Other"]
    cnt = np.array([210, 120, 90, 40, 25, 15])
    cum = np.cumsum(cnt) / cnt.sum() * 100
    fig, ax = chart_frame()
    ax.bar(cats, cnt, color=NAVY2)
    ax.set_ylabel("Defect count")
    ax2 = ax.twinx()
    ax2.plot(cats, cum, color=LIME1, marker="o", lw=2)
    ax2.axhline(80, color=GRAY2, ls="--", lw=1)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Cumulative %")
    ax.set_title("Defect Pareto · 500 defects (synthetic)", color=NAVY)
    save(fig, "c09.png")
    top_share = float(cnt[0] / cnt.sum() * 100)
    need = int(np.argmax(cum >= 80) + 1)
    assert need == 3 and cum[1] < 75 and cum[2] > 82
    syn = {"Particle": ["파티클", "입자"], "Scratch": ["스크래치", "긁힘"], "Residue": ["잔류물", "잔사"],
           "Void": ["보이드"], "Bridge": ["브리지"], "Other": ["기타"]}
    share_bands = [("30% 미만", 0, 30), ("30–50%", 30, 50), ("50–70%", 50, 70), ("70% 이상", 70, 101)]
    label, lo, hi = pick_band(top_share, share_bands)
    assert band_ok(top_share, lo, hi, 0.25)
    return {
        "image": "c09.png", "group": "main", "kind": "파레토", "top_share": round(top_share, 1),
        "questions": {
            "q1": choice("Particle", cats, syn),
            "q2": choice(label, [b[0] for b in share_bands], {b[0]: [b[0].replace(" ", "")] for b in share_bands}),
            "q3": number(3, 3, 3, "범주"),
        },
    }


def make_c10():
    n = 76
    d = days("2026-09-01", n)
    t = np.arange(n)
    cross = 44                                   # 2026-10-15
    a = 95.0 - 0.06 * (t - cross) + rng.normal(0, 0.06, n)
    b = 95.0 + 0.06 * (t - cross) + rng.normal(0, 0.06, n)
    flips = [i for i in range(1, n) if np.sign(b[i] - a[i]) != np.sign(b[i - 1] - a[i - 1])]
    assert flips and all(abs(i - cross) <= 2 for i in flips), flips
    fig, ax = chart_frame()
    ax.plot(d, a, color=NAVY, lw=2, label="PRD_A")
    ax.plot(d, b, color=LIME1, lw=2, ls="--", label="PRD_B")
    ax.set_ylabel("Yield (%)")
    ax.set_title("Daily yield · PRD_A vs PRD_B (synthetic)", color=NAVY)
    date_axis(ax, d)
    ax.set_xlabel("Date (2026, MM-DD)")
    ax.legend(loc="lower center")
    save(fig, "c10.png")
    who = {"PRD_A": ["A", "prda", "제품a"], "PRD_B": ["B", "prdb", "제품b"]}
    return {
        "image": "c10.png", "group": "main", "kind": "두 계열 교차",
        "questions": {
            "q1": {"type": "date", "truth": d[cross].isoformat(), "tol_days": 4},
            "q2": choice("PRD_B", list(who), who),
        },
    }


def file_info(name):
    path = os.path.join(OUT, name)
    with open(path, "rb") as f:
        raw = f.read()
    w = int.from_bytes(raw[16:20], "big")
    h = int.from_bytes(raw[20:24], "big")
    return {"w": w, "h": h, "bytes": len(raw), "base64_bytes": (len(raw) + 2) // 3 * 4,
            "sha256": hashlib.sha256(raw).hexdigest()}


THRESHOLDS = {
    "_안내": "결과를 보기 전에 적은 문턱이다 (PLAN 08). 비율은 95% Wilson 구간으로 판정한다: "
             "초록 = 점 추정 >= target 그리고 구간 하한 >= floor · 빨강 = 구간 상한 < target · 노랑 = 나머지.",
    "deck_structure": {"target": 0.8, "floor": 0.35},
    "kit3_categorical": {"target": 0.8, "floor": 0.5},
    "kit3_numeric": {"target": 0.7, "floor": 0.35},
    "context_tags_min": 4,
}


def write_json(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRAY1,
                         "axes.labelcolor": GRAY1, "xtick.color": GRAY1, "ytick.color": GRAY1})
    k2, ctx, facts_lite, interview = make_kit2()
    charts = {"c01": make_c01(), "c02": make_c02(), "c03": make_c03()}
    charts["c04"], charts["c04L"] = make_dense()
    charts["c05"] = make_c05()
    charts["c06"] = make_c06()
    charts["c07"] = make_c07()
    charts["c08"], charts["c08C"] = make_c08()
    charts["c09"] = make_c09()
    charts["c10"] = make_c10()
    order = ["c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09", "c10", "c04L", "c08C"]
    charts = {k: charts[k] for k in order}

    names = sorted(n for n in os.listdir(OUT) if n.endswith(".png"))
    truth = {
        "format": 1,
        "_안내": "M0 KIT-2 · KIT-3 정답이다. 시험받는 모델에게 이 파일을 보이지 않는다 (README › 주의). "
                 "모든 이름 · 숫자는 합성이다.",
        "generator": {"script": "kit/llm/make_inputs.py", "seed": SEED, "python": platform.python_version(),
                      "matplotlib": matplotlib.__version__, "numpy": np.__version__},
        "thresholds": THRESHOLDS,
        "images": {n: file_info(n) for n in names},
        "kit2": {"a": k2["a"], "b": k2["b"], "ctx": ctx},
        "kit3": charts,
    }
    write_json("truth.json", truth)
    write_json("facts_lite.json", facts_lite)
    write_json("interview_lite.json", interview)
    for n in names:
        info = truth["images"][n]
        print("%-12s %5d x %-5d %8d bytes" % (n, info["w"], info["h"], info["bytes"]))
    print("truth.json · facts_lite.json · interview_lite.json 을 썼습니다 - %s" % OUT)


if __name__ == "__main__":
    main()
