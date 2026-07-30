using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;

// Thread-safe in-memory shared spreadsheet.
// Synchronization: one GLOBAL ReaderWriterLockSlim (structureLock) guarding the
// table shape, one ReaderWriterLockSlim PER ROW for cell content, and one
// SemaphoreSlim capping concurrent searches (nUsers; -1 = no limit).
// Deadlock avoidance: global lock before any row lock; multiple row locks taken
// in ascending index order.
class SharableSpreadSheet
{
    // The data: a jagged list of rows, each row is a list of cell strings.
    private List<List<string>> cells;

    // One reader-writer lock per row, kept parallel to 'cells'.
    private List<ReaderWriterLockSlim> rowLocks;

    // Global lock guarding the table structure (number/identity of rows & columns).
    private readonly ReaderWriterLockSlim structureLock = new ReaderWriterLockSlim();

    // Caps concurrent search operations. null means "no limit".
    private readonly SemaphoreSlim searchSemaphore;

    //Function #1
    public SharableSpreadSheet(int nRows, int nCols, int nUsers = -1)
    {
        // nUsers used for the concurrent-search limit, -1 means no limit.
        if (nRows <= 0 || nCols <= 0)
            throw new ArgumentException("Spreadsheet dimensions must be positive (nRows > 0, nCols > 0).");

        // construct an nRows*nCols spreadsheet, every cell starts as empty string
        cells = new List<List<string>>(nRows);
        rowLocks = new List<ReaderWriterLockSlim>(nRows);

        for (int r = 0; r < nRows; r++)
        {
            var row = new List<string>(nCols);
            for (int c = 0; c < nCols; c++)
                row.Add(string.Empty);
            cells.Add(row);
            rowLocks.Add(new ReaderWriterLockSlim());
        }

        // Only build the semaphore if a real limit was requested.
        searchSemaphore = (nUsers > 0) ? new SemaphoreSlim(nUsers, nUsers) : null;
    }

