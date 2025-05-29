# Hauptprogramm für automatischen Jenga-Turmbau mit Staubli TX2-40 Roboter
# Implementiert objektorientierte Architektur für modulare Robotersteuerung

from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

from robot_controller import RobotController
from magazine import Magazine
from tower import Tower
from jenga_piece_collection import JengaPiece, JengaPieceCollection


def main():
    """Hauptfunktion für den automatisierten Jenga-Turmbau"""
    try:
        # Verbindung zu RoboDK-Simulation herstellen
        rdk = Robolink()
        
        # Initialisierung der Teilsysteme mit objektorientiertem Ansatz
        robot_controller = RobotController(rdk)
        magazine = Magazine(rdk)
        tower = Tower(rdk)
        
        # Jenga-Steine als Objektsammlung verwalten (15 Steine)
        pieces = JengaPieceCollection(rdk, 15)
        print(f"Initialized Jenga robot system with {len(pieces)} pieces")
        
        # Robotersystem in Ausgangslage bringen
        print("Initializing robot system...")
        robot_controller.initialize()
        
        # Pickup-Positionen im Magazin berechnen und generieren
        pick_above_poses, pick_poses = magazine.get_pick_positions()
        print("Magazine pickup positions generated")
        
        # Start des sequenziellen Turmbaus
        print("Starting Jenga tower construction...")
        
        # Iterative Verarbeitung aller Jenga-Steine in numerischer Reihenfolge
        for piece in pieces:
            print(f"Processing {piece} for layer {tower.get_layer_for_piece(piece)+1}")
            
            # Kompletter Bewegungsablauf: Aufnehmen aus Magazin und Platzieren im Turm
            robot_controller.move_piece(
                piece, 
                magazine, 
                tower, 
                pick_above_poses, 
                pick_poses
            )
        
        # Turmbau erfolgreich abgeschlossen - Roboter in Home-Position
        print("Jenga tower construction completed!")
        robot_controller.move_to_home()
            
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
