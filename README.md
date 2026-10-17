# rosuH's Skills

[![skills.sh](https://img.shields.io/badge/skills.sh-skills-black)](https://skills.sh/rosuh/skills)

English | [简体中文](README.zh-CN.md)

My personal collection of agent skills. Each skill focuses on one task, with concise, reusable instructions for AI agents.

## Skills

| Skill | Purpose |
| --- | --- |
| [ascii-explainer](skills/ascii-explainer/SKILL.md) | Explain concepts, business logic, workflows, system architecture, and trade-offs with ASCII diagrams. |
| [sub-agent](skills/sub-agent/SKILL.md) | Delegate research, debugging, and implementation while the main agent owns planning, coordination, and review. |

## Installation

Requires Node.js and npm. Run this command in your project directory, then choose the skills and agents to install:

```bash
npx skills@latest add rosuH/skills
```

To install both skills globally for Codex:

```bash
npx skills@latest add rosuH/skills --skill ascii-explainer sub-agent --agent codex --global
```

To list the available skills:

```bash
npx skills@latest add rosuH/skills --list
```

See the [skills CLI documentation](https://github.com/vercel-labs/skills#install-a-skill) for installation options.

## Claude Code and Cursor

Install `sub-agent` for either agent:

```bash
npx skills@latest add rosuH/skills --skill sub-agent --agent claude-code
npx skills@latest add rosuH/skills --skill sub-agent --agent cursor
```

Invoke it with `/sub-agent` in either agent. The skill uses standard `SKILL.md`; delegation depends on the tools and permissions available in the session.

See [Claude Code skills](https://code.claude.com/docs/en/skills) and [Cursor Agent Skills](https://cursor.com/docs/context/skills) for loading behavior, and [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) and [Cursor subagents](https://cursor.com/docs/context/subagents) for delegation capabilities.

## Usage Examples

These examples use Codex's `$skill-name` notation. In Claude Code and Cursor, use `/skill-name`.

### ASCII explanations

```text
Use $ascii-explainer to explain the full lifecycle of an HTTP request with an ASCII diagram.
```

```text
Compare synchronous calls and message queues with ASCII diagrams. Show data flow and failure paths.
```

### Subagent coordination

```text
Use $sub-agent to implement this feature. Delegate code reading, implementation, and tests while the main agent owns planning, coordination, and final review.
```

## Adding a Skill

Add instructions in `skills/<skill-name>/SKILL.md`, with `name` and `description` in the YAML frontmatter. Keep supporting files in the same skill directory, then update the list above.

```text
skills/
+-- ascii-explainer/
|   +-- SKILL.md
+-- sub-agent/
    +-- SKILL.md
```

Repository structure inspired by [mattpocock/skills](https://github.com/mattpocock/skills).
