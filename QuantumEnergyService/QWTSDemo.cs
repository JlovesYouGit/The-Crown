using System;

namespace QuantumEnergyService
{
    /// <summary>
    /// Demonstrates the QWTS (Quantized Wave Transmission States) conversion algorithm
    /// </summary>
    public class QWTSDemo
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("Quantum Energy Management - QWTS Conversion Demo");
            Console.WriteLine("===============================================");
            Console.WriteLine();
            
            // Test various energy inputs
            DemonstrateConversion(0.0f, 0.0f);  // Idle system
            DemonstrateConversion(25.0f, 10.0f); // Light usage
            DemonstrateConversion(75.0f, 50.0f); // Medium usage
            DemonstrateConversion(100.0f, 100.0f); // Maximum usage
            
            Console.WriteLine();
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
        
        private static void DemonstrateConversion(float cpuUtilization, float gpuUtilization)
        {
            // Calculate total system energy consumption (simplified model)
            double totalEnergy = (cpuUtilization / 100.0) + (gpuUtilization / 100.0);
            
            // Convert to Quantized Wave Transmission States (QWTS)
            // Each watt is converted to QWTS with electron splitting (3 pieces X-axis, 3 layers Y-axis)
            int electronSplitFactor = 3 * 3; // 9 splits per watt
            
            // Calculate QWTS with speed factor (2/3 speed of light)
            double qwtsValue = totalEnergy * electronSplitFactor * (2.0 / 3.0);
            
            // Energy duplication factor for lower QWT shapes
            double duplicationFactor = 1.5; // Each QWT replicates into 1.5 additional units
            
            double replicatedQWTS = qwtsValue * duplicationFactor;
            
            Console.WriteLine($"Input: CPU {cpuUtilization:F1}% + GPU {gpuUtilization:F1}% = {totalEnergy:F2}W");
            Console.WriteLine($"QWTS Value: {qwtsValue:F2}");
            Console.WriteLine($"Replicated QWTS: {replicatedQWTS:F2}");
            Console.WriteLine($"Energy Preservation Ratio: {replicatedQWTS / totalEnergy:F2}x");
            Console.WriteLine();
        }
    }
}