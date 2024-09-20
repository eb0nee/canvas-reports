## Getting Started

*These instructions are intended for computers running MacOS or Linux.*

Download the repository. Navigate to the `canvas-grade-reports` directory to run the following lines. This is achievable using a text editor like VSCode.

### Prerequisites

Run the following line in the terminal.
  ```
  pip install -r requirements.txt
  ```

## Usage
1. Download the current Outcomes report from Canvas. This should be a **CSV file**.
2. Place the report in the `outcome_reports` folder.
3. In the terminal, enter the following command:
   ```
   python main.py outcome_report.csv
   ```
   where `outcome_report.csv` is the name of the chosen report.

4. The script will save a grade report in a CSV file that is uploadable to Canvas. To upload, navigate to the Canvas "Grades" page, where you can then upload the report.
5. Confirm all the changes within Canvas
