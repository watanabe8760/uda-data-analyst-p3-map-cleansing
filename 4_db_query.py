from pymongo import MongoClient
import json
from bson import json_util
from pprint import pprint
from pprint import pformat
from pandas import DataFrame
import calendar
import seaborn as sns
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# Connect to "singapore" collection in "map" database
mp = MongoClient('localhost:27017').map
sg = mp.singapore
# Clear data in singapore
mp.drop_collection("singapore")
# Import JSON file to "singapore" collection
with open("./input/singapore.json", "r") as f:
    sg.insert_many(json.load(f, object_hook=json_util.object_hook))


# Show sample records
pprint(sg.find_one({"xml" : "osm"}))
pprint(sg.find_one({"xml" : "bounds"}))
pprint(list(sg.find({"xml" : "node"})[:3]))
pprint(list(sg.find({"xml" : "relation"})[:3]))
pprint(list(sg.find({"xml" : "way"})[:3]))

pprint(list(sg.aggregate([{"$match" : {"$and" : [{"xml" : "node"}, \
                                                 {"tag" : {"$exists" : True}}]}}, \
                          {"$sample" : {"size" : 3}}])))
pprint(list(sg.aggregate([{"$match" : {"$and" : [{"xml" : "relation"}, \
                                                 {"tag" : {"$exists" : True}}, \
                                                 {"member" : {"$exists" : True}}]}}, \
                          {"$sample" : {"size" : 3}}])))
pprint(list(sg.aggregate([{"$match" : {"$and" : [{"xml" : "way"}, \
                                                 {"nd" : {"$exists" : True}}, \
                                                 {"tag" : {"$exists" : True}}]}}, \
                          {"$sample" : {"size" : 3}}])))

# Count number of records (parent elements)
print "Total   :", sg.count()
print "osm     :", sg.count({"xml" : "osm"})
print "bounds  :", sg.count({"xml" : "bounds"})
print "node    :", sg.count({"xml" : "node"})
print "relation:", sg.count({"xml" : "relation"})
print "way     :", sg.count({"xml" : "way"})


def count_child_tag(collection, parent_tag, child_tag):
    """
    Counts number of child elements in a specified parent element.
    """
    pipeline = [{"$match" : {"$and" : [{"xml" : parent_tag}, \
                                       {child_tag : {"$exists" : True}}]}}, \
                {"$unwind" : "$" + child_tag}, \
                {"$group" : {"_id" : None, \
                             "count" : {"$sum" : 1}}}, \
                {"$project" : {"_id" : False, "count" : True}}]
    return list(collection.aggregate(pipeline))[0]

count_child_tag(sg, "node", "tag")
count_child_tag(sg, "relation", "member")
count_child_tag(sg, "relation", "tag")
count_child_tag(sg, "way", "nd")
count_child_tag(sg, "way", "tag")
#node/tag        {u'count': 80376} <- 80464     : Diff = -88 eqauls node-tag@postcode-invalid.log
#relation/member {u'count': 69885} <- 69885     : No diff
#relation/tag    {u'count': 6191}  <- 6191      : No diff
#way/nd          {u'count': 1146529} <- 1146529 : No diff
#way/tag         {u'count': 366132} <- 375303   : Diff = -9171 equals way-tag@postcode-invalid.log


def count_tag_val(collection, parent_tag, key):
    """
    Aggregates and counts "v(alue)" of */tag in a specified parent.
    
    Args:
        collection: A collection object.
        parent_tag: "node", "relation" or "way".
        key: "k(ey)" of tag element.
    """
    pipeline = [{"$match" : {"$and" : [{"xml" : parent_tag}, \
                                       {"tag" : {"$exists" : True}}]}}, \
                {"$unwind" : "$tag"}, \
                {"$match" : {"tag.k" : key}}, \
                {"$group" : {"_id" : "$tag.v", \
                             "count" : {"$sum" : 1}}}, \
                {"$sort" : {"count" : -1}}]
    return list(collection.aggregate(pipeline))

with open('./output/node-tag@name_db.txt', 'w') as f:
    f.write(pformat(count_tag_val(sg, "node", "name")))
with open('./output/node-tag@postcode_db.txt', 'w') as f:
    f.write(pformat(count_tag_val(sg, "node", "addr:postcode")))
with open('./output/way-tag@postcode_db.txt', 'w') as f:
    f.write(pformat(count_tag_val(sg, "way", "addr:postcode")))


# Number of unique users
len(list(sg.distinct("user")))

# Number of contribution per user
users = DataFrame(list( \
            sg.aggregate([{"$group" : {"_id" : "$user", \
                                       "count" : {"$sum" : 1}}}, \
                          {"$sort" : {"count" : -1}}])))
# Barplot of user contribution
sns.barplot(x="count", y="_id", data=users, orient="h", color="lightblue")
sns.barplot(x="count", y="_id", data=users, orient="h", color="lightblue", log=True)



# When was each element registered or updated?
# (Aggregattion by year and month of timestamp)
history = DataFrame(list( \
             sg.aggregate([{"$match" : {"$or" : [{"xml" : "node"}, \
                                                 {"xml" : "relation"}, \
                                                 {"xml" : "way"}]}}, \
                           {"$group" : {"_id" : {"year" : {"$year" : "$timestamp"}, \
                                                 "month" : {"$month" : "$timestamp"}}, \
                                       "count" : {"$sum" : 1}}}, 
                           {"$project" : {"year" : "$_id.year",
                                          "month" : "$_id.month",
                                          "_id" : 0, 
                                          "count" : 1}}, \
                           {"$sort" : {"month" : 1, 
                                       "year" : 1}}])))
#history["Month"] = [calendar.month_name[m][:3] for m in history["month"]]
#history["ym"] = [str(y) for y in history["year"]] + history["Month"]
# Barplot of history
sns.barplot(x="count", y="year", data=history, orient="h", color="lightblue", errcolor="blue")



# Project node location (longitude / latitude) on map
# Get the map coordinate from bounds tag
bounds = sg.find_one({"xml" : "bounds"})
# Create ajustment terms for the map coordinate
lon_ajst = (bounds["maxlon"] - bounds["minlon"]) / 3
lat_ajst = (bounds["maxlat"] - bounds["minlat"]) / 3
# Get longitude and latitude from node tags
node = DataFrame(list(sg.aggregate([{"$match" : {"xml" : "node"}}, \
                                    {"$project" : {"lat" : 1, "lon" : 1}}])))

plt.figure(figsize=(12, 8))
m = Basemap(projection='merc', resolution="f", 
            llcrnrlon=bounds["minlon"]+lon_ajst, llcrnrlat=bounds["minlat"]+lat_ajst,
            urcrnrlon=bounds["maxlon"]-lon_ajst, urcrnrlat=bounds["maxlat"]-lat_ajst)
m.drawcoastlines()
#m.drawcountries()
m.fillcontinents(color='burlywood')
xpt, ypt = m(list(node["lon"]), list(node["lat"]))
m.plot(xpt, ypt, 'g.', alpha=0.01)
plt.show()
# [Reference] https://github.com/BillMills/python-mapping

# Jointplot of location
sns.jointplot(x="lon", y="lat", data=node, kind="kde", space=0, color="g", size=8, \
              xlim=(bounds["minlon"]+lon_ajst, bounds["maxlon"]-lon_ajst), \
              ylim=(bounds["minlat"]+lat_ajst, bounds["maxlat"]-lat_ajst))
# [Reference] http://stackoverflow.com/questions/23969619/plotting-with-seaborn-using-the-matplotlib-object-oriented-interface
