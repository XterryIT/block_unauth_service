import psutil
import time



def get_services():
    """
    Сканирует систему и ВОЗВРАЩАЕТ словарь {порт: {имя, pid}}.
    """
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


def print_services():
    service_dict = get_services()

    print("-" * 55)
    print(f"{'PORT':<10} {'RUNNING PROCESS':<25} {'PID':<10}")
    print("*" * 55)

    for port, service_info in service_dict.items():
        process_name = service_info['name']
        pid = service_info['pid'] if service_info['pid'] is not None else 'N/A'
        print(f"{port:<10} {process_name:<25} {pid:<10}")
    print("#"*55)


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

                    p = psutil.Process(pid_to_kill)

                    print(f"Terminating process: {pid_to_kill} ({process_name})")
                    
                    p.kill()

                    time.sleep(10)

                    print_services()

                elif temp.lower() == 'no':
                    print(f"  -> Adding procces to table {pid_to_kill} ({process_name}).")

                    base_services = current_services

                    print_services()
        
        
        
        

if __name__ == "__main__":
    main()
