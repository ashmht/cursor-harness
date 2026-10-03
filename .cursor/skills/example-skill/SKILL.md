---
name: example-skill
author: you@example.com
status: alpha
description: >-
  Template skill demonstrating the recommended SKILL.md structure.
  Replace this with your actual skill description.
args:
  - name: target
    description: The target to operate on
    required: true
  - name: verbose
    description: Whether to produce detailed output
    required: false
---

# Example Skill

Use this skill when the user asks to (describe trigger conditions here).

## When This Skill Applies

- User asks to do X
- User mentions Y or Z

## Prerequisites

- Tool or CLI must be available
- Access to relevant system

## Workflow

1. **Gather context**: Read relevant files or query systems.
2. **Execute**: Perform the main task.
3. **Verify**: Check the result.
4. **Report**: Summarize what was done.
