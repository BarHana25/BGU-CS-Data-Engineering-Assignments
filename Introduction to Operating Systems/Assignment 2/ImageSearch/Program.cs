using System;
using System.Drawing;
using System.IO;
using System.Threading;

namespace ImageSearch
{
   class Program
   {
       // Lock object to synchronize console output and prevent interleaving of text from different threads
       static readonly object printLock = new object();

       static void Main(string[] args)
       {
           // 1. Validation of command-line arguments
           if (args.Length != 4)
           {
               Console.WriteLine("Error: Invalid number of parameters.");
               Console.WriteLine("Usage: ImageSearch <image1> <image2> <nThreads> <algorithm>");
               Environment.Exit(1);
           }

           string image1Path = args[0]; 
           string image2Path = args[1];
           string nThreadsStr = args[2];
           string algorithm = args[3].ToLower();

           if (!File.Exists(image1Path) || !File.Exists(image2Path))
           {
               Console.WriteLine("Error: One or both image files do not exist.");
               Environment.Exit(1);
           }

           if (!int.TryParse(nThreadsStr, out int nThreads) || nThreads < 1)
           {
               Console.WriteLine("Error: <nThreads> must be an integer greater than 0.");
               Environment.Exit(1);
           }

           if (algorithm != "exact" && algorithm != "euclidian")
           {
               Console.WriteLine("Error: <algorithm> must be 'exact' or 'euclidian'.");
               Environment.Exit(1);
           }

           // 2. Converting images to 2D arrays of Color objects for easier access during the search process
           Color[,] bigImage = ConvertImageToArray(image1Path);
           Color[,] smallImage = ConvertImageToArray(image2Path);

           int bigHeight = bigImage.GetLength(0);
           int bigWidth = bigImage.GetLength(1);
           int smallHeight = smallImage.GetLength(0);
           int smallWidth = smallImage.GetLength(1);

           // If the small image is larger than the big image in either dimension, it's impossible to find a match, so we can exit early
           if (smallHeight > bigHeight || smallWidth > bigWidth)
           {
               Console.WriteLine("Error: image2 is larger than image1.");
               Environment.Exit(1);
           }

           // 3. Define ranges for searching the big image
           int searchRows = bigHeight - smallHeight + 1;
           int searchCols = bigWidth - smallWidth + 1;

           // 4. Strategy for dividing the work among threads (Row-based slicing)
           Thread[] threads = new Thread[nThreads];
           int rowsPerThread = searchRows / nThreads;
           int remainderRows = searchRows % nThreads; 

           int currentRowStart = 0;

           for (int i = 0; i < nThreads; i++)
           {
               // We capture 'startRow' and 'endRow' in local block variables 
               // to prevent the Lambda expression from capturing the shared 'currentRowStart' or loop counters, 
               // avoiding race conditions during thread initialization .
               int startRow = currentRowStart;
               int rowsForThisThread = rowsPerThread + (i < remainderRows ? 1 : 0);
               int endRow = startRow + rowsForThisThread;

               threads[i] = new Thread(() => SearchImageWorker(bigImage, smallImage, startRow, endRow, searchCols, algorithm));
               threads[i].Start();

               currentRowStart = endRow;
           }

           // Barrier synchronization point. 
           // Main thread blocks and waits for all concurrent worker threads to complete their execution 
           // to ensure no premature process termination and clean resource disposal.
           foreach (Thread t in threads)
           {
               t.Join();
           }
       }

       // Helper method to convert an image file into a 2D array of Colors
       static Color[,] ConvertImageToArray(string imagePath)
       {
           using (Bitmap bmp = new Bitmap(imagePath))
           {
               Color[,] pixels = new Color[bmp.Height, bmp.Width];
               for (int y = 0; y < bmp.Height; y++)
               {
                   for (int x = 0; x < bmp.Width; x++)
                   {
                       pixels[y, x] = bmp.GetPixel(x, y);
                   }
               }
               return pixels;
           }
       }

       // Helper method for the work of each Thread - scans a specific range of rows
       static void SearchImageWorker(Color[,] bigImage, Color[,] smallImage, int startRow, int endRow, int searchCols, string algorithm)
       {
           for (int y = startRow; y < endRow; y++)
           {
               for (int x = 0; x < searchCols; x++)
               {
                   bool isMatch = false;

                   if (algorithm == "exact")
                   {
                       isMatch = CheckExactMatch(bigImage, smallImage, x, y);
                   }
                   else if (algorithm == "euclidian")
                   {
                       isMatch = CheckEuclidianMatch(bigImage, smallImage, x, y);
                   }

                   if (isMatch)
                   {
                       // Synchronizing access to the shared standard output stream (Console) 
                       // to prevent garbled text/interleaving from interleaved thread context switches.
                       lock (printLock)
                       {
                           Console.WriteLine($"{x},{y}");
                       }
                   }
               }
           }
       }

       // Sub-matrix evaluation method: Exact match algorithm
       static bool CheckExactMatch(Color[,] bigImage, Color[,] smallImage, int startX, int startY)
       {
           int smallHeight = smallImage.GetLength(0);
           int smallWidth = smallImage.GetLength(1);

           for (int y = 0; y < smallHeight; y++)
           {
               for (int x = 0; x < smallWidth; x++)
               {
                   if (bigImage[startY + y, startX + x] != smallImage[y, x])
                   {
                       // Immediate return on mismatch drastically reduces redundant CPU cycles.
                       return false; 
                   }
               }
           }
           return true;
       }

       // Sub-matrix evaluation method: Euclidean distance match algorithm
       static bool CheckEuclidianMatch(Color[,] bigImage, Color[,] smallImage, int startX, int startY)
       {
           int smallHeight = smallImage.GetLength(0);
           int smallWidth = smallImage.GetLength(1);
           
           double totalDistance = 0;
           double threshold = 0; 

           for (int y = 0; y < smallHeight; y++)
           {
               for (int x = 0; x < smallWidth; x++)
               {
                   Color bColor = bigImage[startY + y, startX + x];
                   Color sColor = smallImage[y, x];

                   // Computing squared Euclidean distance components to avoid expensive square root operations inside the inner loop
                   double distanceSquared = Math.Pow(bColor.R - sColor.R, 2) +
                                           Math.Pow(bColor.G - sColor.G, 2) +
                                           Math.Pow(bColor.B - sColor.B, 2);

                   totalDistance += Math.Sqrt(distanceSquared);

                   if (totalDistance > threshold)
                   {
                       
                       return false;
                   }
               }
           }

           return totalDistance <= threshold;
       }
   }
}