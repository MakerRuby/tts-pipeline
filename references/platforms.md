# 平台选型与语法速查（2026-10-29 快照）

> 作用：在 S1 帮用户选平台；在 S3/S4 查目标平台的表演标签和发音写法。
> 不负责：通用技法（见 craft.md）；交付规范（见 qa-delivery.md）。
> 读者：执行 skill 的 agent。
> 更新触发：每次 S1 联网核实时，发现与本表不符就更新本表，并在表头改日期。
> **时效警告**：TTS 平台几个月就会换代。凡是涉及型号、价格、授权、停服的内容，S1 都要先用 WebSearch 核实一次。本表只作初筛参考。
> "中文自然度"一栏是定性判断，来源是厂商定位和社区评价，**没有经过独立盲测**。最终用 S2 的试音盲选来决定。

## §1 决策树（S1 先走这个）

1. **实时 / 低延迟（D2）**：
   - 境内：火山实时语音（端到端）、百炼 qwen3-tts-flash-realtime、MiniMax turbo；
   - 海外：Cartesia Sonic、ElevenLabs v4 Turbo；
   - 本机：CosyVoice3 双流式、Qwen3-TTS（需要自己优化推理）。
2. **多人对话（C）**：
   - 中文：豆包播客模型（云）、MOSS-TTSD / FireRedTTS-2（本机，许可证要先核实）；
   - 英文：ElevenLabs Text to Dialogue、Dia2（本机，Apache）。
3. **需要严格控时长（A 对画面、D1）**：IndexTTS-2.5（duration_factor 取 0.5–2.0，大于 1 放慢）；或者选有语速参数的云平台，写稿时就控制字数。
4. **数据不能出本机**：CosyVoice3、Qwen3-TTS、VoxCPM2、IndexTTS-2.5、GPT-SoVITS；或讯飞离线 SDK。
5. **其他中文项目（A / B 的默认路径）**：
   - 云端优先：火山豆包 2.0、MiniMax speech-2.8、百炼（CosyVoice / Qwen-TTS）；
   - 英文或多语种为主时选 ElevenLabs v4；
   - 中文多音字要求高时，优先选**支持拼音标注**的平台（MiniMax、CosyVoice、IndexTTS、讯飞），ElevenLabs 只能靠发音词典。
6. **网络**：不方便访问海外服务时，排除 ElevenLabs、Gemini、Cartesia。

输出给用户的格式：1 个推荐 + 1 个备选。每个都写明选它的理由、优势、代价、对后续阶段的影响（比如"选它，S4 只能用发音词典"）。

## 2. 商业平台

