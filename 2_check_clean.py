import xml.etree.cElementTree as ET
from datetime import datetime
from pprint import pformat
import re

# Load XML data
tree = ET.parse("./input/singapore.osm")

# Tag names (exclude the root "osm")
TAGS = ["bounds",
        "node", "node/tag", \
        "relation", "relation/tag", "relation/member", \
        "way", "way/nd", "way/tag"]

# Data type of attributes
DTYPE = {
    "bounds"          : {'maxlat'   : float,
                         'maxlon'   : float,
                         'minlat'   : float,
                         'minlon'   : float},
    "node"            : {'changeset': int,
                         'id'       : int,
                         'lat'      : float,
                         'lon'      : float,
                         'timestamp': datetime,
                         'uid'      : int,
                         'user'     : str,
                         'version'  : int}, 
    "node/tag"        : {'k'        : str, 
                         'v'        : str},
    "relation"        : {'changeset': int,
                         'id'       : int,
                         'timestamp': datetime,
                         'uid'      : int,
                         'user'     : str,
                         'version'  : int},
    "relation/tag"    : {'k'        : str, 
                         'v'        : str}, 
    "relation/member" : {'ref'      : int, 
                         'role'     : str, 
                         'type'     : str}, 
    "way"             : {'changeset': int,
                         'id'       : int,
                         'timestamp': datetime,
                         'uid'      : int,
                         'user'     : str,
                         'version'  : int},  
    "way/nd"          : {'ref'      : int},
    "way/tag"         : {'k'        : str, 
                         'v'        : str}
}


def get_all_vals(tree, tag, attr):
    """
    Returns all values of an attribute in a specific tag.
    """
    vals = []
    for element in tree.findall(tag):
        vals.append(element.get(attr))
    return vals


def check_range_of_loc(tree):
    """
    Checks if latitude and longitude in node are within the range specified in bounds.
    """
    bounds = tree.find('bounds')
    maxlat = bounds.get("maxlat")
    maxlon = bounds.get("maxlon")
    minlat = bounds.get("minlat")
    minlon = bounds.get("minlon")
    for element in tree.findall("node"):
        lat = element.get('lat')
        lon = element.get('lon')
        if lat > maxlat or lat < minlat:
            error_msg("Latitude is out of range.", "bounds", "lat", lat)
        if lon > maxlon or lon < minlon:
            error_msg("Longitude is out of range.", "bounds", "lat", lat)
check_range_of_loc(tree)


# [Warning] Do not execute. Too slow to complete.
def check_node_ref(tree):
    """
    Checks if references pointing to nodes exist.
        [Pointer]
            "relation/member@ref" 
            "way/nd@ref"
        [Origin]
            "node@id"
    Returns:
        Number of refs that do not exist.
    """
    ids = get_all_vals(tree, "node", "id")
    refs = get_all_vals(tree, "relation/member", "ref")
    refs.append(get_all_vals(tree, "way/nd", "ref"))
    return len(refs) - sum([r in ids for r in refs])
#check_node_ref(tree)


# node/tag[@k='name']
node_tag_names = tree.findall("node/tag[@k='name']")
  
def capitalize_head(tag_elements):
    """
    Capitalizes head of each word in "v(alue)" of */tag elements.
    Ignores common prepositions. (of, at, on, in, by, to, for, and, the)
    
    Args:
        tag_elements: A list of */tag elements.
    Yields:
        The change is directly reflected in xml elements.
    Returns:
        A list of tuples (before, after).
    """
    lower_head = re.compile(r'^[a-z]| [a-z]')
    ignored = re.compile(r'of |at |on |in |by |to |for |and |the ')
    modified = []
    for element in tag_elements:
        bef = element.get("v")
        while ignored.search(bef) is not None:
            bef = ignored.sub('', bef)
        if lower_head.search(bef):
            bef = element.get("v")
            aft = ''
            for word in bef.split(' '):
                if word in ('of', 'at', 'on', 'in', 'by', 'to', 'for', 'and', 'the'):
                    aft += word + ' '
                else:
                    aft += word[0].capitalize() + word[1:] + ' '
            element.set("v", aft.rstrip())
            modified.append((bef, aft.rstrip()))
    return modified

