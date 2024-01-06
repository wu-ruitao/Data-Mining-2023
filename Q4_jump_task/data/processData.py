# link: https://snap.stanford.edu/data/loc-gowalla.html
import pandas as pd
import os

output_folder = './output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# make string2Id 从0开始，同时考虑 road.csv and traj.csv
import csv
string2Id = {}
string2Id['[-1,-1]'] = -1
total = 0
with open('road.csv', "r") as f:
    reader = csv.reader(f)
    count = -2
    for row in reader:
        count += 1
        if count == -1:
            continue

        node_list = row[1][1:-1].split(", [")
        start = node_list[0]
        if start not in string2Id:
            string2Id[start] = total
            total += 1
        for node in node_list[1:]:
            node = '[' + node
            if node not in string2Id:
                string2Id[node] = total
                total += 1

with open('all_traj.csv', 'r') as f2:
    reader = csv.reader(f2)
    count = -2
    for row in reader:
        count += 1
        if count == -1:
            continue
        node = row[3]
        if node not in string2Id:
            string2Id[node] = total
            total += 1

print(total)
import json
with open("string2Id.json", "w") as r:
    json.dump(string2Id, r)

# step1: get /data2023.geo

# N = pd.read_csv('./node.csv')
# node = N.drop(['geo_id','type','coordinates','highway'], axis=1)
geo_id = []
coordinates = []

for n, id in string2Id.items():
    geo_id.append(id)
    coordinates.append(n)
# node["geo_id"] = pd.Series(geo_id)
# node["coordinates"] = pd.Series(coordinates)
node = pd.DataFrame({'geo_id': geo_id, 'type': 'Point', 'coordinates': coordinates})

node = node.reindex(columns=['geo_id', 'type', 'coordinates'])
node.to_csv(output_folder + '/data2023.geo', index=False)
print("finish geo")

# step2: get /data2023.usr
traj = pd.read_csv('./all_traj.csv')

usr_info = pd.unique(traj['entity_id'])
usr_info = pd.DataFrame(usr_info, columns=['usr_id'])
usr_info.to_csv(output_folder + '/data2023.usr', index=False)
print("finish usr")

# step3: get /data2023.dyna

dyna = traj.drop(['coordinates'], axis=1)
# dyna = dyna.rename(columns={'id': 'dyna_id'})   # dyna_id
dyna['type'] = 'trajectory'

# 转化 location
location = []
dyna_id = []
for index, row in traj.iterrows():
    dyna_id.append(index)
    coordinate = row['coordinates']
    location_id = string2Id[coordinate]
    location.append(location_id)

dyna['location'] = location
dyna["dyna_id"] = dyna_id
dyna = dyna.reindex(columns=['dyna_id', 'type', 'time', 'entity_id', 'traj_id', 'location', 'current_dis', 'speeds', 'holidays'])
dyna.to_csv(output_folder + '/data2023.dyna', index=False)
print("finish dyna")

# step4: get rel
road = pd.read_csv('road.csv')

rel = road.drop('coordinates', axis=1)
rel = rel.rename(columns={'id': 'rel_id'})
rel['type'] = 'geo'
origin_id = []
destination_id = []

for index, row in road.iterrows():
    coordinate = row['coordinates']
    node_list = row[1][1:-1].split(", [")
    start = node_list[0]
    end = '[' + node_list[-1]

    origin_id.append(string2Id[start])
    destination_id.append(string2Id[end])

rel['origin_id'] = origin_id
rel['destination_id'] = destination_id

rel = rel.reindex(columns=['rel_id', 'type', 'origin_id', 'destination_id', 'highway', 'length', 'lanes', 'tunnel', 'bridge', 'maxspeed', 'width', 'alley', 'roundabout'])
rel.to_csv(output_folder + '/data2023.rel', index=False)
print("finish rel")