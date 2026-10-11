# rosuH's Skills

[![skills.sh](https://img.shields.io/badge/skills.sh-ascii--explainer-black)](https://skills.sh/rosuh/skills)

English | [简体中文](README.zh-CN.md)

My personal collection of agent skills. Each skill focuses on one task, with concise, reusable instructions for AI agents.

## Skills

| Skill | Purpose |
| --- | --- |
| [ascii-explainer](skills/ascii-explainer/SKILL.md) | Explain concepts, business logic, workflows, system architecture, and trade-offs with ASCII diagrams. |

## Installation

Requires Node.js and npm. Run this command in your project directory:

```bash
npx skills@latest add rosuH/skills --skill ascii-explainer
```

Choose your agent during installation. To install globally for Codex:

```bash
npx skills@latest add rosuH/skills --skill ascii-explainer --agent codex --global
```

To list the available skills:

```bash
npx skills@latest add rosuH/skills --list
```

See the [skills CLI documentation](https://github.com/vercel-labs/skills#install-a-skill) for installation options.

## Usage Examples

```text
Use $ascii-explainer to explain the full lifecycle of an HTTP request with an ASCII diagram.
```

```text
Compare synchronous calls and message queues with ASCII diagrams. Show data flow and failure paths.
```

## Adding a Skill

Add instructions in `skills/<skill-name>/SKILL.md`, with `name` and `description` in the YAML frontmatter. Keep supporting files in the same skill directory, then update the list above.

```text
skills/
+-- ascii-explainer/
    +-- SKILL.md
    +-- agents/
        +-- openai.yaml
```

Repository structure inspired by [mattpocock/skills](https://github.com/mattpocock/skills).