# Capitalizes head of each word in name
with open('./output/node-tag@name-capitalized.txt', 'w') as f:
    f.write(pformat(capitalize_head(node_tag_names)))


def standardize_name(tag_elements, target_exp, standardized):
    """
    Standardizes "v(alue)" of */tag elements.
    Changes values which correspond to a regular experssion target_exp.
    
    Args:
        tag_elements: A list of */tag elements.
        target_exp: A regular expression targetted. Case-insensitive.
        standardized: A standardized value converted into.
    Yields:
        The change is directly reflected in xml elements.
    Returns:
        A list of tuples (before, after).
    """
    target = re.compile(target_exp, re.IGNORECASE)
    modified = []
    for element in tag_elements:
        bef = element.get("v")
        if target.search(bef):
            aft = target.sub(standardized, bef)
            element.set("v", aft)
            modified.append((bef, aft))
    return modified

# Recover abbreviated words in name
with open('./output/node-tag@name-abbrev.txt', 'w') as f:
    f.write("'^blk ' -> 'Block '\n")
    f.write(pformat(standardize_name(node_tag_names, r"^blk ", "Block ")))
    f.write("\n\n' blk ' -> ' Block '\n")
    f.write(pformat(standardize_name(node_tag_names, r" blk ", " Block ")))
    f.write("\n\n'^opp ' -> 'Opposite '\n")
    f.write(pformat(standardize_name(node_tag_names, r"^opp ", "Opposite ")))
    f.write("\n\n' opp ' -> ' Opposite '\n")
    f.write(pformat(standardize_name(node_tag_names, r" opp ", " Opposite ")))
    f.write("\n\n'^bef ' -> 'Before '\n")
    f.write(pformat(standardize_name(node_tag_names, r"^bef ", "Before ")))
    f.write("\n\n' bef ' -> ' Before '\n")
    f.write(pformat(standardize_name(node_tag_names, r" bef ", " Before ")))
    f.write("\n\n'^aft ' -> 'After '\n")
    f.write(pformat(standardize_name(node_tag_names, r"^aft ", "After ")))
    f.write("\n\n' aft ' -> ' After '\n")
    f.write(pformat(standardize_name(node_tag_names, r" aft ", " After ")))

# Standardizes franchised stores' name
with open('./output/node-tag@name-franchise.txt', 'w') as f:
    f.write(pformat(standardize_name(node_tag_names, r"7.11|7.eleven|seven.11|seven.eleven", "7-Eleven")))
    f.write("\n\n")
    f.write(pformat(standardize_name(node_tag_names, r"starbucks coffee|starbucks", "Starbucks")))
    f.write("\n\n")
    f.write(pformat(standardize_name(node_tag_names, r"mcdonald.s .+|mcdonalds .+|mcdonald.s|mcdonalds", "McDonald's")))
    f.write("\n\n")
    f.write(pformat(standardize_name(node_tag_names, r"mos.burger", "MOS Burger")))
    f.write("\n\n")
    f.write(pformat(standardize_name(node_tag_names, r"pizza.hut .+|pizza.hut", "Pizza Hut")))

