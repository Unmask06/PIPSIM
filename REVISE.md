# REVISE.md - Project Handover Guide 🚀

**PANDORA Pipesim Pilot** - A Desktop Application for Hydraulic Pipeline Simulation

Last Updated: 2025-02-11  
Version: 2025.2.11

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Code Structure](#architecture--code-structure)
3. [Core Components](#core-components)
4. [Workflows & Features](#workflows--features)
5. [Technical Stack](#technical-stack)
6. [Development Workflow](#development-workflow)
7. [Critical Nuances & Gotchas](#critical-nuances--gotchas)
8. [Access Control & Licensing](#access-control--licensing)
9. [Deployment & Distribution](#deployment--distribution)
10. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

### What is PANDORA Pipesim Pilot?

PANDORA Pipesim Pilot is a **desktop GUI application** built to streamline hydraulic pipeline modeling and simulation workflows using Schlumberger's **Pipesim software**. It wraps the Pipesim Python Toolkit (sixgill) with an intuitive Tkinter interface to reduce costs and improve efficiency when managing multiple hydraulic projects.

### Why Does This Exist?

- **Problem**: Pipesim is powerful but costly with limited licenses
- **Solution**: Provide an efficient, user-friendly interface for common Pipesim operations
- **Key Value**: Most operations only require the Python Toolkit license (cheaper), not the full Pipesim license

### Target Users

- Hydraulic engineers working on pipeline projects
- Bilfinger Study Team members
- Users with PIPESIM 2024.2 and Python Toolkit installed

---

## 🏗️ Architecture & Code Structure

### Directory Layout

```
PIPSIM/
├── app/
│   ├── app.py                  # Main application entry point
│   ├── config/                 # Configuration & access control
│   │   └── __init__.py         # VERSION, BASE_URL, fetch_response()
│   ├── core/                   # Business logic layer
│   │   ├── __init__.py         # Custom exceptions
│   │   ├── model_builder.py   # Create models from Excel
│   │   ├── model_populater.py # Populate/export model data
│   │   ├── multi_case_modeller.py # Multi-case generation
│   │   ├── network_simulation.py  # Run simulations
│   │   ├── excel_handling.py   # Excel I/O operations
│   │   ├── unit_conversion.py  # Unit conversion utilities
│   │   └── setup/              # Setup utilities
│   ├── frames/                 # UI layer (Tkinter frames)
│   │   ├── home.py             # Main navigation frame
│   │   ├── create_model.py    # Create model workflow UI
│   │   ├── populate_model.py  # Populate model workflow UI
│   │   ├── multi_case.py      # Multi-case workflow UI
│   │   ├── run_simulation.py  # Run simulation workflow UI
│   │   ├── copy_flowline_data.py # Copy flowline workflow UI
│   │   └── summarize.py       # Summarize results UI (WIP)
│   ├── project/                # Shared utilities
│   │   ├── __init__.py         # FRAME_STORE, utility functions
│   │   └── userguide/          # User documentation
│   │       ├── introduction.md
│   │       └── workflow-userguide.md
│   ├── widgets/                # Custom Tkinter widgets
│   │   ├── cascade_combo_box.py
│   │   └── dual_combo_box.py
│   └── logging.yml             # Logging configuration
├── create_pyz.py               # Package application as .pyz
├── encrypt.bat                 # Obfuscate code with PyArmor
├── run.bat                     # Local development launcher
├── requirements.txt            # Python dependencies
└── variables.json              # Default simulation variables
```

### Architectural Pattern

**Layered Architecture:**
1. **UI Layer** (`app/frames/`) - Tkinter frames for user interaction
2. **Business Logic** (`app/core/`) - Core modeling/simulation logic
3. **Integration Layer** (`sixgill`) - Pipesim Python Toolkit wrapper

**Key Design Patterns:**
- **Frame-based Navigation**: FRAME_STORE dictionary manages all UI screens
- **Threading**: Long-running operations use threading to prevent UI freezing
- **Exception Handling**: Custom exceptions (ExcelInputError, PipsimModellingError, NetworkSimulationError)

---

## 🔧 Core Components

### 1. Model Builder (`model_builder.py`)

**Purpose**: Create Pipesim models from scratch using Excel templates

**Key Methods:**
- `create_model()`: Builds complete model from Excel data
- `_create_component()`: Creates individual Pipesim components
- `_create_connection()`: Connects components in sequence

**Input**: Excel file with component names and types in paired columns

**License Required**: Python Toolkit only

### 2. Model Populater (`model_populater.py`)

**Purpose**: Import/export data between Excel and existing Pipesim models

**Modes:**
- `export`: Extract all component data to Excel
- `bulk_import`: Import data from exported Excel back to model
- `simple_import`: Import data from custom Excel sheet
- `flowline_geometry_import`: Import flowline geometry specifically

**Key Methods:**
- `populate_model()`: Main entry point
- `export_values()`: Export model to Excel
- `bulk_import_values()`: Import from Excel to model
- `import_flowline_geometry()`: Import flowline data

**License Required**: Python Toolkit only

### 3. Multi-Case Modeller (`multi_case_modeller.py`)

**Purpose**: Generate multiple Pipesim files by combining well profiles and conditions

**How It Works:**
1. Reads Excel file with cases (columns = case names, rows = parameters)
2. For each case column, creates a new `.pips` file
3. Updates parameters in each file based on Excel values
4. Deactivates low-flow wells (< 0.001 STBD)

**Key Constants:**
- `MINIMUM_FLOWRATE = 0.001` (STBD)

**Excel Format:**
- First 4 columns: Component Name, Component Type, Parameter, Unit
- Remaining columns: Case names with parameter values

**Output Naming**: `<base_name>_<case_name>.pips`

**License Required**: Python Toolkit only

### 4. Network Simulator (`network_simulation.py`)

**Purpose**: Run Pipesim simulations and export results to Excel

**Key Methods:**
- `run_existing_model()`: Main simulation workflow
- `deactivate_lowflow_sinks()`: Deactivate wells with flow < 0.001 STBD
- `run_simulation()`: Execute Pipesim network simulation
- `extract_results()`: Extract node and profile results
- `save_results()`: Save results to Excel files

**Outputs:**
- `Node_Results.xlsx`: System-level results (pressure, temperature, etc.)
- `Profile_Results.xlsx`: Profile data along flowlines

**License Required**: BOTH Pipesim AND Python Toolkit

### 5. Copy Flowline Data (`copy_flowline_data.py`)

**Purpose**: Copy flowline information from source model to all models in a folder

**Key Function:**
- `copy_flowline_data(source_file, destination_folder)`

**Performance Note**: VERY SLOW - approximately 50 seconds per flowline!

**License Required**: Python Toolkit only

---

## 🚀 Workflows & Features

### 1. Create Model Workflow

**UI**: `CreateModelFrame` → **Core**: `ModelBuilder`

**Steps:**
1. Select Pipesim file (new or existing)
2. Select Excel file
3. Choose sheet name
4. Select unit system (Metric/Field)
5. Submit to create model

**Runtime**: ~1-2 minutes per model

### 2. Populate Model Workflow

**UI**: `PopulateModelFrame` → **Core**: `ModelPopulater`

**Modes:**
- **Export**: Extract model data to Excel for review/editing
- **Bulk Import**: Import previously exported data back
- **Simple Import**: Import from custom formatted Excel
- **Flowline Geometry**: Import specific flowline geometry data

**Runtime**: ~1-2 minutes per model

### 3. Multi-Case Workflow

**UI**: `MultiCaseFrame` → **Core**: `MultiCaseModeller`

**Steps:**
1. Select Excel file with case matrix
2. Choose sheet for well profiles
3. Select base Pipesim file
4. Submit to generate multiple case files

**Important**: Keep base filename SHORT to avoid Windows path length issues

**Runtime**: ~5-10 minutes per case (depends on model complexity)

### 4. Run Simulation Workflow

**UI**: `RunSimulationFrame` → **Core**: `NetworkSimulator`

**Steps:**
1. Select folder containing `.pips` files
2. Choose system variables to extract (Pressure, Temperature, etc.)
3. Choose profile variables to extract (Pressure, Velocity, etc.)
4. Select unit system
5. Submit to run all simulations

**Outputs**: Excel files with results in the same folder

**Runtime**: ~5-10 minutes per simulation

### 5. Copy Flowline Data Workflow

**UI**: `init_update_conditions_frame()` → **Core**: `copy_flowline_data()`

**Steps:**
1. Select source Pipesim file
2. Select destination folder
3. Submit to copy flowline data to all files in folder

**Warning**: EXTREMELY TIME-CONSUMING (~50 sec/flowline)

### 6. Summarize Results Workflow ⚠️

**Status**: UNDER DEVELOPMENT (currently shows placeholder message)

**UI**: `init_summarize_frame()`

**Intended Purpose**: Aggregate results from multiple simulation outputs

---

## 💻 Technical Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.11 | Application logic |
| **GUI Framework** | Tkinter | Built-in | User interface |
| **Pipesim API** | sixgill | N/A | Pipesim Python Toolkit |
| **Data Handling** | pandas | 2.0.* | Excel/data manipulation |
| **Excel I/O** | openpyxl, xlwings | 3.1.*, 0.33.* | Excel file operations |
| **Logging** | colorlog | 6.9.* | Colored console logging |
| **HTTP** | requests, Flask | N/A, 3.1.* | Access control |
| **Code Obfuscation** | PyArmor | 9.0.* | Protect source code |

### Python Interpreter

**Critical**: Application MUST run with Schlumberger's Python installation:
```
C:/Program Files/Schlumberger/PIPESIM_PTK_2024.2/python.exe
```

This is the ONLY Python environment with the `sixgill` library installed.

### Dependencies (`requirements.txt`)

```
colorama==0.4.*
colorlog==6.9.*
Flask==3.1.*
numpy==1.*
openpyxl==3.1.*
pandas==2.0.*
pathlib2==2.3.*
PyYAML==6.0.*
XlsxWriter==3.2.*
xlwings==0.33.*
pyarmor==9.0.*
```

---

## 🔨 Development Workflow

### Running Locally

**Option 1: Using run.bat**
```batch
cd /path/to/PIPSIM
run.bat
```

**Option 2: Direct Python**
```bash
"C:/Program Files/Schlumberger/PIPESIM_PTK_2024.2/python.exe" -m app.app
```

**Option 3: Running as module**
```bash
cd /path/to/PIPSIM
"C:/Program Files/Schlumberger/PIPESIM_PTK_2024.2/python.exe" -m app.app
```

### Key Environment Variables

- `APPDATA`: Used to create application data directory
  - Path: `%APPDATA%/Pandora/Pipesim Pilot`

### Frame Navigation System

All UI screens are stored in `FRAME_STORE` dictionary:

```python
from app.project import FRAME_STORE, switch_frame

# Navigate to a different frame
switch_frame(FRAME_STORE[FrameNames.CREATE_MODEL])
```

**Available Frame Keys** (from `FrameNames` class):
- `HOMEFRAME = "home"`
- `CREATE_MODEL = "create_model"`
- `POPULATE_MODEL = "populate_model"`
- `COPY_FLOWLINE_DATA = "copy_flowline_data"`
- `RUN_SIMULATION = "run_simulation"`
- `SUMMARIZE = "summarize"`
- `MULTI_CASE = "multi_case"`

### Logging Configuration

Logging is configured via `app/logging.yml`:
- **Colored console output** using `colorlog`
- **Timestamp format**: `%H:%M`
- **Log levels**: DEBUG (cyan), INFO (white/green), WARNING (yellow), ERROR (red)

**Key loggers:**
- `app.core.model_builder`
- `app.core.simulation_modeller`
- `app.core.network_simulation`

### Threading Pattern

Long-running operations use threading to prevent UI freeze:

```python
def submit_action():
    def task():
        progress_bar.start()
        try:
            # Do work here
            pass
        finally:
            progress_bar.stop()
    
    threading.Thread(target=task).start()
```

---

## ⚠️ Critical Nuances & Gotchas

### 1. **Trail Mode Flag** ⚠️

**Location**: `app.py` → `check_access()` function

```python
def check_access(app: tk.Tk, trail=True):  #! trail=False in production
```

**IMPORTANT**: Set `trail=True` for development/testing, `trail=False` for production!

**What it does:**
- `trail=True`: Uses hardcoded date-based access (7 days from Feb 10, 2025)
- `trail=False`: Checks with production server for access control

### 2. **Minimum Flowrate Threshold**

**Value**: `0.001 STBD` (Stock Tank Barrels per Day)

**Used in:**
- `MultiCaseModeller.MINIMUM_FLOWRATE`
- `NetworkSimulator.MIN_FLOWRATE`

**Purpose**: Automatically deactivate wells/sinks with negligible flow to prevent simulation errors

### 3. **Excel Format Requirements**

**Multi-Case Excel:**
- First 4 columns MUST be: `Component Name`, `Component Type`, `Parameter`, `Unit`
- Case names should be SHORT (avoid long Windows paths)
- Component types must match `Parameters` class from sixgill

**Create Model Excel:**
- Components in paired columns: `[Name1, Type1, Name2, Type2, ...]`
- Must have even number of columns

### 4. **File Naming Conventions**

**Multi-Case Output:**
```
<base_filename>_<case_name>.pips
```

Example: `base.pips` + case "Overall-max-S-HP" → `base_Overall-max-S-HP.pips`

**Keep base filename SHORT!** Windows has 260 character path limit.

### 5. **Result File Naming**

**Hard-coded in NetworkSimulator:**
- `Node_Results.xlsx`
- `Profile_Results.xlsx`

These files are created in the same folder as the `.pips` file.

### 6. **Unit Note in Multi-Case**

From `workflow-userguide.md`:
> `Unit` doesn't perform any unit conversion, it is just for display purpose.

The "Unit" column is informational only!

### 7. **Performance Bottlenecks**

**Extremely Slow Operations:**
- **Copy Flowline Data**: ~50 seconds per flowline
- **Multi-Case Generation**: ~5-10 minutes per case
- **Running Simulations**: ~5-10 minutes per model

### 8. **Excel File Locking**

When using `xlwings`, Excel files may be locked. Close Excel application before operations.

### 9. **Model Validation**

In `network_simulation.py`:
```python
if self.model.tasks.networksimulation.validate():  # Returns True if INVALID!
    raise NetworkSimulationError("Model validation unsuccessful.")
```

**Counterintuitive**: `validate()` returns `True` when validation FAILS!

### 10. **Access Denied Frame**

If access control fails, app shows "Access Denied" screen with message:
> "You are using outdated software. Please contact the administrator."

This triggers when:
- Server returns non-"OK" status
- Trail period expired
- Network connection failed

---

## 🔐 Access Control & Licensing

### Server-Based Access Control

**Server URL**: `https://sv03919.res1.rlaone.net/streamline/pipesim-pilot/getAccess`

**Request**:
```json
{
  "version": "2025.2.11"
}
```

**Response**:
```json
{
  "status": "OK",  // or "error"
  "message": "Access granted"
}
```

### Trail Mode

**Location**: `app/config/__init__.py` → `fetch_response()`

**Trail Period**: 7 days from Feb 10, 2025 (hardcoded)

**Usage**: Development/testing without server connection

### License Requirements by Workflow

| Workflow | Python Toolkit | Pipesim License |
|----------|----------------|-----------------|
| Create Model | ✅ | ❌ |
| Populate Model | ✅ | ❌ |
| Multi-Case | ✅ | ❌ |
| Copy Flowline | ✅ | ❌ |
| Run Simulation | ✅ | ✅ |
| Summarize | ❌ | ❌ |

**Key Insight**: Only "Run Simulation" needs the expensive Pipesim license!

### Network Requirement

Application requires connection to **office network** for:
- Access control validation
- Documentation links
- Sample file downloads

---

## 📦 Deployment & Distribution

### Packaging Process

**Step 1: Obfuscate Code** (`encrypt.bat`)
```batch
pyarmor.exe gen -O pipesim-pilot -r app
```

Creates obfuscated version in `pipesim-pilot/` folder

**Step 2: Create .pyz Archive** (`create_pyz.py`)
```python
zipapp.create_archive(
    "pipesim-pilot",
    "pipesim-pilot.pyz",
    interpreter="C:/Program Files/Schlumberger/PIPESIM_PTK_2024.2/python.exe"
)
```

Creates self-contained `.pyz` file with hardcoded Python interpreter

### Distribution Files

**Main deliverable**: `pipesim-pilot.pyz`
- Self-contained Python zip application
- Includes obfuscated code + dependencies
- Runs with embedded interpreter path

**Installation Script**: `pipesim-pilot.ps1` (PowerShell)
- Downloads from: `https://sv03919.res1.rlaone.net/streamline`
- Installs dependencies if needed
- Launches the application

### User Installation Flow

1. Download `pipesim-pilot.ps1` from server
2. Create working directory
3. Right-click → "Run with PowerShell"
4. Script auto-installs dependencies
5. Application launches
6. Future runs: just double-click `pipesim-pilot.ps1`

### Pre-requisites

Users MUST have:
- **PIPESIM 2024.2** installed
- **Python Toolkit** (sixgill) installed
- Connection to **office network**

---

## 🚧 Future Enhancements

### 1. Summarize Results Workflow

**Status**: Placeholder implemented, functionality pending

**Purpose**: Aggregate results from multiple simulation runs

**Current State**: Shows "Wait" message: "Data summarization feature is not available yet"

**Files**: `app/frames/summarize.py`

### 2. Completed Items

Recent fixes:
- ✅ Removed unit argument from Copy Flowline Data workflow (commit c2304d8)

### 3. Known Limitations

**Disabled Features:**
- Summarize Results button is `tk.DISABLED` in home screen

**Performance Issues:**
- Copy Flowline Data is extremely slow (needs optimization)

### 4. Potential Improvements

**Code Quality:**
- Add comprehensive unit tests
- Improve error messages
- Add input validation helpers

**Features:**
- Batch operations for multiple files
- Progress indicators with percentage/ETA
- Configurable flowrate thresholds
- Resume failed operations

**Performance:**
- Optimize Copy Flowline Data operation
- Parallel processing for multi-case generation
- Caching for frequently accessed data

**UI/UX:**
- Add keyboard shortcuts
- Drag-and-drop file selection
- Recent files list
- Configuration presets

### 5. Technical Debt

**Documentation:**
- Add inline code comments (currently minimal)
- Create API reference for core modules
- Add troubleshooting guide

**Testing:**
- No automated tests present (files matching `*test*` are gitignored)
- Need unit tests for core modules
- Need integration tests for workflows

**Configuration:**
- Hardcoded paths (Python interpreter, server URL)
- Consider config file for deployment-specific settings

---

## 📚 Additional Resources

### Documentation Links

**User Guides** (in repo):
- `app/project/userguide/introduction.md` - Installation & getting started
- `app/project/userguide/workflow-userguide.md` - Detailed workflow instructions

**Online Documentation**:
- URL pattern: `{BASE_URL}/docs/static/user-guide/pipesim-pilot/index.html#`
- Sample Excel: `{BASE_URL}/download/pipesim-pilot/Sample-Pilot-File.xlsx`

**Help Menu Features:**
- Component Parameters: Opens `DualCascadeListBox` with all available Pipesim parameters
- Documentation: Opens online user guide in browser
- Sample Import File: Downloads Excel template

### Git Repository

**Current branches:**
- `main` - Production branch
- `copilot/*` - AI-assisted development branches

**Recent commits:**
- `c2304d8` - fix: remove unit arg from copy flowline data workflow
- Earlier history grafted/truncated

### Contact & Support

**For queries**: Contact **Bilfinger Study Team**

---

## 🎓 Key Takeaways for New Developers

### Essential Knowledge

1. **Python Environment**: MUST use Schlumberger's Python (has sixgill)
2. **Frame Navigation**: All UI managed via `FRAME_STORE` dictionary
3. **Threading**: Long operations must use threads to prevent UI freeze
4. **Trail Mode**: Toggle `trail=True/False` in `check_access()`
5. **License Tiers**: Most operations need only Python Toolkit license

### Common Pitfalls

1. **Model validation**: Returns `True` when INVALID (counterintuitive!)
2. **Unit column**: Is display-only, doesn't perform conversion
3. **File paths**: Keep filenames SHORT (Windows 260 char limit)
4. **Excel locking**: Close Excel before operations
5. **Flowrate threshold**: Wells below 0.001 STBD auto-deactivated

### Development Workflow

1. Edit code in `app/` directory
2. Run locally with `run.bat`
3. Test workflows thoroughly
4. Update `VERSION` in `app/config/__init__.py`
5. Run `encrypt.bat` to obfuscate
6. Run `python create_pyz.py` to package
7. Distribute `.pyz` file

### Quick Reference

**Frame Names:**
```python
FrameNames.HOMEFRAME           # "home"
FrameNames.CREATE_MODEL        # "create_model"
FrameNames.POPULATE_MODEL      # "populate_model"
FrameNames.COPY_FLOWLINE_DATA  # "copy_flowline_data"
FrameNames.RUN_SIMULATION      # "run_simulation"
FrameNames.SUMMARIZE           # "summarize"
FrameNames.MULTI_CASE          # "multi_case"
```

**Exception Types:**
```python
ExcelInputError(message, excel_path, sheet_name=None)
PipsimModellingError(message, pipsim_path)
NetworkSimulationError(message, model_path)
```

**Core Classes:**
```python
ModelBuilder(pipsim_file, excel_file, sheet_name, units)
ModelPopulater(pipesim_file, excel_file, mode, unit, sheet_name)
MultiCaseModeller(base_model, excel_path, sheet_name, units)
NetworkSimulator(model_path, system_vars, profile_vars, unit, folder)
```

---

## 🎉 Welcome Back!

You've been away for 6 months, but this guide should have everything you need to jump back in. The codebase is well-structured, the architecture is straightforward, and the workflows are clearly defined.

**Start Here:**
1. Run `run.bat` to launch the app locally
2. Review the user guides in `app/project/userguide/`
3. Check the recent commits for any changes since you left
4. Test each workflow to refresh your memory

**Remember:**
- Keep filenames SHORT
- Use threading for long operations
- Check the trail mode flag before deployment
- Most operations need only Python Toolkit license

**Good luck, and welcome back to the project!** 🚀

---

*Document prepared as a comprehensive handover guide for returning developers.*
*For questions or updates, modify this document and commit to the repository.*
