using System;
using System.ServiceProcess;
using System.Threading;

namespace QuantumEnergyService
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        static void Main(string[] args)
        {
            // Check if running as a service
            if (Environment.UserInteractive)
            {
                // Running as console application
                RunAsConsole();
            }
            else
            {
                // Running as Windows service
                ServiceBase[] ServicesToRun;
                ServicesToRun = new ServiceBase[]
                {
                    new CosmicQubitWindowsService(),
                    new IntegratedEnergyCoolingService(),
                    new ArmorBiosOptimizationService(),
                    new InvisibleBiosGatewayService()
                };
                ServiceBase.Run(ServicesToRun);
            }
        }
        
        static void RunAsConsole()
        {
            Console.WriteLine("Quantum Energy Service (Console Mode)");
            Console.WriteLine("===================================");
            
            // Create and initialize the cosmic qubit service
            var cosmicService = new CosmicQubitManagementService();
            cosmicService.LoadQubitState();
            
            // Display cosmic service status
            Console.WriteLine(cosmicService.GetServiceStatus());
            Console.WriteLine();
            
            // Create and start the integrated energy cooling service
            var coolingService = new IntegratedEnergyCoolingService();
            
            // Display cooling service status
            Console.WriteLine(coolingService.GetServiceStatus());
            Console.WriteLine();
            
            // Create and start the armor BIOS optimization service
            var armorService = new ArmorBiosOptimizationService();
            
            // Display armor service status
            Console.WriteLine(armorService.GetServiceStatus());
            Console.WriteLine();
            
            // Create and start the invisible BIOS gateway service
            var invisibleGatewayService = new InvisibleBiosGatewayService();
            
            // Display invisible gateway service status
            Console.WriteLine(invisibleGatewayService.GetServiceStatus());
            Console.WriteLine();
            
            // Start the services
            cosmicService.StartService();
            
            Console.WriteLine("Services are now running.");
            Console.WriteLine("Press any key to stop...");
            Console.ReadKey();
            
            // Stop the services
            cosmicService.StopService();
            
            Console.WriteLine("\nService shutdown complete.");
        }
    }
}