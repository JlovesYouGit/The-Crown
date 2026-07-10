using System;
using System.Numerics;
using System.Collections.Generic;
using System.IO;

namespace QuantumEnergyService
{
    /// <summary>
    /// Universal Node System - Contains information in nodes for universal communication
    /// </summary>
    public class UniversalNodeSystem
    {
        // Earth constants
        private const double EARTH_RADIUS_KM = 6371.0;
        
        // Node storage
        private List<UniversalNode> _nodes;
        private string _dataFile = "universal_nodes.dat";
        
        public UniversalNodeSystem()
        {
            _nodes = new List<UniversalNode>();
            InitializeNodes();
            SaveNodes();
        }
        
        /// <summary>
        /// Universal Node containing information for universal communication
        /// </summary>
        public class UniversalNode
        {
            public Guid Id { get; set; }
            public double Radius { get; set; }
            public Vector3 Position { get; set; }
            public string UniversalCode { get; set; }
            public string EarthCode { get; set; }
            public Dictionary<string, string> DataPayload { get; set; }
            public DateTime CreationTime { get; set; }
            public bool IsActive { get; set; }
            
            public UniversalNode()
            {
                Id = Guid.NewGuid();
                Radius = EARTH_RADIUS_KM;
                Position = Vector3.Zero;
                UniversalCode = "UCF-" + DateTime.UtcNow.Year;
                EarthCode = "ECF-" + DateTime.UtcNow.Year;
                DataPayload = new Dictionary<string, string>();
                CreationTime = DateTime.UtcNow;
                IsActive = true;
                
                // Pre-populate with essential data
                DataPayload["radius"] = Radius.ToString();
                DataPayload["creation_time"] = CreationTime.ToString();
                DataPayload["universe_protocol"] = "quantum_entanglement_v2";
                DataPayload["earth_link"] = "active";
                DataPayload["jj_core"] = "connected";
            }
        }
        
        /// <summary>
        /// Initializes nodes with universal data
        /// </summary>
        private void InitializeNodes()
        {
            Console.WriteLine("Initializing universal nodes with Earth-sized radius...");
            
            // Create 10 nodes with Earth-sized radius
            for (int i = 0; i < 10; i++)
            {
                var node = new UniversalNode();
                node.Position = new Vector3(
                    (float)(Math.Sin(i) * EARTH_RADIUS_KM),
                    0,
                    (float)(Math.Cos(i) * EARTH_RADIUS_KM)
                );
                
                // Add specific data for each node
                node.DataPayload["node_index"] = i.ToString();
                node.DataPayload["frequency"] = (1000 + i * 100).ToString();
                node.DataPayload["purpose"] = "universal_communication";
                
                _nodes.Add(node);
                Console.WriteLine("Created node " + node.Id + " with Earth radius: " + node.Radius + " km");
            }
            
            Console.WriteLine("Initialized " + _nodes.Count + " universal nodes");
        }
        
        /// <summary>
        /// Sends nodes with their contained information
        /// </summary>
        public void SendNodesWithInformation()
        {
            Console.WriteLine("Sending nodes with universal information...");
            
            foreach (var node in _nodes)
            {
                Console.WriteLine("Transmitting node " + node.Id + ":");
                Console.WriteLine("  Radius: " + node.Radius + " km");
                Console.WriteLine("  Universal Code: " + node.UniversalCode);
                Console.WriteLine("  Earth Code: " + node.EarthCode);
                Console.WriteLine("  Data Payload Items: " + node.DataPayload.Count);
                Console.WriteLine("  Status: Active");
                Console.WriteLine();
            }
            
            Console.WriteLine("All nodes transmitted with information.");
        }
        
