using System;
using System.ServiceProcess;
using System.Threading;
using System.Threading.Tasks;
using System.IO;
using System.Diagnostics;
using System.Numerics;
using System.Management;

namespace QuantumEnergyService
{
    /// <summary>
    /// Integrated Energy Cooling Service - Manages the particle accelerator-based energy cooling system
    /// that separates positive and negative energy particles at the millimeter level
    /// </summary>
    public partial class IntegratedEnergyCoolingService : ServiceBase
    {
        private CancellationTokenSource _cancellationTokenSource;
        private Task _coolingTask;
        private HardwareCommunicationModule _hardwareComm;
        private readonly string _logFile = "c:\\QuantumEnergyService\\energy_cooling_service.log";
        private readonly Random _random = new Random();
        
        // Energy particle properties
        private double _positiveEnergyLevel = 0;
        private double _negativeEnergyLevel = 0;
        private double _separationDistance = 0; // Millimeters
        private bool _systemActive = false;
        
        // Ghost particle field properties
        private double _yinYangBalance = 0.5; // 0.0 = pure Yin, 1.0 = pure Yang
        private double _ghostParticleDensity = 0;
        private int _reactionRate = 0;
        
        public IntegratedEnergyCoolingService()
        {
            ServiceName = "IntegratedEnergyCoolingService";
            CanPauseAndContinue = true;
            CanShutdown = true;
            CanStop = true;
        }

        protected override void OnStart(string[] args)
        {
            try
            {
                LogMessage("Integrated Energy Cooling Service starting...");
                
                // Initialize hardware communication module
                _hardwareComm = new HardwareCommunicationModule();
                
                _cancellationTokenSource = new CancellationTokenSource();
                _systemActive = true;
                
                // Start the cooling process
                _coolingTask = Task.Run(async () => 
                {
                    while (!_cancellationTokenSource.Token.IsCancellationRequested)
                    {
                        // Manage energy particle separation
                        ManageEnergyParticleSeparation();
                        
                        // Control ghost particle field
                        ControlGhostParticleField();
                        
                        // Optimize system performance
                        OptimizeCoolingPerformance();
                        
                        // Communicate with hardware devices
                        await CommunicateWithHardware();
                        
                        // Log system status periodically
                        LogSystemStatus();
                        
                        // Wait before next cycle (100ms for high-frequency operation)
                        await Task.Delay(100, _cancellationTokenSource.Token);
                    }
                });
                
                LogMessage("Integrated Energy Cooling Service started successfully");
            }
            catch (Exception ex)
            {
                LogMessage("Error starting Integrated Energy Cooling Service: " + ex.Message);
                throw;
            }
        }

        protected override void OnStop()
        {
            try
            {
                LogMessage("Integrated Energy Cooling Service stopping...");
                
                _systemActive = false;
                _cancellationTokenSource.Cancel();
                
                // Wait for task completion
                if (_coolingTask != null && !_coolingTask.IsCompleted)
                {
                    _coolingTask.Wait(5000); // Wait up to 5 seconds
                }
                
                // Dispose hardware communication module
                _hardwareComm?.Dispose();
                
                LogMessage("Integrated Energy Cooling Service stopped successfully");
            }
            catch (Exception ex)
            {
                LogMessage("Error stopping Integrated Energy Cooling Service: " + ex.Message);
            }
        }

        /// <summary>
        /// Manages the separation of positive and negative energy particles
        /// </summary>
        private void ManageEnergyParticleSeparation()
        {
            // Simulate energy intake from environment
            double energyIntake = _random.NextDouble() * 100;
            
            // Separate positive and negative energy components
            _positiveEnergyLevel = energyIntake * _yinYangBalance;
            _negativeEnergyLevel = energyIntake * (1 - _yinYangBalance);
            
            // Maintain separation at millimeter level (0.1 - 1.0 mm)
            _separationDistance = 0.1 + (_random.NextDouble() * 0.9);
            
            // Accelerate protons and electrons in 3D dimensional axis planes
            // This creates a more complex motion pattern than conventional 2D systems
            Vector3 protonAcceleration = new Vector3(
                (float)(_random.NextDouble() * 2 - 1),
                (float)(_random.NextDouble() * 2 - 1),
                (float)(_random.NextDouble() * 2 - 1)
            );
            
            Vector3 electronAcceleration = new Vector3(
                (float)(_random.NextDouble() * -2 + 1),
                (float)(_random.NextDouble() * -2 + 1),
                (float)(_random.NextDouble() * -2 + 1)
            );
            
            // Constantly missing protons and electrons creates acceleration effect
            // This is simulated by varying the energy levels
            _positiveEnergyLevel += protonAcceleration.Length() * 10;
            _negativeEnergyLevel += Math.Abs(electronAcceleration.Length() * 10);
        }

