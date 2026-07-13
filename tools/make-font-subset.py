#!/usr/bin/env python3
"""重建站名毛筆體（Yuji Boku, OFL）的子集。

為什麼需要：原本 game-assets/fonts/yujiboku-stations.woff2 是從 tokaido-pixel 一起
fork 過來的——那是**東海道** 55 站站名切出來的 141 字。中山道的站名是另一組字，
44 站用到的 73 字裡缺了 41 個，35 站的名籤靜靜 fallback 到楷體。字型缺字不會報錯，
只會讓地圖上的字體悄悄變成混的。

字集不用手列，直接從程式與資料推出來（列漏了才是下次出事的原因）：
  ・data/stations.json 全 70 站站名——先切好，續走 45–70 時不必重來
  ・繪卷書籤的漢數字（一〜七十）
  ・index.html 裡指定了 Yuji Boku 的 UI 字串（完歩證、雅號、道中日數…）

用法：python3 tools/make-font-subset.py
需要網路（Google Fonts 的 text= API 會直接回傳切好的 woff2）。
"""
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "game-assets/fonts/yujiboku-stations.woff2"
CSS = "https://fonts.googleapis.com/css2"
# 沒有這個 UA 就拿到 ttf；給現代 UA 才回 woff2
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

# index.html 裡用 Yuji Boku 排的 UI 字串。改了 UI 文案就要跟著補這裡——
# 漏了不會報錯，只會讓那幾個字掉回楷體。
UI = """
道中第日 完歩之證 雅號授與 自至 年月日 完歩
木曽街道六十九次 日本橋より木曾路を抜け馬籠まで
飛腳級健腳！堂堂健腳旅人 悠悠道中客 道草三昧
韋駄天屋 疾風 早駕籠屋 千里 風流屋 雲水 彌次喜多屋 道草
０１２３４５６７８９0123456789・
"""


def kansuji(n):   # 與 index.html 的 KANSUJI 同構
    d = "一二三四五六七八九"
    return ("" if n < 20 else d[n // 10 - 1]) + ("十" if n >= 10 else "") + \
           ("" if n % 10 == 0 else d[n % 10 - 1])


def main():
    import json
    stations = json.load(open(ROOT / "data/stations.json"))["stations"]
    chars = set("".join(s["ja"] for s in stations))          # 全 70 站
    chars |= set("".join(kansuji(n) for n in range(1, 71)))  # 繪卷書籤
    chars |= set(UI) - set(" \n")
    text = "".join(sorted(chars))
    print(f"需要 {len(text)} 字")

    url = f"{CSS}?{urllib.parse.urlencode({'family': 'Yuji Boku', 'text': text})}"
    css = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode()
    # 切好的字型網址長這樣：fonts.gstatic.com/l/font?kit=…（沒有 .woff2 副檔名，
    # 格式看 format('woff2') 那段，別用副檔名判斷）
    m = re.search(r"src:\s*url\((https://[^)]+)\)\s*format\('woff2'\)", css)
    if not m:
        raise SystemExit(f"CSS 裡沒有 woff2 連結：\n{css[:400]}")
    woff = urllib.request.urlopen(urllib.request.Request(m.group(1), headers=UA), timeout=30).read()
    OUT.write_bytes(woff)
    print(f"→ {OUT.relative_to(ROOT)}  {len(woff) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
