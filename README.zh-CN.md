# rosuH's Skills

[![skills.sh](https://img.shields.io/badge/skills.sh-skills-black)](https://skills.sh/rosuh/skills)

[English](README.md) | 简体中文

我的个人 Agent Skills 集合。每个 skill 专注一件事，用简短、可复用的指令帮助 AI 完成任务。

## Skills

| Skill | 用途 |
| --- | --- |
| [ascii-explainer](skills/ascii-explainer/SKILL.md) | 用 ASCII 文本图解释概念、业务逻辑、执行流程、系统架构和方案差异。 |
| [sub-agent](skills/sub-agent/SKILL.md) | 委派研究、排障和实现，由主 Agent 负责方案、编排、纠偏与验收。 |

## 安装

需要 Node.js 和 npm。在目标项目目录运行，然后选择要安装的技能和 Agent：

```bash
npx skills@latest add rosuH/skills
```

将两个技能全局安装到 Codex：

```bash
npx skills@latest add rosuH/skills --skill ascii-explainer sub-agent --agent codex --global
```

查看仓库内可安装的 skills：

```bash
npx skills@latest add rosuH/skills --list
```

安装选项详见 [skills CLI 文档](https://github.com/vercel-labs/skills#install-a-skill)。

## Claude Code 和 Cursor

安装 `sub-agent`：

```bash
npx skills@latest add rosuH/skills --skill sub-agent --agent claude-code
npx skills@latest add rosuH/skills --skill sub-agent --agent cursor
```

两者均可通过 `/sub-agent` 调用。技能使用标准 `SKILL.md`，委派行为取决于当前会话实际提供的工具与权限。`agents/openai.yaml` 是可选的 Codex 界面元数据，不是 Claude Code 或 Cursor 的子 Agent 定义。

格式与加载方式见 [Claude Code skills](https://code.claude.com/docs/en/skills) 和 [Cursor Agent Skills](https://cursor.com/docs/context/skills)；委派能力见 [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) 和 [Cursor subagents](https://cursor.com/docs/context/subagents)。

## 使用示例

以下示例使用 Codex 的 `$skill-name` 写法；在 Claude Code 和 Cursor 中使用 `/skill-name`。

### ASCII 解释

```text
使用 $ascii-explainer，用 ASCII 图解释一次 HTTP 请求的完整流程。
```

```text
用 ASCII 图对比同步调用和消息队列，标出数据流与失败路径。
```

### 子 Agent 协作

```text
使用 $sub-agent 完成这个功能：委派代码阅读、实现和测试，由主 Agent 负责方案、编排、纠偏和最终验收。
```

## 添加 Skill

在 `skills/<skill-name>/SKILL.md` 中保存指令，并在文件开头声明 `name` 和 `description`。如有附属文件，一并放在该 skill 目录中，再更新上方列表。

```text
skills/
+-- ascii-explainer/
|   +-- SKILL.md
+-- sub-agent/
    +-- SKILL.md
    +-- agents/
        +-- openai.yaml
```

仓库组织方式参考 [mattpocock/skills](https://github.com/mattpocock/skills)。
