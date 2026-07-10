import sys
import os
from Hardware_Acceleration_Service import HardwareAccelerationService

class HardwareTargetTerminal:
    def __init__(self):
        self.service = HardwareAccelerationService()
        self.current_target = "CPU"
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print terminal header"""
        print("=" * 60)
        print("   HARDWARE TARGET SELECTION TERMINAL")
        print("   CPU/GPU Configuration with Windows DLL Setup")
        print("=" * 60)
        print()
    
    def show_hardware_info(self):
        """Show detected hardware information"""
        print("[HARDWARE DETECTION]")
        hardware = self.service.detect_hardware()
        
        for i, hw in enumerate(hardware):
            print(f"  {i+1}. {hw['type']}: {hw['model']}")
            if hw['type'] == "CPU":
                print(f"      Cores: {hw['cores']}")
                print(f"      Architecture: {hw['arch']}")
                print(f"      Acceleration: {hw['acceleration']}")
            elif hw['type'] == "GPU":
                print(f"      Memory: {hw['memory']} GB")
                print(f"      Compute Units: {hw['compute_units']}")
                print(f"      Acceleration: {hw['acceleration']}")
        print()
    
    def show_current_configuration(self):
        """Show current hardware configuration"""
        status = self.service.get_service_status()
        print("[CURRENT CONFIGURATION]")
        print(f"  Target: {self.current_target}")
        print(f"  CPU: {'ENABLED' if status['cpu_enabled'] else 'DISABLED'}")
        print(f"  GPU: {'ENABLED' if status['gpu_enabled'] else 'DISABLED'}")
        print(f"  Acceleration Level: {status['acceleration_level']}")
        print(f"  DLL Libraries: {'LOADED' if status['dll_loaded'] else 'NOT LOADED'}")
        print()
    
    def show_menu(self):
        """Show terminal menu"""
        print("Available Commands:")
        print("  detect - Redetect hardware")
        print("  cpu - Target CPU only")
        print("  gpu - Target GPU only (if available)")
        print("  hybrid - Target both CPU and GPU")
        print("  configure - Configure Windows DLL settings")
        print("  test - Run acceleration benchmark")
        print("  status - Show current configuration")
        print("  help - Show this help")
        print("  exit - Exit terminal")
        print()
    
    def process_command(self, command):
        """Process terminal command"""
        command = command.strip().lower()
        
        if command == "detect":
            self.show_hardware_info()
        elif command == "cpu":
            self.service.configure_hardware_target("CPU")
            self.current_target = "CPU"
            print("[TARGET] CPU targeting enabled")
            print()
        elif command == "gpu":
            if self.service.gpu_enabled:
                self.service.configure_hardware_target("GPU")
                self.current_target = "GPU"
                print("[TARGET] GPU targeting enabled")
            else:
                print("[TARGET] GPU not available, cannot target GPU")
            print()
        elif command == "hybrid":
            self.service.configure_hardware_target("HYBRID")
            self.current_target = "HYBRID"
            print("[TARGET] Hybrid CPU/GPU targeting enabled")
            print()
        elif command == "configure":
            self.service.set_windows_dll_configuration()
            print("[CONFIG] Windows DLL configuration updated")
            print()
        elif command == "test":
            self.service.run_acceleration_test()
            print()
        elif command == "status":
            self.show_current_configuration()
        elif command == "help":
            self.show_menu()
        elif command == "exit":
            print("[TERMINAL] Exiting hardware target terminal...")
            return False
        else:
            print(f"[ERROR] Unknown command: {command}")
            print("Type 'help' for available commands")
            print()
        
        return True
    
    def run_terminal(self):
        """Run the hardware target terminal"""
        self.clear_screen()
        self.print_header()
        
        # Initialize service
        print("Initializing hardware acceleration service...")
        self.service.initialize_acceleration_service()
        print()
        
        # Show initial hardware info
        self.show_hardware_info()
        self.show_current_configuration()
        self.show_menu()
        
        # Main terminal loop
        running = True
        while running:
            try:
                user_input = input("[HW TERMINAL] ").strip()
                if user_input:
                    running = self.process_command(user_input)
            except KeyboardInterrupt:
                print("\n[TERMINAL] Interrupted by user")
                break
            except EOFError:
                break

def main():
    terminal = HardwareTargetTerminal()
    terminal.run_terminal()

if __name__ == "__main__":
    main()