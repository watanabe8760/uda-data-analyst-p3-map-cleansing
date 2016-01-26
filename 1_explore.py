import xml.etree.cElementTree as ET
from pprint import pprint
from pprint import pformat

# Load XML data
tree = ET.parse("./input/singapore.osm")


def count_tag(tree):
    """
    Count number of tags in xml.
    """
    tags = {}
    for e in tree.iter():
        if e.tag not in tags:
            tags[e.tag] = 1
        else:
            tags[e.tag] += 1
    return tags
pprint(count_tag(tree))
#    {'bounds': 1,
#     'member': 69885,
#     'nd': 1146529,
#     'node': 931707,
#     'osm': 1,
#     'relation': 1762,
#     'tag': 461958,
#     'way': 139814}


def check_structure(parent, element):
    """
    Recursively drill down an element passed and count all elements under the element.
    
    Args:
        parent: A list [int, dict] which indicates parent element count and child elements.
        element: An Element object of xml to be checked.
    Yields:
        A hierarchical list [int, dict] which expresses structure of the element.
        Note, the result will be directly reflected in "parent".
    """
    if parent[1].has_key(element.tag):
        parent[1][element.tag][0] += 1
    else:
        parent[1][element.tag] = [1, {}]
    for child in element:
        # Recursive call for children
        check_structure(parent[1][element.tag], child)

# Check structure of xml
structure = [1, {}]
check_structure(structure, tree.getroot())
pprint(structure)
#{'osm': [1,
#         {'bounds': [1, {}],
#          'node': [931707, 
#                       {'tag': [80464, {}]}],
#          'relation': [1762, 
#                       {'member': [69885, {}], 
#                        'tag': [6191, {}]}],
#          'way': [139814, 
#                       {'nd': [1146529, {}], 
#                        'tag': [375303, {}]}]}]}


# Tag names (exclude the root "osm")
TAGS = ["bounds",
        "node", "node/tag", \
        "relation", "relation/tag", "relation/member", \
        "way", "way/nd", "way/tag"]


# Root tags 'osm'
pprint(tree.getroot().attrib)
#    {'generator': 'osmconvert 0.7T',
#     'timestamp': '2016-01-09T00:27:02Z',
#     'version': '0.6'}

def count_attributes(tree, tag):
    """
    Count total number of attributes in tag.
    """
    attributes = {}
    for element in tree.findall(tag):
        for attr in element.attrib.keys():
            if attr not in attributes:
                attributes[attr] = 1
            else:
                attributes[attr] += 1
    return attributes
for tag in TAGS:
    print tag
    pprint(count_attributes(tree, tag))
    print ""
#    bounds
#    {'maxlat': 1, 'maxlon': 1, 'minlat': 1, 'minlon': 1}
#    
#    node
#    {'changeset': 931707,
#     'id': 931707,
#     'lat': 931707,
#     'lon': 931707,
#     'timestamp': 931707,
#     'uid': 931707,
#     'user': 931707,
#     'version': 931707}
#    
#    node/tag
#    {'k': 80464, 'v': 80464}
#    
#    relation
#    {'changeset': 1762,
#     'id': 1762,
#     'timestamp': 1762,
#     'uid': 1762,
#     'user': 1762,
#     'version': 1762}
#    
#    relation/tag
#    {'k': 6191, 'v': 6191}
#    
#    relation/member
#    {'ref': 69885, 'role': 69885, 'type': 69885}
#    
#    way
#    {'changeset': 139814,
#     'id': 139814,
#     'timestamp': 139814,
#     'uid': 139814,
#     'user': 139814,
#     'version': 139814}
#    
#    way/nd
#    {'ref': 1146529}
#    
#    way/tag
#    {'k': 375303, 'v': 375303}



def show_samples(tree, tags, n):
    """
    Show n sample elements of specified tags.
    """
    for tag in tags:
        print tag
        for element in tree.findall(tag)[:n]:
            pprint(element.attrib)
        print ""
show_samples(tree, TAGS, 3)


def count_k(tag_elements):
    """
    Count value of "k(ey)" attribute in "*/tag" element.
    
    Args:
        tag_elements: */tag elements which have "k" attribute.
    Return:
        A list of tupples (count, k) in descending order of count.
    """
    count = {}
    for element in tag_elements:
        if count.has_key(element.get("k")):
            count[element.get("k")] += 1
        else:
            count[element.get("k")] = 1
    return sorted([(cnt, k) for (k, cnt) in count.items()], reverse=True)
# Count value of k(ey) in "*/tag"
with open('./output/node-tag.txt', 'w') as f:
    f.write(pformat(count_k(tree.findall("node/tag"))))
with open('./output/relation-tag.txt', 'w') as f:
    f.write(pformat(count_k(tree.findall("relation/tag"))))
with open('./output/way-tag.txt', 'w') as f:
    f.write(pformat(count_k(tree.findall("way/tag"))))


def count_v(tag_elements):
    """
    Count value of "v(alue)" attribute in "*/tag" element.
    
    Args:
        tag_elements: */tag elements which have "v" attribute.
    Return:
        A list of tupples (count, k) in descending order of count.
    """
    count = {}
    for element in tag_elements:
        if count.has_key(element.get("v")):
            count[element.get("v")] += 1
        else:
            count[element.get("v")] = 1
    return sorted([(cnt, v) for (v, cnt) in count.items()], reverse=True)
    # Sorted by "v(alue)"
    #return sorted([(v, cnt) for (v, cnt) in count.items()])

# Check some "v(alue)" in "node/tag"
with open('./output/node-tag@name.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='name']"))))
# [Problem 1] Words do not start with capital latter
#    Every word should starts with capital letter
# [Problem 2] Abbrebiation of common words
#    Opp -> Opposite
#    Bef -> Bofore
#    Aft -> After
#    Blk -> Block
# [Problem 3] Unstandardized franchised stores' name
#    7-Eleven
#    Starbucks
#    McDonald's
#    MOS Burger
#    Pizza Hut

with open('./output/node-tag@highway.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='highway']"))))
with open('./output/node-tag@location.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='location']"))))
with open('./output/node-tag@amenity.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='amenity']"))))
with open('./output/node-tag@street.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='addr:street']"))))
with open('./output/node-tag@postcode.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("node/tag[@k='addr:postcode']"))))
# [Problem 1] Alphabets are included
#    'S118556'
#    'S120517'
#    'Singapore 408564'
# [Problem 2] Not six digits
# [Problem 3] Wrong first two digits
#    The first two digits should indicate a specific district
# [Reference] https://en.wikipedia.org/wiki/Postal_codes_in_Singapore
#             https://www.ura.gov.sg/realEstateIIWeb/resources/misc/list_of_postal_districts.htm

# Check some "v(alue)" in "relation/tag"
with open('./output/relation-tag@type.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("relation/tag[@k='type']"))))
with open('./output/relation-tag@name.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("relation/tag[@k='name']"))))
with open('./output/relation-tag@route.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("relation/tag[@k='route']"))))


# Check some "v(alue)" in "way/tag"
with open('./output/way-tag@highway.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("way/tag[@k='highway']"))))
with open('./output/way-tag@name.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("way/tag[@k='name']"))))
with open('./output/way-tag@postcode.txt', 'w') as f:
    f.write(pformat(count_v(tree.findall("way/tag[@k='addr:postcode']"))))
# [Problems 1~3] Same as above