        /// <summary>
        /// Controls the ghost particle field that enables constant reaction
        /// </summary>
        private void ControlGhostParticleField()
        {
            // Combine chaos energy (dark matter) and light matter into Yin and Yang divisions
            double chaosEnergy = _random.NextDouble() * 50;
            double lightEnergy = _random.NextDouble() * 50;
            
            // Create Yin-Yang balance (0.0 = pure Yin/dark, 1.0 = pure Yang/light)
            _yinYangBalance = chaosEnergy / (chaosEnergy + lightEnergy + 0.001); // +0.001 to prevent division by zero
            
            // Generate ghost particle field density
            _ghostParticleDensity = (_positiveEnergyLevel + _negativeEnergyLevel) * 0.1;
            
            // Reaction rate depends on energy levels and separation efficiency
            _reactionRate = (int)((_positiveEnergyLevel + _negativeEnergyLevel) / _separationDistance);
        }

        /// <summary>
        /// Optimizes cooling performance for Windows system and hardware communication
        /// </summary>
        private void OptimizeCoolingPerformance()
        {
            // Get actual hardware metrics instead of random values
            var metrics = _hardwareComm.GetHardwareMetrics();
            
            // Calculate system load based on actual hardware utilization
            double systemLoad = (metrics.CpuUtilization + metrics.GpuUtilization) / 200.0;
            
            // Modify energy levels based on actual system requirements
            if (systemLoad > 0.8)
            {
                // High load - increase cooling
                _positiveEnergyLevel *= 1.1;
                _negativeEnergyLevel *= 1.1;
            }
            else if (systemLoad < 0.3)
            {
                // Low load - reduce cooling
                _positiveEnergyLevel *= 0.9;
                _negativeEnergyLevel *= 0.9;
            }
            
            // Maintain optimal separation distance for best performance
            if (_separationDistance < 0.3 || _separationDistance > 0.8)
            {
                // Adjust to optimal range
                _separationDistance = 0.5;
            }
        }

        /// <summary>
        /// Communicates with hardware devices for energy management
        /// </summary>
        private async Task CommunicateWithHardware()
        {
            // Communicate with hardware devices every 5 seconds (50 cycles * 100ms = 5,000ms)
            static int cycleCount = 0;
            if (++cycleCount % 50 == 0)
            {
                bool success = await _hardwareComm.CommunicateWithHardwareDevices();
                if (success)
                {
                    LogMessage("Successfully communicated with hardware devices");
                }
                else
                {
                    LogMessage("Failed to communicate with hardware devices");
                }
            }
        }
        
        /// <summary>
        /// Logs the current system status
        /// </summary>
        private void LogSystemStatus()
        {
            // Log detailed status every 10 seconds (100 cycles * 100ms = 10,000ms)
            static int cycleCount = 0;
            if (++cycleCount % 100 == 0)
            {
                string status = $"Energy Cooling Status - Positive: {_positiveEnergyLevel:F2}W, " +
                               $"Negative: {_negativeEnergyLevel:F2}W, " +
                               $"Separation: {_separationDistance:F2}mm, " +
                               $"YinYang Balance: {_yinYangBalance:F2}, " +
                               $"Ghost Density: {_ghostParticleDensity:F2}, " +
                               $"Reaction Rate: {_reactionRate}";
                
                LogMessage(status);
            }
        }

        /// <summary>
        /// Gets the current service status
        /// </summary>
        public string GetServiceStatus()
        {
            string hardwareInfo = "";
            try
            {
                var metrics = _hardwareComm.GetHardwareMetrics();
                hardwareInfo = $"- CPU Utilization: {metrics.CpuUtilization:F1}%\n" +
                              $"- GPU Utilization: {metrics.GpuUtilization:F1}%\n" +
                              $"- Memory Utilization: {metrics.MemoryUtilization:F1}%\n" +
                              $"- Disk Utilization: {metrics.DiskUtilization:F1}%\n";
            }
            catch
            {
                hardwareInfo = "- Hardware Info: Not available\n";
            }
            
            return $"Integrated Energy Cooling Service Status:\n" +
                   $"- System Active: {_systemActive}\n" +
                   $"- Positive Energy: {_positiveEnergyLevel:F2}W\n" +
                   $"- Negative Energy: {_negativeEnergyLevel:F2}W\n" +
                   $"- Separation Distance: {_separationDistance:F2}mm\n" +
                   $"- Yin-Yang Balance: {_yinYangBalance:F2}\n" +
                   $"- Ghost Particle Density: {_ghostParticleDensity:F2}\n" +
                   $"- Reaction Rate: {_reactionRate}\n" +
                   hardwareInfo +
                   $"- Service State: {this.Status}";
        }

        /// <summary>
        /// Logs a message to the service log file
        /// </summary>
        private void LogMessage(string message)
        {
            try
            {
                string logEntry = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " - " + message + Environment.NewLine;
                File.AppendAllText(_logFile, logEntry);
            }
            catch
            {
                // Ignore logging errors
            }
        }
    }
}