| 平台 | 当前型号（截至 2026-10） | 中文 | 情绪控制 | 发音控制 | 多人 | 实时 | 克隆 | 价格量级 |
|---|---|---|---|---|---|---|---|---|
| 火山 / 豆包语音 | 语音合成 2.0（seed-tts-2.0）、声音复刻 2.0、播客模型、实时语音 3.0、音色设计 | 高 | 文本前加 `[#自然语言指令]`；context_texts / 引用上文 | SSML（phoneme 细节待核实） | 播客模型（双人） | ✅ | ✅ 参考音频 14–30 秒 | 2.1–2.8 元/万字符 |
| 阿里百炼 | qwen-audio-3.0-tts、cosyvoice-v3.5、qwen3-tts-flash(-realtime) | 高，方言多 | `instruction` 自然语言；文本内情感/拟声标签 | 开源版 `[j][ǐ]`；云端待核实 | — | ✅ | ✅ + 声音设计 | 0.8–1.4 元/万字符 |
| MiniMax | speech-2.8-hd / turbo | 高 | `emotion` 参数；`(breath)` `(emm)` `(chuckle)` 等约 20 个标签 | 行内 `(he2)平`；`pronunciation_dict`：`处理/(chu3)(li3)`，声调 1–5（5 为轻声） | — | turbo | ✅ 约 10 秒 | $60–100/百万字符 |
| 讯飞 | 超拟人合成 x4–x6 发音人 | 高 | `oral_level` 口语化等级（x4） | 停顿 `[p500]`；多音字格式待核实 | — | ✅ | 一句话复刻 | 在线价格待核实；离线 SDK 单个发音人 2000 元起 |
| ElevenLabs | Eleven v4 / v4 Turbo（2026-09-28） | 中 | `[audio tags]` 写英文自然语言 | **v3/v4 不支持 SSML**（包括 break）；只能用发音词典（alias / IPA / CMU） | ✅ Text to Dialogue | v4 Turbo | 即时克隆 + 专业克隆（PVC） | $40–80/百万字符 |
| Azure | Neural / Neural HD / MAI-Voice | 中高 | SSML `express-as` | SSML `<phoneme>`，zh-CN 用 sapi 拼音 | SSML 多 voice | ✅ | 专业定制（需录同意声明） | $15–22/百万字符 |
| Google | gemini-3.8-flash(-lite)-tts（预览版） | 中高（待核实） | `style` 字段；尖括号声音事件 | — | ✅ | lite | 设计 / 复刻 | 待核实 |
| Cartesia | Sonic 3.6 | 中（待核实） | 情绪 / 笑声标签 | 待核实 | — | ✅ 官方称 <90ms，第三方测中位数 166ms | ✅ | 约 $37/百万字符 |
| Fish Audio | Drama 3（2026-10-13）、S2.1 Pro | 中高 | `[sighs]` `<whisper>…</whisper>` | 待核实 | 待核实 | API | ✅ | 待核实 |

**停服 / 弃用（新项目不要接）**：
- Hume TTS/EVI：2026-11-13 停服；
- OpenAI tts-1、tts-1-hd、gpt-4o-mini-tts：2027-01-06 关停；
- ElevenLabs 本地 MCP：已归档，改用托管 MCP（见 `config/mcp.json`）。

## 3. 开源模型（可本机部署）

| 模型 | 中文 | 控制方式 | 多人 / 实时 / 克隆 | 授权 |
|---|---|---|---|---|
| Fun-CosyVoice3-0.5B | 高，18+ 方言 | `[breath]` `[laughter]` `<strong>词</strong>`；instruct（中英文都可，格式 `You are a helpful assistant. …<\|endofprompt\|>`）；拼音 `[j][ǐ]`；英文 CMU 音素 | 无多人；双流式约 150ms；零样本克隆 | Apache-2.0 |
| Qwen3-TTS 0.6B / 1.7B | 高 | 自然语言指令；声音设计 | 首包理论 97ms（官方代码跑不到）；3 秒克隆 | Apache-2.0（以 LICENSE 文件为准） |
| IndexTTS-2.5 | 高 | 8 维情绪向量或情绪文本；`<行\|XING2>`；duration_factor | 约 6GB 显存；克隆 | bilibili 许可：可商用；月活超过 1 亿或年营收超过 10 亿元需另行授权 |
| VoxCPM2 | 高，30 种语言 | 声音设计；可控克隆 | 流式；克隆 | Apache-2.0 |
| MOSS-TTSD v1.0 | 中英 | 剧本写说话人标签 | 多人，单次最长 60 分钟 | **待核实** |
| GPT-SoVITS | 高 | 靠参考音频控制 | 1 分钟数据微调 | MIT |
| Dia2 1B / 2B | 只有英文 | `[S1]` `[S2]`、`(laughs)` | 多人；流式 | Apache-2.0 |
| Kokoro-82M / v1.1-zh | 一般 | 无 | CPU 可实时；不能克隆 | Apache |
| Fish Drama 3 | 中高 | 导演标签 | 需 48GB 显存（int4 约 22GB） | 年营收低于 50 万美元可商用；做托管服务另需授权 |

## 4. §授权红线（商用前必查）

