using System.ComponentModel;
using System.Configuration.Install;
using System.ServiceProcess;

namespace QuantumEnergyService
{
    [RunInstaller(true)]
    public partial class IntegratedEnergyCoolingServiceInstaller : Installer
    {
        private ServiceProcessInstaller serviceProcessInstaller;
        private ServiceInstaller serviceInstaller;

        public IntegratedEnergyCoolingServiceInstaller()
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
            this.serviceInstaller.ServiceName = "IntegratedEnergyCoolingService";
            this.serviceInstaller.DisplayName = "Integrated Energy Cooling Service";
            this.serviceInstaller.Description = "Manages the particle accelerator-based energy cooling system that separates positive and negative energy particles at the millimeter level, creating a ghost particle field for constant reaction";
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