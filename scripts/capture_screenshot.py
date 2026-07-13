#!/usr/bin/env python3
"""Capture a clean Boulder GUI screenshot for the catalog docs.

Loads the given example, runs the simulation, selects the first reactor node
(so the Plots tab renders), and screenshots the page. Intended to be run
against a Boulder instance with NO third-party plugin installed, so the
screenshot shows plain "Boulder" branding.

Usage: python scripts/capture_screenshot.py <url> <output_png>
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: capture_screenshot.py <url> <output_png>", file=sys.stderr)
        return 1
    url, out_path = sys.argv[1], sys.argv[2]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1024})
        page.goto(url, wait_until="networkidle")

        # Run the simulation.
        page.get_by_role("button", name="Run Simulation").click()
        page.wait_for_timeout(3000)

        # Select the first reactor node so the Plots tab has something to show.
        page.evaluate(
            """() => {
                const cy = window.__boulderCy;
                if (!cy) return;
                const node = cy.nodes().filter(n => !n.data('isGroup'))[0];
                if (!node) return;
                const rp = node.renderedPosition();
                const rect = cy.container().getBoundingClientRect();
                const opts = {bubbles: true, cancelable: true,
                              clientX: rect.left + rp.x, clientY: rect.top + rp.y,
                              button: 0};
                const target = cy.container().querySelector('canvas') || cy.container();
                target.dispatchEvent(new MouseEvent('mousedown', opts));
                target.dispatchEvent(new MouseEvent('mouseup', opts));
                target.dispatchEvent(new MouseEvent('click', opts));
            }"""
        )
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Plots").click()
        page.wait_for_timeout(1500)

        page.screenshot(path=out_path, full_page=True)
        browser.close()
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
