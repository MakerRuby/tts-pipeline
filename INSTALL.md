# 安装到任意 Agent

> 作用：说明如何把本 skill 安装到各个 Agent 平台，以及装好后如何验证。
> 不负责：skill 的使用流程（见 SKILL.md）。
> 读者：用户本人。
> 更新触发：某个平台的 skills 路径变化时。
> 依赖：`scripts/` 需要 Python 3.9+，只用标准库；`zhconv` 为可选依赖，装上后支持繁简统一。ASR 转写需要用户自备，推荐 FunASR paraformer-zh 或 Whisper。

## 文件登记表

| 路径 | 职能 |
|---|---|
| `SKILL.md` | 入口：运行规则、S0–S9 流程、资源索引 |
| `references/principles.md` | 第一性原理与工作方法 |
| `references/scenarios.md` | 四类场景卡 |
| `references/platforms.md` | 平台选型、授权红线、语法对照（2026-10 快照） |
| `references/craft.md` | 音色、写稿、表演、对话、抽卡、后期技法 |
| `references/prompts.md` | P1–P6 提示词模板 |
| `references/lexicon.md` | 通用多音字与数字读法，同时是扫描脚本的数据源 |
| `references/qa-delivery.md` | 样片评审、诊断表、自动闸门、交付规范、合规 |
| `scripts/` | 建项目、发音扫描、ASR 回检 |
| `assets/project-starter/` | 项目目录模板 |
| `assets/examples/audition-text.md` | 试音文本 |
| `config/mcp.json` | ElevenLabs 托管 MCP 配置 |

`tts-pipeline/` 已符合 Agent Skills 开放标准（一个目录 + 带 YAML frontmatter 的 SKILL.md）。
该标准由 Anthropic 发起，已被 30+ 个 Agent 平台支持，**同一份文件无需修改即可跨平台使用**。

**但要注意：标准只规定了 SKILL.md 的内容格式，没有规定它放在哪个目录。**
目录位置由各家自己决定，这是跨平台唯一的坑。

## 1. 复制目录即可

把整个 `tts-pipeline` 目录拷进目标 Agent 的 skills 目录：

```bash
cp -r tts-pipeline ~/.claude/skills/
```

目录名必须与 frontmatter 的 `name` 一致（现在是 `tts-pipeline`）。改名要同时改 `SKILL.md` 第 2 行。

## 2. 各平台路径（关键：不是所有 Agent 都能读同一个位置）

Agent Skills 生态里有一个社区约定路径 `.agents/skills/`，常被称为 canonical。
**但只有一部分 Agent 原生扫描它。**

| Agent | 用户级路径 | 原生读 `~/.agents/skills/`？ |
|---|---|---|
| **Claude Code** | `~/.claude/skills/` | **否** — 文档未列此路径，必须放自己的目录 |
| **WorkBuddy** | `~/.workbuddy/skills/` | 否 |
| Codex / ChatGPT | `~/.codex/skills/` 或 `$HOME/.agents/skills/` | **是** |
| Cursor | `~/.cursor/skills/` 或 `~/.agents/skills/` | **是**（另外还兼容 `.claude/`、`~/.codex/`） |
| GitHub Copilot | `~/.copilot/skills/` 或 `~/.agents/skills/` | **是** |
| Gemini CLI | `~/.gemini/skills/` 或 `~/.agents/skills/` 别名 | **是**（`.agents` 优先级更高） |
| Windsurf | `~/.codeium/windsurf/skills/` | 否 |
| Trae / Kiro / Continue / Roo | `~/.trae/` `~/.kiro/` `~/.continue/` `~/.roo/` + `/skills/` | 否 |
| OpenCode | `~/.config/opencode/skills/` | 是（项目级 `.agents/skills/`） |

项目级（团队共享，可进 git）：
- Claude Code 用 `.claude/skills/`
- Codex / Cursor / Copilot / OpenCode 用 **`.agents/skills/`**

> **踩坑点**：`.agents/skills/`（**复数**）是多工具通用的约定；`.agent/skills/`（**单数**）是 Google Antigravity 专用的另一个东西。别写错。

Windows 上 `~` 即 `C:/Users/DELL/`。

## 3. 推荐拓扑：真实目录 + junction

因为 Claude Code 不读 `~/.agents/skills/`，最稳的做法是——**把真实文件放在 canonical，其余全部软链过去**：

```powershell
# 1) 真实目录（canonical，Codex / Cursor / Copilot / Gemini 原生可发现）
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
Copy-Item -Recurse "C:\Users\DELL\WorkBuddy\2026-10-29-00-15-47\tts-pipeline" "$env:USERPROFILE\.agents\skills\"

# 2) 需要软链的平台：目标目录必须已存在，链接名必须不存在
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.workbuddy\skills"

cmd /c mklink /J "$env:USERPROFILE\.claude\skills\tts-pipeline" "$env:USERPROFILE\.agents\skills\tts-pipeline"
cmd /c mklink /J "$env:USERPROFILE\.workbuddy\skills\tts-pipeline" "$env:USERPROFILE\.agents\skills\tts-pipeline"
```

一份源码，改一处全平台生效。`mklink /J` 对目录无需管理员；`ln -s` 在 Windows 上常因未开开发者模式失败。

## 4. 验证是否被发现

重启 Agent，然后问一个匹配触发词的问题：

```
我想做一期 AI 配音的科普视频
```

Agent 应当自动加载 skill，并从 S0 开始问你场景、用途、体量、约束和已有素材。不加载时依次排查：

1. `head -3 <安装路径>/tts-pipeline/SKILL.md` — 第 1 行必须是 `---`
2. frontmatter 的 `name` 是否等于目录名（只许小写字母、数字、连字符）
3. `description` 是否含具体触发词（"TTS""配音""旁白"），而不是泛泛的"处理音频"
4. 确认该平台支持的安装路径，对照第 2 节表格
5. `claude --debug` 查看 skill 发现过程与告警

## 5. 关于 `npx skills`

skills.sh 的 CLI，俗称 `npx skills`。它不止能装社区 skill：

| 命令 | 用途 |
|---|---|
| `npx skills find` | 搜索 skills.sh 市场（商业模式，公开 skill） |
| `npx skills add <repo>` | 安装，**支持 GitHub/GitLab URL、git URL、本地磁盘路径** |
| `npx skills add <path> --agent claude-code` | 只装到指定 Agent |
| `npx skills add <path> --agent '*'` | 装到所有支持的 Agent |
| `npx skills init my-skill` | 脚手架生成一个新 skill |
| `npx skills ls -g` / `check` / `update` | 列出全局安装 / 检查更新 / 更新 |

**本地自写的 skill 也可以用它装**（指向磁盘路径即可），好处是它会自动把 skill 放到**每个 Agent 各自的目录**，省去手动建链接。

它的行为特点要知道：不带 `-y` 会弹交互式勾选界面让你选装到哪些工具；带 `-y` 会按检测结果全选，可能在项目里一下子生成多个目录副本。想要干净可控的话，用第 3 节的 junction 方案。
