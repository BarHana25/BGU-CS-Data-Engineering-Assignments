using System;
using System.IO;

public class VectorSearch
{
    private const int VectorSize = 3072; // גודל וקטור סטנדרטי של Ollama
    // פונקציית המעטפת שנקראת מתוך Program.cs
    public static int Search(float[] queryVector, string algorithm, string fileName)
    {
        // פתיחת הקובץ הבינארי לקריאה
        using (FileStream stream = new FileStream(fileName, FileMode.Open, FileAccess.Read))
        {
            if (algorithm.ToUpper() == "IVF")
            {
                return Search_IVF(stream, queryVector);
            }
            else if (algorithm.ToUpper() == "HNSW")
            {
                // חישוב סך כל הוקטורים בקובץ כדי לדעת מהו טווח ההגרלה המקסימלי
                int totalVectors = (int)(stream.Length / (VectorSize * sizeof(float)));
                return Search_HNSW(stream, queryVector, totalVectors);
            }
            else
            {
                throw new ArgumentException("Unknown algorithm. Use 'IVF' or 'HNSW'.");
            }
        }
    }

    // מימוש IVF - קריאה סדרתית (Sequential I/O)
    public static int Search_IVF(FileStream stream, float[] queryVector)
    {
        byte[] buffer = new byte[VectorSize * sizeof(float)];
        int bestIndex = -1;
        float maxSimilarity = float.MinValue;
        int currentIndex = 0;

        // קריאה רציפה של כל הקובץ מההתחלה עד הסוף
        while (stream.Read(buffer, 0, buffer.Length) > 0)
        {
            float[] currentVector = ByteToFloatArray(buffer);
            float similarity = CalculateCosineSimilarity(queryVector, currentVector);

            if (similarity > maxSimilarity)
            {
                maxSimilarity = similarity;
                bestIndex = currentIndex;
            }
            currentIndex++;
        }
        return bestIndex;
    }

    // מימוש HNSW - קפיצות אקראיות (Random I/O using Seek)
    public static int Search_HNSW(FileStream stream, float[] queryVector, int totalVectors)
    {
        byte[] buffer = new byte[VectorSize * sizeof(float)];
        int bestIndex = -1;
        float maxSimilarity = float.MinValue;

        // נדמה טיול על גרף בעזרת קפיצות אקראיות בקובץ
        Random rng = new Random(42);
        for (int i = 0; i < 5000; i++) // נדגום 5000 נקודות אקראיות
        {
            int randomIndex = rng.Next(0, totalVectors);
            long offset = (long)randomIndex * VectorSize * sizeof(float);

            // הפעולה הקריטית : קפיצה למיקום אקראי בדיסק
            stream.Seek(offset, SeekOrigin.Begin);
            stream.Read(buffer, 0, buffer.Length);

            float[] currentVector = ByteToFloatArray(buffer);
            float similarity = CalculateCosineSimilarity(queryVector, currentVector);

            if (similarity > maxSimilarity)
            {
                maxSimilarity = similarity;
                bestIndex = randomIndex;
            }
        }
        return bestIndex;
    }


    private static float[] ByteToFloatArray(byte[] bytes){
        float[] floats = new float[bytes.Length / sizeof(float)];
        for (int i = 0; i < floats.Length; i++)
        {
            // המרה של 4 בתים למספר float אחד
            floats[i] = BitConverter.ToSingle(bytes, i * sizeof(float));
        }
        return floats;
    }
    private static float CalculateCosineSimilarity(float[] v1, float[] v2) {
        float dotProduct = 0.0f;
        float normA = 0.0f;
        float normB = 0.0f;

        for (int i = 0; i < v1.Length; i++)
        {
            dotProduct += v1[i] * v2[i];
            normA += v1[i] * v1[i];
            normB += v2[i] * v2[i];
        }

        // הגנה מפני חילוק באפס במקרה של וקטור ריק
        if (normA == 0 || normB == 0) return 0;

        return dotProduct / (float)(Math.Sqrt(normA) * Math.Sqrt(normB));
    }
}