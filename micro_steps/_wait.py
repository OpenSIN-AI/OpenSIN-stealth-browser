"""Intelligent DOM polling utilities for the OpenAI temp-rotator pipeline.
Replaces hardcoded asyncio.sleep() calls with condition-based polling."""
import asyncio
import time

async def wait_for_condition(tab, js_condition: str, timeout: float = 15, poll_interval: float = 0.3) -> bool:
    """Poll a JS expression until truthy. Returns True on success, False on timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            result = await tab.evaluate(js_condition)
            if result:
                return True
        except Exception:
            pass
        await asyncio.sleep(poll_interval)
    return False

async def wait_for_url_contains(tab, substring: str, timeout: float = 15) -> bool:
    """Wait until tab URL contains substring."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if substring in str(tab.target.url):
                return True
        except Exception:
            pass
        await asyncio.sleep(0.3)
    return False

async def wait_for_selector(tab, selector: str, timeout: float = 15) -> bool:
    """Wait until document.querySelector(selector) is not null."""
    return await wait_for_condition(tab, f'document.querySelector("{selector}") !== null', timeout=timeout)
