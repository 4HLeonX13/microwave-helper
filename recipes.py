"""HMR-DA2713 中文說明書第 16–19 頁；人工核對表格後建立。

這是面板行程資料，不是通用食譜或食物重量換算公式。
時間依階段順序對應火力，不推算未列出的份量。
"""

SOURCE = "HMR-DA2713 使用說明書（UM_HMR-DA2713(EN_TW)_2504.pdf）"
POWER_WATTS = {f"P{level}": level * 9 for level in range(10, 101, 10)}
RECIPES = []


def add(code, name, button, page, settings, portions, note=""):
    choices = []
    for portion, times in portions:
        durations = times.split("+")
        assert len(durations) == len(settings)
        stages = [dict(setting=setting, time=time) for setting, time in zip(settings, durations)]
        total = sum(int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in durations)
        choices.append(dict(value=portion, label=portion, stages=stages,
                            total_time=f"{total // 60:02d}:{total % 60:02d}"))
    RECIPES.append(dict(id=code, name=name, button=button, page=page,
                        source=SOURCE, portions=choices, note=note))


add("Hd01", "藜麥", "健康食譜", 16, ["P100（900W）", "P50（450W）"], [("100g", "03:00+15:00"), ("200g", "05:00+15:00")])
add("Hd02", "北非小米", "健康食譜", 16, ["P100（900W）", "P50（450W）"], [("200g", "04:00+08:00"), ("300g", "05:00+10:00")])
add("Hd03", "通心粉", "健康食譜", 16, ["P80（720W）"], [("100g", "10:00"), ("200g", "12:00")])
add("Hd04", "糙米", "健康食譜", 16, ["P100（900W）", "P50（450W）"], [("200g", "05:30+25:00"), ("300g", "08:00+30:00")])
add("Hd05", "麥片", "健康食譜", 16, ["P100（900W）", "P50（450W）"], [("2oz（57g）", "03:30+03:30"), ("4oz（114g）", "05:30+05:30")])

for code, name, portions in [
    ("dd01", "冷凍豌豆", [("200g", "04:00"), ("400g", "07:00")]),
    ("dd02", "冷凍混合蔬菜", [("200g", "04:00"), ("400g", "07:00")]),
    ("dd03", "冷凍花椰菜", [("200g", "05:00"), ("400g", "08:00")]),
    ("dd04", "新鮮菠菜", [("200g", "02:30"), ("400g", "04:30")]),
    ("dd05", "冷凍青豆", [("200g", "05:00"), ("400g", "08:00")]),
    ("dd06", "沒有皮的馬鈴薯", [("400g", "06:00"), ("800g", "10:00")]),
    ("dd07", "帶皮馬鈴薯", [("2 顆（每顆約 200g）", "08:30"), ("4 顆（每顆約 200g）", "15:00")]),
]:
    add(code, name, "日常食譜", 17, ["P100（900W）"], portions,
        "加熱前先將馬鈴薯表皮戳孔（說明書第 6 頁）。" if code == "dd07" else "")
add("dd08", "冷凍烤寬麵條", "日常食譜", 17, ["組合火力 C-1"], [("300g", "15:00"), ("600g", "20:00")])
add("dd09", "烤雞胸肉", "日常食譜", 17, ["燒烤 60% ＋ 烘烤 240°C"], [("200g", "16:00"), ("400g", "20:00")])
add("dd10", "羊排", "日常食譜", 17, ["組合火力 C-4"], [("900g", "35:00")])
add("dd11", "烤牛肉", "日常食譜", 17, ["組合火力 C-4"], [("900g", "35:00")])
add("dd12", "烤大蒜麵包", "日常食譜", 17, ["組合火力 C-4"], [("200g", "09:00")])

add("A01", "爆米花", "爆米花", 17, ["P100（900W）"], [("50g", "01:40"), ("100g", "02:00")])
add("A02", "魚類", "魚類", 18, ["P80（720W）"], [("150g", "03:00"), ("250g", "04:00"), ("350g", "05:30"), ("450g", "06:30"), ("650g", "08:30")])
add("A03", "肉類", "肉類", 18, ["組合火力 C-4"], [("500g", "29:00"), ("750g", "34:00"), ("1000g", "39:00"), ("1200g", "44:00")], "聽到提示聲時翻動食物。")
add("A04", "蛋糕", "蛋糕", 18, ["烘烤 150°C"], [("475g", "65:00")])
add("A05", "披薩", "披薩", 18, ["組合火力 C-4"], [("100g", "08:00"), ("200g", "10:00"), ("300g", "12:00")])
add("A06", "義大利麵", "義大利麵", 18, ["P80（720W）"], [("50g（另加冷水 450g）", "18:00"), ("100g（另加冷水 800g）", "20:00"), ("150g（另加冷水 1200g）", "22:00")], "份量按麵的重量選擇；冷水需另外加入，不能把麵與水的總重量當成面板份量。")

