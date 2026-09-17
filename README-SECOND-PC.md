# 在第二台電腦執行微波料理助手

這份私人安裝包內含網站程式及 `.env` 設定。請只傳給可信任的電腦；不要上傳到 GitHub、公開雲端或分享連結。安裝包不含原電腦的料理歷程。

## 事前條件

- 第二台電腦已安裝並啟動 Docker Desktop，或具備 Docker Engine 與 Docker Compose。
- 可以連接網路，以取得 Python 基礎映像並呼叫外部 AI API。
- 本機連接埠 8000 未被其他程式占用。

## 啟動

1. 將私人 ZIP 解壓到第二台電腦的固定資料夾。
2. 在該資料夾開啟終端機，執行：

   ```text
   docker compose up --build -d
   ```

3. 在**第二台電腦**的瀏覽器開啟 `http://127.0.0.1:8000/`。
4. 測試說明書料理與手動模式，再測試 AI 建議模式。
5. 完成一次料理後按「我已完成這次料理，加入歷程」，確認歷程出現；重新啟動容器後再確認紀錄仍在。

若 8000 已被占用，可在 `.env` 增加 `MICROWAVE_HOST_PORT=8001`，重新執行啟動指令，並改開啟 `http://127.0.0.1:8001/`。

## 歷程與日常操作

第二台電腦的歷程保存在解壓資料夾的 `data/history.json`。首次啟動沒有此檔案是正常的；按下完成料理按鈕後才會建立。更新或重建容器時保留 `data/`，紀錄就會保留。不要把 `data/` 加進 Git 或新的安裝包。

```text
docker compose ps
docker compose logs --tail=50
docker compose stop
docker compose start
```

若要停止並移除容器，可執行 `docker compose down`；它不會刪除這個資料夾中的 `data/`。`docker compose up --build -d` 可重建並啟動。

## 密鑰與隱私

`.env` 僅供 Docker Compose 在啟動時提供環境變數，不會被複製進 Docker 映像檔，也不會由網站提供下載。若密鑰失效，需在第二台電腦的 `.env` 更新 `AI_API_KEY` 並重新建立容器。請勿分享此私人安裝包或將 `.env` 提交到 Git。

目前每台電腦各自執行一份後端並儲存自己的歷程；一台電腦關機不會影響另一台電腦。但外部 AI 模式仍需要第二台電腦可以連到 API 服務。
