#!/usr/bin/env python3
"""把 index.html 裡每站的三個隱藏細節座標畫回真跡上，輸出對照圖供逐張核對。

為什麼需要這支：座標是「看著圖標出來的」，但看的是哪一張圖會變。
plate.py 修過兩次（最長連續區間 → 最外側跨越點、掃描暗線平滑），
每修一次畫芯框就位移，之前標好的座標就悄悄失準——木曾谷 13 站與蕨都中過。
座標本身不會報錯，只會讓玩家點不到東西，所以只能用眼睛驗。

用法：
  python3 tools/check-details.py            # 全部，輸出到 $TMPDIR/detail-check/
  python3 tools/check-details.py 03 21 44   # 只看指定幾站（大圖＋格線）
"""
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("TMPDIR", "/tmp")) / "detail-check"
HIT_R = 0.075   # 必須與 index.html 的 HIT_R 一致：圈的大小就是玩家的命中範圍


def stations():
    block = (ROOT / "index.html").read_text().split("const STATIONS = [", 1)[1].split("\n];", 1)[0]
    for m in re.finditer(r'slug:"([^"]+)".*?details:\[(.*?)\],\n', block, re.S):
        pts = re.findall(r'\[([\d.]+),([\d.]+),"([^"]+)"', m.group(2))
        assert len(pts) == 3, f"{m.group(1)} 有 {len(pts)} 個細節，應為 3"
        yield m.group(1), [(float(x), float(y), lab) for x, y, lab in pts]


def draw(slug, pts, width, grid):
    im = Image.open(ROOT / f"game-assets/originals/{slug}.jpg").convert("RGB")
    im = im.resize((width, round(width * im.height / im.width)), Image.Resampling.LANCZOS)
    W, H = im.size
    d = ImageDraw.Draw(im)
    if grid:
        for i in range(1, 10):
            d.line([(W * i / 10, 0), (W * i / 10, H)], fill=(255, 0, 255))
            d.line([(0, H * i / 10), (W, H * i / 10)], fill=(255, 0, 255))
    for j, (x, y, _) in enumerate(pts):
        cx, cy, r = x * W, y * H, HIT_R * W   # 命中半徑是相對「寬」算的，圈也照寬畫
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 0, 255), width=3)
        d.text((cx - 4, cy - 6), str(j + 1), fill=(255, 0, 255))
    d.text((6, 6), f"{slug}  " + " / ".join(f"{j+1}.{p[2]}" for j, p in enumerate(pts)),
           fill=(255, 0, 255))
    return im


def main():
    OUT.mkdir(exist_ok=True)
    want = sys.argv[1:]
    sel = [(s, p) for s, p in stations() if not want or s[:2] in want]
    if want:   # 指定站：一張一張出大圖，標得準不準看得清楚
        for slug, pts in sel:
            draw(slug, pts, 900, grid=True).save(OUT / f"{slug}.png")
    else:      # 全部：四張一頁，先粗掃，可疑的再用上面的單站模式細看
        W, H = 700, 470
        for g in range(0, len(sel), 4):
            sheet = Image.new("RGB", (W * 2, H * 2), "white")
            for i, (slug, pts) in enumerate(sel[g:g + 4]):
                sheet.paste(draw(slug, pts, W, grid=False).resize((W, H)),
                            ((i % 2) * W, (i // 2) * H))
            sheet.save(OUT / f"sheet-{g // 4:02d}.png")
    print(f"{len(sel)} 站 → {OUT}/")


if __name__ == "__main__":
    main()
