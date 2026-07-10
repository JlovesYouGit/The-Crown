using System;
using System.IO;

namespace QuantumEnergyService
{
    public class CosmicWorldExplorer
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("Cosmic World Explorer");
            Console.WriteLine("====================");
            Console.WriteLine();
            
            // Display current qubit data
            DisplayCurrentQubitData();
            
            Console.WriteLine();
            
            // Display universe map data
            DisplayUniverseMapData();
            
            Console.WriteLine();
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
        
        private static void DisplayCurrentQubitData()
        {
            Console.WriteLine("Current Qubit Status:");
            Console.WriteLine("--------------------");
            
            try
            {
                if (File.Exists("c:\\QuantumEnergyService\\qubit_data.txt"))
                {
                    string[] lines = File.ReadAllLines("c:\\QuantumEnergyService\\qubit_data.txt");
                    
                    foreach (string line in lines)
                    {
                        if (line.Contains("Snapshot Count"))
                        {
                            Console.WriteLine("📊 " + line);
                        }
                        else if (line.Contains("Qubit-"))
                        {
                            Console.WriteLine("⚛️  " + line);
                        }
                        else if (line.Contains("Last Updated"))
                        {
                            Console.WriteLine("🕐 " + line);
                        }
                    }
                }
                else
                {
                    Console.WriteLine("No current qubit data available.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error reading qubit data: " + ex.Message);
            }
        }
        
        private static void DisplayUniverseMapData()
        {
            Console.WriteLine("Mapped Celestial Objects:");
            Console.WriteLine("------------------------");
            
            try
            {
                if (File.Exists("c:\\QuantumEnergyService\\universe_map.dat"))
                {
                    string[] lines = File.ReadAllLines("c:\\QuantumEnergyService\\universe_map.dat");
                    
                    bool inCelestialSection = false;
                    int objectCount = 0;
                    string currentObjectName = "";
                    
                    for (int i = 0; i < lines.Length; i++)
                    {
                        string line = lines[i].Trim();
                        
                        if (line == "[CELESTIAL_OBJECTS]")
                        {
                            inCelestialSection = true;
                            i++; // Skip the count line
                            continue;
                        }
                        
                        if (line == "[QUBIT_WAYPOINTS]")
                        {
                            break; // End of celestial objects section
                        }
                        
                        if (inCelestialSection)
                        {
                            if (objectCount % 9 == 0)
                            {
                                // This is the object name
                                currentObjectName = line;
                                Console.WriteLine("🌍 " + currentObjectName + ":");
                            }
                            else if (objectCount % 9 == 1)
                            {
                                // X position
                                Console.Write("   Position: (" + line + ", ");
                            }
                            else if (objectCount % 9 == 2)
                            {
                                // Y position
                                Console.Write(line + ", ");
                            }
                            else if (objectCount % 9 == 3)
                            {
                                // Z position
                                Console.WriteLine(line + ")");
                            }
                            else if (objectCount % 9 == 7)
                            {
                                // Mass
                                Console.WriteLine("   Mass: " + line);
                            }
                            else if (objectCount % 9 == 8)
                            {
                                // Object type
                                Console.WriteLine("   Type: " + line);
                                Console.WriteLine();
                            }
                            
                            objectCount++;
                        }
                    }
                    
                    Console.WriteLine("Total mapped celestial objects: " + (objectCount / 9));
                    Console.WriteLine("Total qubit waypoints tracked: " + lines[lines.Length - 1]);
                }
                else
                {
                    Console.WriteLine("No universe map data available.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error reading universe map: " + ex.Message);
            }
        }
    }
}