#!/usr/bin/env python3
"""抓北斎《木曽路名所一覧》全解析度 overworld（7898x5873）。

神戸市立博物館的 IIIF 把「整圖交付」鎖在 900px（/full/full、/full/max、sizeByW 全部只回 900），
但 ≤900px 的 region 回傳原生像素——所以按 tile 切、逐塊取原尺寸、再拼回來。
這就是它自己的 viewer 放大時做的事。

授權 CC BY-ND 4.0（提供：神戸市立博物館）：可原樣使用並標註，不得改作。
→ overworld 只能縮放，不能像素化 / 做成動態影片。溯源寫進 assets/sources.json。

用法：python3 tools/fetch-overworld.py
"""
import json, time, urllib.error, urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IIIF = ("https://online.bunka.go.jp//iipsrv/iipsrv.fcgi"
        "?IIIF=285011/_365298/285011_365298263940846893228_org.tif")
TILE = 896          # 必須 ≤900：超過就會被伺服器縮到 900，拼出來反而糊掉
UA = {"User-Agent": "nakasendo-pixel/0.1 (public-domain art sourcing)"}
OUT = ROOT / "assets/00-overworld-kisoji-meisho-ichiran.jpg"


def get(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
            time.sleep(10 * (i + 1))


def main():
    info = json.loads(get(f"{IIIF}/info.json"))
    W, H = info["width"], info["height"]
    print(f"母檔 {W}x{H}，切成 {-(-W // TILE)}x{-(-H // TILE)} 塊", flush=True)

    canvas = Image.new("RGB", (W, H))
    n = 0
    for y in range(0, H, TILE):
        for x in range(0, W, TILE):
            w, h = min(TILE, W - x), min(TILE, H - y)   # 邊緣塊會被裁短，用實際回傳尺寸貼
            tile = Image.open(BytesIO(get(f"{IIIF}/{x},{y},{w},{h}/full/0/default.jpg")))
            assert tile.size == (w, h), f"tile@{x},{y} 期待 {(w, h)} 得到 {tile.size}——被伺服器縮放了"
            canvas.paste(tile, (x, y))
            n += 1
            print(f"  {n:>3} tile@{x},{y} {tile.size}", flush=True)
            time.sleep(0.5)

    OUT.parent.mkdir(exist_ok=True)
    canvas.save(OUT, quality=95, subsampling=0)
    print(f"\n→ {OUT.relative_to(ROOT)}  {canvas.size}  {OUT.stat().st_size / 1e6:.1f} MB")

    src = ROOT / "assets/sources.json"
    rec = json.loads(src.read_text()) if src.exists() else []
    rec = [r for r in rec if r["file"] != OUT.name] + [{
        "file": OUT.name,
        "title_ja": "木曽路名所一覧",
        "artist": "葛飾北斎 (1760–1849)",
        "year": 1819,
        "holder": "神戸市立博物館",
        "via": "文化遺産オンライン（文化庁）IIIF",
        "page": "https://www.kobecitymuseum.jp/collection/detail?heritage=365298",
        "iiif": IIIF,
        "px": f"{W}x{H}",
        "license": "CC BY-ND 4.0",
        "license_note": "原作為 public domain（北斎歿 1849）；ND 附加於掃描本身。"
                        "遊戲中只做等比縮放並標註提供者，不做像素化等改作。",
    }]
    src.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    print(f"→ {src.relative_to(ROOT)} 已記錄溯源與授權")


if __name__ == "__main__":
    main()
