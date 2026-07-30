using System;
using System.Threading;
using System.Threading.Tasks; // Required for the concurrent stress test (Parallel.For)

public interface IBinaryTree
{
    void Add(string value);
    void Delete(string value);
    int Search(string value);
    void PrintSorted();
}

class TreeNode
{
    public string Value;
    public int RefCount; // Reference counter
    public TreeNode Left;
    public TreeNode Right;

    public TreeNode(string value)
    {
        Value = value;
        RefCount = 1; // When a node is created, the counter starts at 1
    }
}

public class ThreadSafeBinaryTree : IBinaryTree
{
    private TreeNode root;

    // --- Synchronization variables (Readers-Writers) ---
    private int read_count = 0;
    private Mutex mutex = new Mutex(); // Protects read_count (locked and released always in the same thread)
    
    // Using SemaphoreSlim instead of Mutex solves the Thread Affinity issue and prevents Deadlocks in the readers-writers model
    private SemaphoreSlim rw_mutex = new SemaphoreSlim(1, 1); 

    // ==========================================
    // Writer methods - Exclusive access
    // ==========================================

    public void Add(string value)
    {
        // Protection against null values - exception thrown before synchronization starts
        if (value == null) throw new ArgumentNullException(nameof(value), "Value cannot be null.");

        rw_mutex.Wait(); // Writer lock - no one else can access the tree
        try
        {
            if (root == null)
            {
                root = new TreeNode(value);
                return;
            }

            TreeNode current = root;
            while (true)
            {
                // Alphabetical comparison of strings based on ASCII values only
                int cmp = string.CompareOrdinal(value, current.Value);
                
                if (cmp == 0)
                {
                    // The string exists - increase the counter
                    current.RefCount++;
                    return;
                }
                else if (cmp < 0)
                {
                    // Go left
                    if (current.Left == null)
                    {
                        current.Left = new TreeNode(value);
                        return;
                    }
                    current = current.Left;
                }
                else
                {
                    // Go right
                    if (current.Right == null)
                    {
                        current.Right = new TreeNode(value);
                        return;
                    }
                    current = current.Right;
                }
            }
        }
        finally
        {
            rw_mutex.Release(); // Release writer lock
        }
    }

    public void Delete(string value)
    {
        // Protection against null values
        if (value == null) throw new ArgumentNullException(nameof(value), "Value cannot be null.");

        rw_mutex.Wait(); // Writer lock
        try
        {
            root = DeleteHelper(root, value);
        }
        finally
        {
            rw_mutex.Release(); // Release writer lock
        }
    }

    // --- Private helper methods for deletion ---
    
    private TreeNode DeleteHelper(TreeNode node, string value)
    {
        if (node == null) return null; // Value not found in the tree

        // Using CompareOrdinal for absolute comparison
        int cmp = string.CompareOrdinal(value, node.Value);

        if (cmp < 0)
        {
            node.Left = DeleteHelper(node.Left, value);
        }
        else if (cmp > 0)
        {
            node.Right = DeleteHelper(node.Right, value);
        }
        else
        {
            // We found the node
            node.RefCount--;

            // If the counter is greater than 0, no physical deletion is needed
            if (node.RefCount > 0) return node;

            // Counter reached 0, physical deletion is required:
            
            // Case 1 + 2: The node has one child or no children at all
            if (node.Left == null) return node.Right;
            if (node.Right == null) return node.Left;

            // Case 3: The node has two children
            // Find the successor (the minimum value in the right subtree)
            TreeNode minNode = FindMin(node.Right);
            
            // Copy its data to the current node
            node.Value = minNode.Value;
            node.RefCount = minNode.RefCount;

            // Physically delete the successor node we copied from
            node.Right = RemoveMin(node.Right);
        }

        return node;
    }

    private TreeNode FindMin(TreeNode node)
    {
        while (node.Left != null) node = node.Left;
        return node;
    }

    private TreeNode RemoveMin(TreeNode node)
    {
        if (node.Left == null) return node.Right;
        node.Left = RemoveMin(node.Left);
        return node;
    }

    // ==========================================
    // Reader methods - Concurrent access
    // ==========================================

