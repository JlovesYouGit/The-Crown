using System;
using System.IO;
using System.Collections.Generic;

namespace QuantumEnergyService
{
    public class QubitVisualizer
    {
        private string _dataFile = "c:\\QuantumEnergyService\\qubit_data.txt";
        
        public void DisplayQubitData()
        {
            Console.WriteLine("Cosmic Qubit Visualizer");
            Console.WriteLine("======================");
            
            try
            {
                if (File.Exists(_dataFile))
                {
                    string[] lines = File.ReadAllLines(_dataFile);
                    
                    Console.WriteLine("Qubit Data Visualization:");
                    Console.WriteLine("------------------------");
                    
                    foreach (string line in lines)
                    {
                        if (line.StartsWith("Qubit-"))
                        {
                            // Parse qubit data
                            string[] parts = line.Split(':');
                            if (parts.Length >= 2)
                            {
                                string qubitId = parts[0];
                                string data = parts[1];
                                
                                // Display with visual formatting
                                Console.WriteLine("┌─────────────────────────────────────┐");
                                Console.WriteLine("│ " + qubitId.PadRight(35) + "│");
                                Console.WriteLine("├─────────────────────────────────────┤");
                                Console.WriteLine("│ " + data.PadRight(35) + "│");
                                Console.WriteLine("└─────────────────────────────────────┘");
                                Console.WriteLine();
                            }
                        }
                        else
                        {
                            Console.WriteLine(line);
                        }
                    }
                }
                else
                {
                    Console.WriteLine("No qubit data file found at: " + _dataFile);
                    Console.WriteLine("Start the service to generate data.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error reading qubit data: " + ex.Message);
            }
        }
        
        public void DisplaySystemStats()
        {
            Console.WriteLine("System Statistics");
            Console.WriteLine("=================");
            
            try
            {
                // Display basic system information
                Console.WriteLine("System Time: " + DateTime.Now.ToString());
                Console.WriteLine("Working Directory: " + Environment.CurrentDirectory);
                Console.WriteLine("OS Version: " + Environment.OSVersion.ToString());
                Console.WriteLine("Processor Count: " + Environment.ProcessorCount);
                Console.WriteLine("Machine Name: " + Environment.MachineName);
                
                // Display file information
                if (File.Exists(_dataFile))
                {
                    FileInfo fileInfo = new FileInfo(_dataFile);
                    Console.WriteLine("Data File Size: " + fileInfo.Length + " bytes");
                    Console.WriteLine("Last Write Time: " + fileInfo.LastWriteTime.ToString());
                }
                else
                {
                    Console.WriteLine("Data file does not exist yet.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error getting system stats: " + ex.Message);
            }
        }
        
        public static void Main(string[] args)
        {
            QubitVisualizer visualizer = new QubitVisualizer();
            
            Console.WriteLine("Cosmic Qubit Data Visualization Tool");
            Console.WriteLine("====================================");
            Console.WriteLine();
            
            if (args.Length > 0 && args[0] == "stats")
            {
                visualizer.DisplaySystemStats();
            }
            else
            {
                visualizer.DisplayQubitData();
            }
            
            Console.WriteLine();
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}