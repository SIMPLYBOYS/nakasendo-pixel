#!/usr/bin/env python3
"""k-means 抽色，並回答「單色盤還是雙色盤」。

英泉（濃豔）和廣重（抒情）風格明顯不同，理論上該給兩套色盤。但兩套色盤要付代價：
圖鑑/場景要分流、色票不統一、玩家看到的世界會斷成兩半。所以用數據決定，不憑感覺：

  對每一幅，比較「用合併色盤量化」和「用該繪師自己的色盤量化」的誤差。
  若合併色盤的誤差只差一點點 → 單色盤就夠，不要多養一套。

用法：python3 tools/make-palette.py [-k 14]
輸出 assets/palette.json（合併，供 make-station-assets.py 用）+ docs/palette-report.md
"""
import argparse, json
from pathlib import Path

import numpy as np
from PIL import Image

import plate

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = 600    # 取樣寬度。太小（<400）會把落款朱印糊進背景，朱色就永遠抽不出來


def pixels(path):
    im = plate.crop(Image.open(path).convert("RGB"))   # 裁到畫芯：去紙邊，但保住題箋與朱印
    im = im.resize((SAMPLE, max(1, round(im.height * SAMPLE / im.width))), Image.Resampling.LANCZOS)
    return np.asarray(im, dtype=np.float64).reshape(-1, 3)


def vermilion(X):
    """朱：紅的成分大於黃的成分。這條線是為了把朱（#ba6d4a）和赭黃（#ab8a4f）分開——
    兩者 R 都大於 B，差別在赭黃的 G-B 更大。"""
    R, G, B = X[:, 0], X[:, 1], X[:, 2]
    return (R - G > 45) & ((R - G) > (G - B)) & (R > 90)


def kmeans(X, k, iters=60, seed=0):
    """Lloyd + k-means++ 初始化。為了 k=14、幾十萬點——不值得為此拉 sklearn 進來。"""
    rng = np.random.default_rng(seed)
    C = X[rng.integers(len(X))][None, :]
    for _ in range(k - 1):                       # k-means++：離現有中心越遠越可能被選中
        d2 = ((X[:, None] - C[None]) ** 2).sum(-1).min(1)
        C = np.vstack([C, X[rng.choice(len(X), p=d2 / d2.sum())]])
    for _ in range(iters):
        lab = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        new = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
        if np.allclose(new, C):
            break
        C = new
    lab = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
    share = np.bincount(lab, minlength=k) / len(X)
    return C, share


def rmse(X, C):
    """每個像素到最近色票的 RMSE——量化誤差，越低越貼近原作。"""
    return float(np.sqrt(((X[:, None] - C[None]) ** 2).sum(-1).min(1).mean()))


def hexes(C):
    return ["#%02x%02x%02x" % tuple(np.clip(c, 0, 255).astype(int)) for c in C]


def swatch(C, share, path, label):
    """畫成色條，寬度按佔比——肉眼比對兩套色盤差在哪。"""
    W, H = 900, 90
    im = Image.new("RGB", (W, H + 22), "white")
    x = 0
    for c, s in sorted(zip(C, share), key=lambda t: -t[1]):
        w = max(1, round(W * s))
        im.paste(tuple(np.clip(c, 0, 255).astype(int)), (x, 22, min(W, x + w), H + 22))
        x += w
    from PIL import ImageDraw
    ImageDraw.Draw(im).text((4, 5), label, fill="black")
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", type=int, default=14)  # 與東海道同 k，兩條路線色票數一致
    args = ap.parse_args()
    k = args.k

    doc = json.load(open(ROOT / "data/stations.json"))
    have = [s for s in doc["stations"] if (ROOT / f"assets/{s['slug']}.jpg").exists()]
    by_artist = {"英泉": [], "広重": []}
    for s in have:
        by_artist[s["artist"]].append(s)
    print(f"樣本：英泉 {len(by_artist['英泉'])} 幅、広重 {len(by_artist['広重'])} 幅\n")

    px = {s["slug"]: pixels(ROOT / f"assets/{s['slug']}.jpg") for s in have}
    sets = {a: np.vstack([px[s["slug"]] for s in ss]) for a, ss in by_artist.items()}
    sets["合併"] = np.vstack(list(sets.values()))

    # 朱色保留一個色票。k-means 最小化面積加權誤差，而朱只佔 ~1%（落款印、題箋、
    # 少數夕照），純分群必定犧牲它——實測 k=14 抽出來一個紅都沒有，68/69 幅的
    # 朱印會被量化成橄欖黃。每幅浮世繪都有朱印，這是領域常識，不該交給分群去「發現」。
    pal = {}
    for name, X in sets.items():
        red = vermilion(X)
        sub = X[np.random.default_rng(0).choice(len(X), min(len(X), 60_000), replace=False)]
        C, share = kmeans(sub[~vermilion(sub)], k - 1)
        C = np.vstack([C, X[red].mean(0)])                     # 第 14 槽 = 朱
        share = np.append(share * (1 - red.mean()), red.mean())
        pal[name] = (C, share)
        print(f"  {name:<3} 色盤抽出（樣本 {len(sub):,} 點）")
        swatch(C, share, ROOT / f"docs/palette-{name}.png", f"{name}  k={k}")

    # 決策：對每幅畫比「合併色盤」與「本家色盤」的誤差
    rows, pen = [], []
    for s in have:
        X = px[s["slug"]]
        own, both = rmse(X, pal[s["artist"]][0]), rmse(X, pal["合併"][0])
        rows.append((s, own, both))
        pen.append((both - own) / own * 100)
    avg = float(np.mean(pen))

    lines = [f"# 色盤：單盤 vs 雙盤（k={k}）\n",
             f"樣本 {len(have)} 幅（英泉 {len(by_artist['英泉'])} / 広重 {len(by_artist['広重'])}）。",
             "指標：每幅在「合併色盤」下的量化 RMSE，比在「本家繪師色盤」下高出多少。\n",
             f"**合併色盤的平均額外誤差：{avg:+.1f}%**\n",
             "| # | 站 | 繪師 | 本家色盤 RMSE | 合併色盤 RMSE | 代價 |",
             "|---|---|---|---|---|---|"]
    for (s, own, both), p in sorted(zip(rows, pen), key=lambda t: -t[1])[:12]:
        lines.append(f"| {s['n']} | {s['ja']} | {s['artist']} | {own:.2f} | {both:.2f} | {p:+.1f}% |")
    lines.append("\n（只列代價最高的 12 幅）\n")
    for name in ("合併", "英泉", "広重"):
        lines.append(f"### {name}\n![{name}](palette-{name}.png)\n")
        lines.append("`" + "` `".join(hexes(pal[name][0])) + "`\n")
    (ROOT / "docs/palette-report.md").write_text("\n".join(lines))

    C, share = pal["合併"]
    order = np.argsort(-share)
    json.dump({"colors": [hexes(C)[i] for i in order],
               "share": [round(float(share[i]), 4) for i in order],
               "method": f"k-means k={k - 1} + 1 reserved vermilion slot, over {len(have)} "
                         f"Kisokaido prints (auto plate crop), Eisen+Hiroshige combined"},
              open(ROOT / "assets/palette.json", "w"), indent=1)

    print(f"\n=== 合併色盤的平均額外誤差：{avg:+.1f}% ===")
    print("→ assets/palette.json, docs/palette-report.md")


if __name__ == "__main__":
    main()
