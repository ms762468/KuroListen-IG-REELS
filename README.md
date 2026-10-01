# KuroListen IG Reels

將 LINE 聊天中的有趣故事改寫成 30 秒內的口說 Reels。阿玲本人敘述，引用時可微幅變聲，畫面搭配毛孩照片，不需多角演戲。

## 使用方式

在 Codex 開啟這個專案，上傳新的 LINE CSV 或 ZIP，說「幫我生成 Reels 腳本」。專案的 AGENTS.md 會引導使用 `skills/kuro-reels/SKILL.md`。亦可將 `skills/kuro-reels` 資料夾複製到個人 Codex skills 目錄，使用 `$kuro-reels` 指定呼叫。

技能負責寫作判斷；`scripts/ingest.py` 負責比對檔案與訊息。它不會自行編故事。每次先執行：

```text
python skills/kuro-reels/scripts/ingest.py 新聊天.zip --project . --commit --report tmp/import_report.json
```

相同匯出自動跳過；新訊息先檢查是否真的屬於新情境。同一毛孩、同一家長的不同故事可以另做一篇。相同事件換標題或笑話不算新故事。顯示名稱可能重複，不能只靠名字合併聊天室。

## 本批成果

追加「家長確認高光」30 篇，累計 107 篇。新增稿在 `outputs/20261001_highlights/`，選題文字在 `data/highlight_specs.tsv`。每份增加家長原文確認，保留已知資訊與更正的先後順序；這些是該次家長的回饋，不是整體準確率統計。原本 77 篇保留不變。新增批次口述估時 25–28 秒。

可重建本批新增 Word（相同來源範圍已存在時略過）：

```text
python skills/kuro-reels/scripts/build_highlights.py --project . --specs data/highlight_specs.tsv --batch 20261001_highlights
```

`deliverables/` 同時提供新增 30 篇與累計 107 篇的壓縮檔。

2026 年 10 月 1 日提供的 127 個聊天室，共整理 77 份腳本，來自 71 個聊天室，6 個聊天室各有兩篇。55 個只有行政對話的聊天室略過，1 個缺少家長完整回應的案例暫不改編。這是本批已選情境，不代表所有歷史素材都已用完。

每篇 Word 都有帳號名稱、毛孩名字、原始日期、搜尋關鍵字、來源邏輯列、分段口說及畫面提示。口說長度約 23–28 秒，為文字估算，拍攝時仍應試讀。照片不在 CSV 內，需另選獲准的照片。公開台詞預設不含姓名。

家長更正或雙方理解不同也可保留為故事，呈現兩邊說法而不強行判定對錯。溝通轉述不等於可驗證的動物原話。

## 檔案

- `skills/kuro-reels/`：可安裝技能及匯入工具。
- `data/raw/20261001/`：依使用者明確要求保留並同步的原始 ZIP 和 127 份 CSV。
- `data/story_manifest.json`：已產生故事、來源訊息鍵及 Word 路徑。
- `data/ingest_state.json`：跨匯出的聊天室與訊息指紋。
- `data/story_specs.tsv`：本批腳本的可編輯文字素材。
- `data/skipped_chats.json`：略過聊天室及原因；後續新增實際故事仍可處理。
- `outputs/20261001_reels/`：Word、索引及略過清單。
- `deliverables/`：供下載的腳本 ZIP。

原始資料含私人對話；同步到本儲存庫不代表可直接公開照片、原文截圖或客戶身分，也不代表可傳至其他服務。
