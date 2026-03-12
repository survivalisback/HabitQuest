# Weeklys - Matteo

## Week 0 - 09.02.2026 - 13.02.2026

Das haben wir geschafft:
- Überblick über kommenden Block von Herr Müller Tofal und Herr Kluge bekommnen
- Projektideen überlegt/gesammelt
- Entschieden für einen HabitTracker der sich von gewöhnlichen Trackern durch Gamification unterscheidet
- Projektantrag erstellt
- Userstories erstellt
- Use-Case-Diagramm erstellt

Daran arbeiten wir als nächstes:
- Grobe vorlage für Backend und Frontend entwickeln
- Weitere UML Diagramme

## Week 1 - 16.02.2026 - 20.02.2026

Das habe ich geschafft:
- Erstellen eines UML Klassendiagramms
    - Nicht vollständig, erstmal nur skizziert
- Anpassen der Ordnerstruktur
- Erstellen einer UV-Umgebung
- Erstellen eines einfachen Python Interfaces (Grobe Dateistruktur, imports/exports, etc.)

Daran arbeite ich als nächstes:
- Weitere Backend-Entwicklung
    - Erstellen von API Endpunkten zum Frontend
- Entwicklung eines Datenbank-entwurfs

## Week 2 - 23.02.2026 - 27.02.2026

Das habe ich geschafft:
- Erstellen einer grundlegenden Backend-Struktur
    - Grundlegende API Funktionalität
    - Grundlegende Funktionalitäten für hauptfunktionen (bspw. Habit erstellung, bearbeitung, löschung, etc.)
    - Datenbankanbindung erstellt
- Erstellung eines groben Datenbankentwurfs
- Erstellung der Datenbank basierend auf dem Datenbankentwurf
- Problem: Python imports funktionieren nicht

Daran arbeite ich als nächstes:
- Fehler bei Python imports beheben
- Manuelle tests ob Frontend zu Backend Anbindung funktioniert
- Service/Business logik implementieren
    - bspw. XP-Reward, Streaks, etc.

## Week 3 - 02.03.2026 - 06.03.2026
 
Das habe ich geschafft:
- Python imports gefixed
- Service/Business logik implementiert
    - XP-Rewards
 
Daran arbeite ich als nächstes:
- Manuelle tests ob Fronted zu Backend Anbindung funktioniert
- Service/Business logik implementieren
- Datenbank erweitern/anpassen
    - Für toggle funktion und ggf. Rewards
- ggf. KI Anbindung
## Week 4 - 09.03.2026 - 13.03.2026
 
Das habe ich geschafft:
- Erste manuelle tests ob Frontend zu Backend Anbindung funktioniert
- Toggle Funktion implementiert
    - inkl. abezogener XP-Rewards, sollte ein Habit zurück getoggled werden
- Multi-User-Support implementiert
    - Anmeldung/Registierung
    - User bezogene Habit-Speicherung
    - Datenbank erweitert/angepasst
    - JWT Tokens zur Verifizierung auch ohne Anmeldung
    - Anpassen der API Endpunkte sowie der Servicelogik zur Verwendung der JWT Tokens
 
Daran arbeite ich als nächstes:
- Erneute manuelle tests ob Frontend zu Backend Anbindung funktioniert
    - Mit JWT Tokens/Login
- KI Anbindung zur XP-Berechnung