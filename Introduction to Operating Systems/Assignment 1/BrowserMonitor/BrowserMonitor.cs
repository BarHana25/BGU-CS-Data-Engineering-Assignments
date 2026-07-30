using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;

namespace BrowserMonitor
{
    class BrowserMonitor
    {
        static void Main(string[] args)
        {
            // List of browsers we want to monitor,I changed the browser names to match a MacBook
            string[] browsersToWatch = { "Google Chrome", "Microsoft Edge", "firefox", "Opera" };
            
            // Dictionary to store processes found in the previous check (PID -> Browser Name)
            Dictionary<int, string> lastKnownProcesses = new Dictionary<int, string>();

            Console.WriteLine("Browser Monitor is running... Press Ctrl+C to stop.\n");

            while (true)
            {
                // Set to store PIDs found in the current check
                HashSet<int> currentIterationPIDs = new HashSet<int>();

                foreach (string browserName in browsersToWatch)
                {
                    // Get all active processes with this specific name
                    Process[] processes = Process.GetProcessesByName(browserName);

                    foreach (Process p in processes)
                    {
                        currentIterationPIDs.Add(p.Id);

                        // If the PID wasn't in the dictionary before, it means the process just started
                        if (!lastKnownProcesses.ContainsKey(p.Id))
                        {
                            Console.WriteLine($"[+] {browserName} (PID: {p.Id}) has started at {DateTime.Now:HH:mm:ss}");
                            lastKnownProcesses.Add(p.Id, browserName);
                        }
                    }
                }

                // Check for closed processes: 
                // If a PID was in the dictionary but isn't in the current check, it was closed
                var closedPIDs = lastKnownProcesses.Keys
                    .Where(pid => !currentIterationPIDs.Contains(pid))
                    .ToList();

                foreach (int pid in closedPIDs)
                {
                    string browserName = lastKnownProcesses[pid];
                    Console.WriteLine($"[-] {browserName} (PID: {pid}) has closed at {DateTime.Now:HH:mm:ss}");
                    lastKnownProcesses.Remove(pid);
                }

                // Pause the loop for one second as required
                Thread.Sleep(1000);
            }
        }
    }
}