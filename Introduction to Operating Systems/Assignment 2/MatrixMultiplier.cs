using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;

namespace MergeSortApp
{
   class Program
   {
       static void Main(string[] args)
       {
           Console.WriteLine("Generating a large array of random strings...");
          
           // Creating a very large array to see the advantage of multithreading
           int arraySize = 1000000; // One million elements (can be reduced if the computer freezes)
           string[] rawData = new string[arraySize];
           Random rand = new Random();
          
           for (int i = 0; i < arraySize; i++)
           {
               // Creating a short random string
               rawData[i] = rand.Next(1000, 999999).ToString();
           }

           MTMergeSort sorter = new MTMergeSort();
          
           Console.WriteLine($"Starting Multithreaded MergeSort on {arraySize} elements...");
           Stopwatch sw = Stopwatch.StartNew();
          
           // Calling the parallel sort function
           List<string> sortedList = sorter.MergeSort(rawData, 1000);
           // nMin = 1000 means that any chunk smaller than 1000 will be sorted normally to save unnecessary thread creation
          
           sw.Stop();
          
           Console.WriteLine("Sorting completed!");
           Console.WriteLine($"Total time taken: {sw.ElapsedMilliseconds} ms");
          
           // Small sample check to ensure the array is actually sorted
           Console.WriteLine("\nFirst 5 elements of sorted list:");
           for(int i = 0; i < 5; i++)
           {
               Console.WriteLine(sortedList[i]);
           }
       }
   }

   class MTMergeSort
   {
       // performs the multithreaded merge-sort
       // Get list of string as input (strList) and the minimum numbers that each thread sort (nMin)
       public List<string> MergeSort(string[] strList, int nMin = 2)
       {
           // 1. Threshold Check (Base Case):
           // If the array size is less than or equal to nMin, sort it sequentially.
           if (strList.Length <= nMin)
           {
               List<string> list = new List<string>(strList);
               list.Sort(); // Sequential built-in sort
               return list;
           }

           // 2. Fork Phase (Split the array into two halves)
           int mid = strList.Length / 2;
           string[] leftArray = strList.Take(mid).ToArray();
           string[] rightArray = strList.Skip(mid).ToArray();

           // Fixing Null warnings: initializing as empty lists
           List<string> leftSorted = new List<string>();
           List<string> rightSorted = new List<string>();

           // Create two child threads to sort each half recursively
           Thread leftThread = new Thread(() => { leftSorted = MergeSort(leftArray, nMin); });
           Thread rightThread = new Thread(() => { rightSorted = MergeSort(rightArray, nMin); });

           // Start executing the threads concurrently
           leftThread.Start();
           rightThread.Start();

           // 3. Join Phase (Synchronization)
           // The parent thread MUST wait for both child threads to finish before merging
           leftThread.Join();
           rightThread.Join();

           // 4. Merge Phase
           // Merge the two sorted halves and return the final sorted list
           return MergeLists(leftSorted, rightSorted);
       }

       // Helper method to merge two sorted lists of strings
       private List<string> MergeLists(List<string> left, List<string> right)
       {
           List<string> result = new List<string>(left.Count + right.Count);
           int i = 0, j = 0;

           // Compare and merge elements
           while (i < left.Count && j < right.Count)
           {
               // Using string.Compare() as requested
               if (string.Compare(left[i], right[j]) <= 0)
               {
                   result.Add(left[i]);
                   i++;
               }
               else
               {
                   result.Add(right[j]);
                   j++;
               }
           }

           // Add any remaining elements from the left list
           while (i < left.Count)
           {
               result.Add(left[i]);
               i++;
           }

           // Add any remaining elements from the right list
           while (j < right.Count)
           {
               result.Add(right[j]);
               j++;
           }

           return result;
       }
   }
}