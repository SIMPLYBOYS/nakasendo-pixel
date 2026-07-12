# Nakasendō Pixel — 中山道・木曽街道六十九次

[Tōkaidō Pixel](../tokaido-pixel) 的山線姊妹作。同一套公式：北斎鳥瞰圖當 overworld，每站進到浮世繪真跡裡找細節。

| | 東海道（本線） | 中山道（本作） |
|---|---|---|
| Overworld | 北斎《東海道名所一覧》1818 | 北斎《木曽路名所一覧》1819（翌年姊妹作） |
| 宿場系列 | 広重《東海道五十三次》保永堂版 | 渓斎英泉 24 + 広重 47 =《木曽海道六拾九次之内》71 幅 / 70 編號 |
| 站數 | 53+2 | 69+1 |
| 招牌事件 | 川止め（大川渡涉） | 峠越え・大雪（中山道當年正是為了避開渡河才被選走） |

版權：英泉歿 1848、広重歿 1858、北斎歿 1849 —— 全系列 public domain。

## 現況：Phase 0 素材普查 ✅ 通過

兩個未驗證風險都拆掉了 →  **[完整報告](docs/phase0-asset-survey.md)**

- **Overworld**（第一風險）：北斎《木曽路名所一覧》**7898×5873** 可取得，比東海道的 overworld（2500px）還高。Commons 上沒有，唯一來源是神戸市立博物館的 IIIF（授權 CC BY-ND —— 原樣縮放使用合規，像素化不行；東海道的 overworld 本來就沒像素化，所以不受影響）。
- **宿場系列**：**68/70** 有 ≥2000px 橫大判掃描（NDL 為主，洗馬有 LOC 8991px）。缺口是終點段的草津、大津。
- **MVP 切片（洗馬 → 馬籠 13 站）**：**13/13 全綠**，已逐張目視確認。
- **繪師歸屬**：英泉 24 / 廣重 46（+ 中津川第二版）—— 與文獻公認的 24/47 吻合。

### Phase 1 進行中

- [x] overworld 的 IIIF tile 抓取器（[tools/fetch-overworld.py](tools/fetch-overworld.py)，7898×5873）
- [x] **色盤：單盤成立** —— 合併色盤 vs 各繪師本家色盤，平均額外誤差只有 +1.0%，
      不值得為此把場景與圖鑑分流成兩套（[報告](docs/palette-report.md)）
- [x] 〈洗馬〉月夜通過量化 pipeline —— 東海道沒驗過的光線 case
- [x] MVP 13 站（洗馬→馬籠）遊戲資產產出
- [ ] 補草津、大津（NDL / LOC / Rijksmuseum）
- [ ] 路線維度（overworld 切換 + 事件表分流）
- [ ] 山線事件表：峠越え・大雪（東海道的「川止め」在這裡反轉成賣點）

引擎與 pipeline 直接重用 tokaido-pixel，本作是 content pack 不是新遊戲；唯一程式改動是加「路線」維度。分析全文見 vault `research/中山道-木曾街道六十九次-像素遊戲擴充分析.md`。

- [`data/stations.json`](data/stations.json) — 70 幅清單、繪師、掃描來源、MVP 標記
- [`tools/find-scans.py`](tools/find-scans.py) — 普查腳本（內含踩過的坑，別重踩）
- [`tools/plate.py`](tools/plate.py) — 自動偵測畫芯，去紙邊但保住題箋與朱印
- [`tools/make-palette.py`](tools/make-palette.py) — k-means 抽色 + 朱色保留槽

## License

MIT（程式碼）。浮世繪掃描為 public domain，溯源記於 `assets/sources.json`。
