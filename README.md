# block_unauth_service
Monitoring and blocking unauthorized services - protection against malware registering as a system service


Opis każdej linijki kodu

Oto szczegółowa analiza twojego kodu, linia po linii, w języku polskim.

Importy

    import psutil: Importuje bibliotekę psutil. Jest ona używana do pobierania informacji o procesach systemowych i połączeniach sieciowych.

    import time: Importuje bibliotekę time. Jest ona używana do wstrzymywania (usypiania) wykonania skryptu na określony czas.

def get_services()

Ta funkcja skanuje system w poszukiwaniu nasłuchujących portów i zwraca słownik.

    def get_services():: Definiuje funkcję o nazwie get_services, która nie przyjmuje żadnych argumentów.

    services = {}: Tworzy pusty słownik (dictionary) i przypisuje go do zmiennej services. Będzie on przechowywał znalezione usługi.

    for conn in psutil.net_connections('inet'):: Rozpoczyna pętlę for, która iteruje (przechodzi) po każdym połączeniu sieciowym zwróconym przez funkcję psutil.net_connections(). Argument 'inet' ogranicza wyszukiwanie tylko do połączeń z rodziny IPv4 oraz IPv6.

    if conn.status == 'LISTEN':: Wewnątrz pętli, sprawdza warunek. Wykonuje kod poniżej tylko wtedy, gdy atrybut status bieżącego połączenia (conn) jest równy ciągowi znaków 'LISTEN'.

    port = conn.laddr.port: Pobiera numer portu z atrybutu laddr (adres lokalny) połączenia i przypisuje go do zmiennej port.

    if conn.pid:: Sprawdza, czy atrybut pid (Process ID) połączenia nie jest pusty (czy nie jest None). Oznacza to, że system był w stanie zidentyfikować proces powiązany z tym portem.

    try:: Rozpoczyna blok try, który służy do obsługi błędów. Kod wewnątrz jest "pilnowany" pod kątem wystąpienia wyjątku.

    process = psutil.Process(conn.pid): Używa psutil, aby utworzyć obiekt reprezentujący proces systemowy, na podstawie jego identyfikatora (conn.pid). Obiekt ten jest przypisywany do zmiennej process.

    services[port] = {'name': process.name(), 'pid': conn.pid}: Dodaje nowy wpis do słownika services. Kluczem wpisu staje się numer portu (port). Wartością jest nowy słownik, który zawiera dwa klucze: 'name' (przechowujący nazwę procesu zwróconą przez process.name()) oraz 'pid' (przechowujący numer PID).

    except psutil.NoSuchProcess:: Definiuje blok except, który wykonuje się, jeśli blok try zgłosi błąd NoSuchProcess. Taki błąd zdarza się, gdy proces zdążył się zakończyć, zanim skrypt zdążył pobrać jego nazwę.

    services[port] = {'name': "Process vanished", 'pid': None}: W przypadku wystąpienia błędu NoSuchProcess, do słownika services dodawany jest wpis z informacją o błędzie.

    else:: Definiuje blok else, który wykonuje się, jeśli warunek if conn.pid: (sprawdzenie, czy PID istnieje) nie został spełniony.

    services[port] = {'name': "Unknown (No PID)", 'pid': None}: Dodaje wpis do słownika services z informacją, że PID jest nieznany (prawdopodobnie z powodu braku uprawnień).

    return services: Po zakończeniu pętli for, funkcja zwraca wypełniony słownik services.

def initialization()

Ta funkcja jest uruchamiana raz na starcie, aby pokazać początkowy stan usług.

    def initialization():: Definiuje funkcję initialization bez argumentów.

    start_services = get_services(): Wywołuje funkcję get_services() opisaną powyżej. Zwrócony przez nią słownik zostaje przypisany do zmiennej start_services.

    print(f"Monitoring has been initiated..."): Drukuje w terminalu sformatowany ciąg znaków (f-string) z informacją o starcie monitoringu i liczbie znalezionych usług.

    print("-" * 55): Drukuje w terminalu 55 znaków myślnika, tworząc linię oddzielającą.

    print(f"{'PORT':<10} {'RUNNING PROCESS':<25} {'PID':<10}"): Drukuje sformatowany nagłówek tabeli. :<10 i :<25 oznaczają wyrównanie tekstu do lewej i zarezerwowanie odpowiednio 10 lub 25 znaków na ten tekst.

    print("*" * 55): Drukuje 55 znaków gwiazdki jako kolejny separator.

    for port, service_info in start_services.items():: Rozpoczyna pętlę iterującą po słowniku start_services. Metoda .items() zwraca jednocześnie klucz (przypisany do port) i wartość (przypisaną do service_info).

    process_name = service_info['name']: Ze słownika service_info (który jest wartością) wyciąga wartość powiązaną z kluczem 'name' i przypisuje ją do process_name.

    pid = service_info['pid'] if service_info['pid'] is not None else 'N/A': Jest to skrócony zapis warunku (ternary operator). Przypisuje on do zmiennej pid wartość service_info['pid'], ale tylko wtedy, gdy ta wartość nie jest None. Jeśli jest None, przypisuje ciąg znaków 'N/A'.

    print(f"{port:<10} {process_name:<25} {pid:<10}"): Drukuje sformatowany wiersz tabeli, wstawiając wartości port, process_name i pid.

    return start_services: Zwraca słownik start_services, który zawiera początkowy stan usług.

