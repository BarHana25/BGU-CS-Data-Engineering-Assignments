using System;
using System.Threading;

// Q3.B - Multiple users simulator.
// Usage: Simulator <rows> <cols> <nThreads> <nOperations> <mssleep>
//
// Creates a rows*cols spreadsheet, fills it with strings, then launches
// nThreads threads. Each thread performs nOperations RANDOM operations
// (every operation the class supports EXCEPT load/save), sleeping mssleep
// milliseconds between operations. Every operation is logged with a timestamp.
// Log lines are color-coded by operation type for readability.
class Program
{
    // A small lock so a colored line (set color -> write -> reset) is printed
    // atomically and colors from different threads don't mix.
    static readonly object consoleLock = new object();

    static void Main(string[] args)
    {
        // ---- 1. Parse command-line arguments ----
        if (args.Length != 5)
        {
            Console.WriteLine("Usage: Simulator <rows> <cols> <nThreads> <nOperations> <mssleep>");
            return;
        }

        int rows        = int.Parse(args[0]);
        int cols        = int.Parse(args[1]);
        int nThreads    = int.Parse(args[2]);
        int nOperations = int.Parse(args[3]);
        int msSleep     = int.Parse(args[4]);

        Console.WriteLine("==================================================");
        Console.WriteLine("           SHARABLE SPREADSHEET SIMULATOR");
        Console.WriteLine("==================================================");
        Console.WriteLine($"Spreadsheet size : {rows} x {cols}");
        Console.WriteLine($"Number of users  : {nThreads}");
        Console.WriteLine($"Ops per user     : {nOperations}");
        Console.WriteLine($"Sleep between ops: {msSleep} ms");
        Console.WriteLine("==================================================\n");

        // ---- 2. Create the spreadsheet and fill it with prepared strings ----
        // Each cell starts as "R<row>C<col>", e.g. R3C5.
        var sheet = new SharableSpreadSheet(rows, cols, nThreads);
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                sheet.setCell(r, c, $"R{r}C{c}");

        Console.WriteLine("---- Spreadsheet BEFORE simulation ----");
        PrintSheet(sheet);
        Console.WriteLine("\n---- Simulation started ----\n");

        // ---- 3. Launch nThreads threads, each doing nOperations random ops ----
        Thread[] users = new Thread[nThreads];
        for (int i = 0; i < nThreads; i++)
        {
            int userId = 100 + i;                   // friendly user id for the logs
            users[i] = new Thread(() => UserWork(sheet, userId, nOperations, msSleep));
            users[i].Start();
        }

        // Wait for every user to finish.
        foreach (var t in users)
            t.Join();

        // ---- Print the spreadsheet at the end ----
        Console.WriteLine("\n---- Simulation finished ----\n");
        Console.WriteLine("---- Spreadsheet AFTER simulation ----");
        PrintSheet(sheet);
        Console.WriteLine("\nAll users completed their operations successfully.");
    }

