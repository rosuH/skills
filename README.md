# rosuH's Skills

我的个人 Agent Skills 集合。每个 skill 专注一件事，用简短、可复用的指令帮助 AI 完成任务。

## Skills

| Skill | 用途 |
| --- | --- |
| [ascii-explainer](skills/ascii-explainer/SKILL.md) | 用 ASCII 文本图解释概念、业务逻辑、执行流程、系统架构和方案差异。 |

## 安装

需要 Node.js 和 npm。在目标项目目录运行：

```bash
npx skills@latest add rosuH/skills --skill ascii-explainer
```

安装时选择需要使用的 agent。若要全局安装到 Codex：

```bash
npx skills@latest add rosuH/skills --skill ascii-explainer --agent codex --global
```

查看仓库内可安装的 skills：

```bash
npx skills@latest add rosuH/skills --list
```

安装选项详见 [skills CLI 文档](https://github.com/vercel-labs/skills#install-a-skill)。

## 使用示例

```text
使用 $ascii-explainer，用 ASCII 图解释一次 HTTP 请求的完整流程。
```

```text
用 ASCII 图对比同步调用和消息队列，标出数据流与失败路径。
```

## 添加 Skill

在 `skills/<skill-name>/SKILL.md` 中保存指令，并在文件开头声明 `name` 和 `description`。如有附属文件，一并放在该 skill 目录中，再更新上方列表。

```text
skills/
+-- ascii-explainer/
    +-- SKILL.md
    +-- agents/
        +-- openai.yaml
```

仓库组织方式参考 [mattpocock/skills](https://github.com/mattpocock/skills)。
