"""S7 ASR 回检：原文 vs 转写，计算字错率（CER）并列出逐处差异。

用法：
    python asr_check.py <原文.md> <转写.txt|.srt> [--dialogue] [--threshold 0.02]

原文用 script/02_directed.md（标签会被自动去掉）。不要用 03_final：
CosyVoice 等平台的拼音标注会替换原字，导致误报漏读。
--dialogue：对话稿，去掉行首说话人前缀（A：/[S1]）。
转写由你选用的 ASR 产出（中文推荐 FunASR paraformer-zh，英文 Whisper large-v3）。
最简方式：pip install funasr 后，用 AutoModel(model="paraformer-zh") 对音频调用 generate，把文本存成 .txt；
或用剪映、飞书妙记等工具导出 SRT 字幕。
归一化方法借鉴 seed-tts-eval：去表演标记与标点、全角转半角、英文小写；
若已安装 zhconv 则繁转简。错误数由 difflib 对齐得出（S+D+I，近似最小编辑距离）。
CER 超过阈值时退出码为 1。只依赖标准库（zhconv 可选）。
"""
import argparse
import difflib
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from polyphone_scan import strip_markup  # noqa: E402  与扫描脚本共用标记规则

try:
    import zhconv
except ImportError:
    zhconv = None

CONTEXT = 8


def read_transcript(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.lower().endswith(".srt"):
        lines = [l for l in text.splitlines() if l.strip() and not l.strip().isdigit() and "-->" not in l]
        text = "\n".join(lines)
    return text


def normalize(text):
    """返回 (归一化字符串, 每个字符在原文中的行号)。"""
    chars, lines = [], []
    line = 1
    for ch in text:
        if ch == "\n":
            line += 1
            continue
        c = unicodedata.normalize("NFKC", ch).lower()
        if zhconv:
            c = zhconv.convert(c, "zh-cn")
        for x in c:
            cat = unicodedata.category(x)
            if cat.startswith(("P", "Z", "S", "C")):
                continue
            chars.append(x)
            lines.append(line)
    return "".join(chars), lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("transcript")
    ap.add_argument("--threshold", type=float, default=0.02)
    ap.add_argument("--dialogue", action="store_true")
    args = ap.parse_args()

    ref_raw = strip_markup(Path(args.original).read_text(encoding="utf-8"), strip_speaker=args.dialogue)
    ref, ref_lines = normalize(ref_raw)
    hyp, _ = normalize(read_transcript(args.transcript))
    if not ref:
        sys.exit("原文为空")

    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
    rows, s = [], {"替换": 0, "漏读": 0, "多读": 0}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a, b = ref[i1:i2], hyp[j1:j2]
        if tag == "replace":
            n = min(len(a), len(b))
            s["替换"] += n
            if len(a) > len(b):
                s["漏读"] += len(a) - n
            else:
                s["多读"] += len(b) - n
            kind = "替换"
        elif tag == "delete":
            s["漏读"] += len(a)
            kind = "漏读"
        else:
            s["多读"] += len(b)
            kind = "多读"
        line = ref_lines[min(i1, len(ref_lines) - 1)]
        context = ref[max(0, i1 - CONTEXT):i1] + "【" + a + "】" + ref[i2:i2 + CONTEXT]
        rows.append(f"| {line} | {kind} | {a or '∅'} | {b or '∅'} | {context} |")

    errors = sum(s.values())
    cer = errors / len(ref)
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"# ASR 回检：{Path(args.original).name}\n")
    print(f"- 原文字数（归一化后）：{len(ref)}")
    print(f"- 错误：{errors}（替换 {s['替换']} / 漏读 {s['漏读']} / 多读 {s['多读']}）")
    print(f"- CER：{cer:.2%}（阈值 {args.threshold:.0%}）→ {'通过' if cer <= args.threshold else '未通过'}")
    if not zhconv:
        print("- 提示：未安装 zhconv，未做繁简统一")
    print("\n每一处差异都需人工判断：音频错 / ASR 错。可交给 P4 归类。\n")
    if rows:
        print("| 原文行 | 类型 | 原文 | 转写 | 上下文 |")
        print("|---|---|---|---|---|")
        print("\n".join(rows))
    else:
        print("无差异。")
    sys.exit(0 if cer <= args.threshold else 1)


if __name__ == "__main__":
    main()
