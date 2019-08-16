// Application written by Noah Jorgensen
// Powershell scripts written by Noah Jorgensen and Jon Ramirez
//-----------------------------------------------------------------
// To be used on Windows 10, 64-bit versions only
// Written for the University of New Haven
// Fall 2019

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using Microsoft.Win32;
using System.Security.Principal;


namespace WifiFix
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            bool systemArch = Environment.Is64BitOperatingSystem;
            if (systemArch == false) //false = 32 bit
            {
                //the system is not 64 bit!
                MessageBox.Show("You cannot run this tool on this computer because the computer is a 32-bit architecture.\n\n" +
                    "If you need further assistance, bring the computer into the University Student Support Desk located " +
                    "in the back of the book store.", 
                    "32-Bit System");
                System.Environment.Exit(1);
            }

            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            bool adminWindow = principal.IsInRole(WindowsBuiltInRole.Administrator);
            if (adminWindow == false) //false = not as admin
            {
                //you did not run as admin
                MessageBox.Show("This tool must be run as administrator.\n" +
                    "You can run it as administrator by right clicking the icon, and selecting the 'Run as administrator' option.",
                    "Administrative Privileges Required");
                System.Environment.Exit(1);
            }

            //If all checks pass, begin the program
            InitializeComponent();
        }

        //Forget university SSID's
        private void DisconnectClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "netsh wlan delete profile name='ChargerWifi';" +
                    "netsh wlan delete profile name='ChargerGuest - STS';" +
                    "netsh wlan delete profile name='UNHStudent';" +
                    "netsh wlan delete profile name='UNH';" +
                    "netsh wlan delete profile name='OITBroadband';" +
                    "netsh wlan delete profile name='ChargerGuest';" +
                    "netsh wlan delete profile name='Devices';" +
                    "netsh wlan delete profile name='FH*';" +
                    "netsh wlan delete profile name='MS*'"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("University SSID's Forgotten", "Process Complete");
            }
        }

        //Turn hibernate off
        private void HibernateClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "powercfg /hibernate off"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("Hibernate Disabled", "Process Complete");
            }
        }

        //Flush DNS
        private void FlushClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "ipconfig /flushdns"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("DNS Flushed", "Process Complete");
            }
        }

        //Turn NIC Powersave mode off
        private void NICPowersaveClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "ForEach ($NIC in (Get-NetAdapter -Physical)){;" +
                    "$PowerSaving = Get-CimInstance -ClassName MSPower_DeviceEnable -Namespace root\\wmi | ? {$_.InstanceName -match [Regex]::Escape($NIC.PnPDeviceID)};" +
                    "If ($PowerSaving.Enable){ $PowerSaving.Enable = $false; $PowerSaving | Set-CimInstance } }"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("NIC Powersave Mode Disabled", "Process Complete");
            }
        }

        //Disable wan miniports
        private void WANMiniportsClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "Disable-NetAdapter -InterfaceDescription 'WAN Miniport*' -IncludeHidden -Confirm:$false"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("WAN Miniports Disabled", "Process Complete");
            }
        }

        //Turn off hotspot 2.0
        private void Hotspot2Clicked(object sender, RoutedEventArgs e)
        {

            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\WlanSvc\\AnqpCache -Name OsuRegistrationStatus -Value 0"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("Hotspot 2.0 Disabled", "Process Complete");
            }

            /*
            using (var hklm = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
            using (var key = hklm.OpenSubKey("SOFTWARE\\Microsoft\\WlanSvc\\AnqpCache", true))
            {
                if (key != null)  //must check for null key
                {
                    key.SetValue("OsuRegistrationStatus", 0);
                    MessageBox.Show("Hotspot 2.0 Disabled", "Process Complete");
                }
            }
            */
        }

        //winsock reset
        private void WinsockClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "netsh winsock reset"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("Winsock Reset", "Process Complete");
            }
        }

        //tcp/ip reset
        private void TCPIPClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "netsh int ip reset;" +
                    "netsh int tcp reset"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("TCP/IP Reset", "Process Complete");
            }
        }

        //diable randomized mac addresses
        private void RandMACClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "$WiFi = Get-NetAdapter -Name '*Wi-Fi*';" +
                    "$RegPath = 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4D36E972-E325-11CE-BFC1-08002BE10318}';" +
                    "($Key = Get-ItemProperty -Path $RegPath\\* -Name AdapterModel) 2> $Null;" +
                    "If($Key.AdapterModel -eq $WiFi.InterfaceDescription){;" +
                    "New-ItemProperty -Path $RegPath\\$($Key.PSChildName) -Name NetworkAddress -Value $($WiFi.MacAddress) -PropertyType String -Force}"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("Randomized MAC Addresses Disabled", "Process Complete");
            }
        }

        //run all fixes
        private void AllClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "netsh wlan delete profile name='ChargerWifi';" +
                    "netsh wlan delete profile name='ChargerGuest - STS';" +
                    "netsh wlan delete profile name='UNHStudent';" +
                    "netsh wlan delete profile name='UNH';" +
                    "netsh wlan delete profile name='OITBroadband';" +
                    "netsh wlan delete profile name='ChargerGuest';" +
                    "netsh wlan delete profile name='Devices';" +
                    "netsh wlan delete profile name='FH*';" +
                    "netsh wlan delete profile name='MS*'; " +
                    "powercfg /hibernate off; " +
                    "ipconfig /flushdns; " +
                    "ForEach ($NIC in (Get-NetAdapter -Physical)){;" +
                    "$PowerSaving = Get-CimInstance -ClassName MSPower_DeviceEnable -Namespace root\\wmi | ? {$_.InstanceName -match [Regex]::Escape($NIC.PnPDeviceID)};" +
                    "If ($PowerSaving.Enable){ $PowerSaving.Enable = $false; $PowerSaving | Set-CimInstance } }" +
                    "Disable-NetAdapter -InterfaceDescription 'WAN Miniport*' -IncludeHidden -Confirm:$false;" +
                    "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\WlanSvc\\AnqpCache -Name OsuRegistrationStatus -Value 0;" + 
                    "netsh winsock reset;" + 
                    "netsh int ip reset;" +
                    "netsh int tcp reset;" +
                    "$WiFi = Get-NetAdapter -Name '*Wi-Fi*';" +
                    "$RegPath = 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4D36E972-E325-11CE-BFC1-08002BE10318}';" +
                    "($Key = Get-ItemProperty -Path $RegPath\\* -Name AdapterModel) 2> $Null;" +
                    "If($Key.AdapterModel -eq $WiFi.InterfaceDescription){;" +
                    "New-ItemProperty -Path $RegPath\\$($Key.PSChildName) -Name NetworkAddress -Value $($WiFi.MacAddress) -PropertyType String -Force}"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);

                /*
                using (var hklm = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                using (var key = hklm.OpenSubKey("SOFTWARE\\Microsoft\\WlanSvc\\AnqpCache", true))
                {
                    if (key != null)  //must check for null key
                    {
                        key.SetValue("OsuRegistrationStatus", 0);
                    }
                }
                */

                MessageBox.Show("All Actions Finished\n\n" +
                    "Please restart your computer to complete the process", "Process Complete");
            }
        }

        //Turn UNH network to private (must be run last after everything finishes and restart)
        private void PrivateClicked(object sender, RoutedEventArgs e)
        {
            using (var PowerShellInstance = PowerShell.Create(InitialSessionState.CreateDefault2()))
            {
                PowerShellInstance.AddScript(
                    "$ConnectionProfile = Get-NetConnectionProfile;" +
                    "If($ConnectionProfile.Name -eq 'newhaven.local' -or 'ChargerWifi'){ Set-NetConnectionProfile -NetworkCategory Private }"
                    );
                var result = PowerShellInstance.BeginInvoke();
                while (result.IsCompleted == false) Thread.Sleep(1000);
                MessageBox.Show("UNH Network Set to Private", "Process Complete");
            }
        }
    }
}
