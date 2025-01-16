# Creating a Model Workflow

## **Table of Contents**
1. [Creating a Model Workflow](#creating-a-model-workflow)
   - [Steps](#steps)
   - [Build Model from Scratch](#build-model-from-scratch)
   - [Populate Existing Model](#populate-existing-model)
2. [Running Simulations Workflow](#running-simulations-workflow)
   - [Steps](#steps-1)
3. [Summarizing Results Workflow](#summarizing-results-workflow)
   - [Steps](#steps-2)
4. [Updating Conditions Workflow](#updating-conditions-workflow)
   - [Steps](#steps-3)
5. [Available Features](#available-features)
6. [Functionality of Each Frame](#functionality-of-each-frame)
7. [Structure of Excel Sheets](#structure-of-excel-sheets)
8. [Expected Runtime and License Requirements](#expected-runtime-and-license-requirements)

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

# Available Features

- **Create Model Workflow**
- **Run Simulation Workflow**
- **Summarize Data**
- **Update Conditions Workflow**

---

# Functionality of Each Frame

## **Home Frame:**
- **Description:** The home frame is the main landing page of the application. It provides navigation buttons to access different workflows.
- **Functionality:**
  - **Create Model Workflow:** Navigates to the frame for creating or populating a model.
  - **Update Conditions Workflow:** Navigates to the frame for updating flowline conditions.
  - **Run Simulation Workflow:** Navigates to the frame for running simulations.
  - **Summarize Results Workflow:** Navigates to the frame for summarizing simulation results.
  - **Exit:** Closes the application.

## **Create Model Frame:**
- **Description:** This frame allows users to create a model from scratch or populate an existing model using an Excel file.
- **Functionality:**
  - **Pipesim File:** Allows users to select the Pipesim file.
  - **Excel File:** Allows users to select the Excel file.
  - **Sheet Name:** Allows users to select the sheet name from the Excel file.
  - **Model Options:** Provides options to create a model from scratch or populate an existing model.
  - **Submit:** Submits the selected options and creates or populates the model.

## **Update Conditions Frame:**
- **Description:** This frame allows users to copy flowline data from a source model to all models in a specified folder.
- **Functionality:**
  - **Source Model:** Allows users to select the source model.
  - **Destination Folder:** Allows users to select the destination folder.
  - **Copy Data:** Copies the flowline data from the source model to all models in the destination folder.

## **Run Simulation Frame:**
- **Description:** This frame allows users to run simulations for all `.pips` files in a specified folder.
- **Functionality:**
  - **Folder Containing Pipesim Files:** Allows users to select the folder containing the Pipesim files.
  - **System Variables:** Allows users to select the system variables for the simulation.
  - **Profile Variables:** Allows users to select the profile variables for the simulation.
  - **Unit:** Allows users to select the unit for the simulation.
  - **Run Simulations:** Runs the simulation for all `.pips` files in the selected folder.

## **Summarize Results Frame:**
- **Description:** This frame allows users to summarize the results of the model Node and Profile Results.
- **Functionality:**
  - **Folder Containing Data Files:** Allows users to select the folder containing the data files.
  - **Submit:** Generates the summary of the results.

---

# Structure of Excel Sheets

## **Create Model Workflow:**

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

---

# Expected Runtime and License Requirements

## **Create Model Workflow:**
- **Expected Runtime:** Approximately 1-2 minutes per model
- **License Requirement:** Only Python Toolkit license required

## **Run Simulation Workflow:**
- **Expected Runtime:** Approximately 5-10 minutes per simulation, depending on the model size
- **License Requirement:** Both Pipesim and Python Toolkit licenses required

## **Summarize Results Workflow:**
- **Expected Runtime:** Approximately 2-3 minutes per summary
- **License Requirement:** No additional license required

## **Update Conditions Workflow:**
- **Expected Runtime:** Heavily time-consuming process. Approximately 50 seconds to copy data for one flowline.
- **License Requirement:** Only Python Toolkit license required
