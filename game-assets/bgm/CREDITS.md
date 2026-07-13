# 音樂出處

這個資料夾裡的三首曲子**不是**本專案的作品。它們的授權允許再散佈（這正是選它們的原因——
公開 repo 裡的檔案任何人都能 fork 或下載，多數日系素材站的規約禁止這件事），
但 CC BY 要求標註作者與授權，而且標註要跟著檔案走。你 fork 了這個 repo，就繼承這份義務。

| 檔案 | 曲名 | 作曲 | 授權 | 來源 |
|---|---|---|---|---|
| `01-shinrin-yoku.mp3` | Shinrin-Yoku | Patrick de Arteaga | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | https://opengameart.org/content/shinrin-yoku |
| `02-sakura-variation.mp3` | Sakura (Variation) | WuxiaScrub | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | https://opengameart.org/content/sakura-variation |
| `03-ishikari-lore.mp3` | Ishikari Lore | Kevin MacLeod | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | https://incompetech.com/ |
| `04-ripples.mp3` | Ripples | Kevin MacLeod | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | https://incompetech.com/ |

標註字串（作者指定的寫法）：

```
"Shinrin-Yoku" by Patrick de Arteaga (https://patrickdearteaga.com) — CC BY 4.0
    ↑ 作者在 OGA 頁上指明：「Attribute as Patrick de Arteaga and a link to patrickdearteaga.com」
"Sakura (Variation)" by WuxiaScrub (https://wuxia-scrub.itch.io/) — CC BY 4.0
    ↑ 作者在 OGA 頁上指明：「Please attribute to WuxiaScrub and link to my itch.io profile like so:
      WuxiaScrub (https://wuxia-scrub.itch.io/)」
"Ishikari Lore" Kevin MacLeod (incompetech.com) — Licensed under Creative Commons: By Attribution 4.0 License
                                                  http://creativecommons.org/licenses/by/4.0/
"Ripples" Kevin MacLeod (incompetech.com) — Licensed under Creative Commons: By Attribution 4.0 License
                                            http://creativecommons.org/licenses/by/4.0/
```

Patrick de Arteaga 與 WuxiaScrub 都把連結寫進了指定的標註形式——那些連結是授權義務，
不是禮貌，刪掉就不合規了。四首全是 CC BY（沒有 CC0），所以標註對每一首都是必要的。

原檔皆為 CC 授權（允許改作／格式轉換）：Shinrin-Yoku 與 Sakura (Variation) 的原始檔是 ogg，
Kevin MacLeod 兩首的原檔是 320 kbps mp3。四首都以 ffmpeg 轉為 128 kbps mp3——Safari 對
Ogg Vorbis 的支援不可靠，統一成 mp3 才能到處播。

遊戲裡另有一首 8-bit 道中曲，那是本作用 Web Audio 合成的（`index.html` 裡的 `bgmChiptune`），
不是錄音，也沒有第三方授權；三首 mp3 都載不到時會由它接手。
