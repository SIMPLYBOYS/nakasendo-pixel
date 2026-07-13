#!/usr/bin/env python3
"""Phase 0 素材普查：掃 Wikimedia Commons，回報《木曽海道六拾九次之内》70 幅的掃描可得性。

兩個坑（都踩過）：
1. 同名異系列。「木曽街道六十九次」還有國芳武者繪、國貞役者繪兩套，站名相同、
   Commons 上混在一起。判別靠版式：英泉/廣重這套是橫大判（w>h），那兩套是直幅。
2. 版上刻的字 ≠ 現代站名（三留野→三渡野、醒井→醒か井、愛知川→恵智川…）。
   所以優先用 NDL 標題裡的漢數字編號（「三拾弐 …洗馬」）比對，站名只當後備。

輸出 data/scan-candidates.json。用法：python3 tools/find-scans.py
"""
import json, re, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://commons.wikimedia.org/w/api.php"
MIN_PX = 2000  # 量化 pipeline 的解析度地板

# 這套系列在 Commons 上的三個主要來源，各自的命名習慣不同
QUERIES = [
    'insource:"木曽海道"',                       # NDL-DC 全套（~4400/6144px，標題帶版上編號）
    'insource:"木曽街道"',                       # 版上系列名有 海道/街道 兩種寫法，都要撈
    'insource:"Kisokaido" insource:"LCCN"',      # Library of Congress（最高 8991px）
    'insource:"Kisokaido" -insource:"Kuniyoshi"',
    'Kisokaido Hiroshige Eisen station',
    '日本橋雪之曙 Eisen',                         # 第 1 幅版上不叫「日本橋」，單獨撈（BnF 5598px）
]
ROOT_CAT = "Category:The Sixty-nine Stations of the Kiso-kaidō"


def api(params):
    body = urllib.parse.urlencode({**params, "format": "json"}).encode()  # 大 batch 會爆 HTTP 414
    req = urllib.request.Request(API, data=body, headers={"User-Agent": "nakasendo-pixel/0.1 (asset survey)"})
    for wait in (0, 20, 60, 120):  # 429 退避重試
        if wait:
            time.sleep(wait)
        try:
            return json.load(urllib.request.urlopen(req, timeout=40))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    raise RuntimeError("Commons API 持續 429，稍後再試")


def paged(params, key):
    out, cont = [], {}
    while True:
        d = api({**params, **cont})
        out += list((d.get("query", {}).get(key, {}) or {}).values()) if isinstance(d.get("query", {}).get(key), dict) \
            else d.get("query", {}).get(key, [])
        if "continue" not in d:
            return out
        cont = d["continue"]


