using System.ComponentModel;
using System.Configuration.Install;
using System.ServiceProcess;

namespace QuantumEnergyService
{
    [RunInstaller(true)]
    public partial class ArmorBiosOptimizationServiceInstaller : Installer
    {
        private ServiceProcessInstaller serviceProcessInstaller;
        private ServiceInstaller serviceInstaller;

        public ArmorBiosOptimizationServiceInstaller()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.serviceProcessInstaller = new ServiceProcessInstaller();
            this.serviceInstaller = new ServiceInstaller();

            // 
            // serviceProcessInstaller
            // 
            this.serviceProcessInstaller.Account = ServiceAccount.LocalSystem;
            this.serviceProcessInstaller.Password = null;
            this.serviceProcessInstaller.Username = null;

            // 
            // serviceInstaller
            // 
            this.serviceInstaller.ServiceName = "ArmorBiosOptimizationService";
            this.serviceInstaller.DisplayName = "Armor BIOS Optimization Service";
            this.serviceInstaller.Description = "Connects armor layout with motherboard BIOS for unified optimization with self-adaptive core and smart fan control";
            this.serviceInstaller.StartType = ServiceStartMode.Automatic;

            // 
            // ProjectInstaller
            // 
            this.Installers.AddRange(new Installer[] {
                this.serviceProcessInstaller,
                this.serviceInstaller});
        }
    }
}