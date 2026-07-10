using System;
using System.ServiceProcess;

namespace QuantumEnergyService
{
    static class QubitServiceProgram
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        static void Main()
        {
            ServiceBase[] ServicesToRun;
            ServicesToRun = new ServiceBase[] 
            { 
                new QubitWindowsService() 
            };
            ServiceBase.Run(ServicesToRun);
        }
    }
}