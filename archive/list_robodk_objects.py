from robodk import *
from robolink import *

def list_all_objects():
    """Lists all objects available in the RoboDK station"""
    # Connect to RoboDK
    RDK = robolink.Robolink()
    
    # Get all items in the station
    item_list = RDK.ItemList()
    
    print("Available RoboDK Objects:")
    print("========================")
    
    # Print each item with its type
    for item in item_list:
        item_name = item.Name()
        item_type = item.Type()
        
        # Convert item type to readable string
        type_str = "Unknown"
        if item_type == ITEM_TYPE_STATION:
            type_str = "Station"
        elif item_type == ITEM_TYPE_ROBOT:
            type_str = "Robot"
        elif item_type == ITEM_TYPE_FRAME:
            type_str = "Frame"
        elif item_type == ITEM_TYPE_TOOL:
            type_str = "Tool"
        elif item_type == ITEM_TYPE_OBJECT:
            type_str = "Object"
        elif item_type == ITEM_TYPE_TARGET:
            type_str = "Target"
        elif item_type == ITEM_TYPE_PROGRAM:
            type_str = "Program"
        
        print(f"- {item_name} (Type: {type_str})")
    
    print("\nTotal objects:", len(item_list))

if __name__ == "__main__":
    list_all_objects()