air = "燒烤 60% ＋ 烘烤 240°C"
add("AF01", "冷凍薯條", "氣炸食譜", 18, ["燒烤 100% ＋ 烘烤 240°C", air], [("300g", "06:00+16:00")])
add("AF02", "冷凍薯角", "氣炸食譜", 18, ["燒烤 100% ＋ 烘烤 240°C", air], [("450g", "15:00+15:00")])
for code, name, page, portion, time in [
    ("AF03", "冷凍雞塊", 18, "350g", "24:00"),
    ("AF04", "冷凍炸魷魚", 18, "250g", "18:00"),
    ("AF05", "冷凍洋蔥圈", 18, "250g", "16:00"),
    ("AF06", "冷凍炸蝦", 19, "250g", "18:00"),
    ("AF07", "冷凍炸雞排", 19, "400g", "24:00"),
    ("AF08", "烤新鮮魚片", 19, "300g", "18:00"),
    ("AF09", "冷凍水牛雞翅", 19, "420g", "22:00"),
    ("AF10", "冷凍炸雞翅", 19, "500g（每塊約 40g）", "28:00"),
]:
    add(code, name, "氣炸食譜", page, [air], [(portion, time)])


def recipe_steps(recipe_id, portion):
    recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if recipe is None:
        raise ValueError("這道料理沒有已核對的行程資料，請選擇清單中的料理，或改用包裝指示手動設定。")
    choice = next((p for p in recipe["portions"] if p["value"] == portion), None)
    if choice is None:
        raise ValueError("此份量未列在說明書中，請選擇提供的份量；程式不會按比例推算。")
    button, code = recipe["button"], recipe["id"]
    steps = ["依原食譜準備食物，核對食物名稱中的冷凍／新鮮條件與指定份量，使用適合本行程火力的容器。"]
    settings = " ".join(stage["setting"] for stage in choice["stages"])
    if all(stage["setting"].startswith("P") for stage in choice["stages"]):
        steps.append("使用可微波容器；不要使用金屬容器、金屬架或烤盤（說明書第 8、11 頁）。")
    elif "組合" in settings:
        steps.append("本行程含組合火力，使用同時適合微波與高溫烹調的器具；C-1、C-4 請勿使用金屬器具（說明書第 14 頁）。")
    else:
        steps.append("使用適合燒烤／烘烤溫度的耐熱器具；僅標示可微波的塑膠容器不適用。")
    if code.startswith("Hd"):
        steps.append("本表未提供完整加水量與備料方法，請先依食譜完成備料，不要直接將乾穀物或乾麵空燒。")
    if recipe["note"]:
        steps.append(recipe["note"])
    steps.append("將食物放入爐內並關好爐門，從待機狀態開始設定。")
    if button == "氣炸食譜":
        steps += [f"重複按面板「氣炸食譜」，直到顯示 {code}（{recipe['name']}）。",
                  f"本行程固定對應 {portion}，不另外設定重量、微波功率或時間。"]
    elif button in ("健康食譜", "日常食譜"):
        steps += [f"重複按面板「{button}」，直到顯示 {code}（{recipe['name']}）。",
                  "按「開始/+30秒」確認子選單，畫面顯示預設重量或份量。",
                  f"按「－／＋」選擇 {portion}。"]
    else:
        steps += [f"按面板「{button}」，再重複按同一按鍵，直到顯示對應份量：{portion}。"]
    steps.append("按「開始/+30秒」開始烹調，機器會依選定行程自動控制火力與時間。")
    if button == "氣炸食譜":
        steps.append("烹調中聽到提示聲時翻動食物（說明書第 19 頁）。")
    stage_summary = "；".join(f"{stage['setting']}／{stage['time']}" for stage in choice["stages"])
    history = dict(
        mode="recipe",
        food=recipe["name"],
        detail=portion,
        program=f"{button} {code}",
        settings=stage_summary,
    )
    return dict(message=f"{recipe['name']}／{portion}／{button} {code}",
                steps=steps, recipe=recipe, selection=choice, history=history,
                source=f"{SOURCE}，料理表第 {recipe['page']} 頁；操作見第 "
                       + ("18–19" if button == "氣炸食譜" else "16" if button in ("健康食譜", "日常食譜") else "17–18") + " 頁。")