    public int Search(string value)
    {
        // Protection against null values
        if (value == null) throw new ArgumentNullException(nameof(value), "Value cannot be null.");

        // --- Reader entry protocol ---
        mutex.WaitOne();
        read_count++;
        if (read_count == 1) // If I am the first reader, I lock the writers
        {
            rw_mutex.Wait();
        }
        mutex.ReleaseMutex();

        int resultCount = 0;
        try
        {
            TreeNode current = root;
            while (current != null)
            {
                // Using CompareOrdinal for absolute comparison
                int cmp = string.CompareOrdinal(value, current.Value);
                if (cmp == 0)
                {
                    resultCount = current.RefCount;
                    break;
                }
                else if (cmp < 0)
                {
                    current = current.Left;
                }
                else
                {
                    current = current.Right;
                }
            }
        }
        finally
        {
            // --- Reader exit protocol ---
            mutex.WaitOne();
            read_count--;
            if (read_count == 0) // If I am the last reader to exit, I release the writers
            {
                rw_mutex.Release();
            }
            mutex.ReleaseMutex();
        }
        
        return resultCount;
    }

    public void PrintSorted()
    {
        mutex.WaitOne();
        read_count++;
        if (read_count == 1) rw_mutex.Wait();
        mutex.ReleaseMutex();

        try
        {
            PrintInOrder(root);
        }
        finally
        {
            mutex.WaitOne();
            read_count--;
            if (read_count == 0) rw_mutex.Release();
            mutex.ReleaseMutex();
        }
    }

    // --- Private helper method for printing ---
    
    private void PrintInOrder(TreeNode node)
    {
        if (node == null) return;
        
        PrintInOrder(node.Left);
        Console.WriteLine($"{node.Value} ({node.RefCount})");
        PrintInOrder(node.Right);
    }
}

class Program
{
    static void Main(string[] args)
    {
        ThreadSafeBinaryTree tree = new ThreadSafeBinaryTree();

        Console.WriteLine("=== part 1: Original Population ===");
        AddMultiple(tree, "Bumblebee", 5);
        AddMultiple(tree, "Grimlock", 3);
        AddMultiple(tree, "Ironhide", 1);
        AddMultiple(tree, "Jazz", 2);
        AddMultiple(tree, "Megatron", 6);
        AddMultiple(tree, "Optimus Prime", 10);
        AddMultiple(tree, "Ratchet", 1);
        AddMultiple(tree, "Starscream", 4);
        AddMultiple(tree, "Wheeljack", 2);

        tree.PrintSorted();
        Console.WriteLine();

        Console.WriteLine("=== part 2: Case Sensitivity Test ===");
        tree.Add("optimus prime"); // Lowercase letters only
        tree.Add("OPTIMUS PRIME"); // Uppercase letters only
        Console.WriteLine($"Search 'Optimus Prime': {tree.Search("Optimus Prime")} (Expected: 10)"); 
        Console.WriteLine($"Search 'optimus prime': {tree.Search("optimus prime")} (Expected: 1)");
        Console.WriteLine($"Search 'OPTIMUS PRIME': {tree.Search("OPTIMUS PRIME")} (Expected: 1)");
        Console.WriteLine();

        Console.WriteLine("=== part 3: Delete Logic Test ===");
        tree.Delete("Megatron"); // Decrease counter (from 6 to 5)
        Console.WriteLine($"Search 'Megatron' after 1 delete: {tree.Search("Megatron")} (Expected: 5)");

        tree.Add("Ghost");
        tree.Delete("Ghost"); // Physical deletion (from 1 to 0)
        Console.WriteLine($"Search 'Ghost' after delete: {tree.Search("Ghost")} (Expected: 0)");
        Console.WriteLine();

        Console.WriteLine("=== part 4: Null Safety Test ===");
        try 
        {
            tree.Add(null);
            Console.WriteLine("Fail: Did not throw exception!");
        } 
        catch (ArgumentNullException) 
        {
            Console.WriteLine("Success: Caught null exception successfully.");
        }
        Console.WriteLine();

        Console.WriteLine("=== part 5: Concurrency Stress Test ===");
        ThreadSafeBinaryTree stressTree = new ThreadSafeBinaryTree();

        // Run 1,000 concurrent operations without deadlock
        Parallel.For(0, 1000, i =>
        {
            string threadItem = "Item_" + (i % 10); // 10 unique keys to create multiple collisions
            
            stressTree.Add(threadItem); 
            int count = stressTree.Search(threadItem); 
            
            if (i % 2 == 0) 
            {
                stressTree.Delete(threadItem); 
            }
        });

        Console.WriteLine("Stress Test Completed Successfully. Tree contents:");
        stressTree.PrintSorted(); 
    }

    /// <summary>
    /// Helper method to add a string to the tree a specified number of times
    /// </summary>
    static void AddMultiple(ThreadSafeBinaryTree tree, string value, int count)
    {
        for (int i = 0; i < count; i++)
        {
            tree.Add(value);
        }
    }
}