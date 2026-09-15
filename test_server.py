import json
import socket
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from recipes import RECIPES
from server import MicrowaveHandler


class QuietHandler(MicrowaveHandler):
    def log_message(self, *args):
        pass


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history_directory = tempfile.TemporaryDirectory()
        QuietHandler.history_file = Path(cls.history_directory.name) / "history.json"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.history_directory.cleanup()

    def request(self, path, params=None):
        try:
            response = urlopen(self.base + path + ("?" + urlencode(params) if params else ""), timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def post(self, path, data, raw=False):
        body = data if raw else json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = Request(self.base + path, data=body, method="POST",
                          headers={"Content-Type": "application/json"})
        try:
            response = urlopen(request, timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def recipe(self, code, portion, **extra):
        return self.request("/api/steps", dict(mode="recipe", recipe=code, portion=portion, **extra))

    def test_catalog_and_every_listed_portion(self):
        status, data = self.request("/api/recipes")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["recipes"]), 33)
        self.assertEqual(len({r["id"] for r in data["recipes"]}), 33)
        for recipe in data["recipes"]:
            for portion in recipe["portions"]:
                with self.subTest(recipe=recipe["id"], portion=portion["value"]):
                    status, result = self.recipe(recipe["id"], portion["value"])
                    self.assertEqual(status, 200)
                    self.assertIn(recipe["button"], " ".join(result["steps"]))
                    self.assertIn(str(recipe["page"]), result["source"])

    def test_idle_browser_connection_does_not_block_api(self):
        with socket.create_connection(self.server.server_address, timeout=2):
            self.assertEqual(self.request("/api/recipes")[0], 200)
        with urlopen(self.base + "/", timeout=3) as response:
            self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_frozen_fries_two_stages_and_panel_route(self):
        status, data = self.recipe("AF01", "300g", power="P10", minutes="1")
        self.assertEqual(status, 200)
        self.assertEqual(data["selection"]["total_time"], "22:00")
        self.assertEqual(data["selection"]["stages"], [
            {"setting": "燒烤 100% ＋ 烘烤 240°C", "time": "06:00"},
            {"setting": "燒烤 60% ＋ 烘烤 240°C", "time": "16:00"},
        ])
        self.assertTrue(any("氣炸食譜" in s and "AF01" in s for s in data["steps"]))
        self.assertFalse(any("按「微波火力」" in s for s in data["steps"]))

    def test_fish_direct_button(self):
        _, data = self.recipe("A02", "350g")
        self.assertEqual(data["selection"]["stages"], [{"setting": "P80（720W）", "time": "05:30"}])
        self.assertTrue(any("按面板「魚類」" in s for s in data["steps"]))
        self.assertFalse(any("確認子選單" in s for s in data["steps"]))

    def test_grains_and_special_units(self):
        _, data = self.recipe("Hd04", "200g")
        self.assertEqual(data["selection"]["total_time"], "30:30")
        self.assertEqual([s["time"] for s in data["selection"]["stages"]], ["05:30", "25:00"])
        self.assertTrue(any("確認子選單" in s for s in data["steps"]))
        self.assertEqual(self.recipe("dd07", "2 顆（每顆約 200g）")[0], 200)
        self.assertEqual(self.recipe("dd07", "400g")[0], 400)
        _, pasta = self.recipe("A06", "50g（另加冷水 450g）")
        self.assertIn("冷水", pasta["recipe"]["note"])

    def test_unsupported_inputs(self):
        for code, portion in [("炒飯", "300g"), ("AF01", "200g"), ("A02", "351g"), ("", "")]:
            status, data = self.recipe(code, portion)
            self.assertEqual(status, 400)
            self.assertNotIn("steps", data)
        self.assertEqual(self.request("/api/steps", {"mode": "unknown"})[0], 400)

    def test_manual_still_works_and_validates(self):
        params = dict(food="炒飯", state="chilled", weight="100", power="P80", minutes="2", seconds="30")
        status, data = self.request("/api/steps", params)
        self.assertEqual(status, 200)
        self.assertIn("02:30", data["steps"][4])
        for change in [dict(minutes="95", seconds="1"), dict(power=""), dict(weight="0"), dict(state="bad")]:
            self.assertEqual(self.request("/api/steps", params | change)[0], 400)

    def test_history_persists_recipe_and_manual_records(self):
        QuietHandler.history_file.unlink(missing_ok=True)
        self.assertEqual(self.request("/api/history"), (200, {"history": []}))

        _, recipe_steps_data = self.recipe("AF01", "300g")
        status, saved_recipe = self.post("/api/history", recipe_steps_data["history"])
        self.assertEqual(status, 201)
        self.assertEqual(saved_recipe["record"]["food"], "冷凍薯條")
        self.assertEqual(saved_recipe["record"]["mode_label"], "說明書料理")

        manual = {"mode": "manual", "food": "ABC", "detail": "冷凍／250 公克",
                  "program": "手動微波 P80", "settings": "720W／02:30"}
        self.assertEqual(self.post("/api/history", manual)[0], 201)
        status, data = self.request("/api/history")
        self.assertEqual(status, 200)
        self.assertEqual([r["food"] for r in data["history"]], ["ABC", "冷凍薯條"])
        self.assertTrue(QuietHandler.history_file.exists())

    def test_history_rejects_incomplete_or_invalid_data(self):
        valid = {"mode": "manual", "food": "ABC", "detail": "冷凍／250 公克",
                 "program": "手動微波 P80", "settings": "720W／02:30"}
        for data in [{}, valid | {"mode": "unknown"}, valid | {"food": ""}, valid | {"food": "x" * 301}]:
            self.assertEqual(self.post("/api/history", data)[0], 400)
        self.assertEqual(self.post("/api/history", b"not-json", raw=True)[0], 400)
        self.assertEqual(self.post("/api/unknown", valid)[0], 404)


if __name__ == "__main__":
    unittest.main()
