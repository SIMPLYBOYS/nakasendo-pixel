# Nakasendō Pixel — 中山道・木曽街道六十九次

[Tōkaidō Pixel](../tokaido-pixel) 的山線姊妹作。同一套公式：北斎鳥瞰圖當 overworld，每站進到浮世繪真跡裡找細節。

| | 東海道（本線） | 中山道（本作） |
|---|---|---|
| Overworld | 北斎《東海道名所一覧》1818 | 北斎《木曽路名所一覧》1819（翌年姊妹作） |
| 宿場系列 | 広重《東海道五十三次》保永堂版 | 渓斎英泉 24 + 広重 47 =《木曽海道六拾九次之内》71 幅 / 70 編號 |
| 站數 | 53+2 | 69+1 |
| 招牌事件 | 川止め（大川渡涉） | 峠越え・大雪（中山道當年正是為了避開渡河才被選走） |

版權：英泉歿 1848、広重歿 1858、北斎歿 1849 —— 全系列 public domain。

## 現況：素材 70/70 到齊，MVP 可玩

兩個未驗證風險都拆掉了 →  **[完整報告](docs/phase0-asset-survey.md)**

- **Overworld**（第一風險）：北斎《木曽路名所一覧》**7898×5873** 可取得，比東海道的 overworld（2500px）還高。Commons 上沒有，唯一來源是神戸市立博物館的 IIIF（授權 CC BY-ND —— 原樣縮放使用合規，像素化不行；東海道的 overworld 本來就沒像素化，所以不受影響）。
- **宿場系列**：**70/70 全數到齊**。NDL 為主（~4470px），洗馬有 LOC 8991px；終點段的草津、大津 Commons 與 NDL 皆無，最後在波士頓美術館找到（2000px，剛好踩在 pipeline 地板上）。
- **MVP 切片（日本橋 → 軽井沢 19 站）**：素材全綠，每站 3 個隱藏細節逐張看圖標出。
- **繪師歸屬**：英泉 24 / 廣重 46（+ 中津川第二版）—— 與文獻公認的 24/47 吻合。

### 玩玩看

```bash
python3 -m http.server 8000   # 然後開 http://localhost:8000
```

| | |
|---|---|
| ![鳥瞰圖](docs/screenshots/overworld.png) | ![場景](docs/screenshots/scene.png) |
| *北斎《木曽路名所一覧》當 overworld——江戶出發，翻過碓氷峠* | *開場：英泉〈日本橋 雪之曙〉。每站找三個藏在畫裡的細節* |

### Phase 1 進行中

- [x] overworld 的 IIIF tile 抓取器（[tools/fetch-overworld.py](tools/fetch-overworld.py)，7898×5873）
- [x] **色盤：單盤成立** —— 合併色盤 vs 各繪師本家色盤，平均額外誤差僅 +3%，
      不值得為此把場景與圖鑑分流成兩套（[報告](docs/palette-report.md)）
- [x] 〈洗馬〉月夜通過量化 pipeline —— 東海道沒驗過的光線 case
- [x] MVP 19 站（日本橋→軽井沢）遊戲資產產出
- [x] **引擎 fork 自 tokaido-pixel**，換上中山道的 overworld、19 站與山線事件表
- [x] **MVP 切片：日本橋 → 軽井沢（1–19 幅）** —— 從路的起點走到第一道大關山（碓氷峠），
      對應東海道「日本橋→箱根」的切法。開場全是英泉的濃豔筆觸，廣重從第 12 幅才接手
- [x] 山線事件表：峠越え・大雪・福島關所・皇女和宮下向——東海道的招牌事件「川止め」
      在這裡不存在，因為中山道當年正是為了避開大川渡涉才被選走
- [ ] overworld 節點座標：19 站有 17 站是讀圖上的地名卡片定出的；倉賀野與板鼻是內插，
      但兩站都夾在已驗證的鄰站之間
- [ ] 延伸切片：木曽谷十三宿（洗馬→馬籠）的作者內容已完成，存於
      [`data/stations-kiso-authored.js`](data/stations-kiso-authored.js)，接上前需重驗 map 座標

引擎與 pipeline 直接重用 tokaido-pixel，本作是 content pack 不是新遊戲；唯一程式改動是加「路線」維度。分析全文見 vault `research/中山道-木曾街道六十九次-像素遊戲擴充分析.md`。

- [`data/stations.json`](data/stations.json) — 70 幅清單、繪師、掃描來源、MVP 標記
- [`tools/find-scans.py`](tools/find-scans.py) — 普查腳本（內含踩過的坑，別重踩）
- [`tools/plate.py`](tools/plate.py) — 自動偵測畫芯，去紙邊但保住題箋與朱印
- [`tools/make-palette.py`](tools/make-palette.py) — k-means 抽色 + 朱色保留槽

## License

MIT（程式碼）。浮世繪掃描為 public domain，溯源記於 `assets/sources.json`。
