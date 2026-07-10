using System;
using System.ServiceProcess;
using System.Threading;
using System.IO;
using System.Timers;

namespace QuantumEnergyService
{
    public partial class QubitWindowsService : ServiceBase
    {
        private Thread _workerThread;
        private bool _isRunning;
        private string _logFile = "c:\\QuantumEnergyService\\qubit_service.log";
        private System.Timers.Timer _timer;
        private int _snapshotCount = 0;
        
        public QubitWindowsService()
        {
            InitializeComponent();
        }
        
        protected override void OnStart(string[] args)
        {
            try
            {
                LogMessage("Qubit Windows Service starting...");
                _isRunning = true;
                
                // Start timer for periodic tasks
                _timer = new System.Timers.Timer(10000); // 10 seconds
                _timer.Elapsed += TimerElapsed;
                _timer.Start();
                
                LogMessage("Qubit Windows Service started successfully");
            }
            catch (Exception ex)
            {
                LogMessage("Error starting service: " + ex.Message);
            }
        }
        
        protected override void OnStop()
        {
            try
            {
                LogMessage("Qubit Windows Service stopping...");
                _isRunning = false;
                
                // Stop timer
                if (_timer != null)
                {
                    _timer.Stop();
                    _timer.Dispose();
                }
                
                LogMessage("Qubit Windows Service stopped successfully");
            }
            catch (Exception ex)
            {
                LogMessage("Error stopping service: " + ex.Message);
            }
        }
        
        private void TimerElapsed(object sender, ElapsedEventArgs e)
        {
            try
            {
                _snapshotCount++;
                LogMessage("Taking qubit snapshot #" + _snapshotCount);
                GenerateQubitData();
            }
            catch (Exception ex)
            {
                LogMessage("Error in timer elapsed: " + ex.Message);
            }
        }
        
        private void GenerateQubitData()
        {
            try
            {
                // Generate sample qubit data
                string[] qubitData = {
                    "Qubit-001: Position(100,200,300) Energy: 5000K",
                    "Qubit-002: Position(400,500,600) Energy: 7500K",
                    "Qubit-003: Position(700,800,900) Energy: 10000K",
                    "Qubit-004: Position(150,250,350) Energy: 6200K",
                    "Qubit-005: Position(450,550,650) Energy: 8100K"
                };
                
                // Write data to file
                using (StreamWriter writer = new StreamWriter("c:\\QuantumEnergyService\\qubit_data.txt"))
                {
                    writer.WriteLine("Snapshot Count: " + _snapshotCount);
                    foreach (string data in qubitData)
                    {
                        writer.WriteLine(data);
                    }
                    writer.WriteLine("Last Updated: " + DateTime.Now.ToString());
                }
                
                LogMessage("Qubit data generated and saved");
            }
            catch (Exception ex)
            {
                LogMessage("Error generating qubit data: " + ex.Message);
            }
        }
        
        private void LogMessage(string message)
        {
            try
            {
                string logEntry = DateTime.Now.ToString() + " - " + message + Environment.NewLine;
                File.AppendAllText(_logFile, logEntry);
            }
            catch
            {
                // Ignore logging errors
            }
        }
        
        private void InitializeComponent()
        {
            this.ServiceName = "QubitWindowsService";
        }
    }
}