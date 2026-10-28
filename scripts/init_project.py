"""S0 建立语音制作项目目录。

用法：
    python init_project.py <目标目录> [--name 项目名] [--scenario A|B|C|D] [--chapters N]

从 assets/project-starter 复制模板，创建 script/ refs/ audio/ 子目录。
--chapters N：长篇按章生产，脚本放 script/ch01…chNN/，音频放 audio/*/chNN/。
已存在的文件不覆盖（便于对已有项目补齐缺失文件）。
"""
import argparse
import shutil
from pathlib import Path

STARTER = Path(__file__).resolve().parent.parent / "assets" / "project-starter"
DIRS = ["script", "refs/consent", "audio/raw", "audio/selected", "audio/master"]
SCRIPT_FILES = ["00_source.md", "01_spoken.md", "02_directed.md", "03_final.md"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--name", default=None)
    ap.add_argument("--scenario", default="{{A/B/C/D}}")
    ap.add_argument("--chapters", type=int, default=0)
    args = ap.parse_args()

    root = Path(args.target).resolve()
    root.mkdir(parents=True, exist_ok=True)
    name = args.name or root.name
    created, skipped = [], []

    for src in STARTER.iterdir():
        dst = root / src.name
        if dst.exists():
            skipped.append(src.name)
            continue
        if src.suffix == ".md":
            text = src.read_text(encoding="utf-8")
            text = text.replace("{{项目名}}", name).replace("{{A/B/C/D}}", args.scenario)
            dst.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        created.append(src.name)

    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    units = [f"ch{i:02d}" for i in range(1, args.chapters + 1)] if args.chapters else [""]
    for u in units:
        sdir = root / "script" / u
        sdir.mkdir(parents=True, exist_ok=True)
        for a in ("raw", "selected", "master"):
            (root / "audio" / a / u).mkdir(parents=True, exist_ok=True)
        for f in SCRIPT_FILES:
            p = sdir / f
            if not p.exists():
                p.write_text(f"<!-- {f}：见 README.md 登记表 -->\n", encoding="utf-8")
                created.append(str(p.relative_to(root)).replace("\\", "/"))

    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"项目目录：{root}")
    print("新建：" + (", ".join(created) or "无"))
    if skipped:
        print("已存在未覆盖：" + ", ".join(skipped))


if __name__ == "__main__":
    main()