    // The work each user (thread) performs.
    static void UserWork(SharableSpreadSheet sheet, int userId, int nOperations, int msSleep)
    {
        // Each thread gets its OWN Random, seeded differently, so threads
        // don't share a Random (which is not thread-safe) and don't all
        // generate the same sequence.
        var rnd = new Random(Environment.TickCount + userId);

        for (int op = 0; op < nOperations; op++)
        {
            try
            {
                // Read the current size each time (another thread may have changed it).
                var size = sheet.getSize();
                int curRows = size.Item1;
                int curCols = size.Item2;

                // Pick a random operation (0..13) - all ops except load/save.
                int choice = rnd.Next(0, 14);

                switch (choice)
                {
                    case 0: // setCell  -> write (green)
                    {
                        int r = rnd.Next(curRows), c = rnd.Next(curCols);
                        string val = "val" + rnd.Next(1000);
                        sheet.setCell(r, c, val);
                        Log(userId, ConsoleColor.Green, $"wrote \"{val}\" into cell [{r},{c}].");
                        break;
                    }
                    case 1: // getCell  -> read (cyan)
                    {
                        int r = rnd.Next(curRows), c = rnd.Next(curCols);
                        string val = sheet.getCell(r, c);
                        Log(userId, ConsoleColor.Cyan, $"read cell [{r},{c}], got \"{val}\".");
                        break;
                    }
                    case 2: // searchString  -> search (yellow)
                    {
                        string target = $"R{rnd.Next(curRows)}C{rnd.Next(curCols)}";
                        var p = sheet.searchString(target);
                        Log(userId, ConsoleColor.Yellow, $"searched \"{target}\", found at cell [{p.Item1},{p.Item2}].");
                        break;
                    }
                    case 3: // searchInRow  -> search (yellow)
                    {
                        int r = rnd.Next(curRows);
                        string target = $"R{r}C{rnd.Next(curCols)}";
                        int c = sheet.searchInRow(r, target);
                        Log(userId, ConsoleColor.Yellow, $"searched \"{target}\" in row {r}, found at column {c}.");
                        break;
                    }
                    case 4: // searchInCol  -> search (yellow)
                    {
                        int c = rnd.Next(curCols);
                        string target = $"R{rnd.Next(curRows)}C{c}";
                        int r = sheet.searchInCol(c, target);
                        Log(userId, ConsoleColor.Yellow, $"searched \"{target}\" in column {c}, found at row {r}.");
                        break;
                    }
                    case 5: // searchInRange  -> search (yellow)
                    {
                        int r1 = rnd.Next(curRows), r2 = rnd.Next(r1, curRows);
                        int c1 = rnd.Next(curCols), c2 = rnd.Next(c1, curCols);
                        string target = $"R{r1}C{c1}";
                        var p = sheet.searchInRange(c1, c2, r1, r2, target);
                        Log(userId, ConsoleColor.Yellow, $"searched \"{target}\" in range rows[{r1}-{r2}] cols[{c1}-{c2}], " +
                                    $"found at [{p.Item1},{p.Item2}].");
                        break;
                    }
                    case 6: // exchangeRows  -> structural-ish (green)
                    {
                        int r1 = rnd.Next(curRows), r2 = rnd.Next(curRows);
                        sheet.exchangeRows(r1, r2);
                        Log(userId, ConsoleColor.Green, $"exchanged row {r1} with row {r2}.");
                        break;
                    }
                    case 7: // exchangeCols  -> structural-ish (green)
                    {
                        int c1 = rnd.Next(curCols), c2 = rnd.Next(curCols);
                        sheet.exchangeCols(c1, c2);
                        Log(userId, ConsoleColor.Green, $"exchanged column {c1} with column {c2}.");
                        break;
                    }
                    case 8: // addRow  -> structure change (blue)
                    {
                        int r = rnd.Next(curRows);
                        sheet.addRow(r);
                        Log(userId, ConsoleColor.Blue, $"added a new row after row {r}.");
                        break;
                    }
                    case 9: // addCol  -> structure change (blue)
                    {
                        int c = rnd.Next(curCols);
                        sheet.addCol(c);
                        Log(userId, ConsoleColor.Blue, $"added a new column after column {c}.");
                        break;
                    }
                    case 10: // findAll (case sensitive)  -> search (yellow)
                    {
                        string target = $"R{rnd.Next(curRows)}C{rnd.Next(curCols)}";
                        var all = sheet.findAll(target, true);
                        Log(userId, ConsoleColor.Yellow, $"findAll \"{target}\" (case-sensitive) returned {all.Length} cell(s).");
                        break;
                    }
                    case 11: // findAll (case insensitive)  -> search (yellow)
                    {
                        string target = $"r{rnd.Next(curRows)}c{rnd.Next(curCols)}";
                        var all = sheet.findAll(target, false);
                        Log(userId, ConsoleColor.Yellow, $"findAll \"{target}\" (ignore-case) returned {all.Length} cell(s).");
                        break;
                    }
                    case 12: // setAll  -> write (green)
                    {
                        string oldStr = $"R{rnd.Next(curRows)}C{rnd.Next(curCols)}";
                        string newStr = "upd" + rnd.Next(1000);
                        sheet.setAll(oldStr, newStr, true);
                        Log(userId, ConsoleColor.Green, $"replaced all \"{oldStr}\" cells with \"{newStr}\".");
                        break;
                    }
                    case 13: // getSize  -> read (cyan)
                    {
                        var s = sheet.getSize();
                        Log(userId, ConsoleColor.Cyan, $"checked the spreadsheet size: {s.Item1} rows x {s.Item2} columns.");
                        break;
                    }
                }
            }
            catch (Exception ex)
            {
                // Under heavy concurrency an index that was valid a moment ago can
                // become invalid (e.g. another thread changed the sheet), or a
                // search may simply not find its target. We log it in gray and keep
                // going - a stress test only requires that the object never CORRUPTS
                // data or DEADLOCKS, not that every random op succeeds.
                Log(userId, ConsoleColor.DarkGray, $"operation skipped ({ex.Message})");
            }

            // Sleep between operations.
            Thread.Sleep(msSleep);
        }
    }

    // Logging with a timestamp and a color. The whole line is printed under a
    // lock so the color set/reset can't interleave with another thread.
    static void Log(int userId, ConsoleColor color, string message)
    {
        string time = DateTime.Now.ToString("HH:mm:ss");
        lock (consoleLock)
        {
            Console.ForegroundColor = color;
            Console.WriteLine($"User [{userId}] at {time}: {message}");
            Console.ResetColor();
        }
    }

    // Print the whole spreadsheet (used at start and end). Truncates very large
    // sheets so the console doesn't get flooded.
    static void PrintSheet(SharableSpreadSheet sheet)
    {
        var size = sheet.getSize();
        int rows = size.Item1, cols = size.Item2;

        int maxR = Math.Min(rows, 8);     // show at most 8 rows
        int maxC = Math.Min(cols, 8);     // and 8 cols, to keep it readable

        for (int r = 0; r < maxR; r++)
        {
            var line = new System.Text.StringBuilder();
            for (int c = 0; c < maxC; c++)
            {
                string val = sheet.getCell(r, c);
                if (val.Length == 0) val = "-";
                line.Append(val.PadRight(10));
            }
            if (cols > maxC) line.Append("...");
            Console.WriteLine(line.ToString());
        }
        if (rows > maxR) Console.WriteLine("...");
        Console.WriteLine($"(size: {rows} rows x {cols} columns)");
    }
}