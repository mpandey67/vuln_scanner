import platform

import subprocess

def what_system():
    # This function is to determine whether this is windows or linux system 
    current_machine=platform.system()
    return current_machine

class windows:
    def windows_softs(self):
        import winreg # dont import this at start as winreg is not available for linux and hence it will throw error on linux device.
        # Function to fetch installed software for windows
        software_list = []
        registry_paths = [
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
            r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        
        for hive in hives:
            for path in registry_paths:
                try:
                    reg = winreg.ConnectRegistry(None, hive)
                    key = winreg.OpenKey(reg, path)
                    
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                                display_version = winreg.QueryValueEx(subkey, 'DisplayVersion')[0]
                                software_list.append((display_name, display_version))
                            except FileNotFoundError:
                                pass
                            finally:
                                subkey.Close()
                            i += 1
                        except OSError:
                            break
                except FileNotFoundError:
                    continue
                finally:
                    key.Close()
                    
        cmd = 'powershell "Get-AppxPackage | Select Name, Version"'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, shell=True)
        lines = result.stdout.strip().split('\n')[2:]  # Skip header lines
        software_list1 = []
        for line in lines:
            parts = line.split()
            name = parts[0]
            version = parts[1]
            software_list1.append((name, version))
        return software_list+software_list1

    

class linux:
    # CLass for linux packages
    def __init__(self) -> None:
        self.linux_software_list=[]
    def linux_pack(self):
        # main func in class linux to call from orifinal main function
        def get_installed_software():
            # This func checks for installed distros on which currnt ttarget is running and based on this respective function is called  
            distro = platform.system()
            if distro == 'Linux':
                distro_name, distro_version, _ = platform.linux_distribution(full_distribution_name=False)
                
                if distro_name.lower() in ['ubuntu', 'debian']:
                    return get_installed_software_apt()
                elif distro_name.lower() in ['centos', 'fedora', 'redhat']:
                    return get_installed_software_rpm()
                elif distro_name.lower() in ['arch', 'manjaro']:
                    return get_installed_software_pacman()
                else:
                    raise ValueError(f"Unsupported Linux distribution: {distro_name}")
            else:
                raise ValueError(f"Unsupported operating system: {distro}")

        def get_installed_software_apt():
            result = subprocess.run(['dpkg-query', '-W', '-f=${Package} ${Version} ${Architecture}\n'], stdout=subprocess.PIPE, text=True)
            packages = result.stdout.strip().split('\n')
            software_list = [tuple(package.split()) for package in packages]
            return software_list

        def get_installed_software_rpm():
            result = subprocess.run(['rpm', '-qa', '--qf', '%{NAME} %{VERSION}-%{RELEASE} %{ARCH}\n'], stdout=subprocess.PIPE, text=True)
            packages = result.stdout.strip().split('\n')
            software_list = [tuple(package.split(' ', 1)) for package in packages]
            return software_list

        def get_installed_software_pacman():
            result = subprocess.run(['pacman', '-Q'], stdout=subprocess.PIPE, text=True)
            packages = result.stdout.strip().split('\n')
            software_list = [tuple(package.split()) for package in packages]
            return software_list


        try:
            software_list = get_installed_software()
            for software in software_list:
                self.linux_software_list.append((software[0],software[1],software[2]))
        except ValueError as e:
            print(e)
        return self.linux_software_list
        
    
    


current_machine=what_system()
if current_machine.lower()=='windows':
    windows_object=windows()
    windows_software_list=windows_object.windows_softs()
    print(windows_software_list)
if current_machine.lower()=='linux':
    linux_object=linux()
    linux_software_list=linux_object.linux_pack()
    print(linux_software_list)

flag=0
for find in windows_software_list:
    if 'vlc' in find[0].lower() or find=='mozilla':
        flag=1

if flag==1:
    print("found")
else:
    print("not_found")