def imageinfo(titles):
    out = []
    for i in range(0, len(titles), 40):
        d = api({"action": "query", "titles": "|".join(titles[i:i + 40]),
                 "prop": "imageinfo", "iiprop": "url|size|extmetadata"})
        for p in (d.get("query", {}).get("pages", {}) or {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata", {})
            gv = lambda k: re.sub(r"<[^>]+>", "", (em.get(k, {}) or {}).get("value", "") or "")
            out.append({"title": p["title"], "width": ii.get("width") or 0, "height": ii.get("height") or 0,
                        "license": gv("LicenseShortName"), "artist_meta": gv("Artist")[:60],
                        "credit": gv("Credit")[:60], "url": ii.get("url")})
    return out


# NDL 標題的編號用字混雜：十/拾、二/弐/貮、一/壱，偶爾直接寫阿拉伯數字
DIG = {"一": 1, "壱": 1, "二": 2, "弐": 2, "貮": 2, "三": 3, "参": 3, "四": 4,
       "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
D = "".join(DIG)
# 版上編號永遠緊貼系列名之前。系列名有「木曽海道六拾九次之内」「木曽海道」「木曽街道」多種寫法。
# 只抓緊鄰的那個數字——不能全域 search，否則系列名裡的「六拾九」會把 70 幅全判成第 69 幅（踩過）。
NUM_RE = re.compile(rf"[-\s]([{D}]?[十拾][{D}]?|[{D}]|\d{{1,2}})\s*木曽[海街]道")

def print_num(title):
    m = NUM_RE.search(title)
    if not m:
        return None
    s = m.group(1)
    if s.isdigit():
        return int(s)
    if mm := re.fullmatch(rf"([{D}]?)[十拾]([{D}]?)", s):
        return DIG.get(mm.group(1), 1) * 10 + DIG.get(mm.group(2), 0)
    return DIG.get(s)


# 橫大判的規格。實測 68 幅正版全落在 1.43–1.56，放寬到 1.30–1.70 留容差。
# 光靠 w>h 擋不住《續膝栗毛》的書封（草津，1.12，還是 PDF）——它也是橫的。
ASPECT = (1.30, 1.70)

def is_series(c):
    """英泉/廣重這套是橫大判單張錦繪。排除：
    - 直幅 → 國芳武者繪、國貞役者繪（站名相同，是另外兩套系列）
    - 長寬比離譜 → 書封、圖冊頁
    - PDF → NDL 的和本書籍掃描（《續膝栗毛》之類），不是單張版畫"""
    if c["title"].lower().endswith(".pdf") or not c["height"]:
        return False
    return ASPECT[0] <= c["width"] / c["height"] <= ASPECT[1]


def rank(c, ja=None):
    """排序鍵，由重到輕：

    1. 標題裡有沒有本站站名 —— **版上的編號會撞號**。〈恵智川〉（愛知川）與〈武佐〉
       兩張都刻著「六拾六」，〈鳥居本〉刻「六拾三」但實際排第 64。只看編號的話，
       66 號會被較大張的武佐（4505px）搶走，愛知川就沒圖了（踩過）。
    2. NDL 同一幅有兩版：6144x4096 是連色卡與裱框一起拍的原始檔，
       『-crd』是已裁到畫框的（~4400px，仍遠高於地板）。裁好的優先。
    3. 最後才比大小——不要只挑最大張。

    站名比不到就退回編號＋大小（版上刻的常是異體字：塩なた・あし田・大久手・みゑじ…）。
    """
    named = bool(ja) and ja in c["title"]
    cropped = "-crd" in c["title"] or "crd." in c["title"]
    return (not named, not cropped, -c["width"])


def artist_of(c):
    blob = f"{c['title']} {c['artist_meta']}"
    if re.search(r"Eisen|英泉|渓斎|Keisai", blob, re.I):
        return "英泉"
    if re.search(r"Hiroshige|広重|廣重", blob, re.I):
        return "広重"
    return None


def main():
    doc = json.load(open(ROOT / "data/stations.json"))
    stations = doc["stations"]

    titles = set()
    for q in QUERIES:
        print(f"搜尋 {q} …", flush=True)
        for p in paged({"action": "query", "generator": "search", "gsrnamespace": 6,
                        "gsrlimit": 500, "gsrsearch": q, "prop": "info"}, "pages"):
            titles.add(p["title"])
        time.sleep(1)
    for m in paged({"action": "query", "list": "categorymembers", "cmtitle": ROOT_CAT,
                    "cmtype": "file|subcat", "cmlimit": 500}, "categorymembers"):
        if m["title"].startswith("Category:"):
            titles |= {x["title"] for x in paged({"action": "query", "list": "categorymembers",
                                                  "cmtitle": m["title"], "cmtype": "file",
                                                  "cmlimit": 500}, "categorymembers")}
        else:
            titles.add(m["title"])

    print(f"{len(titles)} 個候選檔，抓 imageinfo …", flush=True)
    pool = imageinfo(sorted(titles))
    landscape = [c for c in pool if is_series(c)]
    print(f"  橫大判 {len(landscape)} / 直幅剔除 {len(pool) - len(landscape)}（國芳武者繪・國貞役者繪）\n", flush=True)

    # 先用版上編號建索引（最可靠：版上刻的站名是異體字，編號不是），再用站名/romaji 補
    by_num = {}
    for c in landscape:
        if n := print_num(c["title"]):
            by_num.setdefault(n, []).append(c)
    bogus = [n for n in by_num if not 1 <= n <= 70]
    assert not bogus, f"編號解析爆掉：{bogus}"  # 系列名污染會讓全部落在 69，這行會擋下
    print(f"  編號索引命中 {len(by_num)}/70 幅\n", flush=True)

    results, gaps = {}, []
    for s in stations:
        # 草津・大津 只在 MFA 有（Commons 與 NDL 皆無），來源手動釘住——別讓 Commons 掃描把它們洗掉
        if s.get("scan", {}).get("pinned"):
            print(f"  PIN {s['n']:>2} {s['ja']:<5} {s['artist']:<3} {s['scan']['px']}  {s['scan']['holder']}", flush=True)
            continue
        ja, romaji = s["ja"], s["slug"].split("-", 1)[1]
        hits = list(by_num.get(s["n"], []))
        seen = {h["title"] for h in hits}
        for c in landscape:
            if c["title"] in seen:
                continue
            if ja in c["title"] or re.search(rf"\b{romaji}\b", c["title"], re.I):
                hits.append(c); seen.add(c["title"])
        hits.sort(key=lambda c: rank(c, ja))
        results[s["slug"]] = hits[:5]

        best = hits[0]["width"] if hits else 0
        s["artist"] = next((a for a in (artist_of(c) for c in hits) if a), None)
        if hits and best >= MIN_PX:
            b = hits[0]
            s["scan"] = {"px": f"{b['width']}x{b['height']}", "license": b["license"],
                         "title": b["title"], "url": b["url"]}
            s["status"] = "assets"
        else:
            s.pop("scan", None)  # 缺口必須清掉舊紀錄，否則上一輪的錯誤命中會留下來裝綠燈
            s["status"] = "todo"
            gaps.append((s["ja"], best))
        flag = "OK " if best >= MIN_PX else ("LOW" if best else "MISS")
        print(f"  {flag} {s['n']:>2} {ja:<5} {s['artist'] or '?':<3} best={best or '-'}px ({len(hits)})", flush=True)

    # 守門：兩站共用同一張掃描 = 有一站被鄰站頂掉了（愛知川就是這樣被武佐洗掉的）。
    # 這種錯不會讓任何東西壞掉，只會讓那一站默默展示別人的畫。
    used = {}
    for s in stations:
        if t := s.get("scan", {}).get("title"):
            assert t not in used, f"{s['ja']} 與 {used[t]} 共用同一張掃描：{t}"
            used[t] = s["ja"]

    json.dump(results, open(ROOT / "data/scan-candidates.json", "w"), ensure_ascii=False, indent=1)
    json.dump(doc, open(ROOT / "data/stations.json", "w"), ensure_ascii=False, indent=1)

    ok = len(stations) - len(gaps)
    mvp_gap = [g for g in gaps if any(s["mvp"] and s["ja"] == g[0] for s in stations)]
    print(f"\n=== {ok}/{len(stations)} 站有 ≥{MIN_PX}px 橫大判掃描 ===")
    if gaps:
        print("缺口：", ", ".join(f"{ja}({px or 'none'})" for ja, px in gaps))
    print(f"MVP（洗馬→馬籠 13 站）缺口：{len(mvp_gap)}")
    from collections import Counter
    print("繪師：", dict(Counter(s["artist"] or "?" for s in stations)))


if __name__ == "__main__":
    main()
