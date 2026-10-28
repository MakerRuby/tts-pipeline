"""S4 发音风险扫描：多音字、数字、英文/缩写、符号、超长句。

用法：
    python polyphone_scan.py <稿件.md> --project-lexicon <项目>/lexicon.md [--dialogue] [--max-len 25]

稿件用 script/02_directed.md（或分章的 script/chNN/02_directed.md）。
--dialogue：对话稿，去掉行首说话人前缀。

多音字清单读自 skill 的 references/lexicon.md §B 表格第一列（单一事实来源）。
项目词典表格第一列中出现的词，其中的多音字视为"已确认"，不再报告。
只用标准库；输出 Markdown，供 P3 发音审校使用。
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

SKILL_LEXICON = Path(__file__).resolve().parent.parent / "references" / "lexicon.md"
CONTEXT = 6

# 表演标签、HTML 注释等不参与朗读的标记
# 删除：注释、[英文标签]、[#中文指令]（豆包）、[旁白|角色]（P2 说话人标注）、
# CosyVoice 拼音 [h][ǎo]、(小写标签/数字调拼音)、<#0.5#> 等 <标记>。
# 保留原字：IndexTTS 的 <行|XING2> → 行（已标注，视为安全，见 ANNOTATED）。
MARKUP = re.compile(
    r"<!--.*?-->"
    r"|\[#[^\]]*\]"
    r"|\[[^\]\n]*\|[^\]\n]*\]"
    r"|(?:\[[a-züāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]{1,6}\])+"
    r"|\[[\x00-\x7F]*?\]"
    r"|\([a-z0-9 _-]+\)"
    r"|<[^>一-鿿]*>",
    re.S,
)
INDEXTTS = re.compile(r"<([一-鿿])\|[A-Za-z]+\d>")
SPEAKER = re.compile(r"(?m)^[ \t]*(?:\[S\d\]|[^\s：:，。！？]{1,6}[：:])[ \t]*")
NUMBER = re.compile(r"[-+−]?\d[\d,，.:：/%％\-–~]*\d?%?")
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9.+&'_-]*")
SYMBOL = re.compile(r"[%％℃°¥$€£@#&~～/\\|＋+×÷=<>≈≥≤]")
SENTENCE_END = re.compile(r"[。！？!?；;\n]+")


def load_polyphones(path):
    """读取 §B 表格第一列的单个汉字。"""
    chars = {}
    in_b = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_b = line.startswith("## B")
            continue
        if in_b and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            is_header = cells[1:2] == ["读音一"]
            if not is_header and len(cells) >= 3 and len(cells[0]) == 1 and "一" <= cells[0] <= "鿿":
                chars[cells[0]] = f"{cells[1]} / {cells[2]}"
    return chars


def load_project_words(path):
    """项目词典表格第一列（跳过表头和分隔行）。"""
    words = set()
    if not path:
        return words
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and not re.match(r"^\|\s*[-:]+", line):
            first = line.strip("|").split("|")[0].strip()
            if first and first not in {"原词", "字", "词"}:
                words.add(first)
    return words


def strip_markup(text, strip_speaker=False):
    """去掉不朗读的标记，用等长空格替换以保持字符位置。

    IndexTTS 的 <行|XING2> 保留原字"行"（放在原位置末尾）。
    strip_speaker：去掉行首"A：""主持人："这类说话人前缀（对话稿用）。
    """
    text = INDEXTTS.sub(lambda m: " " * (len(m.group(0)) - 1) + m.group(1), text)
    text = MARKUP.sub(lambda m: " " * len(m.group(0)), text)
    if strip_speaker:
        text = SPEAKER.sub(lambda m: " " * len(m.group(0)), text)
    return text


def annotated_positions(raw):
    """IndexTTS 已标注字在 strip_markup 结果中的位置（视为已确认）。"""
    return {m.end() - 1 for m in INDEXTTS.finditer(raw)}


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def ctx(text, start, end):
    s = text[max(0, start - CONTEXT):start]
    e = text[end:end + CONTEXT]
    return (s + "【" + text[start:end] + "】" + e).replace("\n", " ").replace("|", "｜")


def covered_positions(text, words):
    """项目词典词所覆盖的字符位置（一次算好，长篇也快）。"""
    pos = set()
    for w in words:
        for m in re.finditer(re.escape(w), text):
            pos.update(range(m.start(), m.end()))
    return pos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--project-lexicon")
    ap.add_argument("--max-len", type=int, default=25, help="超长句阈值（字），默认 25")
    ap.add_argument("--max-forms", type=int, default=8, help="每个多音字最多列出的词形数，默认 8")
    ap.add_argument("--dialogue", action="store_true", help="对话稿：去掉行首说话人前缀（A：/[S1]）")
    args = ap.parse_args()

    raw = Path(args.script).read_text(encoding="utf-8")
    text = strip_markup(raw, strip_speaker=args.dialogue)
    polys = load_polyphones(SKILL_LEXICON)
    words = load_project_words(args.project_lexicon)

    by_char = defaultdict(list)
    done = covered_positions(text, words) | annotated_positions(raw)
    for i, ch in enumerate(text):
        if ch in polys and i not in done:
            by_char[ch].append(i)

    out = [f"# 发音风险扫描：{Path(args.script).name}", ""]
    out.append(f"## 1. 多音字（{sum(len(v) for v in by_char.values())} 处，{len(by_char)} 个字）")
    out.append("")
    out.append(f"同一词形（前后各一字）合并计数，每个词形只示例首次出现；每字最多列 {args.max_forms} 个词形。")
    out.append("")
    if by_char:
        out.append("| 字 | 常见读音 | 词形 | 次数 | 首次行 | 上下文 |")
        out.append("|---|---|---|---|---|---|")
        for ch in sorted(by_char, key=lambda c: -len(by_char[c])):
            forms = {}
            for i in by_char[ch]:
                form = text[max(0, i - 1):i + 2].strip() or ch
                forms.setdefault(form, []).append(i)
            ranked = sorted(forms.items(), key=lambda kv: -len(kv[1]))
            for form, idxs in ranked[:args.max_forms]:
                i = idxs[0]
                out.append(f"| {ch} | {polys[ch]} | {form} | {len(idxs)} | {line_of(text, i)} | {ctx(text, i, i + 1)} |")
            if len(ranked) > args.max_forms:
                out.append(f"| {ch} | | 另有 {len(ranked) - args.max_forms} 个词形 | | | 用 --max-forms 调大 |")
    else:
        out.append("未命中。")

    sections = [
        ("2. 数字（需按 lexicon §C 写成读法）", NUMBER),
        ("3. 英文 / 缩写（定读法：逐字母或按词）", LATIN),
        ("4. 符号", SYMBOL),
    ]
    for title, pat in sections:
        hits = [m for m in pat.finditer(text) if m.group(0).strip("-–~,，.:：/")]
        out += ["", f"## {title}（{len(hits)} 处）", ""]
        if hits:
            out.append("| 原文 | 行 | 上下文 |")
            out.append("|---|---|---|")
            for m in hits:
                out.append(f"| {m.group(0)} | {line_of(text, m.start())} | {ctx(text, m.start(), m.end())} |")
        else:
            out.append("无。")

    long_s = []
    pos = 0
    for seg in SENTENCE_END.split(text):
        start = text.find(seg, pos)
        pos = start + len(seg)
        han = len(re.findall(r"[一-鿿]", seg))
        if han > args.max_len:
            long_s.append((line_of(text, start), han, seg.strip()[:40]))
    out += ["", f"## 5. 超长句（>{args.max_len} 字，{len(long_s)} 句，S3 应已拆分）", ""]
    if long_s:
        out.append("| 行 | 字数 | 开头 |")
        out.append("|---|---|---|")
        for ln, n, head in long_s:
            out.append(f"| {ln} | {n} | {head.replace('|', '｜')}… |")
    else:
        out.append("无。")

    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
