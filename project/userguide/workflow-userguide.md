# PANDORA - Pipesim Pilot User Guide

## **Table of Contents**
1. [Creating a Model Workflow](#creating-a-model-workflow)
2. [Running Simulations Workflow](#running-simulations-workflow)
3. [Multi-Case Simulation Workflow](#multi-case-simulation-workflow)
4. [Summarizing Results Workflow](#summarizing-results-workflow)
5. [Updating Conditions Workflow](#updating-conditions-workflow)

---

# Creating a Model Workflow

To create a model from scratch using an Excel file or populate an existing model with data from an Excel file, follow these steps:

## **Steps:**

1. **Open the application.**
2. Navigate to the **"Create Model Workflow"** section.
3. Select the **Pipesim file** and the **Excel file.**
4. Choose the appropriate option:

### **Build Model from Scratch:**

- The Excel sheet should contain the component name in the first column and its type in the second column.

   | Name           | Component        | Name   | Component        |
   | ---------------| ---------------- |--------|----------------- |
   | Src-101        | Source           | Src-102| Source           |
   | 6-BFW-001      | Flowline         | 6-BFW-002 | Flowline       |
   | 6-BFW-002      | Flowline         | 6-BFW-003 | Flowline       |
   | P-101          | Pump             | P-102  | Pump             |
   | FV-101         | GenericEquipment | FV-102 | GenericEquipment |
   | J1             | Junction         | J2     | Junction         |
   | Sk             | Sink             | Sk2    | Sink             |


### **Populate Existing Model:**

- The Excel sheet should contain the component name in the first column and the corresponding data in the subsequent columns.

   **Example:**
   | Component Name | Length | Diameter | Roughness | Elevation |
   | -------------- | ------ | -------- | --------- | --------- |
   | 6-BFW-001      | 1000   | 0.5      | 0.0001    | 100       |
   | 6-BFW-002      | 2000   | 0.6      | 0.0002    | 200       |
   | P-101          | 1000   | 0.5      | 0.0001    | 100       |
   | FV-101         | 2000   | 0.6      | 0.0002    | 200       |

 - *Note* : Flowline parameters should be selected
5. Click **"Submit"** to proceed.

---

## **Input Required:**
- **Pipesim file**
- **Excel file**

## **License Requirement:**
- Only Python Toolkit license required

## **Expected Runtime:**
- Approximately 1-2 minutes per model

---

# Running Simulations Workflow

To run simulations for all `.pips` files in a specified folder, follow these steps:

## **Steps:**

1. **Open the application.**
2. Navigate to the **"Run Simulation Workflow"** section.
3. Select the **folder containing the Pipesim files.**
4. Click **"Run Simulations"** to start the simulation process.

## **Input Required:**
- Folder containing Pipesim files

## **License Requirement:**
- Both Pipesim and Python Toolkit licenses required

## **Expected Runtime:**
- Approximately 5-10 minutes per simulation, depending on the model size

---

# Multi-Case Simulation Workflow

To run multiple simulation cases and compare their results, follow these steps:

## **Steps:**

1. **Open the application.**
2. Navigate to the **"Multi-Case Simulation Workflow"** section.
3. Select the **Excel file** containing the well profiles and conditions.
4. Select the **appropriate sheets** for well profiles and conditions from the dropdown menus.
5. Select the **base Pipesim file**.
6. Click **"Submit"** to start the process.

## **Input Required:**
- **Excel file** with well profiles and conditions
- **Well Profile Sheet Name**
- **Conditions Sheet Name**
- **Base Pipesim file**

## **Naming Convention:**
- Keep the base Pipesim file name short, e.g., `base.pips`.
- Column names for well profiles and conditions in the Excel file **should not contain underscores (_)**.
  - Example Well Profile columns: `Overall-max`, `MinFlowRate`, `MaxFlowRate`
  - Example Conditions columns: `S-HP` (abbrevation for Summer High Pressure), `S-HP-EO` (for Summer High Pressure Early Operations)
- Ensure well profile and conditions column names are unique and short to avoid long output file names.
- Output file naming convention: `<base_pip_file_name>_<well_profile_name>_<conditions_name>.pips`
  - Example output file name: `Overall-max_S-HP_base.pips`

## **Excel File Format:**
- The Excel file should contain two sheets: one for well profiles and the other for conditions.
- Well Profile sheet:
    - The first column should contain the well name.
    - Subsequent columns should contain the well profile data.
    - Column should not contain underscores (_).
    - Sample table:

   | Wells        | Overall-max | MinFlowRate | MaxFlowRate |
   | ------------ | ----------- | ----------- | ----------- |
   | BB-1023         | 1000        | 500         | 1500        |
   | Well-102      | 1200        | 600         | 1800        |
   | well         | 800         | 400         | 1200        |

- Conditions sheet:
    - The first column should contain the condition abbreviation.
    - A condition can have multiple components, just repeat the condition abbreviation for each component in first column.
    - Second column should contain the component name.
    - Third column should contain the component type.
    - Fourth column should contain the Parameter corresponding to the component.
    - Fifth column should contain the value of the parameter.
    - Column should not contain underscores (_).
    - Sample table:

    | Conditions | Component Name | Component Type      | Parameter            | Value |
    | ---------- | -------------- | ------------------- | -------------------- | ----- |
    | S-HP       | P-101          | Pump                | PressureDifferential | 100   |
    | S-HP       |                | SimulationSettings  | Ambient Temperature  | 72    |
    | S-LP       | P-101          | Pump                | PressureDifferential | 50    |
    | S-LP       |                | SimulationSettings  | Ambient Temperature  | 72    |
    | W-HP       | P-101          | Pump                | PressureDifferential | 100   |
    | W-LP       | P-101          | Pump                | PressureDifferential | 50    |



## **License Requirement:**
- Only Python Toolkit licenses required

## **Expected Runtime:**
- Approximately 5-10 minutes per case, depending on the model size

---

# Summarizing Results Workflow

To summarize the results of the model Node and Profile Results, follow these steps:

## **Steps:**

1. **Open the application.**
2. Navigate to the **"Summarize Data"** section.
3. Select the **folder containing the data files.**
4. Click **"Submit"** to generate the summary.

## **Input Required:**
- Folder containing Excel files generated through the Run Simulation Workflow

## **License Requirement:**
- No additional license required

## **Expected Runtime:**
- Approximately 2-3 minutes per summary

---

# Updating Conditions Workflow

To copy the flowline data from a source model to all the models in a folder, follow these steps:

## **Steps:**

1. **Open the application.**
2. Navigate to the **"Update Conditions Workflow"** section.
3. Select the **source model** and the **destination folder.**
4. Click **"Copy Data"** to start the process.

## **Input Required:**
- **Source model**
- **Destination folder**

## **License Requirement:**
- Only Python Toolkit license required

## **Expected Runtime:**
- Heavily time-consuming process.
- Approximately 50 seconds to copy data for one flowline.

---