def print_services()

Ta funkcja jest podobna do initialization, ale służy tylko do wydrukowania aktualnego stanu usług w dowolnym momencie.

    def print_services():: Definiuje funkcję print_services bez argumentów.

    service_dict = get_services(): Wywołuje get_services(), aby pobrać świeżą listę usług i zapisuje ją w service_dict.

    print("-" * 55): Drukuje separator.

    print(f"{'PORT':<10} ..."): Drukuje nagłówek tabeli (identyczny jak w initialization).

    print("*" * 55): Drukuje separator.

    for port, service_info in service_dict.items():: Rozpoczyna pętlę iterującą po service_dict.

    process_name = service_info['name']: Pobiera nazwę procesu.

    pid = service_info['pid'] if service_info['pid'] is not None else 'N/A': Pobiera PID lub 'N/A'.

    print(f"{port:<10} ..."): Drukuje sformatowany wiersz tabeli.

    print("#"*55): Drukuje końcowy separator.

def main()

To jest główna funkcja programu, która zawiera nieskończoną pętlę monitorującą.

    def main():: Definiuje funkcję main bez argumentów.

    base_services = initialization(): Wywołuje funkcję initialization() jeden raz. Zwrócony słownik staje się "bazą" znanych usług i jest zapisywany w base_services.

    while True:: Rozpoczyna nieskończoną pętlę. Kod wewnątrz będzie się wykonywał bez przerwy.

    time.sleep(10): Wstrzymuje wykonanie pętli na 10 sekund.

    current_services = get_services(): Wywołuje get_services(), aby pobrać aktualną listę usług i zapisuje ją w current_services.

    base_ports = set(base_services.keys()): Pobiera wszystkie klucze (numery portów) ze słownika base_services i tworzy z nich zbiór (set).

    current_ports = set(current_services.keys()): Robi to samo dla słownika current_services.

    new_ports = current_ports - base_ports: Wykonuje operację różnicy zbiorów. W new_ports znajdą się tylko te porty, które istnieją w current_ports, ale nie istnieją w base_ports.

    if new_ports:: Sprawdza, czy zbiór new_ports nie jest pusty. Kod poniżej wykona się tylko wtedy, gdy znaleziono nowe usługi.

    print("\n" + "#"*55): Drukuje separatory i komunikat o wykryciu nowych usług.

    for port in new_ports:: Rozpoczyna pętlę iterującą po każdym porcie ze zbioru new_ports.

    service_info = current_services[port]: Pobiera ze słownika current_services wartość (wewnętrzny słownik) dla danego portu.

    process_name = service_info['name']: Wyciąga nazwę procesu.

    pid_to_kill = service_info['pid']: Wyciąga PID procesu.

    print(f"\n[+] Port: ..."): Drukuje informację o wykrytym nowym procesie.

    if pid_to_kill is None:: Sprawdza, czy PID jest None (nieznany).

    print(" -> Cannot kill: ..."): Drukuje komunikat o błędzie (brak PID).

    continue: Natychmiast przerywa bieżącą iterację pętli for i przechodzi do następnego portu na liście new_ports.

    temp = input(f" -> Do you want to kill ..."): Wyświetla pytanie do użytkownika (czy zabić proces) i czeka na jego odpowiedź, którą zapisuje w zmiennej temp.

    if temp.lower() == 'yes':: Sprawdza, czy użytkownik wpisał "yes" (zamieniając tekst na małe litery za pomocą .lower()).

    p = psutil.Process(pid_to_kill): Tworzy obiekt procesu psutil na podstawie PID.

    print(f"Terminating process: ..."): Drukuje komunikat o zamiarze zatrzymania procesu.

    p.kill(): Wysyła sygnał SIGKILL do procesu, natychmiast go zatrzymując.

    time.sleep(10): Wstrzymuje wykonanie na 10 sekund (aby dać systemowi czas na ewentualny restart usługi).

    print_services(): Wywołuje funkcję print_services(), aby pokazać nową listę aktywnych usług.

    elif temp.lower() == 'no':: Sprawdza, czy użytkownik wpisał "no".

    print(f" -> Adding procces to table ..."): Drukuje komunikat o dodaniu procesu do "bazy".

    base_services = current_services: (Kluczowa linia) Nadpisuje stary słownik base_services nowym słownikiem current_services. Od tego momentu nowo wykryta usługa staje się częścią "bazy" i nie będzie już zgłaszana jako nowa.

    print_services(): Wywołuje print_services(), aby pokazać listę usług (już z dodanym nowym procesem).

Uruchomienie skryptu

    if __name__ == "__main__":: Jest to standardowy idiom w Pythonie. Ten warunek jest prawdziwy tylko wtedy, gdy plik jest uruchamiany bezpośrednio (a nie importowany jako moduł).

    main(): Wywołuje funkcję main(), co rozpoczyna działanie całego programu.
