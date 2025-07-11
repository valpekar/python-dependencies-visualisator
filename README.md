# Python Dependency Visualizer CLI

A robust, extensible tool to visualize Python project dependencies as interactive graphs and export them to high-quality PDF, using a clean, modular architecture.

<img width="500" alt="Screenshot 2025-07-11 at 16 43 51" src="https://github.com/user-attachments/assets/3f942ff0-220c-4cb9-bef3-21d827a71ffc" />

## Features
- Parses `requirements.txt` and fetches dependencies recursively from PyPI
- Builds a directed dependency graph (using NetworkX)
- Generates interactive HTML visualizations (PyVis/vis.js)
- Exports the graph to high-quality PDF (using Playwright)
- Minimalist, modern UI with smooth zoom and loading overlay
- Clean CLI interface with configurable options
- Modular, extensible codebase (service, factory, exporter, config layers)

## Installation
1. Clone the repository and enter the project directory:
   ```bash
   git clone <repo-url>
   cd <repo-dir>
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browser binaries (required for PDF export):
   ```bash
   playwright install
   ```

## Usage
Generate an interactive HTML dependency graph:
```bash
python main.py --file requirements.txt --output my_graph.html --depth 1
```
Export the graph to PDF:
```bash
python main.py --file requirements.txt --output my_graph.html --pdf my_graph.pdf --depth 1
```

### CLI Options
- `--file`   : Path to requirements.txt (default: requirements.txt)
- `--output` : Output HTML file (default: dependency_graph.html)
- `--pdf`    : Output PDF file (optional)
- `--depth`  : Max dependency depth (default: 1)

## Project Structure
```
project-root/
  main.py                # CLI entrypoint, orchestration
  config.py              # Centralized configuration
  assets.py              # Static HTML/CSS/JS templates
  requirements.txt       # Python dependencies
  exporter/
    html_exporter.py     # HTML generation and post-processing
    pdf_exporter.py      # PDF export logic (Playwright)
    exporter_factory.py  # (optional) Exporter factory pattern
  core/
    graph_service.py     # (optional) Graph/data logic service layer
```

## Extending the Tool
- **Add new exporters**: Implement a new exporter in `exporter/` and register it in `exporter_factory.py`.
- **Change config**: Edit `config.py` for graph size, timeouts, or other settings.
- **Change UI**: Edit HTML/CSS/JS in `assets.py`.

## License
[Your License Here]

## Contributing / Contact
Pull requests and issues welcome! For questions, contact [your-email@example.com]. 
