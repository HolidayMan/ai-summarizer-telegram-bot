import asyncio
import importlib
import logging
import sys
from typing import Callable, Awaitable

logging.basicConfig(level=logging.INFO)

_TASKS: dict[str, str] = {
    "daemon": "app.ai_analysis.daemon",
    "document": "app.ai_analysis.document_processor",
    "summary": "app.ai_analysis.daily_summary",
}


async def _run(module_name: str):
    module = importlib.import_module(module_name)
    if not hasattr(module, "run") and not hasattr(module, "scheduled_runner"):
        raise SystemExit(f"Module {module_name} does not expose run/scheduled_runner")

    if hasattr(module, "run"):
        coro: Callable[[], Awaitable[None]] = getattr(module, "run")  # type: ignore
    else:
        coro = getattr(module, "scheduled_runner")  # type: ignore

    await coro()


def main():
    # default to daemon
    task = sys.argv[1] if len(sys.argv) >= 2 else "daemon"
    if task not in _TASKS:
        print("Usage: python -m app.ai_analysis [daemon|document|summary]")
        raise SystemExit(1)

    asyncio.run(_run(_TASKS[task]))


if __name__ == "__main__":
    main()
