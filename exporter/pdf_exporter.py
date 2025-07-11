"""
pdf_exporter.py - PDF export for Python Dependency Visualizer CLI using Playwright
"""
import os
import logging

PDF_LOADING_SELECTOR = '#minimalLoading'
PDF_LOADING_TIMEOUT_MS = 15000
PDF_GRAPH_READY_TIMEOUT_MS = 20000
PDF_PHYSICS_WAIT_MS = 2000

logger = logging.getLogger(__name__)

def export_pdf_with_playwright(output_html: str, pdf_output: str) -> None:
    """
    Export the HTML graph to a high-quality PDF using Playwright.
    Waits for the graph to fully load and stabilize before exporting.
    """
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'file://{os.path.abspath(output_html)}')

            # Wait for the minimalist loading indicator to disappear
            page.wait_for_selector(
                PDF_LOADING_SELECTOR,
                state='detached',
                timeout=PDF_LOADING_TIMEOUT_MS
            )

            # Wait for the graph to be fully rendered and stable
            page.wait_for_function(
                '''() => {
                    if (window.network && window.network.body) {
                        const nodes = window.network.body.nodeIndices;
                        const edges = window.network.body.edgeIndices;
                        return nodes && nodes.length > 0 && edges && edges.length >= 0;
                    }
                    return false;
                }''',
                timeout=PDF_GRAPH_READY_TIMEOUT_MS
            )

            # Additional wait for physics stabilization
            page.wait_for_timeout(PDF_PHYSICS_WAIT_MS)

            # Scroll the graph into view
            page.evaluate('''() => { document.getElementById('mynetwork').scrollIntoView(); }''')

            # Export PDF using only prefer_css_page_size and no width/height
            page.pdf(
                path=pdf_output,
                print_background=True,
                margin={
                    'top': '0px',
                    'right': '0px',
                    'bottom': '0px',
                    'left': '0px'
                },
                prefer_css_page_size=True
            )
            browser.close()
        logger.info(f'Graph also exported to {pdf_output}')
    except ImportError:
        logger.error('Playwright is not installed. Install it with: pip install playwright && playwright install')
    except Exception as e:
        logger.error(f'PDF export failed: {e}') 