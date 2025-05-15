# Aufgabe 2
```val3
proc jengaTransport()
   movej(home)
   movel(posA_above)
   movel(posA_grab)
   setVacuum(true)
endproc
```
# Aufgabe 3
```val3
-- Pseudocode in VAL3 für Jenga-Stein Transport --

-- Hauptprogramm
proc jengaTransport()
   movej(home)
   movel(posA_above)
   movel(posA_grab)
   setVacuum(true)
   wait(1.0)
   movel(posA_above)
   movel(posB_above)
   movel(posB_place)
   setVacuum(false)
   wait(1.0)
   movel(posB_above)
   movej(home)
endproc

-- Hilfsfunktionen (hier symbolisch, da reale Steuerung vom Setup abhängt)
proc setVacuum(bool status)
   if status then
      dio[1] = true
   else
      dio[1] = false
   endIf
endproc
````
# Struktur der Koordinatenwerte
```val3
-- Koordinatenwerte sind exemplarisch (Einheit: mm, Winkel in Grad)

point home_pos     = [500, 0, 300, 180, 0, 180]      -- Sichere Home-Position oben über dem Tisch
point posA_grab    = [300, 100, 130, 180, 0, 180]     -- Greifhöhe bei Punkt A (Z um 20 mm tiefer)
point posA_above   = posA_grab + [0, 0, 20, 0, 0, 0]     -- Über Punkt A mit 2 cm Sicherheitsabstand
point posB_place   = [100, -200, 130, 180, 0, 180]    -- Ablagehöhe bei Punkt B (ebenfalls -20 mm Z)
point posB_above   = posB_grab + [0, 0, 20, 0, 0, 0]      -- Über Punkt B mit Sicherheitsabstand

-- Erklärung der Struktur:
-- [X, Y, Z, RX, RY, RZ]
-- X, Y, Z: Position in Raumkoordinaten
-- RX, RY, RZ: Orientierung des Werkzeugs (z. B. Greifer)
```

