#!/usr/bin/env python3
"""Capture a clean Boulder GUI screenshot for the catalog docs.

Loads the given example and screenshots it in one of three modes. Intended to
be run against a Boulder instance with NO third-party plugin installed, so
the screenshot shows plain "Boulder" branding.

Usage: python scripts/capture_screenshot.py <url> <output_png> [options]

Modes (--mode):
  plots (default) -- run the single-shot simulation, select a reactor node
    (first node, or --node <id> for a specific one), click the Plots tab.
  network -- run the single-shot simulation and screenshot as-is; the
    reactor network diagram is always visible above the tab strip, so no
    tab click is needed.
  sweep -- trigger a parameter sweep via the Run-control split button's
    "Run Sweep" mode, wait for it to finish, and screenshot the page (the
    Sweep Results chart renders in the right-hand Scenario pane). Use
    --sweep-series to pick specific series (comma-separated) in the sweep
    plot's Y-axis picker instead of leaving the default selection.
"""

from __future__ import annotations

import argparse

from playwright.sync_api import Page, sync_playwright


def _select_node(page: Page, node_id: str | None) -> None:
    """Click a reactor node in the Cytoscape canvas so the Plots tab has data.

    Selects the first non-group node, or the node matching *node_id* (by
    Cytoscape element id) when given.
    """
    page.evaluate(
        """(nodeId) => {
            const cy = window.__boulderCy;
            if (!cy) return;
            const candidates = cy.nodes().filter(n => !n.data('isGroup'));
            const node = nodeId
                ? candidates.filter(n => n.id() === nodeId)[0]
                : candidates[0];
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
        }""",
        node_id,
    )
    page.wait_for_timeout(500)


def _run_sweep(page: Page, sweep_series: list[str], sweep_x: str | None, skip_run: bool) -> None:
    """Switch the split button to "Run Sweep", run it, and wait for results.

    When *skip_run* is set, an already-populated Scenario pane (from a prior
    ``run_sweep.py`` invocation writing the ``*_scenarios.h5`` cache) is used
    as-is instead of re-triggering a fresh sweep -- re-running some sweeps
    back-to-back against a warm server has been observed to occasionally hit
    a flaky ``net.solve_steady()`` non-convergence, whereas the cached
    scenarios are already known-good.
    """
    if not skip_run:
        page.click("#run-mode-caret")
        page.get_by_role("menuitemradio", name="Run Sweep").click()
        page.click("#run-primary")
    # Sweeps solve N scenarios sequentially server-side; give it a generous
    # window and rely on the results chart appearing as the completion signal.
    page.wait_for_selector("text=Sweep results", timeout=60000)
    # Also wait for the primary button's "Sweeping…" progress label to clear,
    # so the screenshot doesn't catch a mid-run state.
    page.wait_for_function(
        "() => !document.querySelector('#run-primary')?.textContent?.includes('Sweeping')",
        timeout=120000,
    )
    page.wait_for_timeout(2000)

    if sweep_x:
        page.get_by_label("X axis").select_option(label=sweep_x)
        page.wait_for_timeout(300)

    if not sweep_series:
        return

    # Replace the auto-selected default family with exactly the requested
    # series: drop every active chip, then add the requested ones in order.
    while True:
        remove_buttons = page.locator("[data-testid^='remove-series-']")
        if remove_buttons.count() == 0:
            break
        remove_buttons.first.click()
        page.wait_for_timeout(150)

    add_select = page.locator("select[data-testid='y-axis-add-select']")
    for series_label in sweep_series:
        add_select.select_option(label=series_label)
        page.wait_for_timeout(300)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("output_png")
    parser.add_argument("--mode", choices=["plots", "network", "sweep"], default="plots")
    parser.add_argument("--node", default=None, help="Cytoscape node id to select")
    parser.add_argument(
        "--sweep-series",
        default="",
        help="Comma-separated series labels to add to the sweep plot's Y-axis picker",
    )
    parser.add_argument(
        "--sweep-x",
        default=None,
        help="Friendly label of the sweep plot's X-axis series to select",
    )
    parser.add_argument(
        "--sweep-skip-run",
        action="store_true",
        help="Use an already-populated Scenario pane instead of re-running the sweep",
    )
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1024})
        page.goto(args.url, wait_until="networkidle")

        if args.mode == "sweep":
            series = [s.strip() for s in args.sweep_series.split(",") if s.strip()]
            _run_sweep(page, series, args.sweep_x, args.sweep_skip_run)
        else:
            page.get_by_role("button", name="Run Simulation").click()
            # Some transient examples (e.g. nanosecond micro_step chunking)
            # take much longer than a fixed sleep to solve; wait for the
            # primary button's "Running…" label AND the "Simulation
            # Running…" progress modal to clear instead of guessing.
            page.wait_for_function(
                "() => !document.querySelector('#run-primary')?.textContent?.includes('Running')",
                timeout=60000,
            )
            page.locator("text=Simulation Running").wait_for(state="hidden", timeout=60000)
            page.wait_for_timeout(1000)
            if args.mode == "plots":
                _select_node(page, args.node)
                page.get_by_role("button", name="Plots").click()
                page.wait_for_timeout(1500)
            # "network" mode: the reactor topology diagram is a permanent
            # element above the tab strip, always visible regardless of which
            # tab is active -- no further action needed. (The "Network" tab
            # itself is an unrelated Graphviz-rendered diagram that requires
            # an optional dependency; not what this mode is after.)

        page.screenshot(path=args.output_png, full_page=True)
        browser.close()
    print(f"wrote {args.output_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
