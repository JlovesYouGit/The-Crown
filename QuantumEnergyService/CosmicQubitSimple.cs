using System;
using System.Collections.Generic;
using System.Threading;
using System.IO;

namespace QuantumEnergyService
{
    /// <summary>
    /// Simplified Cosmic Qubit Management Service
    /// </summary>
    public class CosmicQubitSimple
    {
        private List<string> _qubitData;
        private string _dataFile;
        private bool _isRunning;
        private int _snapshotCount;
        
        public CosmicQubitSimple()
        {
            _qubitData = new List<string>();
            _dataFile = "c:\\QuantumEnergyService\\qubit_data.txt";
            _isRunning = false;
            _snapshotCount = 0;
            InitializeData();
        }
        
        private void InitializeData()
        {
            // Initialize with some sample data
            _qubitData.Add("Qubit-001: Position(100,200,300) Energy: 5000K");
            _qubitData.Add("Qubit-002: Position(400,500,600) Energy: 7500K");
            _qubitData.Add("Qubit-003: Position(700,800,900) Energy: 10000K");
            Console.WriteLine("Initialized " + _qubitData.Count + " qubits");
        }
        
        public void StartService()
        {
            _isRunning = true;
            Console.WriteLine("Cosmic Qubit Simple Service Started");
            
            // Simulate service work
            Thread workerThread = new Thread(DoWork);
            workerThread.Start();
        }
        
        private void DoWork()
        {
            int counter = 0;
            while (_isRunning)
            {
                counter++;
                
                // Every 10 cycles, take a snapshot
                if (counter % 10 == 0)
                {
                    TakeSnapshot();
                }
                
                // Every 30 cycles, save data
                if (counter % 30 == 0)
                {
                    SaveData();
                    Console.WriteLine("Service running - Cycle " + counter);
                }
                
                Thread.Sleep(1000);
            }
        }
        
        public void TakeSnapshot()
        {
            _snapshotCount++;
            Console.WriteLine("Snapshot #" + _snapshotCount + " taken");
        }
        
        public void RecallData()
        {
            Console.WriteLine("Recalling data from last snapshot");
            LoadData();
        }
        
        private void SaveData()
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(_dataFile))
                {
                    writer.WriteLine("Snapshot Count: " + _snapshotCount);
                    foreach (string data in _qubitData)
                    {
                        writer.WriteLine(data);
                    }
                    writer.WriteLine("Last Updated: " + DateTime.Now.ToString());
                }
                Console.WriteLine("Data saved to " + _dataFile);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error saving data: " + ex.Message);
            }
        }
        
        private void LoadData()
        {
            try
            {
                if (File.Exists(_dataFile))
                {
                    using (StreamReader reader = new StreamReader(_dataFile))
                    {
                        string line;
                        while ((line = reader.ReadLine()) != null)
                        {
                            Console.WriteLine("Loaded: " + line);
                        }
                    }
                    Console.WriteLine("Data loaded from " + _dataFile);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error loading data: " + ex.Message);
            }
        }
        
        public void StopService()
        {
            _isRunning = false;
            SaveData();
            Console.WriteLine("Cosmic Qubit Simple Service Stopped");
        }
        
        public string GetStatus()
        {
            return "Cosmic Qubit Simple Service Status:\n" +
                   "- Active Qubits: " + _qubitData.Count + "\n" +
                   "- Snapshots Taken: " + _snapshotCount + "\n" +
                   "- Service Running: " + (_isRunning ? "Yes" : "No") + "\n" +
                   "- Data File: " + _dataFile;
        }
    }
    
    public class CosmicQubitSimpleProgram
    {
        private static CosmicQubitSimple _service;
        
        public static void Main(string[] args)
        {
            Console.WriteLine("Cosmic Qubit Simple Service");
            Console.WriteLine("==========================");
            
            _service = new CosmicQubitSimple();
            Console.WriteLine(_service.GetStatus());
            Console.WriteLine();
            
            _service.StartService();
            Console.WriteLine("Service started. Commands: 'q' to quit, 's' for status, 'r' for recall");
            
            while (true)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true);
                    if (key.KeyChar == 'q' || key.KeyChar == 'Q')
                    {
                        break;
                    }
                    else if (key.KeyChar == 's' || key.KeyChar == 'S')
                    {
                        Console.WriteLine();
                        Console.WriteLine(_service.GetStatus());
                        Console.WriteLine();
                    }
                    else if (key.KeyChar == 'r' || key.KeyChar == 'R')
                    {
                        Console.WriteLine();
                        _service.RecallData();
                        Console.WriteLine();
                    }
                }
                
                Thread.Sleep(100);
            }
            
            _service.StopService();
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}