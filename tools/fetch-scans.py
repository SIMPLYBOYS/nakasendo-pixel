#!/usr/bin/env python3
"""依 data/stations.json 下載宿場掃描到 assets/。

走 Commons 的縮圖 API 取 2800px，不抓 4400px 原檔——Wikimedia 對原檔直抓會 429，
並明確要求改用縮圖；而 pipeline 最大只需要 2600px（見 make-station-assets.py），
原檔本來就用不到。

用法：
  python3 tools/fetch-scans.py           # 全部 status=assets 的站
  python3 tools/fetch-scans.py --mvp     # 只抓 MVP 切片（洗馬→馬籠 13 站）
已存在就跳過，可中斷續抓。原始掃描不進版控（見 .gitignore），這支腳本就是重現方式。
"""
import argparse, json, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "nakasendo-pixel/0.1 (public-domain art sourcing)"}
WIDTH = 2800  # pipeline 的 large 是 2600px，留一點裁邊餘裕


def get(url, data=None, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            return urllib.request.urlopen(req, timeout=120).read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
            time.sleep(15 * (i + 1))
    raise RuntimeError("unreachable")


def thumb_urls(titles):
    """一次問 Commons 拿指定寬度的縮圖 URL（一批上限 50 個 title）。"""
    out = {}
    for i in range(0, len(titles), 40):
        body = urllib.parse.urlencode({
            "action": "query", "titles": "|".join(titles[i:i + 40]), "prop": "imageinfo",
            "iiprop": "url", "iiurlwidth": WIDTH, "format": "json"}).encode()
        pages = json.loads(get(API, body))["query"]["pages"]
        for p in pages.values():
            if ii := p.get("imageinfo"):
                out[p["title"]] = ii[0].get("thumburl") or ii[0]["url"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mvp", action="store_true", help="只抓 MVP 13 站")
    args = ap.parse_args()

    doc = json.load(open(ROOT / "data/stations.json"))
    todo = [s for s in doc["stations"]
            if s["status"] == "assets" and (s["mvp"] or not args.mvp)
            and not (ROOT / f"assets/{s['slug']}.jpg").exists()]
    (ROOT / "assets").mkdir(exist_ok=True)
    if not todo:
        print("全部已存在")
        return
    print(f"{len(todo)} 站待抓（{WIDTH}px 縮圖）\n")
    urls = thumb_urls([s["scan"]["title"] for s in todo])

    for s in todo:
        out = ROOT / f"assets/{s['slug']}.jpg"
        out.write_bytes(get(urls[s["scan"]["title"]]))
        print(f"  {s['slug']:<16} {s['artist']}  {out.stat().st_size / 1e6:.1f} MB", flush=True)
        time.sleep(2)

    print(f"\n→ assets/  共 {len(list((ROOT / 'assets').glob('*.jpg')))} 張")


if __name__ == "__main__":
    main()
