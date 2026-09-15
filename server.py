from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
import json
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse, parse_qs
from uuid import uuid4
from recipes import RECIPES, recipe_steps

class MicrowaveHandler(SimpleHTTPRequestHandler):
    history_file = Path(__file__).with_name("history.json")
    history_lock = Lock()

    def end_headers(self):
        # 開發時每次重新取得最新網頁與料理資料。
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status, data):
        # 把 Python 字典轉成 JSON，再編碼成要傳送的位元組
        response = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def read_history(self):
        if not self.history_file.exists():
            return []
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save_history(self, records):
        temporary_file = self.history_file.with_suffix(".json.tmp")
        temporary_file.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        temporary_file.replace(self.history_file)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/api/history":
            self.send_json(404, {"message": "找不到此 API。"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if not 0 < content_length <= 10000:
                raise ValueError
            body = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"message": "歷程資料格式不正確。"})
            return

        allowed_modes = {"recipe": "說明書料理", "manual": "依包裝手動微波"}
        if not isinstance(body, dict) or body.get("mode") not in allowed_modes:
            self.send_json(400, {"message": "歷程模式不正確。"})
            return

        fields = {}
        for name in ("food", "detail", "program", "settings"):
            value = body.get(name)
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > 300:
                self.send_json(400, {"message": "歷程內容不完整或過長。"})
                return
            fields[name] = value.strip()

        record = {
            "id": uuid4().hex,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "mode": body["mode"],
            "mode_label": allowed_modes[body["mode"]],
            **fields,
        }
        try:
            with self.history_lock:
                records = self.read_history()
                records.insert(0, record)
                self.save_history(records[:200])
        except OSError:
            self.send_json(500, {"message": "無法寫入料理歷程。"})
            return
        self.send_json(201, {"message": "已加入料理歷程。", "record": record})

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/recipes":
            self.send_json(200, {"recipes": RECIPES})
            return

        if parsed_url.path == "/api/history":
            with self.history_lock:
                records = self.read_history()
            self.send_json(200, {"history": records})
            return

        if parsed_url.path == "/api/steps":
            query = parse_qs(parsed_url.query)
            mode = query.get("mode", ["manual"])[0]
            if mode == "recipe":
                try:
                    data = recipe_steps(query.get("recipe", [""])[0], query.get("portion", [""])[0])
                except ValueError as error:
                    self.send_json(400, {"message": str(error)})
                    return
                self.send_json(200, data)
                return
            if mode != "manual":
                self.send_json(400, {"message": "請選擇說明書料理或手動微波。"})
                return
            food_name = query.get("food", [""])[0].strip()
            food_state = query.get("state", [""])[0]

            state_names = {
                "chilled": "冷藏",
                "frozen": "冷凍"
            }

            if not food_name:
                self.send_json(400, {"message": "請先輸入食物名稱。"})
                return

            if food_state not in state_names:
                self.send_json(400, {"message": "食物狀態請選擇冷藏或冷凍。"})
                return

            state_label = state_names[food_state]
            weight_text = query.get("weight", [""])[0]

            try:
                weight = int(weight_text)
                if weight <= 0:
                    raise ValueError
            except ValueError:
                self.send_json(400, {"message": "重量請輸入大於 0 的整數公克。"})
                return
            
            power = query.get("power", [""])[0]

            power_watts = {
                "P100": 900,
                "P90": 810,
                "P80": 720,
                "P70": 630,
                "P60": 540,
                "P50": 450,
                "P40": 360,
                "P30": 270,
                "P20": 180,
                "P10": 90
            }

            if power not in power_watts:
                self.send_json(400, {"message": "請選擇有效的微波功率。"})
                return

            watts = power_watts[power]

            # 前端檢查不能取代後端驗證，直接呼叫 API 也要檢查。
            try:
                minutes = int(query.get("minutes", [""])[0])
                seconds = int(query.get("seconds", [""])[0])
                if not (0 <= minutes <= 95 and 0 <= seconds <= 59):
                    raise ValueError
            except ValueError:
                self.send_json(400, {"message": "加熱時間請填整數：分鐘 0～95，秒數 0～59，兩欄皆不可留白。"})
                return

            total_seconds = minutes * 60 + seconds
            if not 0 < total_seconds <= 95 * 60:
                self.send_json(400, {"message": "加熱時間須大於 0，且不可超過 95 分鐘。"})
                return

            time_label = f"{minutes:02d}:{seconds:02d}"
            
            data = {
                "message": (
                    f"{food_name}／{state_label}／{weight} 公克／{watts}W／{time_label}："
                    "以下是 HMR-DA2713 手動微波的操作順序。"
                    "功率與時間請依食物包裝指示確認。"
                ),
                "steps": [
                    "依包裝指示準備食物，使用可微波容器，放入爐內並關好爐門。",
                    "在待機狀態下，按「微波火力」，畫面會顯示 P100。",
                    f"按「＋／－」或重複按「微波火力」，直到顯示 {power}（{watts}W）。",
                    "按一次「開始／＋30秒」確認功率，畫面會顯示預設時間 15:00。",
                    f"按「＋／－」，把加熱時間調整至 {time_label}（{minutes} 分 {seconds} 秒）。",
                    "確認功率與時間後，再按一次「開始／＋30秒」開始加熱。"
                ],
                "history": {
                    "mode": "manual",
                    "food": food_name,
                    "detail": f"{state_label}／{weight} 公克",
                    "program": f"手動微波 {power}",
                    "settings": f"{watts}W／{time_label}"
                }
            }

            self.send_json(200, data)
        else:
            # 其他網址繼續提供 HTML、CSS 等檔案
            super().do_GET()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), MicrowaveHandler)
    print("伺服器已啟動：http://127.0.0.1:8000")
    server.serve_forever()
