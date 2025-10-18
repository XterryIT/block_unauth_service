import psutil
import time

# --- FUNKCJA GŁÓWNA SKANUJĄCA ---

def get_services():
    """
    Skanuje system i ZWRACA słownik, gdzie kluczem jest port,
    a wartością jest kolejny słownik zawierający nazwę i PID procesu.
    Format: {port: {'name': 'nazwa_procesu', 'pid': 1234}}
    """
    # Tworzy pusty słownik, który będzie przechowywał znalezione usługi
    services = {}
    
    # Rozpoczyna pętlę przez wszystkie aktywne połączenia internetowe (IPv4 i IPv6)
    for conn in psutil.net_connections('inet'):
        
        # Interesują nas tylko te połączenia, które są w stanie "LISTEN" (nasłuchiwanie)
        if conn.status == 'LISTEN':
            
            # Pobieramy numer portu dla tego połączenia
            port = conn.laddr.port
            
            # Sprawdzamy, czy system był w stanie zidentyfikować PID procesu (wymaga 'sudo' dla wszystkich procesów)
            if conn.pid:
                try:
                    # Jeśli mamy PID, próbujemy uzyskać obiekt "Process" na jego podstawie
                    process = psutil.Process(conn.pid)
                    
                    # Zapisujemy do naszego słownika port jako klucz
                    # oraz nazwę procesu i jego PID jako wartość
                    services[port] = {'name': process.name(), 'pid': conn.pid}
                    
                except psutil.NoSuchProcess:
                    # Obsługa błędu, jeśli proces zdążył się zamknąć między skanowaniem a pobraniem nazwy
                    services[port] = {'name': "Process vanished", 'pid': None}
            else:
                # Jeśli nie mamy PID (np. brak uprawnień sudo), zapisujemy informację
                services[port] = {'name': "Unknown (No PID)", 'pid': None}
                
    # Zwracamy gotowy słownik ze wszystkimi znalezionymi usługami
    return services

# --- FUNKCJA INICJALIZACYJNA ---

def initialization():
    """
    Uruchamiana tylko raz na starcie skryptu.
    Pobiera początkowy stan usług i drukuje go w tabeli.
    Zwraca początkową "bazę" usług.
    """
    # Wywołujemy funkcję skanującą, aby pobrać początkowy stan
    start_services = get_services()

    # Drukujemy komunikaty powitalne i podsumowanie
    print(f"Monitoring has been initiated. Initially, {len(start_services)} services were identified.")
    print("-" * 55)

    # Drukujemy nagłówek tabeli z odpowiednim formatowaniem (wyrównanie i szerokość kolumn)
    print(f"{'PORT':<10} {'RUNNING PROCESS':<25} {'PID':<10}")
    print("*" * 55)

    # Przechodzimy przez każdą usługę znalezioną na starcie
    for port, service_info in start_services.items():
        
        # Wyciągamy nazwę procesu ze słownika 'service_info'
        process_name = service_info['name']
        
        # Wyciągamy PID. Jeśli PID to 'None', zamiast tego użyjemy tekstu 'N/A'
        pid = service_info['pid'] if service_info['pid'] is not None else 'N/A'
        
        # Drukujemy sformatowany wiersz tabeli
        print(f"{port:<10} {process_name:<25} {pid:<10}")

    # Zwracamy początkową listę usług, która stanie się naszą "bazą" do porównań
    return start_services

# --- FUNKCJA POMOCNICZA DO DRUKOWANIA ---

def print_services():
    """
    Funkcja pomocnicza do drukowania AKTUALNEGO stanu usług w dowolnym momencie.
    """
    # Pobieramy ŚWIEŻĄ listę usług (skanujemy system ponownie)
    service_dict = get_services()

    # Drukujemy tabelę (tak jak w initialization)
    print("-" * 55)
    print(f"{'PORT':<10} {'RUNNING PROCESS':<25} {'PID':<10}")
    print("*" * 55)

    for port, service_info in service_dict.items():
        process_name = service_info['name']
        pid = service_info['pid'] if service_info['pid'] is not None else 'N/A'
        print(f"{port:<10} {process_name:<25} {pid:<10}")
    print("#"*55)