| 不可直接商用 | 原因 |
|---|---|
| F5-TTS 权重 | CC-BY-NC（代码是 MIT；社区重训版 OpenF5-TTS 为 Apache） |
| Spark-TTS | 权重已从 Apache **改为** CC BY-NC-SA |
| ChatTTS | 代码 AGPLv3+，权重 CC BY-NC 4.0 |
| Fish Speech 1.5 / S2-Pro | CC-BY-NC-SA / Research License（商用需另签授权） |
| Higgs TTS 3 | 研究 / 非商用；创作者变现需署名，做产品需另行授权 |
| VibeVoice | 微软撤回过原始权重，标为仅限研究 |
| ElevenLabs 免费档 | 只有付费计划包含商用授权 |

规则：开源模型以仓库里的 LICENSE 文件为准，不以第三方文章为准。许可证的结论和核实日期写进 `decisions.md`。

## 5. 表演与发音语法对照（S3 / S4 查这里）

| 平台 | 情绪 / 风格 | 非语言音 | 停顿 | 多音字 / 发音 |
|---|---|---|---|---|
| ElevenLabs v4 | `[curious]` `[Low, steady voice, restrained urgency]`（英文，写可听见的嗓音质感） | `[laughs]` `[sighs]` `[clears throat]` | 不支持 break；用省略号、破折号、换行 | 发音词典（alias 最稳）；改写拼写，如 `G D P` |
| 火山豆包 2.0 | `[#用颤抖沙哑、带着哭腔的声音说]`；context_texts 写语境（不计费） | 指令描述 | SSML / 标点 | SSML（待核实） |
| 百炼 Qwen / CosyVoice 云 | `instruction` 字段 | 文本内拟声标签 | 标点 | 以当期文档为准 |
| MiniMax | `emotion` 参数 | `(breath)` `(inhale)` `(emm)` `(chuckle)` `(lip-smacking)` | `<#0.5#>` 停顿（以文档为准） | `(chu3)(li3)` 行内或 pronunciation_dict |
| CosyVoice3 本机 | instruct 文本 | `[breath]` `[laughter]` | 标点 | `她[h][ǎo]看`（声母韵母分开，带调号） |
| IndexTTS-2.5 | 情绪向量或情绪文本 | — | 标点 | `<行\|XING2>` |
| 豆包播客模型 | 由模型根据对话自动演绎 | 自动生成附和、插话 | 自动 | **S1 必须核实**：能否直接输入自写脚本（而不只是源材料）、发音如何控制；请求里有 `aigc_watermark` 字段 |
| MOSS-TTSD | 剧本中的说话人标签 | 待核实 | 标点 | 待核实；许可证也待核实 |
| FireRedTTS-2 | 逐句指定说话人（最多 4 人，单次约 3 分钟） | 待核实 | 标点 | 待核实；许可证也待核实 |
| 讯飞超拟人 | oral_level | — | `[p500]` | 文档"多音字读法"一节 |
| Azure / Google SSML | `<mstts:express-as style>` | — | `<break time>` | `<phoneme alphabet="sapi" ph="hao 4">` |

**通用铁律**：
- 标签语法不能跨平台照搬。不认识的标签会被当成文字念出来。换平台时 S3、S4 的标注要整体重写。
- 一句最多放一个情绪标签。标签要和文本语义一致。

## 6. 可复现性

- 每次生成都记录 model_id、voice_id、seed、指令和标签、参数，写进 `runs.csv`。
- CosyVoice 等本机模型：固定 seed 加固定输入，输出可以复现。
- ElevenLabs 等云平台：seed 只是尽力而为，结果不保证一致。所以选定的音频文件本身才是"成品"，要保存好；不要指望将来能重新生成一模一样的版本。
- ElevenLabs 重新生成中间某段时，传入 previous_text / next_text 或前后段的 request_ids（最多 3 个，有效期 2 小时），保证衔接；**v3 不支持 request stitching**。
