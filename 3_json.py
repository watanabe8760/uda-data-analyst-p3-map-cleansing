from datetime import datetime
import json
from bson import json_util

def convert_xml_2_json(tree, filename):
    """
    Converts xml to json file.
    A field "xml" is added to record tag name.
    
    Args:
        tree: An ElementTree object.
        filename: A JSON file name outputted.
    Yields:
        A JSON file.
    """
    with open("./input/" + filename, "w") as f:
        # Start of JSON file
        f.write("[\n")
        
        # Convert the root element
        root = tree.getroot().attrib.copy()
        root["timestamp"] = datetime.strptime(root["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
        root["xml"] = tree.getroot().tag
        json.dump(root, f, default=json_util.default, indent=4)
        
        # Convert all elements under the root
        for parent in tree.getroot():
            record = parent.attrib.copy()
            record["xml"] = parent.tag
            if parent.iter():
                if parent.tag == "node":
                    # "node/tag"
                    if parent.findall("tag"):
                        record["tag"] = []
                        for child in parent.findall("tag"):
                            record["tag"].append(child.attrib)
                
                elif parent.tag == "relation":
                    # "relation/tag"
                    if parent.findall("tag"):
                        record["tag"] = []
                        for child in parent.findall("tag"):
                            record["tag"].append(child.attrib)
                    # "relation/member"
                    if parent.findall("member"):
                        record["member"] = []
                        for child in parent.findall("member"):
                            record["member"].append(child.attrib)
                    
                elif parent.tag == "way":
                    # "way/nd"
                    if parent.findall("nd"):
                        record["nd"] = []
                        for child in parent.findall("nd"):
                            record["nd"].append(child.get("ref"))
                    # "way/tag"
                    if parent.findall("tag"):
                        record["tag"] = []
                        for child in parent.findall("tag"):
                            record["tag"].append(child.attrib)
                    
                elif parent.tag == "bounds":
                    # bounds element does not have any child
                    None
                else:
                    print "[Error] Unexpected tag :", parent.tag
            # Write a record
            f.write(", \n")
            json.dump(record, f, default=json_util.default, indent=4)
        # End of JSON file
        f.write("\n]")
        
# Convert xml to json
convert_xml_2_json(tree, "singapore.json")