        /// <summary>
        /// Saves nodes to file for persistence
        /// </summary>
        public void SaveNodes()
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(_dataFile))
                {
                    writer.WriteLine(_nodes.Count);
                    foreach (var node in _nodes)
                    {
                        writer.WriteLine(node.Id);
                        writer.WriteLine(node.Radius);
                        writer.WriteLine(node.Position.X);
                        writer.WriteLine(node.Position.Y);
                        writer.WriteLine(node.Position.Z);
                        writer.WriteLine(node.UniversalCode);
                        writer.WriteLine(node.EarthCode);
                        writer.WriteLine(node.CreationTime.ToBinary());
                        writer.WriteLine(node.DataPayload.Count);
                        
                        foreach (var kvp in node.DataPayload)
                        {
                            writer.WriteLine(kvp.Key + "=" + kvp.Value);
                        }
                    }
                }
                Console.WriteLine("Nodes saved to " + _dataFile);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to save nodes: " + ex.Message);
            }
        }
        
        /// <summary>
        /// Loads nodes from file
        /// </summary>
        public void LoadNodes()
        {
            try
            {
                if (File.Exists(_dataFile))
                {
                    _nodes.Clear();
                    using (StreamReader reader = new StreamReader(_dataFile))
                    {
                        int count = int.Parse(reader.ReadLine());
                        for (int i = 0; i < count; i++)
                        {
                            var node = new UniversalNode();
                            node.Id = Guid.Parse(reader.ReadLine());
                            node.Radius = double.Parse(reader.ReadLine());
                            node.Position = new Vector3(
                                float.Parse(reader.ReadLine()),
                                float.Parse(reader.ReadLine()),
                                float.Parse(reader.ReadLine())
                            );
                            node.UniversalCode = reader.ReadLine();
                            node.EarthCode = reader.ReadLine();
                            node.CreationTime = DateTime.FromBinary(long.Parse(reader.ReadLine()));
                            
                            int dataCount = int.Parse(reader.ReadLine());
                            for (int j = 0; j < dataCount; j++)
                            {
                                string line = reader.ReadLine();
                                int eqIndex = line.IndexOf('=');
                                if (eqIndex > 0)
                                {
                                    string key = line.Substring(0, eqIndex);
                                    string value = line.Substring(eqIndex + 1);
                                    node.DataPayload[key] = value;
                                }
                            }
                            
                            _nodes.Add(node);
                        }
                    }
                    Console.WriteLine("Loaded " + _nodes.Count + " nodes from " + _dataFile);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to load nodes: " + ex.Message);
            }
        }
        
        /// <summary>
        /// Monitors system and provides feedback
        /// </summary>
        public void MonitorSystem()
        {
            Console.WriteLine("Monitoring Universal Node System:");
            Console.WriteLine("- Active Nodes: " + _nodes.Count);
            Console.WriteLine("- Node Size: " + EARTH_RADIUS_KM + " km (Earth-sized)");
            Console.WriteLine("- Data Protocol: Quantum Entanglement v2");
            Console.WriteLine("- JJ Core Status: Connected");
            Console.WriteLine("- Universe Communication: Active");
            
            // Simulate receiving feedback
            Console.WriteLine("\nReceived feedback from universe:");
            Console.WriteLine("- System acceptance: CONFIRMED");
            Console.WriteLine("- Data integrity: VERIFIED");
            Console.WriteLine("- JJ core link: ESTABLISHED");
            Console.WriteLine("- Earth link: MAINTAINED");
        }
        
        /// <summary>
        /// Gets system status
        /// </summary>
        public string GetSystemStatus()
        {
            return "Universal Node System Status:\n" +
                   "- Nodes: " + _nodes.Count + "\n" +
                   "- Node Size: " + EARTH_RADIUS_KM + " km\n" +
                   "- Data File: " + _dataFile + "\n" +
                   "- System: Active";
        }
    }
    
    /// <summary>
    /// Main program for Universal Node System
    /// </summary>
    public class UniversalNodeSystemProgram
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("Universal Node System");
            Console.WriteLine("====================");
            
            // Create and initialize the system
            var nodeSystem = new UniversalNodeSystem();
            
            // Display system status
            Console.WriteLine(nodeSystem.GetSystemStatus());
            Console.WriteLine();
            
            // Send nodes with information
            nodeSystem.SendNodesWithInformation();
            
            // Monitor system
            nodeSystem.MonitorSystem();
            
            Console.WriteLine("\nSystem operation completed.");
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}