import os

path = r'D:\papers\UNIVERSITY\PHYS-ASTRO-3A\Workterm Report\Tables'

world_data = {}

for filename in os.listdir(path):
    if filename.endswith('.py') or filename == 'Collected_Data.csv': continue

    location = (filename.replace('_XCO2.csv', '')).replace('_', ' ')

    table_data = ''

    file = open(os.path.join(path, filename), 'r')
    for line in file: table_data += line
    file.close()

    world_data[location] = table_data

file = open(os.path.join(path, 'Collected_Data.csv'), 'w')
for key in world_data.keys():
    file.write(key + '\n')
    file.write(world_data[key] + '\n')

file.close()
