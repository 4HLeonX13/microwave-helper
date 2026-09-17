"""Create a private Docker install ZIP for another trusted computer."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from external_api import _read_env_file


ROOT = Path(__file__).resolve().parent
FILES = (
    ".env",
    ".dockerignore",
    "Dockerfile",
    "compose.yaml",
    "README-SECOND-PC.md",
    "server.py",
    "recipes.py",
    "external_api.py",
    "index.html",
    "style.css",
    "panel_demo.js",
    "assets/hmr-da2713-panel.png",
)


def main():
    if not _read_env_file(ROOT / ".env").get("AI_API_KEY"):
        raise SystemExit("私密安裝包需要 .env 中有 AI_API_KEY。")

    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit(f"缺少安裝檔案：{', '.join(missing)}")

    output = ROOT / "dist" / "microwave-helper-private.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(ROOT / name, arcname=name)
    print(f"已建立私人安裝包：{output}（{len(FILES)} 個檔案）")


if __name__ == "__main__":
    main()
