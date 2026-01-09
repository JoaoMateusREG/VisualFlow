# VisualFlow User Manual

## What is VisualFlow?

VisualFlow is a **visual workflow builder** for web automation and data processing. Create workflows by dragging blocks onto a canvas and connecting them—no coding required.

## Getting Started

### With Docker (Recommended)
```bash
docker-compose up --build
```
Access at: **http://localhost:8164**

### Manual Setup
See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for local development setup.

---

## Creating a Workflow

1. **Drag blocks** from the sidebar onto the canvas
2. **Connect blocks** by dragging from one node's handle to another
3. **Configure blocks** by clicking on them (settings appear on the right)
4. **Run workflow** using the Play button in the header

---

## Block Reference

### 🌐 Web Automation

| Block | Description |
|-------|-------------|
| **Login** | Navigate to URL and fill login form |
| **Open Site** | Navigate to a URL |
| **Click Button** | Click on an element |
| **Wait** | Wait for element or time |
| **Sleep** | Pause execution for N seconds |
| **Capture Table** | Extract HTML table to DataFrame |
| **Execute Script** | Run custom JavaScript |
| **Extract Text** | Extract text using regex |

### 📊 Data Processing

| Block | Description |
|-------|-------------|
| **Spreadsheet** | Read/Create/Save Excel/CSV files |
| **Variable** | Set, get, or transform variables |
| **Group Data** | Group DataFrame by column |
| **Transform Column** | Apply transformation to column |
| **Execute Python** | Run custom Python code |

### 🔄 Control Flow

| Block | Description |
|-------|-------------|
| **Loop For** | Iterate over range or DataFrame rows |
| **Loop While** | Loop while condition is true |
| **Condition** | If/else branching |
| **Schedule** | Configure execution schedule |

---

## Saving & Loading Workflows

### Save Workflow
1. Click **Save** button in the header
2. Enter a name and optional description
3. Workflow is saved to `visualflow_data/workflows/`

### Load Workflow
1. Click **Workflows** tab in the sidebar
2. Select a workflow from the list
3. Click **Load**

### Import Workflow (Drag & Drop)
- Drag a `.json` workflow file onto the canvas
- Or drag into the Workflows modal

---

## File Persistence

All files created by workflows are saved in:

| Environment | Location |
|-------------|----------|
| Docker | `/app/data` (mapped to `./visualflow_data`) |
| Local dev | `./visualflow_data` (project root) |

This includes:
- Downloaded files from Selenium
- Created/saved spreadsheets
- Captured tables

---

## Tips

- **Use XPath** for complex element selection
- **Test selectors** in browser DevTools first
- **Set timeouts** appropriately for slow pages
- **Use variables** to pass data between blocks
- **Save often** to avoid losing work

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
