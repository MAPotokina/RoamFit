# Code Development Conventions

> **Reference**: See [vision.md](./vision.md) for technical architecture, project structure, and system design.

## Core Principles

- **KISS**: Choose the simplest solution that works. Avoid abstractions until needed.
- **MVP First**: Implement minimal features. Add complexity only when required.
- **Single Responsibility**: Each function/class/agent does one thing well.
- **Fail Fast**: Validate inputs early, raise clear errors immediately.
- **No Premature Optimization**: Write clear code first. Optimize only when proven necessary.

## Code Style

- Follow **PEP 8** Python style guide
- Use **snake_case** for functions and variables
- Use **PascalCase** for classes
- Maximum line length: **100 characters**
- Use **type hints** for function parameters and return values (keep simple)

## Function Design

- Functions should be **small and focused** (single responsibility)
- Maximum **20-30 lines** per function (split if longer)
- Use **descriptive names** that explain what the function does
- Return **structured data** (dicts, dataclasses) rather than complex objects
- **One level of abstraction** per function

## Error Handling

- Use **specific exceptions** (ValueError, KeyError) not generic Exception
- **Fail fast**: Validate inputs at function entry
- Return **clear error messages** to users
- Log errors with context (use logging module)
- **No silent failures**: If something fails, raise or log it

## Agent Development

- Each agent is **independent and stateless**
- Agents communicate only through **Orchestrator** (no direct calls)
- Agents return **simple data structures** (dicts, lists)
- Keep agent logic **focused on single purpose**

## Imports

- Group imports: **standard library**, **third-party**, **local** (separated by blank line)
- Use **absolute imports** from project root
- Avoid `from module import *`

## Comments & Documentation

- Write **self-documenting code** (clear names, simple logic)
- Add comments only for **"why"** not "what"
- Use **docstrings** for public functions/classes (one-line or brief)
- No comments for obvious code

## Database

- Use **parameterized queries** (prevent SQL injection)
- Keep queries **simple** (avoid complex joins for MVP)
- Handle database errors explicitly
- Use **context managers** for connections

## LLM Integration

- All LLM calls go through **`utils/llm.py`** wrapper functions
- **Log all LLM calls** (see vision.md LLM Monitoring section)
- Request **JSON responses** when structure is needed
- Keep prompts **clear and concise**
- Handle API failures gracefully (retry once, then fail)

## Testing Approach

- Write **simple tests** for critical paths only (MVP)
- Test **happy paths** and **obvious error cases**
- No complex test infrastructure for MVP
- Manual testing acceptable for UI components

## File Organization

- Follow the **project structure** defined in vision.md
- One **main class/function** per file
- Keep files **under 300 lines** (split if needed)
- Use `__init__.py` files appropriately

## Configuration & Environment

- All configuration via **`.env` file** and `config.py`
- Never hardcode API keys or secrets
- Use **sensible defaults** in code
- Document required environment variables

## Logging

- Use Python's **logging module** (not print statements)
- Log at appropriate **levels** (DEBUG, INFO, WARNING, ERROR)
- Include **context** in log messages (agent name, user action)
- Follow logging approach in vision.md