# --- GŁÓWNA FUNKCJA PROGRAMU ---

def main():
    # 1. INICJALIZACJA: Pobieramy "bazę" usług przy starcie
    base_services = initialization()

    # 2. Rozpoczynamy nieskończoną pętlę monitorowania
    while True:
        # Usypiamy skrypt na 10 sekund
        time.sleep(10)

        # 3. Pobieramy "aktualny" stan usług
        current_services = get_services()

        # 4. PRZYGOTOWANIE DO PORÓWNANIA:
        # Tworzymy zbiór (set) portów z naszej "bazy"
        base_ports = set(base_services.keys())
        # Tworzymy zbiór (set) portów "aktualnych"
        current_ports = set(current_services.keys())

        # 5. PORÓWNANIE:
        # Znajdujemy różnicę zbiorów. W 'new_ports' będą tylko te porty,
        # które są w 'current_ports', ale nie ma ich w 'base_ports'.
        new_ports = current_ports - base_ports

        # 6. REAKCJA NA NOWE USŁUGI:
        # Sprawdzamy, czy zbiór 'new_ports' nie jest pusty
        if new_ports:
            # Drukujemy duże ostrzeżenie
            print("\n" + "#"*55)
            print(f"!!! NEW SERVICE(S) DETECTED: {len(new_ports)} !!!")
            print("#"*55)

            # Przechodzimy pętlą przez KAŻDY nowo znaleziony port
            for port in new_ports:
                
                # Wyciągamy informacje o nowym procesie z 'current_services'
                service_info = current_services[port]
                process_name = service_info['name']
                pid_to_kill = service_info['pid']

                # Drukujemy informacje o nowej usłudze
                print(f"\n[+] Port: {port}, Process: {process_name}, PID: {pid_to_kill}")

                # Sprawdzamy, czy w ogóle mamy PID (jeśli nie, nie możemy zabić procesu)
                if pid_to_kill is None:
                    print("  -> Cannot kill: PID is not available (run script with sudo).")
                    # Przerywamy tę iterację pętli i przechodzimy do następnego nowego portu
                    continue 

                # Pytamy użytkownika o decyzję
                # UWAGA: W input() jest błąd, powinno być {pid_to_kill} zamiast {process_name}
                temp = input(f"  -> Do you want to kill this process (PID: {pid_to_kill})? (yes/no): ")

                # 7. OBSŁUGA DECYZJI UŻYTKOWNIKA:
                # Jeśli użytkownik wpisze "yes" (ignorujemy wielkość liter)
                if temp.lower() == 'yes':
                    
                    # Tworzymy obiekt procesu na podstawie PID
                    p = psutil.Process(pid_to_kill)

                    # Drukujemy informację o zabijaniu
                    print(f"Terminating process: {pid_to_kill} ({process_name})")
                    
                    # "Zabijamy" proces (wysyłamy sygnał SIGKILL)
                    p.kill()

                    # Czekamy 10 sekund (dajemy czas systemowi na reakcję, np. restart usługi)
                    time.sleep(10)

                    # Drukujemy nową, zaktualizowaną listę wszystkich usług
                    print_services()

                # Jeśli użytkownik wpisze "no"
                elif temp.lower() == 'no':
                    print(f"  -> Adding procces to table {pid_to_kill} ({process_name}).")

                    # KLUCZOWA LINIA:
                    # Nadpisujemy starą "bazę" ('base_services') "aktualną" listą ('current_services').
                    # Od teraz, ta nowa usługa jest częścią "bazy" i nie będzie już zgłaszana.
                    base_services = current_services

                    # Drukujemy nową, zaktualizowaną listę wszystkich usług
                    print_services()
            
            # (Uwaga: W tym kodzie 'base_services' jest aktualizowane tylko gdy wpiszesz 'no'.
            # Jeśli wpiszesz 'yes', 'base_services' nie jest aktualizowane w tej pętli,
            # co oznacza, że jeśli system zrestartuje usługę (np. sshd), 
            # zostanie ona wykryta jako "nowa" ponownie w następnej pętli.)


# Standardowy punkt startowy Pythona
if __name__ == "__main__":
    # Wywołuje główną funkcję programu
    main()
