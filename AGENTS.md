# KuroListen Reels workflow

當使用者提供 LINE 聊天紀錄並要求 Reels，讀取 skills/kuro-reels/SKILL.md。
先讀 data/story_manifest.json，執行技能的 ingest.py 進行重複匯入與聊天室比對，再讀取新情境。相同事件不得重複產生；不同情境可新增。
口說敘述加毛孩照片，無多角演戲。內部前情提要要有帳號／毛孩名與來源日期，公開台詞預設匿名。
此專案使用者已授權原始聊天紀錄同步到本遠端；不得擴大傳送到其他服務或改變儲存庫可見性。
