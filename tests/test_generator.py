from pathlib import Path

from generator import infer_file_path, parse_tasks, write_files


def test_parse_tasks_detects_tagged_and_untagged_items() -> None:
    markdown = """
- [ ] [api] products
- [ ] [ui] checkout panel
- [x] [test] inventory sync
- [ ] architecture notes
"""
    tasks = parse_tasks(markdown)

    assert [task.tag for task in tasks] == ["api", "ui", "test", "misc"]
    assert tasks[0].target == "products"
    assert tasks[3].target == "architecture notes"


def test_infer_file_path_for_ui_component() -> None:
    task = parse_tasks("- [ ] [ui] checkout panel")[0]
    assert infer_file_path(task).as_posix() == "frontend/components/CheckoutPanel.tsx"


def test_write_files_generates_expected_structure(tmp_path: Path) -> None:
    todo = """
- [ ] [api] orders
- [ ] [model] order item
- [ ] [test] order service
"""
    tasks = parse_tasks(todo)
    generated = write_files(tasks, output_dir=tmp_path)

    assert len(generated) == 3
    assert (tmp_path / "backend/api/orders.py").exists()
    assert (tmp_path / "backend/models/order_item.py").exists()
    assert (tmp_path / "tests/test_order_service.py").exists()
