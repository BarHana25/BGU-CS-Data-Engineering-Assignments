using System;
using System.Drawing;
using System.Windows.Forms;

namespace SpreadsheetApp
{
    public class Form1 : Form
    {
        private SharableSpreadSheet sheet;
        private DataGridView grid;
        
        // פקדים בהשראת הסרטון: תיבת טקסט לעריכה חיצונית וכפתור עדכון
        private TextBox editTextBox;
        private Button btnUpdate;
        
        // פקדי המטלה
        private Button btnLoad;
        private Button btnSave;
        
        // שמירת מיקום התא שנבחר כפי שהוצג בסרטון
        private int selectedRowIndex = -1;
        private int selectedColIndex = -1;

        public Form1()
        {
            // אתחול הגיליון בגודל התחלתי של 10x10
            sheet = new SharableSpreadSheet(10, 10);
            
            InitializeUI();
            RefreshGrid();
        }

        private void InitializeUI()
        {
            this.Text = "Sharable Spreadsheet App (Video Style Edit)";
            this.Size = new Size(800, 600);

            // --- כפתורי המטלה (Load / Save) ---
            btnLoad = new Button() { Text = "Load", Location = new Point(10, 10), Width = 100 };
            btnLoad.Click += BtnLoad_Click;

            btnSave = new Button() { Text = "Save", Location = new Point(120, 10), Width = 100 };
            btnSave.Click += BtnSave_Click;

            // --- פקדי עריכה (בהשראת הסרטון) ---
            Label lblEdit = new Label() { Text = "Edit Cell:", Location = new Point(300, 15), Width = 60 };
            
            editTextBox = new TextBox() { Location = new Point(360, 12), Width = 200 };
            
            btnUpdate = new Button() { Text = "Update", Location = new Point(570, 10), Width = 100 };
            btnUpdate.Click += BtnUpdate_Click;

            // --- טבלת הנתונים (DataGridView) ---
            grid = new DataGridView()
            {
                Location = new Point(10, 50),
                Size = new Size(760, 500),
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                ReadOnly = true, // הגנה מעריכה ישירה בתוך התא, נדרוש עריכה מהתיבה כמו בסרטון
                SelectionMode = DataGridViewSelectionMode.CellSelect, // בחירת תא בודד
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
            };
            
            // אירוע לחיצה על תא לשליפת הנתונים (מבוסס על הסרטון)
            grid.CellClick += Grid_CellClick;

            // הוספת הרכיבים לחלון
            this.Controls.Add(btnLoad);
            this.Controls.Add(btnSave);
            this.Controls.Add(lblEdit);
            this.Controls.Add(editTextBox);
            this.Controls.Add(btnUpdate);
            this.Controls.Add(grid);
        }

        // --- אירוע שליפת נתונים לתא טקסט בעת לחיצה (מהסרטון) ---
        private void Grid_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex >= 0 && e.ColumnIndex >= 0)
            {
                // שמירת הקואורדינטות של התא שנבחר
                selectedRowIndex = e.RowIndex;
                selectedColIndex = e.ColumnIndex;

                // שליפת המידע מתוך ה-DataGridView אל ה-TextBox (בדומה לשליפת Person בסרטון)
                object cellValue = grid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value;
                editTextBox.Text = cellValue != null ? cellValue.ToString() : "";
            }
        }

        // --- אירוע עדכון הנתונים בחזרה למודל ולמסך ---
        private void BtnUpdate_Click(object sender, EventArgs e)
        {
            if (selectedRowIndex >= 0 && selectedColIndex >= 0)
            {
                try
                {
                    string newValue = editTextBox.Text;
                    
                    // 1. עדכון אובייקט הגיליון (המודל)
                    sheet.setCell(selectedRowIndex, selectedColIndex, newValue);
                    
                    // 2. עדכון התצוגה הגרפית
                    grid.Rows[selectedRowIndex].Cells[selectedColIndex].Value = newValue;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            else
            {
                MessageBox.Show("Please select a cell first.", "Notice", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        // פונקציה הבקטנה טוענת את הנתונים מהאובייקט הלוגי אל תוך ה-Grid
        private void RefreshGrid()
        {
            grid.Rows.Clear();
            grid.Columns.Clear();
            
            var size = sheet.getSize();
            int rows = size.Item1;
            int cols = size.Item2;

            for (int c = 0; c < cols; c++)
            {
                grid.Columns.Add($"Col{c}", $"Col {c}");
            }

            for (int r = 0; r < rows; r++)
            {
                grid.Rows.Add();
                grid.Rows[r].HeaderCell.Value = $"Row {r}";
                for (int c = 0; c < cols; c++)
                {
                    grid.Rows[r].Cells[c].Value = sheet.getCell(r, c);
                }
            }
        }

        // פעולת טעינה מקובץ
        private void BtnLoad_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog ofd = new OpenFileDialog()) 
            {
                ofd.Filter = "Text Files|*.txt|All Files|*.*";
                if (ofd.ShowDialog() == DialogResult.OK) 
                {
                    try 
                    {
                        sheet.load(ofd.FileName);
                        RefreshGrid();
                    } 
                    catch (Exception ex) 
                    {
                        MessageBox.Show(ex.Message, "Error Loading", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }

        // פעולת שמירה לקובץ
        private void BtnSave_Click(object sender, EventArgs e)
        {
            using (SaveFileDialog sfd = new SaveFileDialog()) 
            {
                sfd.Filter = "Text Files|*.txt|All Files|*.*";
                if (sfd.ShowDialog() == DialogResult.OK) 
                {
                    try 
                    {
                        sheet.save(sfd.FileName);
                    } 
                    catch (Exception ex) 
                    {
                        MessageBox.Show(ex.Message, "Error Saving", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }
    }
}




