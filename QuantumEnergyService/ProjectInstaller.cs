using System.ComponentModel;
using System.Configuration;
using System.ServiceProcess;
using System.Configuration.Install;

namespace QuantumEnergyService
{
    [RunInstaller(true)]
    public partial class ProjectInstaller : System.Configuration.Install.Installer
    {
        private ServiceProcessInstaller serviceProcessInstaller;
        private ServiceInstaller serviceInstaller;

        public ProjectInstaller()
        {
            serviceProcessInstaller = new ServiceProcessInstaller();
            serviceInstaller = new ServiceInstaller();

            // Service will run under the Local System account
            serviceProcessInstaller.Account = ServiceAccount.LocalSystem;
            serviceProcessInstaller.Username = null;
            serviceProcessInstaller.Password = null;

            // Service information
            serviceInstaller.ServiceName = "QuantumEnergyService";
            serviceInstaller.DisplayName = "Quantum Energy Management Service";
            serviceInstaller.Description = "Manages CPU/GPU energy consumption using quantized wave transmission states (QWTS)";
            serviceInstaller.StartType = ServiceStartMode.Automatic;

            Installers.Add(serviceProcessInstaller);
            Installers.Add(serviceInstaller);
        }
    }
}