# Record node/tag[@k='name'] after change
with open('./output/node-tag@name_aft.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='name']"))))




def remove_non_numeric(tag_elements):
    """
    Removes non-numerical characters in "v(alue)" of */tag elements.
    
    Args:
        tag_elements: A list of */tag elements.
    Yields:
        The change is directly reflected in xml elements.
    Returns:
        A list of tuples (before, after).
    """
    alpha = re.compile(r"[^0-9]")
    modified = []
    for element in tag_elements:
        bef = element.get("v")
        if alpha.search(bef):
            aft = alpha.sub("", bef)
            element.set("v", aft)
            modified.append((bef, aft))
    return modified

# Remove non-numeric characters in postcode
with open('./output/node-tag@postcode-alphabet.txt', 'w') as f:
    f.write(pformat(remove_non_numeric(tree.findall("node/tag[@k='addr:postcode']"))))
with open('./output/way-tag@postcode-alphabet.txt', 'w') as f:
    f.write(pformat(remove_non_numeric(tree.findall("way/tag[@k='addr:postcode']"))))


#def remove_invalid_postcodes(tag_elements):
#    """
#    Remove tag elements which have invalid postal code.
#        Case 1: Not six digits.
#        Case 2: Invalid first two digits.
#                The first two digits should be between 01 to 82 except 74
#    Args:
#        tag_elements: A list of */tag elements.
#    Yields:
#        Elements are removed from xml elements.
#    Returns:
#        A list of postal codes removed.
#    """
#    removed = []
#    valid_codes = [str(i) for i in xrange(1, 83) if i != 74]
#    valid_codes = ['0' + i if len(i) == 1 else i for i in valid_codes]
#    for element in tag_elements:
#        postcode = element.get("v")
#        if postcode[:2] not in valid_codes:
#            tag_elements.remove(element)
#            removed.append(postcode)
#            continue
#        if len(postcode) != 6:
#            tag_elements.remove(element)
#            removed.append(postcode)
#            
#    return removed

def remove_invalid_postcodes(parents):
    """
    Remove invalid postal code tag elements.
        Case 1: Not six digits.
        Case 2: Invalid first two digits.
                The first two digits should be between 01 to 82 except 74
    Args:
        parents: A list of parent elements that have postcode tag.
    Yields:
        Invalid postal code tag elements are removed from xml elements.
    Returns:
        A list of postal codes removed.
    """
    removed = []
    valid_codes = [str(i) for i in xrange(1, 83) if i != 74]
    valid_codes = ['0' + i if len(i) == 1 else i for i in valid_codes]
    for parent in parents:
        for tag in parent.findall("tag[@k='addr:postcode']"):
            postcode = tag.get("v")
            if postcode[:2] not in valid_codes:
                parent.remove(tag)
                removed.append(postcode)
                continue
            if len(postcode) != 6:
                parent.remove(tag)
                removed.append(postcode)
    
    return removed

# Remove invalid postal code tag elements
with open('./output/node-tag@postcode-invalid.txt', 'w') as f:
    f.write(pformat(remove_invalid_postcodes(tree.findall("node"))))
with open('./output/way-tag@postcode-invalid.txt', 'w') as f:
    f.write(pformat(remove_invalid_postcodes(tree.findall("way"))))


# Record [@k='addr:postcode'] after change
with open('./output/node-tag@postcode_aft.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='addr:postcode']"))))
with open('./output/way-tag@postcode_aft.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("way/tag[@k='addr:postcode']"))))



def error_msg(msg, tag, attr, val):
    """
    Prints error message.
    """
    print "[Error]" , msg, "\n", \
          "        Tag  :", tag, "\n", \
          "        Attr :", attr, "\n", \
          "        Value:",  val

def convert_dtype(tree, tags, dtype):
    """
    Converts string value of xml attributes into specified data type.
    
    Args:
        tree: An ElementTree object.
        tags: A list of tag name targetted for conversion.
        dtype: A dict of attribute's data type converted into.
    Yields:
        Attributes in tree are directly modified.
        In case there is an conversion error, an error message will be shown.
    """
    for tag in tags:
        elements = tree.findall(tag)
        for attr in dtype[tag].keys():
            for element in elements:
                if dtype[tag][attr] == int:
                    try:
                        element.set(attr, int(element.get(attr)))
                    except ValueError:
                        error_msg("Cannot convert into int.", tag, attr, element.get(attr))
                    
                elif dtype[tag][attr] == float:
                    try:
                        element.set(attr, float(element.get(attr)))
                    except ValueError:
                        error_msg("Cannot convert into float.", tag, attr, element.get(attr))
                    
                elif dtype[tag][attr] == datetime:
                    try:
                        element.set(attr, datetime.strptime(element.get(attr), \
                                                            '%Y-%m-%dT%H:%M:%SZ'))
                    except ValueError:
                        error_msg("Cannot convert into datetime.", tag, attr, element.get(attr))
                    
                else:
                    # Do nothing for str
                    None
convert_dtype(tree, TAGS, DTYPE)

