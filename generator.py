#!/usr/bin/env python3
"""Generate a starter codebase from a markdown TODO list."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TASK_PATTERN = re.compile(
    r"^\s*-\s*\[\s?[xX ]\s?\]\s*(?:\[(?P<tag>[a-zA-Z0-9_-]+)\])?\s*(?P<target>[^-][^-]*?)(?:\s*[-:]\s*(?P<description>.*))?$"
)

TEMPLATES = {
    "api": """\
from fastapi import APIRouter

router = APIRouter(prefix=\"/{resource}\", tags=[\"{resource}\"])


@router.get(\"/\")
def list_{resource}():
    return {{\"items\": []}}
""",
    "model": """\
from pydantic import BaseModel


class {class_name}(BaseModel):
    id: str
""",
    "service": """\
class {class_name}Service:
    def run(self) -> None:
        pass
""",
    "ui": """\
export function {component_name}() {{
  return <div>{component_name}</div>;
}}
""",
    "test": """\
def test_placeholder():
    assert True
""",
    "infra": """\
# Infrastructure notes
# TODO: Define resources for {resource}
""",
}

DEFAULT_TEMPLATE = """\
# TODO generated file
# {description}
"""


@dataclass
class Task:
    raw: str
    tag: str
    target: str
    description: str


def parse_tasks(markdown: str) -> list[Task]:
    tasks: list[Task] = []
    for line in markdown.splitlines():
        match = TASK_PATTERN.match(line)
        if not match:
            continue

        tag = (match.group("tag") or "misc").lower().strip()
        target = (match.group("target") or "").strip()
        description = (match.group("description") or "").strip()

        if target:
            tasks.append(Task(raw=line, tag=tag, target=target, description=description))

    return tasks


def to_snake(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def to_pascal(value: str) -> str:
    words = re.split(r"[^a-zA-Z0-9]", value)
    return "".join(word.capitalize() for word in words if word)


def infer_file_path(task: Task) -> Path:
    target = task.target.strip().strip("/")
    if "/" in target:
        return Path(target)

    safe = to_snake(target)
    match task.tag:
        case "api":
            return Path("backend/api") / f"{safe}.py"
        case "model":
            return Path("backend/models") / f"{safe}.py"
        case "service":
            return Path("backend/services") / f"{safe}.py"
        case "ui":
            return Path("frontend/components") / f"{to_pascal(target)}.tsx"
        case "test":
            return Path("tests") / f"test_{safe}.py"
        case "infra":
            return Path("infra") / f"{safe}.md"
        case _:
            return Path("docs") / f"{safe}.md"


def render(task: Task, file_path: Path) -> str:
    resource = to_snake(file_path.stem)
    class_name = to_pascal(file_path.stem)
    component_name = to_pascal(file_path.stem) or "Component"

    template = TEMPLATES.get(task.tag, DEFAULT_TEMPLATE)
    return template.format(
        resource=resource or "resource",
        class_name=class_name or "Model",
        component_name=component_name,
        description=task.description or task.target,
    )


def write_files(tasks: Iterable[Task], output_dir: Path, dry_run: bool = False) -> list[Path]:
    generated: list[Path] = []
    for task in tasks:
        relative_path = infer_file_path(task)
        full_path = output_dir / relative_path
        if full_path.exists():
            continue

        generated.append(relative_path)
        if dry_run:
            continue

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(render(task, relative_path), encoding="utf-8")

    return generated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate code scaffolding from TODO markdown")
    parser.add_argument("todo_file", type=Path, help="Path to markdown TODO file")
    parser.add_argument("--output", type=Path, default=Path("."), help="Output project directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview generated files without writing")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.todo_file.exists():
        parser.error(f"TODO file not found: {args.todo_file}")

    markdown = args.todo_file.read_text(encoding="utf-8")
    tasks = parse_tasks(markdown)

    if not tasks:
        print("No actionable tasks found in TODO list.")
        return 0

    generated = write_files(tasks, output_dir=args.output, dry_run=args.dry_run)

    if not generated:
        print("No files generated (all target files already exist).")
        return 0

    for file in generated:
        print(file.as_posix())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
