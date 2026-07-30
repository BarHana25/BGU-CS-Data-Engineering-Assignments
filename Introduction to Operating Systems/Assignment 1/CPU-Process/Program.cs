using System;
using System.Diagnostics;

class Program
{
    static void Main(string[] args)
    {
        int n = int.Parse(args[0]);
        Console.WriteLine("Running intensive calculations...");

        Stopwatch sw = Stopwatch.StartNew();

        for (int i = 0; i < n; i++)
        {
            CalculateFibonacci(10000);
        }

        sw.Stop();
        Console.WriteLine($"Time for {n} iterations: {sw.Elapsed.TotalMilliseconds:F2} ms");
    }

    static long CalculateFibonacci(int limit)
    {
        long a = 0, b = 1;
        for (int i = 0; i < limit; i++)
        {
            long temp = a + b;
            a = b;
            b = temp;
        }
        return a;
    }
}