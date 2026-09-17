(function (root) {
    "use strict";

    // 座標以裁切後的面板圖 465 × 964 為基準，轉成百分比後可隨圖片縮放。
    const positions = {
        popcorn: [17.7, 10.2], fish: [49.5, 10.2], meat: [80.9, 10.2],
        cake: [17.7, 20.1], pizza: [49.5, 20.1], pasta: [80.9, 20.1],
        healthy: [17.7, 29.7], daily: [49.5, 29.7], airfry: [80.9, 29.7],
        microwave: [17.7, 60.2], timer: [49.5, 60.2], defrost: [80.9, 60.2],
        grill: [17.7, 70.2], combo: [49.5, 70.2], oven: [80.9, 70.2],
        minus: [17.7, 82.5], plus: [80.9, 82.5],
        stop: [17.7, 95.5], start: [80.9, 95.5]
    };
    const labels = {
        popcorn: "爆米花", fish: "魚類", meat: "肉類", cake: "蛋糕",
        pizza: "披薩", pasta: "義大利麵", healthy: "健康食譜",
        daily: "日常食譜", airfry: "氣炸食譜", microwave: "微波火力",
        timer: "定時", defrost: "解凍", grill: "燒烤火力",
        combo: "組合火力", oven: "烘烤／氣炸火力",
        minus: "－", plus: "＋", stop: "停止／取消", start: "開始／＋30秒"
    };
    const names = {
        "爆米花": "popcorn", "魚類": "fish", "肉類": "meat", "蛋糕": "cake",
        "披薩": "pizza", "義大利麵": "pasta", "健康食譜": "healthy",
        "日常食譜": "daily", "氣炸食譜": "airfry", "微波火力": "microwave",
        "定時": "timer", "解凍": "defrost", "燒烤火力": "grill",
        "組合火力": "combo", "烘烤/氣炸火力": "oven",
        "停止/取消": "stop", "開始/+30秒": "start", "開始／＋30秒": "start"
    };

    function buttonForStep(step) {
        if (typeof step !== "string") return null;
        // 「＋／－或重複按微波火力」是二選一；演示用「－」由 P100 往下調。
        if (/按[「『][＋+][／/][－-][」』].*微波火力/.test(step)) return "minus";
        if (/按[「『][＋+][／/][－-][」』]/.test(step)) {
            const time = step.match(/(\d{1,2}):(\d{2})/);
            return time && Number(time[1]) * 60 + Number(time[2]) > 900 ? "plus" : "minus";
        }
        if (/按[「『][－-][／/][＋+][」』]/.test(step)) return "plus";
        const panelButton = step.match(/(?:按|重複按)(?:一次)?(?:面板)?[「『]([^」』]+)[」』]/);
        if (panelButton) return names[panelButton[1]] || null;
        return null;
    }

    function createDemo({ section, details, dot, caption, counter, playButton, previousButton,
                          nextButton, stepsList }) {
        let steps = [];
        let index = 0;
        let timer = null;

        function stopTimer() {
            if (timer !== null) clearInterval(timer);
            timer = null;
            playButton.textContent = "播放演示";
        }

        function showStep(nextIndex) {
            if (!steps.length) return;
            index = Math.max(0, Math.min(nextIndex, steps.length - 1));
            const key = buttonForStep(steps[index]);
            dot.hidden = !key;
            if (key) {
                dot.style.left = `${positions[key][0]}%`;
                dot.style.top = `${positions[key][1]}%`;
                dot.setAttribute("aria-label", `模擬按下${labels[key]}`);
            }
            counter.textContent = `步驟 ${index + 1}／${steps.length}`;
            caption.textContent = key
                ? `${steps[index]}　【紅點：${labels[key]}】`
                : `${steps[index]}　【這一步不需按面板】`;
            Array.from(stepsList.children).forEach((item, itemIndex) => {
                item.classList.toggle("demo-current", itemIndex === index);
            });
            previousButton.disabled = index === 0;
            nextButton.disabled = index === steps.length - 1;
        }

        function play() {
            if (!steps.length) return;
            if (timer !== null) {
                stopTimer();
                return;
            }
            if (index === steps.length - 1) showStep(0);
            playButton.textContent = "暫停演示";
            timer = setInterval(() => {
                if (index === steps.length - 1) {
                    stopTimer();
                } else {
                    showStep(index + 1);
                }
            }, 2000);
        }

        playButton.addEventListener("click", play);
        previousButton.addEventListener("click", () => {
            stopTimer();
            showStep(index - 1);
        });
        nextButton.addEventListener("click", () => {
            stopTimer();
            showStep(index + 1);
        });

        return {
            reset() {
                stopTimer();
                steps = [];
                section.hidden = true;
                details.hidden = true;
                dot.hidden = true;
                Array.from(stepsList.children).forEach(item => item.classList.remove("demo-current"));
            },
            load(newSteps) {
                stopTimer();
                steps = newSteps.filter(step => typeof step === "string");
                section.hidden = steps.length === 0;
                details.hidden = steps.length === 0;
                if (!steps.length) return;
                const firstPress = steps.findIndex(step => buttonForStep(step));
                showStep(firstPress >= 0 ? firstPress : 0);
                // 取得結果後自動開始；使用者可暫停、重播或逐步切換。
                play();
            }
        };
    }

    root.PanelDemo = { buttonForStep, createDemo };
    if (typeof module !== "undefined" && module.exports) module.exports = root.PanelDemo;
})(typeof window !== "undefined" ? window : globalThis);
