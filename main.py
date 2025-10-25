import psutil
import time
import subprocess



def get_services():

    services = {}
    for conn in psutil.net_connections('inet'):
        if conn.status == 'LISTEN':
            port = conn.laddr.port
            if conn.pid:
                try:
                    process = psutil.Process(conn.pid)

                    services[port] = {'name': process.name(), 'pid': conn.pid}
                except psutil.NoSuchProcess:
                    services[port] = {'name': "Process vanished", 'pid': None}
            else:

                services[port] = {'name': "Unknown (No PID)", 'pid': None}
    return services



def initialization():
    start_services = get_services()

    print(f"Monitoring has been initiated. Initially, {len(start_services)} services were identified.")
    print("-" * 55)

    print(f"{'PORT':<10} {'RUNNING PROCESS':<25} {'PID':<10}")
    print("*" * 55)

    for port, service_info in start_services.items():

        process_name = service_info['name']
        pid = service_info['pid'] if service_info['pid'] is not None else 'N/A'
        print(f"{port:<10} {process_name:<25} {pid:<10}")

    return start_services



def show_services():
    service_dict = get_services()

    print("-" * 55)
    print(f"{'PORT':<10} {'RUNNING PROCESS':<25} {'PID':<10}")
    print("*" * 55)

    for port, service_info in service_dict.items():
        process_name = service_info['name']
        pid = service_info['pid'] if service_info['pid'] is not None else 'N/A'
        print(f"{port:<10} {process_name:<25} {pid:<10}")
    print("#"*55)



def terminating_systemctl(pid_to_kill, process_name):
    service_name = None
    try:
        with open(f'/proc/{pid_to_kill}/cgroup', 'r') as f:
            for line in f:

                if '.service' in line:
                    service_name = line.split('/')[-1].strip()
                    break
                        
        if service_name:
        
            print(f"  -> This is a systemd service: {service_name}. Stopping via systemctl...")
            subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True, capture_output=True)
            print(f"  ✅ Service {service_name} STOPPED.")
        else:
            
            print(f"  -> Not a systemd service. Killing process {pid_to_kill}...")
            p = psutil.Process(pid_to_kill)
            p.terminate() # Ask nicely first
            time.sleep(0.5) # Give it a moment
            if p.is_running():
                p.kill() # Force kill
            print(f"  ✅ Process {pid_to_kill} ({process_name}) KILLED.")
    
    
    except psutil.NoSuchProcess:
        print(f"  -> Error: Procces with PID {pid_to_kill} does not exist")
    except psutil.AccessDenied:
        print(f"  -> Error: Acces denided. No enough right to stop procces {pid_to_kill}.")
    except subprocess.CalledProcessError as e:
        print(f"  -> Error: 'systemctl stop' did not work.")
        if e.stderr:
            print(f"  -> {e.stderr.decode()}")
    except FileNotFoundError:
        print(f"  -> Error: Procces {pid_to_kill} disapire before scrip caught it (procces did not find).")
    except Exception as e:
        print(f"  -> Unecspected error: {e}")



def main():
    base_services = initialization()

    while True:
        time.sleep(10)

        current_services = get_services()

        base_ports = set(base_services.keys())
        current_ports = set(current_services.keys())

        new_ports = current_ports - base_ports


        if new_ports:
            print("\n" + "#"*55)
            print(f"!!! NEW SERVICE(S) DETECTED: {len(new_ports)} !!!")
            print("#"*55)


            for port in new_ports:

                service_info = current_services[port]
                process_name = service_info['name']
                pid_to_kill = service_info['pid']

                print(f"\n[+] Port: {port}, Process: {process_name}, PID: {pid_to_kill}")

                if pid_to_kill is None:
                    print("  -> Cannot kill: PID is not available (run script with sudo).")
                    continue 

                temp = input(f"  -> Do you want to kill this process (PID: {process_name})? (yes/no): ")


                if temp.lower() == 'yes':
                    
                    terminating_systemctl(pid_to_kill, process_name)

                    time.sleep(1)

                    show_services()
                        

                elif temp.lower() == 'no':
                    print(f"  -> Adding procces to table {pid_to_kill} ({process_name}).")

                    base_services = current_services
                    
                    time.sleep(1)

                    show_services()
        
        
        
        

if __name__ == "__main__":
    main()
