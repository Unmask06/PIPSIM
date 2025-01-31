# PANDORA - Pipesim Pilot User Guide

### **Table of Contents**

1. [Creating a Model Workflow](#creating-a-model-workflow)
2. [Multi-Case Simulation Workflow](#multi-case-simulation-workflow)
3. [Running Simulations Workflow](#running-simulations-workflow)
4. [Copy Flowline Workflow](#copy-flowline-workflow)
5. [Summarizing Results Workflow](#summarizing-results-workflow)

---

## Creating a Model Workflow

To create a model from scratch using an Excel file or populate an existing model with data from an Excel file, follow these steps:

### **Steps**

1. **Open the application.**
2. Navigate to the **"Create Model Workflow"** section.
3. Select the **Pipesim file** and the **Excel file.**
4. Choose the appropriate option

- The Excel sheet should contain the component name in the first column and its type in the second column.
  | Name      | Component        | Name      | Component        |
  | --------- | ---------------- | --------- | ---------------- |
  | Src-101   | Source           | Src-102   | Source           |
  | 6-BFW-001 | Flowline         | 6-BFW-002 | Flowline         |
  | 6-BFW-002 | Flowline         | 6-BFW-003 | Flowline         |
  | P-101     | Pump             | P-102     | Pump             |
  | FV-101    | GenericEquipment | FV-102    | GenericEquipment |
  | J1        | Junction         | J2        | Junction         |
  | Sk        | Sink             | Sk2       | Sink             |

#### **Populate Existing Model**

- The Excel sheet should contain the component name in the first column and the corresponding data in the subsequent columns.

  **Example:**

  | #  | Name    | Component        | DetailedModel | InnerDiameter | WallThickness | Roughness | ElevationDifference | HorizontalDistance | PressureDifferential | PressureDrop | Pressure | Temperature | LiquidFlowRate |
  | -- | ------- | ---------------- | ------------- | ------------- | ------------- | --------- | ------------------- | ------------------ | -------------------- | ------------ | -------- | ----------- | -------------- |
  | 1  | 6-BFW-1 | Flowline         | False         | 254           | 9             | 0.045     | 10                  | 100                |                      |              |          |             |                |
  | 2  | 6-BFW-2 | Flowline         | False         | 300           | 8             | 0.044     | 20                  | 200                |                      |              |          |             |                |
  | 3  | 6-BFW-3 | Flowline         | False         | 354           | 10            | 0.04      | 30                  | 300                |                      |              |          |             |                |
  | 4  | 6-BFW-4 | Flowline         | False         | 200           | 12            | 0.08      | 40                  | 400                |                      |              |          |             |                |
  | 5  | 6-BFW-5 | Flowline         | False         | 600           | 20            | 0.021     | 50                  | 500                |                      |              |          |             |                |
  | 6  | FE-101  | GenericEquipment |               |               |               |           |                     |                    |                      | 0.2          |          |             |                |
  | 7  | P-101   | Pump             |               |               |               |           |                     |                    | 30                   |              |          |             |                |
  | 8  | P-102   | Pump             |               |               |               |           |                     |                    | 40                   |              |          |             |                |
  | 9  | Src-1   | Source           |               |               |               |           |                     |                    |                      |              | 100      | 50          |                |
  | 10 | Sk-1    | Sink             |               |               |               |           |                     |                    |                      |              |          |             | 5              |
  | 11 | Sk-2    | Sink             |               |               |               |           |                     |                    |                      |              |          |             | 6              |
  | 12 | Sk-3    | Sink             |               |               |               |           |                     |                    |                      |              |          |             | 3              |
  | 13 | Sk-4    | Sink             |               |               |               |           |                     |                    |                      |              |          |             | 2              |

- *Note* : Flowline parameters should be selected

5. Click **"Submit"** to proceed.

---

### **Input Required**

- **Pipesim file**
- **Excel file**

### **License Requirement**

- Only Python Toolkit license required

### **Expected Runtime**

- Approximately 1-2 minutes per model

---

## Multi-Case Simulation Workflow

Multi-Case Simulation Workflow allows you to generate multiple Pipesim files by the combination of well profiles and conditions from an Excel file. The values are fed into the base Pipesim file to create multiple output files.

### **Steps**

1. **Open the application.**
2. Navigate to the **"Multi-Case Simulation Workflow"** section.
3. Select the **Excel file** containing the well profiles and conditions.
4. Select the **appropriate sheets** for well profiles and conditions from the dropdown menus.
5. Select the **base Pipesim file**.
6. Click **"Submit"** to start the process.

### **Input Required**

- **Excel file** with well profiles and conditions
- **Well Profile Sheet Name**
- **Conditions Sheet Name**
- **Base Pipesim file**

### **Naming Convention**

- Keep the base Pipesim file name short, e.g., `base.pips`.
- Column names for well profiles and conditions in the Excel file **should not contain underscores (\_)**.
  - Example Well Profile columns: `Overall-max`, `MinFlowRate`, `MaxFlowRate`, `case-1`
  - Example Conditions columns: `S-HP` (abbreviation for Summer High Pressure), `S-HP-EO` (for Summer High Pressure Early Operations)
- Ensure well profile and conditions column names are unique and short to avoid long output file names.
- Output file naming convention: `<base_pip_file_name>_<well_profile_name>_<conditions_name>.pips`
  - Example output file name: `Overall-max_S-HP_base.pips`

### **Excel File Format**

The Excel file should contain two sheets: one for well profiles and the other for conditions.

#### Well Profile Sheet

- The first column should contain the sink name. Column name should be `Sinks`.
- Pilot will look for the cell in the first row with the value `Sinks` and consider that as the header row.
- Subsequent columns should contain the well profile data.
- Column should not contain underscores (\_).
- Sample table:

| Sinks | O-Max  | O-Min |
| ----- | ------ | ----- |
| Sk-1  | 10     | 7.00  |
| Sk-2  | 12     | 9     |
| Sk-3  | 0.0001 | 5     |
| Sk-4  | 5      | 20    |

#### Conditions Sheet

- The first column should contain the condition abbreviation. Column name should be `Conditions`.
- Similarly, Pilot will look for the cell in the first row with the value `Conditions` and consider that as the header row.
- A condition can have multiple components, just repeat the condition abbreviation for each component in first column.
- Second column should contain the component name.
- Third column should contain the component type.
- Fourth column should contain the Parameter corresponding to the component.
- Fifth column should contain the value of the parameter.
- Column should not contain underscores (\_).
- Sample table:

| Conditions | Component Name | Component Type       | Parameter            | Value |
| ---------- | -------------- | -------------------- | -------------------- | ----- |
| S-HP       | Src-1          | Source               | Pressure             | 120   |
| S-HP       | Src-1          | Source               | Temperature          | 60    |
| S-HP       |                | SimulationSetting    | AmbientTemperature   | 50    |
| S-HP       | P-101          | SharedPumpParameters | PressureDifferential | 10    |
| S-HP       | P-102          | SharedPumpParameters | PressureDifferential | 8     |
| W-LP       | Src-1          | Source               | Pressure             | 88    |
| W-LP       | Src-1          | Source               | Temperature          | 20    |
| W-LP       |                | SimulationSetting    | AmbientTemperature   | 10    |
| W-LP       | P-101          | SharedPumpParameters | PressureDifferential | 15    |
| W-LP       | P-102          | SharedPumpParameters | PressureDifferential | 9     |

### **License Requirement**

- Only Python Toolkit licenses required

### **Expected Runtime**

- Approximately 5-10 minutes per case, depending on the model size

---

## Running Simulations Workflow

To run simulations for all `.pips` files in a specified folder, follow these steps:

### **Steps**

1. **Open the application.**
2. Navigate to the **"Run Simulation Workflow"** section.
3. Select the **folder containing the Pipesim files.**
4. Click **"Run Simulations"** to start the simulation process.

### **Input Required**

- Folder containing Pipesim files

### **License Requirement**

- Both Pipesim and Python Toolkit licenses required

### **Expected Runtime**

- Approximately 5-10 minutes per simulation, depending on the model size

---

## Copy Flowline Workflow

To copy the flowline data from a source model to all the models in a folder, follow these steps:

### **Steps**

1. **Open the application.**
2. Navigate to the **"Update Conditions Workflow"** section.
3. Select the **source model** and the **destination folder.**
4. Click **"Copy Data"** to start the process.

### **Input Required**

- **Source model**
- **Destination folder**

### **License Requirement**

- Only Python Toolkit license required

### **Expected Runtime**

- Heavily time-consuming process.
- Approximately 50 seconds to copy data for one flowline.

---

## Summarizing Results Workflow

To summarize the results of the model Node and Profile Results, follow these steps:

### **Steps**

1. **Open the application.**
2. Navigate to the **"Summarize Data"** section.
3. Select the **folder containing the data files.**
4. Click **"Submit"** to generate the summary.

### **Input Required**

- Folder containing Excel files generated through the Run Simulation Workflow

### **License Requirement**

- No additional license required

### **Expected Runtime**

- Approximately 2-3 minutes per summary

---

