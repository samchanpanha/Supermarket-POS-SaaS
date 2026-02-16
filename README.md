# Supermarket-POS-SaaS

Generate a starter Supermarket POS SaaS codebase from a markdown TODO list.

## What this provides

- A Python CLI (`generator.py`) that parses TODO checklists and creates scaffold files.
- Built-in templates for API, model, service, UI, test, and infra tasks.
- Example TODO list at `todo/TODO.example.md`.

## TODO format

Use markdown checklist items:

```md
- [ ] [api] products
- [ ] [model] product
- [ ] [ui] checkout cart
- [ ] architecture notes
```

- `[...]` after checkbox is an optional tag.
- Supported tags: `api`, `model`, `service`, `ui`, `test`, `infra`.
- Untagged tasks default to `docs/<task-name>.md`.

## Usage

```bash
python generator.py todo/TODO.example.md --output generated
```

Preview only:

```bash
python generator.py todo/TODO.example.md --dry-run
```

## Run tests

```bash
python -m pytest -q
```
