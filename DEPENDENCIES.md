# Dependencies for Python Dependency Visualizer CLI

This project requires the following Python packages:

- requests
- networkx
- pyvis
- playwright

## Playwright Setup
After installing the Python package, you must install the browser binaries once:

```
pip install playwright
playwright install
```

This enables high-quality PDF export of the interactive dependency graph.

## System Requirements
No special system libraries are required beyond standard Python and the above packages. 