using System.ComponentModel;
using System.Configuration.Install;
using System.ServiceProcess;

namespace QuantumEnergyService
{
    [RunInstaller(true)]
    public partial class InvisibleBiosGatewayServiceInstaller : Installer
    {
        private ServiceProcessInstaller serviceProcessInstaller;
        private ServiceInstaller serviceInstaller;

        public InvisibleBiosGatewayServiceInstaller()
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
            this.serviceInstaller.ServiceName = "InvisibleBiosGatewayService";
            this.serviceInstaller.DisplayName = "Invisible BIOS Gateway Service";
            this.serviceInstaller.Description = "Automatically establishes a background gateway between BIOS full control and automated adjusters without user intervention";
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