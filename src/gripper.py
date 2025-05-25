from robodk import robolink

class Gripper:
    def __init__(self, rdk, tool_name="AROB_LWS_VakuumGreifer_14"):
        self.tool = rdk.Item(tool_name, robolink.ITEM_TYPE_TOOL)

    def close(self):
        """Schliesst den Greifer (greift das nächste Objekt)"""
        self.tool.AttachClosest()

    def open(self):
        """Öffnet den Greifer (lässt alle Objekte los)"""
        self.tool.DetachAll()


if __name__ == "__main__":
    # Beispiel zur Verwendung des Greifers
    rdk = robolink.Robolink()
    gripper = Gripper(rdk)
    
    # Greifer öffnen und schließen
    gripper.open()
    print("Greifer geöffnet.")
    gripper.close()
    print("Greifer geschlossen.")
    print(f"Greifer-Tool: {gripper.tool.Name()} at {gripper.tool.Pose()}")