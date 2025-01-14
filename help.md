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

   **Example:**
```
| Component Name | Type           |
| ---------------| -------------- |
| Src-101        | Source         |
| 6-BFW-001      | Flowline       |
| 6-BFW-002      | Flowline       |
| P-101          | Pump           |
| FV-101         | GenericEquipment |
| J1             | Junction       |
| Sk             | Sink           |
```

### **Populate Existing Model:**

- The Excel sheet should contain the component name in the first column and the corresponding data in the subsequent columns.

   **Example:**
   ```plaintext
   Component Name   Length   Diameter   Roughness   Elevation
   6-BFW-001        1000     0.5        0.0001      100
   6-BFW-002        2000     0.6        0.0002      200
   P-101            1000     0.5        0.0001      100
   FV-101           2000     0.6        0.0002      200
   ```

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

