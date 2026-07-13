#!/usr/bin/env python3
"""自動偵測浮世繪掃描的畫芯（版框內），裁掉四周紙邊。

東海道是每站手動量 --crop 比例；69 站手動量不划算，而且手動裁很容易連題箋和
落款印一起切掉——那正是朱色唯一的來源（見 make-palette.py 的朱色保留槽）。

原理：紙邊是一片均勻的米白，畫芯有墨線。逐列/逐行算亮度標準差，
標準差跨過門檻的最長連續區間就是畫芯。

自我檢查：python3 tools/plate.py assets/32-seba.jpg   （印出裁切框並存出預覽）
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

MARGIN = 0.004  # 裁進來一點，避免留下版框外的一線紙白


def detect(im: Image.Image) -> tuple[int, int, int, int]:
    """回傳畫芯的 (left, top, right, bottom)。偵測失敗就回整張圖。"""
    g = np.asarray(im.convert("L").resize((400, 400), Image.Resampling.LANCZOS), dtype=np.float64)

    def span(std):
        # 先平滑：掃描機常在紙的最外緣留一條暗線，單行的尖峰會讓「最外側跨越點」
        # 直接貼齊圖緣、整張都不裁（大津就是這樣只裁掉 5%）。平滑掉孤立尖峰。
        k = 5
        std = np.convolve(std, np.ones(k) / k, mode="same")
        # 門檻取「最平靜的紙邊」和「最花的畫芯」之間；紙邊 std 接近 0
        thr = std.min() + (std.max() - std.min()) * 0.15
        on = np.flatnonzero(std > thr)
        # 取最外側的跨越點，不是最長連續區間——畫面中段常有低變異的淺色帶
        # （柏原的淺色地面就把最長區間截成兩半，結果只裁到上半張）
        return (int(on[0]), int(on[-1])) if len(on) else (0, len(std) - 1)

    t, b = span(g.std(axis=1))
    l, r = span(g.std(axis=0))
    W, H = im.size
    m = MARGIN
    return (round((l / 400 + m) * W), round((t / 400 + m) * H),
            round((r / 400 - m + 1 / 400) * W), round((b / 400 - m + 1 / 400) * H))


def crop(im: Image.Image) -> Image.Image:
    l, t, r, b = detect(im)
    if r - l < im.width * 0.5 or b - t < im.height * 0.5:   # 偵測顯然爆掉就別裁
        return im
    return im.crop((l, t, r, b))


if __name__ == "__main__":
    for p in sys.argv[1:] or ["assets/32-seba.jpg"]:
        im = Image.open(p)
        box = detect(im)
        out = crop(im)
        pct = 100 * (1 - (out.width * out.height) / (im.width * im.height))
        print(f"{Path(p).name:<20} {im.size} → {out.size}  裁掉 {pct:.1f}%  box={box}")
        assert out.width > im.width * 0.5 and out.height > im.height * 0.5, "裁過頭"
