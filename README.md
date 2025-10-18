# block_unauth_service
Monitoring and blocking unauthorized services - protection against malware registering as a system service


Ten skrypt to narzędzie do monitorowania systemu w czasie rzeczywistym, napisane w języku Python. Jego głównym celem jest wykrywanie nowych usług sieciowych, które zaczynają nasłuchiwać na portach komputera. Działa w nieskończonej pętli, co 10 sekund skanując system w poszukiwaniu aktywnych procesów.

Logika działania jest następująca:

    Inicjalizacja: Przy pierwszym uruchomieniu skrypt tworzy "listę bazową" (base_services) wszystkich usług, które aktualnie nasłuchują na portach. Pokazuje tę listę w terminalu, aby użytkownik wiedział, co jest uruchomione na starcie.

    Monitoring: Co 10 sekund skrypt pobiera nową, "chwilową" listę (current_services) wszystkich aktywnych usług.

    Porównanie: Porównuje listę "chwilową" z "listą bazową", używając zbiorów (set), aby znaleźć procesy, które pojawiły się niedawno (są w current_services, ale nie ma ich w base_services).

    Interakcja: Jeśli zostaną wykryte nowe usługi, skrypt informuje o tym użytkownika i dla każdego nowego procesu pyta, czy ma on zostać "zabity" (yes), czy zignorowany (no).

    Reakcja:

        W przypadku wybrania yes, skrypt próbuje natychmiastowo zakończyć proces (p.kill()), a następnie pokazuje zaktualizowaną listę wszystkich usług.

        W przypadku wybrania no, skrypt dodaje wszystkie aktualnie wykryte usługi do "listy bazowej" (base_services = current_services). Dzięki temu zignorowana usługa nie będzie już zgłaszana jako nowa w kolejnych pętlach. Następnie również pokazuje zaktualizowaną listę usług.

Skrypt wykorzystuje bibliotekę psutil do pozyskiwania informacji o procesach i połączeniach sieciowych. Do poprawnego działania (aby widzieć wszystkie procesy systemowe i mieć prawo je zatrzymać) wymaga uruchomienia z uprawnieniami administratora (sudo).
