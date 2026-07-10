using System.ComponentModel;
using System.Configuration.Install;
using System.ServiceProcess;

namespace QuantumEnergyService
{
    [RunInstaller(true)]
    public partial class CosmicQubitServiceInstaller : Installer
    {
        private ServiceProcessInstaller serviceProcessInstaller;
        private ServiceInstaller serviceInstaller;

        public CosmicQubitServiceInstaller()
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
            this.serviceInstaller.ServiceName = "CosmicQubitWindowsService";
            this.serviceInstaller.DisplayName = "Cosmic Qubit Management Service";
            this.serviceInstaller.Description = "Manages qubits in superposition with temperature control, white hole warping, and universe mapping";
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