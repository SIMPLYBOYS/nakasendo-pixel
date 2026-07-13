#!/usr/bin/env python3
"""從神戸市博的原尺寸掃描產出遊戲用的 overworld（兩種寬度，給 srcset 挑）。

  game-assets/overworld.jpg      1600px — 一般螢幕
  game-assets/overworld@2x.jpg   3200px — retina（1440 視窗 × DPR2 需要 2880）

原本只有 1600px，那是直接沿用東海道的尺寸——但東海道的源檔本來就只有 2500px，
1600 幾乎是原生；這裡的源檔有 7898px，用 1600 等於白丟五倍解析度，地圖上的
地名卡片糊成一團。

授權：掃描為 CC BY-ND 4.0（神戸市立博物館）。ND = 禁止改作，
**等比例縮放與格式轉換屬技術重製，不是改作**；但像素化、上色、動畫化會踩線——
所以 overworld 全程維持真跡樣貌，只有宿場場景才進量化 pipeline。

用法：python3 tools/make-overworld.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/00-overworld-kisoji-meisho-ichiran.jpg"
WIDTHS = {"overworld.jpg": 1600, "overworld@2x.jpg": 3200}
# 4:4:4（不做色度次抽樣）：圖上的朱印與紅色地名卡片只有幾 px 寬，
# 預設的 4:2:0 會把它們糊成一片粉紅。progressive 讓大圖邊下載邊顯示。
OPTS = dict(quality=85, subsampling=0, optimize=True, progressive=True)


def main():
    if not SRC.exists():
        raise SystemExit(f"缺少源檔 {SRC}——先跑 tools/fetch-overworld.py")
    src = Image.open(SRC)
    for name, w in WIDTHS.items():
        h = round(w * src.height / src.width)   # 嚴格等比，ND 授權下不能裁切變形
        out = ROOT / "game-assets" / name
        src.resize((w, h), Image.Resampling.LANCZOS).save(out, "JPEG", **OPTS)
        print(f"  {name:<20} {w}×{h}  {out.stat().st_size / 1e6:.1f} MB")
    print(f"\n源檔 {src.size} → 兩種寬度，index.html 以 srcset 讓瀏覽器按 DPR 挑")


if __name__ == "__main__":
    main()
