using System;
using System.Threading.Tasks;

namespace QuantumEnergyService
{
    /// <summary>
    /// Test program to demonstrate JJ Core integration with QTerminal
    /// </summary>
    public class TestJJIntegration
    {
        public static async Task Main(string[] args)
        {
            Console.WriteLine("JJ Core Integration Test");
            Console.WriteLine("=======================");
            Console.WriteLine();
            
            // Test JJ Core integration
            await TestJJCoreIntegration();
            
            Console.WriteLine();
            Console.WriteLine("Test completed. Press any key to exit...");
            Console.ReadKey();
        }
        
        /// <summary>
        /// Test JJ Core integration functionality
        /// </summary>
        private static async Task TestJJCoreIntegration()
        {
            Console.WriteLine("Testing JJ Core Integration...");
            
            try
            {
                // Create JJ Core integration
                var jjIntegration = new JJCoreIntegration();
                
                // Initialize integration
                bool initialized = await jjIntegration.InitializeIntegration();
                
                if (initialized)
                {
                    Console.WriteLine("✓ JJ Core integration initialized successfully");
                    
                    // Test command processing
                    await TestCommandProcessing(jjIntegration);
                    
                    // Show status
                    Console.WriteLine("Integration Status:");
                    Console.WriteLine(jjIntegration.GetIntegrationStatus());
                }
                else
                {
                    Console.WriteLine("✗ Failed to initialize JJ Core integration");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"✗ Error testing JJ Core integration: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Test command processing through JJ Core
        /// </summary>
        private static async Task TestCommandProcessing(JJCoreIntegration integration)
        {
            Console.WriteLine();
            Console.WriteLine("Testing command processing...");
            
            string[] testCommands = {
                "Create a new star in the Andromeda galaxy",
                "Communicate with my future self tomorrow",
                "Scan the universe for signs of intelligent life",
                "Move Earth to a safer orbit"
            };
            
            foreach (string command in testCommands)
            {
                Console.WriteLine($"  Processing: \"{command}\"");
                await integration.ProcessCommandThroughJJCore(command);
                await Task.Delay(500); // Brief delay between commands
            }
            
            Console.WriteLine("✓ Command processing tests completed");
        }
    }
}