    //Function #2
    public string getCell(int row, int col)
    {
        // return the string at [row,col]
        structureLock.EnterReadLock();                 // structure stable while we read
        try
        {
            ValidateCell(row, col);
            rowLocks[row].EnterReadLock();             // shared access to this row
            try
            {
                return cells[row][col];
            }
            finally { rowLocks[row].ExitReadLock(); }
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #3
    public void setCell(int row, int col, string str)
    {
        // set the string at [row,col]
        if (str == null) throw new ArgumentNullException(nameof(str));

        structureLock.EnterReadLock();                 // not a structural change -> reader
        try
        {
            ValidateCell(row, col);
            rowLocks[row].EnterWriteLock();            // exclusive access to this row only
            try
            {
                cells[row][col] = str;
            }
            finally { rowLocks[row].ExitWriteLock(); }
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #4
    public Tuple<int, int> searchString(string str)
    {
        // return first cell indexes that contains the string (first row to last row)
        if (str == null) throw new ArgumentNullException(nameof(str));

        EnterSearch();
        try
        {
            structureLock.EnterReadLock();
            try
            {
                for (int r = 0; r < cells.Count; r++)   // rows visited in ascending order
                {
                    rowLocks[r].EnterReadLock();        // lock one row at a time -> max concurrency
                    try
                    {
                        for (int c = 0; c < cells[r].Count; c++)
                            if (cells[r][c] != null && cells[r][c].Contains(str))
                                return Tuple.Create(r, c);
                    }
                    finally { rowLocks[r].ExitReadLock(); }
                }
            }
            finally { structureLock.ExitReadLock(); }
        }
        finally { ExitSearch(); }

        throw new Exception($"String \"{str}\" was not found in the spreadsheet.");
    }

    //Function #5
    public void exchangeRows(int row1, int row2)
    {
        // exchange the content of row1 and row2
        structureLock.EnterReadLock();
        try
        {
            if (row1 < 0 || row1 >= cells.Count) throw new ArgumentOutOfRangeException(nameof(row1));
            if (row2 < 0 || row2 >= cells.Count) throw new ArgumentOutOfRangeException(nameof(row2));
            if (row1 == row2) return;

            // Lock BOTH rows, lower index first -> consistent ordering, no deadlock.
            int lo = Math.Min(row1, row2);
            int hi = Math.Max(row1, row2);
            rowLocks[lo].EnterWriteLock();
            try
            {
                rowLocks[hi].EnterWriteLock();
                try
                {
                    var tmp = cells[row1];
                    cells[row1] = cells[row2];
                    cells[row2] = tmp;
                }
                finally { rowLocks[hi].ExitWriteLock(); }
            }
            finally { rowLocks[lo].ExitWriteLock(); }
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #6
    public void exchangeCols(int col1, int col2)
    {
        // exchange the content of col1 and col2
        structureLock.EnterReadLock();
        try
        {
            if (col1 < 0 || col1 >= cells[0].Count) throw new ArgumentOutOfRangeException(nameof(col1));
            if (col2 < 0 || col2 >= cells[0].Count) throw new ArgumentOutOfRangeException(nameof(col2));
            if (col1 == col2) return;

            // Each row's two cells are swapped independently -> one row write-lock at a time.
            for (int r = 0; r < cells.Count; r++)       // ascending row order
            {
                rowLocks[r].EnterWriteLock();
                try
                {
                    var tmp = cells[r][col1];
                    cells[r][col1] = cells[r][col2];
                    cells[r][col2] = tmp;
                }
                finally { rowLocks[r].ExitWriteLock(); }
            }
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #7
    public int searchInRow(int row, string str)
    {
        // perform search in a specific row, return the column of the first match
        if (str == null) throw new ArgumentNullException(nameof(str));

        EnterSearch();
        try
        {
            structureLock.EnterReadLock();
            try
            {
                if (row < 0 || row >= cells.Count)
                    throw new ArgumentOutOfRangeException(nameof(row), $"Row {row} is out of range.");

                rowLocks[row].EnterReadLock();
                try
                {
                    for (int c = 0; c < cells[row].Count; c++)
                        if (cells[row][c] != null && cells[row][c].Contains(str))
                            return c;
                }
                finally { rowLocks[row].ExitReadLock(); }
            }
            finally { structureLock.ExitReadLock(); }
        }
        finally { ExitSearch(); }

        throw new Exception($"String \"{str}\" was not found in row {row}.");
    }

    //Function #8
    public int searchInCol(int col, string str)
    {
        // perform search in a specific col, return the row of the first match
        if (str == null) throw new ArgumentNullException(nameof(str));

        EnterSearch();
        try
        {
            structureLock.EnterReadLock();
            try
            {
                if (col < 0 || col >= cells[0].Count)
                    throw new ArgumentOutOfRangeException(nameof(col), $"Col {col} is out of range.");

                for (int r = 0; r < cells.Count; r++)   // ascending row order
                {
                    rowLocks[r].EnterReadLock();
                    try
                    {
                        if (cells[r][col] != null && cells[r][col].Contains(str))
                            return r;
                    }
                    finally { rowLocks[r].ExitReadLock(); }
                }
            }
            finally { structureLock.ExitReadLock(); }
        }
        finally { ExitSearch(); }

        throw new Exception($"String \"{str}\" was not found in column {col}.");
    }

    //Function #9
    public Tuple<int, int> searchInRange(int col1, int col2, int row1, int row2, string str)
    {
        // perform search within a specific range [row1:row2, col1:col2] (inclusive)
        if (str == null) throw new ArgumentNullException(nameof(str));
        if (row1 > row2 || col1 > col2)
            throw new ArgumentException("Invalid range: expected row1<=row2 and col1<=col2.");

        EnterSearch();
        try
        {
            structureLock.EnterReadLock();
            try
            {
                ValidateCell(row1, col1);
                ValidateCell(row2, col2);

                for (int r = row1; r <= row2; r++)      // ascending row order
                {
                    rowLocks[r].EnterReadLock();
                    try
                    {
                        for (int c = col1; c <= col2; c++)
                            if (cells[r][c] != null && cells[r][c].Contains(str))
                                return Tuple.Create(r, c);
                    }
                    finally { rowLocks[r].ExitReadLock(); }
                }
            }
            finally { structureLock.ExitReadLock(); }
        }
        finally { ExitSearch(); }

        throw new Exception($"String \"{str}\" was not found in the given range.");
    }

    //Function #10
    public void addRow(int row1)
    {
        // add a row after row1
        structureLock.EnterWriteLock();                // exclusive: we rebuild the structure
        try
        {
            if (row1 < 0 || row1 >= cells.Count)
                throw new ArgumentOutOfRangeException(nameof(row1), $"Row {row1} is out of range.");

            int nCols = cells[0].Count;
            var newRow = new List<string>(nCols);
            for (int c = 0; c < nCols; c++) newRow.Add(string.Empty);

            cells.Insert(row1 + 1, newRow);            // keep rows and rowLocks parallel
            rowLocks.Insert(row1 + 1, new ReaderWriterLockSlim());
        }
        finally { structureLock.ExitWriteLock(); }
    }

    //Function #11
    public void addCol(int col1)
    {
        // add a column after col1
        structureLock.EnterWriteLock();                // exclusive
        try
        {
            if (col1 < 0 || col1 >= cells[0].Count)
                throw new ArgumentOutOfRangeException(nameof(col1), $"Col {col1} is out of range.");

            foreach (var row in cells)
                row.Insert(col1 + 1, string.Empty);
        }
        finally { structureLock.ExitWriteLock(); }
    }

    //Function #12
    public Tuple<int, int>[] findAll(string str, bool caseSensitive)
    {
        // perform search and return all relevant cells according to caseSensitive
        if (str == null) throw new ArgumentNullException(nameof(str));

        var results = new List<Tuple<int, int>>();
        string needle = caseSensitive ? str : str.ToLowerInvariant();

        EnterSearch();
        try
        {
            structureLock.EnterReadLock();
            try
            {
                for (int r = 0; r < cells.Count; r++)   // ascending row order
                {
                    rowLocks[r].EnterReadLock();
                    try
                    {
                        for (int c = 0; c < cells[r].Count; c++)
                        {
                            string content = cells[r][c] ?? string.Empty;
                            string hay = caseSensitive ? content : content.ToLowerInvariant();
                            if (hay.Contains(needle))
                                results.Add(Tuple.Create(r, c));
                        }
                    }
                    finally { rowLocks[r].ExitReadLock(); }
                }
            }
            finally { structureLock.ExitReadLock(); }
        }
        finally { ExitSearch(); }

        return results.ToArray();
    }

    //Function #13
    public void setAll(string oldStr, string newStr, bool caseSensitive)
    {
        // replace all cells equal to oldStr with newStr according to caseSensitive
        if (oldStr == null || newStr == null)
            throw new ArgumentNullException("oldStr/newStr must not be null.");

        var cmp = caseSensitive ? StringComparison.Ordinal : StringComparison.OrdinalIgnoreCase;

        structureLock.EnterReadLock();                 // content change, not structural
        try
        {
            for (int r = 0; r < cells.Count; r++)       // each row is independent here
            {
                rowLocks[r].EnterWriteLock();          // one row at a time keeps it concurrent
                try
                {
                    for (int c = 0; c < cells[r].Count; c++)
                        if (string.Equals(cells[r][c], oldStr, cmp))
                            cells[r][c] = newStr;
                }
                finally { rowLocks[r].ExitWriteLock(); }
            }
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #14
    public Tuple<int, int> getSize()
    {
        // return the size of the spreadsheet as (nRows, nCols)
        structureLock.EnterReadLock();
        try
        {
            return Tuple.Create(cells.Count, cells[0].Count);
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #15
    public void save(string fileName)
    {
        // save the spreadsheet to a file. Format: first line "rows cols",
        // then one line per row, cells separated by TAB (special chars escaped).
        if (string.IsNullOrEmpty(fileName)) throw new ArgumentException("fileName must be provided.");

        structureLock.EnterReadLock();                 // snapshot the whole sheet consistently
        try
        {
            var sb = new StringBuilder();
            sb.AppendLine($"{cells.Count} {cells[0].Count}");

            for (int r = 0; r < cells.Count; r++)
            {
                rowLocks[r].EnterReadLock();
                try
                {
                    for (int c = 0; c < cells[r].Count; c++)
                    {
                        if (c > 0) sb.Append('\t');
                        sb.Append(Escape(cells[r][c]));
                    }
                    sb.Append('\n');
                }
                finally { rowLocks[r].ExitReadLock(); }
            }

            System.IO.File.WriteAllText(fileName, sb.ToString());
        }
        finally { structureLock.ExitReadLock(); }
    }

    //Function #16
    public void load(string fileName)
    {
        // load the spreadsheet from fileName, replacing current data and size
        if (string.IsNullOrEmpty(fileName)) throw new ArgumentException("fileName must be provided.");
        if (!System.IO.File.Exists(fileName)) throw new ArgumentException($"File '{fileName}' does not exist.");

        string[] lines = System.IO.File.ReadAllText(fileName).Split('\n');
        if (lines.Length == 0) throw new Exception("File is empty or malformed.");

        string[] header = lines[0].Trim().Split(' ');
        if (header.Length != 2) throw new Exception("Malformed header line.");
        int nRows = int.Parse(header[0]);
        int nCols = int.Parse(header[1]);

        var newCells = new List<List<string>>(nRows);
        for (int r = 0; r < nRows; r++)
        {
            string[] parts = lines[r + 1].Split('\t');
            var row = new List<string>(nCols);
            for (int c = 0; c < nCols; c++)
                row.Add(Unescape(c < parts.Length ? parts[c] : string.Empty));
            newCells.Add(row);
        }

        structureLock.EnterWriteLock();                // exclusive swap-in of new structure
        try
        {
            cells = newCells;
            rowLocks = new List<ReaderWriterLockSlim>(nRows);
            for (int r = 0; r < nRows; r++)
                rowLocks.Add(new ReaderWriterLockSlim());
        }
        finally { structureLock.ExitWriteLock(); }
    }

    // Private helper methods

    // Validate a single (row, col) coordinate. Caller holds structureLock (read).
    private void ValidateCell(int row, int col)
    {
        if (row < 0 || row >= cells.Count)
            throw new ArgumentOutOfRangeException(nameof(row), $"Row {row} is out of range [0,{cells.Count - 1}].");
        if (col < 0 || col >= cells[0].Count)
            throw new ArgumentOutOfRangeException(nameof(col), $"Col {col} is out of range [0,{cells[0].Count - 1}].");
    }

    // Take a search "slot" if a limit is configured (blocks until one is free).
    private void EnterSearch()
    {
        if (searchSemaphore != null)
            searchSemaphore.Wait();
    }

    // Give back a search slot.
    private void ExitSearch()
    {
        if (searchSemaphore != null)
            searchSemaphore.Release();
    }

    // Escape \  ->  \\ , tab -> \t , newline -> \n  (so the delimiters stay unambiguous).
    private static string Escape(string s)
    {
        if (s == null) return string.Empty;
        return s.Replace("\\", "\\\\").Replace("\t", "\\t").Replace("\n", "\\n");
    }

    private static string Unescape(string s)
    {
        var sb = new StringBuilder();
        for (int i = 0; i < s.Length; i++)
        {
            if (s[i] == '\\' && i + 1 < s.Length)
            {
                char next = s[++i];
                if (next == 't') sb.Append('\t');
                else if (next == 'n') sb.Append('\n');
                else sb.Append(next);          // handles \\  -> \
            }
            else sb.Append(s[i]);
        }
        return sb.ToString();
    }
}