# tts-pipeline

中文为主的 AI 语音（TTS）真人感制作向导，一套可复用的 Agent Skill。

按阶段和用户互动，主动索要素材，在每个关口给出建议，从场景识别、平台选型、说话人与音色、口语化脚本、发音校准、样片闸门，一路做到批量合成、自动加盲听 QA、后期与合规交付。目标是真假难辨、一次成型。覆盖四类场景：科普/教学解说、有声书/长篇叙事、播客/多人对话、数字人口播/实时语音。

- 入口与流程：SKILL.md（S0–S9 流程与运行规则）
- 跨 Agent 安装：INSTALL.md
- 参考资料：eferences/（原理、场景卡、平台、技法、提示词、词典、QA 与交付）
- 脚本：scripts/（建项目、多音字扫描、ASR 回检）
- 项目模板与试音文本：ssets/

> 注意：SKILL.md 内的模型名、价格、MCP 端点均为 2026-10 快照，执行前请联网核实。

遵循 [Agent Skills](https://agentskills.io) 开放标准（一个目录 + 带 YAML frontmatter 的 SKILL.md），同一份文件可跨多个 Agent 平台使用；安装目录因平台而异，见 INSTALL.md。
