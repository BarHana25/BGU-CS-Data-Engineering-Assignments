
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace RagWorker
{
    class Program
    {
        // יצירת מופע יחיד של HttpClient לתקשורת מול ה-API של Ollama
        static readonly HttpClient client = new HttpClient();

        static async Task Main(string[] args)
        {
            //  בדיקה שהמשתמש הזין את שני הארגומנטים הנדרשים בשורת הפקודה (אלגוריתם חיפוש ושאלה)
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: RagWorker.exe <Algorithm> \"<Search_Query>\"");
                return;
            }

            string algorithm = args[0]; // "IVF" or "HNSW"
            string query = args[1];     // e.g., "Is The Godfather good?"

            try
            {
                Console.WriteLine("1. Generating embedding for the query...");
                // שלב 1: שליחת השאילתה ל-Ollama כדי לקבל וקטור
                float[] queryVector = await GetEmbeddingFromOllama(query);

                Console.WriteLine($"2. Searching local vector database using {algorithm}...");
                // שלב 2: חיפוש וקטורי מקומי ותחילת מדידת זמנים. 
                Stopwatch stopwatch = Stopwatch.StartNew();
                
                // קריאה לפונקציה מתוך קובץ VectorSearch.cs 
                int bestMatchIndex = VectorSearch.Search(queryVector, algorithm, "vectors.bin");
                
                stopwatch.Stop();
                Console.WriteLine($"\n--> Search Time ({algorithm}): {stopwatch.ElapsedMilliseconds} ms <--\n");

                Console.WriteLine("3. Retrieving document...");
                // שלב 3: שליפת שורת הטקסט התואמת מתוך קובץ הטקסט לפי האינדקס
                string retrievedText = File.ReadLines("documents.txt").ElementAt(bestMatchIndex);
                Console.WriteLine($"Retrieved Review: {retrievedText}\n");

                Console.WriteLine("4. Generating AI response...");
                // שלב 4: בניית הפרומפט 
                string finalPrompt = $"Please explain the following movie review based on my query: {retrievedText}";
                
                // שליחה לOllama להפקת התשובה הסופית
                string response = await GenerateResponseFromOllama(finalPrompt);
                Console.WriteLine("\n--- AI Response ---");
                Console.WriteLine(response);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred: {ex.Message}");
            }
        }

        // --- פונקציות עזר לתקשורת מול Ollama ---

        static async Task<float[]> GetEmbeddingFromOllama(string prompt)
        {
            // יצירת אובייקט JSON לפי דרישות ה-API של Ollama
            var requestBody = new { model = "phi3", prompt = prompt };
            string json = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            // שליחת בקשת POST
            HttpResponseMessage response = await client.PostAsync("http://localhost:11434/api/embeddings", content);
            response.EnsureSuccessStatusCode();

            // פענוח התשובה לשליפת מערך הוקטורים
            string responseBody = await response.Content.ReadAsStringAsync();
            using JsonDocument doc = JsonDocument.Parse(responseBody);
            var embeddingElement = doc.RootElement.GetProperty("embedding");

            // המרה ממערך JSON למערך float ב-C#
            float[] vector = new float[embeddingElement.GetArrayLength()];
            int i = 0;
            foreach (var element in embeddingElement.EnumerateArray())
            {
                vector[i++] = element.GetSingle();
            }
            return vector;
        }

        static async Task<string> GenerateResponseFromOllama(string prompt)
        {
            // הגדרת stream=false כדי שנקבל את התשובה כולה בבת אחת ולא בחתיכות
            var requestBody = new { model = "phi3", prompt = prompt, stream = false };
            string json = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            // שליחת הפרומפט המורחב (השאילתה + הטקסט שנשלף)
            HttpResponseMessage response = await client.PostAsync("http://localhost:11434/api/generate", content);
            response.EnsureSuccessStatusCode();

            // חילוץ טקסט התשובה מתוך ה-JSON
            string responseBody = await response.Content.ReadAsStringAsync();
            using JsonDocument doc = JsonDocument.Parse(responseBody);
            return doc.RootElement.GetProperty("response").GetString();
        }
    }
}