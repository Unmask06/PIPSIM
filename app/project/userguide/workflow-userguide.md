# PANDORA - Pipesim Pilot User Guide

### **Table of Contents** 📑

1. [Creating a Model Workflow](#creating-a-model-workflow)
2. [Populate Model Workflow](#populate-model-workflow)
3. [Multi-Case Simulation Workflow](#multi-case-simulation-workflow)
4. [Running Simulations Workflow](#running-simulations-workflow)
5. [Copy Flowline Workflow](#copy-flowline-workflow)
6. [Summarizing Results Workflow](#summarizing-results-workflow)
7. [Downloading Sample Excel File](#downloading-sample-excel-file)

---

## Creating a Model Workflow

To create a model from scratch using an Excel file or populate an existing model with data from an Excel file, follow these steps:

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Create Model Workflow"** section.
3. Select the **Pipesim file** and the **Excel file.**
4. Choose the appropriate option

#### **Create New Model** 🆕

- Refer to the sample Excel sheet for the format. You can download the sample Excel file from the help menu in the application.

#### **Populate Existing Model** 🛠️

- Refer to the sample Excel sheet for the format. You can download the sample Excel file from the help menu in the application.

5. Click **"Submit"** to proceed.

---

### **Input Required** 📂

- **Pipesim file**
- **Excel file**

### **License Requirement** 🔑

- Only Python Toolkit license required

### **Expected Runtime** ⏱️

- Approximately 1-2 minutes per model

---

## Populate Model Workflow

To populate an existing model with data from an Excel file, follow these steps:

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Populate Model Workflow"** section.
3. Select the **Pipesim file** and the **Excel file.**
4. Choose the appropriate mode:
   - **Export**: Export the entire data from the model for the selected components.
   - **Bulk Import**: Bulk import data into the model from the Excel file created by the export mode.
   - **Simple Import**: Import data into the model from a selected sheet in the Excel file.
   - **Flowline Geometry Import**: Import flowline geometry data into the model from the Excel file.
5. Click **"Submit"** to proceed.

---

### **Input Required** 📂

- **Pipesim file**
- **Excel file**

### **License Requirement** 🔑

- Only Python Toolkit license required

### **Expected Runtime** ⏱️

- Approximately 1-2 minutes per model

---

## Multi-Case Simulation Workflow

Multi-Case Simulation Workflow allows you to generate multiple Pipesim files by the combination of well profiles and conditions from an Excel file. The values are fed into the base Pipesim file to create multiple output files.

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Multi-Case Simulation Workflow"** section.
3. Select the **Excel file** containing the well profiles and conditions.
4. Select the **appropriate sheets** for well profiles and conditions from the dropdown menus.
5. Select the **base Pipesim file**.
6. Click **"Submit"** to start the process.

### **Input Required** 📂

- **Excel file** with well profiles and conditions
- **Well Profile Sheet Name**
- **Conditions Sheet Name**
- **Base Pipesim file**

### **Naming Convention** 🏷️

- Keep the base Pipesim file name short, e.g., `base.pips`.
- First 4 columns in the Excel file should be `Component Name`, `Component Type`, `Parameter`, and `Unit`.
  - `Unit` doesn't perfrom any unit conversion, it is just for display purpose.
- Ensure case column names are unique and short to avoid long output file names.
- Output file naming convention: `<base_pip_file_name>_<case_name>.pips`
  - Example output file name: `Overall-max-S-HP_base.pips`

### **License Requirement** 🔑

- Only Python Toolkit licenses required

### **Expected Runtime** ⏱️

- Approximately 5-10 minutes per case, depending on the model size

---

## Running Simulations Workflow

To run simulations for all `.pips` files in a specified folder, follow these steps:

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Run Simulation Workflow"** section.
3. Select the **folder containing the Pipesim files.**
4. Click **"Run Simulations"** to start the simulation process.

### **Input Required** 📂

- Folder containing Pipesim files

### **License Requirement** 🔑

- Both Pipesim and Python Toolkit licenses required

### **Expected Runtime** ⏱️

- Approximately 5-10 minutes per simulation, depending on the model size

---

## Copy Flowline Workflow

To copy the flowline data from a source model to all the models in a folder, follow these steps:

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Update Conditions Workflow"** section.
3. Select the **source model** and the **destination folder.**
4. Click **"Copy Data"** to start the process.

### **Input Required** 📂

- **Source model**
- **Destination folder**

### **License Requirement** 🔑

- Only Python Toolkit license required

### **Expected Runtime** ⏱️

- Heavily time-consuming process.
- Approximately 50 seconds to copy data for one flowline.

---

## Summarizing Results Workflow

To summarize the results of the model Node and Profile Results, follow these steps:

`This feature is currently under development and will be available soon.`

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Summarize Data"** section.
3. Select the **folder containing the data files.**
4. Click **"Submit"** to generate the summary.

### **Input Required** 📂

- Folder containing Excel files generated through the Run Simulation Workflow

### **License Requirement** 🔑

- No additional license required

### **Expected Runtime** ⏱️

- Approximately 2-3 minutes per summary

---

## Downloading Sample Excel File

To download the sample Excel file, follow these steps:

### **Steps** 📝

1. **Open the application.**
2. Navigate to the **"Help"** menu.
3. Select **"Sample Import File"** to download the sample Excel file.

### **License Requirement** 🔑

- No additional license required

### **Expected Runtime** ⏱️

- Instantaneous
