using System;
using System.ServiceProcess;
using System.Threading;
using System.Threading.Tasks;
using System.IO;

namespace QuantumEnergyService
{
    /// <summary>
    /// Windows Service wrapper for Cosmic Qubit Management
    /// </summary>
    public partial class CosmicQubitWindowsService : ServiceBase
    {
        private CosmicQubitManagementService _cosmicService;
        private CancellationTokenSource _cancellationTokenSource;
        private Task _serviceTask;
        
        public CosmicQubitWindowsService()
        {
            InitializeComponent();
            _cosmicService = new CosmicQubitManagementService();
        }
        
        protected override void OnStart(string[] args)
        {
            try
            {
                // Log service start
                LogMessage("Cosmic Qubit Windows Service starting...");
                
                // Start the cosmic qubit management service
                _cancellationTokenSource = new CancellationTokenSource();
                _cosmicService.LoadQubitState();
                _cosmicService.StartService();
                
                // Run service monitoring in background
                _serviceTask = Task.Run(async () => 
                {
                    while (!_cancellationTokenSource.Token.IsCancellationRequested)
                    {
                        // Keep service alive
                        await Task.Delay(60000, _cancellationTokenSource.Token); // Check every minute
                        
                        // Log status periodically
                        LogMessage("Cosmic Qubit Service running - " + DateTime.Now.ToString());
                    }
                });
                
                LogMessage("Cosmic Qubit Windows Service started successfully");
            }
            catch (Exception ex)
            {
                LogMessage("Error starting Cosmic Qubit Windows Service: " + ex.Message);
                throw;
            }
        }
        
        protected override void OnStop()
        {
            try
            {
                LogMessage("Cosmic Qubit Windows Service stopping...");
                
                // Cancel service task
                _cancellationTokenSource.Cancel();
                
                // Stop the cosmic service
                _cosmicService.StopService();
                
                // Wait for task completion
                if (_serviceTask != null && !_serviceTask.IsCompleted)
                {
                    _serviceTask.Wait(5000); // Wait up to 5 seconds
                }
                
                LogMessage("Cosmic Qubit Windows Service stopped successfully");
            }
            catch (Exception ex)
            {
                LogMessage("Error stopping Cosmic Qubit Windows Service: " + ex.Message);
            }
        }
        
        private void LogMessage(string message)
        {
            try
            {
                string logFile = "c:\\QuantumEnergyService\\cosmic_service.log";
                string logEntry = DateTime.Now.ToString() + " - " + message + Environment.NewLine;
                File.AppendAllText(logFile, logEntry);
            }
            catch
            {
                // Ignore logging errors
            }
        }
    }
}