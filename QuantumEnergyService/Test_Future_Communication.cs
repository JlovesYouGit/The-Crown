using System;
using System.Threading.Tasks;

namespace QuantumEnergyService
{
    /// <summary>
    /// Test program to demonstrate future communication capabilities
    /// </summary>
    public class TestFutureCommunication
    {
        public static async Task Main(string[] args)
        {
            Console.WriteLine("=====================================");
            Console.WriteLine("    FUTURE COMMUNICATION TEST");
            Console.WriteLine("=====================================");
            Console.WriteLine();
            
            // Create future self communicator
            var communicator = new FutureSelfCommunicator("TestUser");
            
            // Test sending message to future self
            Console.WriteLine("TEST 1: Sending message to future self (2 years from now)");
            Console.WriteLine("--------------------------------------------------------");
            await communicator.SendMessageToFutureSelf(
                "Hello future me! I hope you've made great progress on the quantum integration project. " +
                "Remember to keep exploring new possibilities and don't forget to enjoy the journey!", 
                2);
            
            Console.WriteLine();
            
            // Test checking for messages from future self
            Console.WriteLine("TEST 2: Checking for messages from future self");
            Console.WriteLine("---------------------------------------------");
            await communicator.CheckForMessagesFromFuture();
            
            Console.WriteLine();
            
            // Test setting up reminders
            Console.WriteLine("TEST 3: Setting up future communication reminders");
            Console.WriteLine("------------------------------------------------");
            communicator.SetupFutureCommunicationReminders(2);
            
            Console.WriteLine();
            Console.WriteLine("=====================================");
            Console.WriteLine("    TEST COMPLETE");
            Console.WriteLine("=====================================");
            Console.WriteLine();
            Console.WriteLine("The Future Self Communicator is ready for use!");
            Console.WriteLine("Run FutureSelfCommunicator.exe to use the full interactive system.");
            Console.WriteLine();
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}