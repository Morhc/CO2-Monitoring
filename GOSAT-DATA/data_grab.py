import h5py, os, datetime, simplekml
import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



focuses = ['North America', 'Global', 'Western Hemisphere', 'Northern Hemisphere', 'Eastern Hemisphere', 'Southern Hemisphere']

#bboxfinder.com
def within(area, lat, lon):

    in_area = False
    p = Point(lon,lat)

    if area == 'North America':
        a = Polygon([(-171.0352, 84.8658), (-171.0352, -6.3153), (-111.1816, -6.3163), (-86.1328, 1.1425), (-60.1172, 22.106), (-16.875, 71.8563), (-6.3281, 84.8658)])
        in_area = a.contains(p)

    elif area == 'South America':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Europe':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Africa':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Asia':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Oceania':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Antarctica':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'China':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'USA':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Russia':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'India':
        a = Polygon([])
        in_area = a.contains(p)

    elif area == 'Global':
        in_area = True

    elif area == 'Northern Hemisphere':
        in_area = lat > 0

    elif area == 'Southern Hemisphere':
        in_area = lat < 0

    elif area == 'Eastern Hemisphere':
        in_area = lon > 0

    elif area == 'Western Hemisphere':
        in_area = lon < 0

    return in_area

path = os.path.dirname(os.path.abspath(__file__))

for focus in focuses:

    print(focus)

    data = [[] for i in range(12)]

    kml = simplekml.Kml()

    for f in sorted(os.listdir(path)):
        if not f.endswith('.tar'): continue

        file = h5py.File(os.path.join(path, f), 'r')

        latitudes = np.array(file['Data/geolocation/latitude'])
        longitudes = np.array(file['Data/geolocation/longitude'])

        footprint_lat = np.array(file['Data/geolocation/footPrintLatitude'])
        footprint_lon = np.array(file['Data/geolocation/footPrintLongitude'])

        landfraction = np.array(file['Data/geolocation/landFraction'])

        snr = np.array(file['scanAttribute/qualityInformation/SNR'])

        xco2 = np.array(file['Data/mixingRatio/XCO2BiasCorrected'])
        xco2_err = np.array(file['Data/mixingRatio/XCO2BiasCorrectedError'])

        edit, err, num_obs, flat, flon = [], [], 0, [], []
        for i in range(len(xco2)):
            if landfraction[i] >= 60 and within(focus, latitudes[i], longitudes[i]):
                edit.append(xco2[i])
                err.append(xco2_err[i])
                flat.append(footprint_lat[i])
                flon.append(footprint_lon[i])
                num_obs += 1


                ob = [(lon, lat) for lon, lat in zip(footprint_lon[i], footprint_lat[i])]

                pol = kml.newpolygon(name = '{}\n{}\n'.format(xco2[i], xco2_err[i]), outerboundaryis = ob)
                pol.style.linestyle.width = 5
                if xco2[i] < 400:
                    pol.style.linestyle.color = simplekml.Color.green
                    pol.style.polystyle.color = simplekml.Color.green
                if xco2[i] < 415:
                    pol.style.linestyle.color = simplekml.Color.yellow
                    pol.style.polystyle.color = simplekml.Color.yellow
                else:
                    pol.style.linestyle.color = simplekml.Color.red
                    pol.style.polystyle.color = simplekml.Color.red




        i = int(f[f.find('_')+5:f.find('_')+7]) - 1
        data[i].append(('{}-{}'.format(f[f.find('_')+1:f.find('_')+5], f[f.find('_')+5:f.find('_')+7]), round(np.mean(edit), 4), \
                        round(np.mean(err), 4), round(np.min(edit), 4), round(np.max(edit), 4), num_obs, flon, flat))



    kml.save(os.path.join(path, '../KML-DATA/{}_XCO2.kml').format(focus.replace(' ', '_')))

    fig, ax = plt.subplots(4, 3, figsize=(12,9))
    plt.subplots_adjust(hspace=0.33)

    m = 0
    for i in range(4):
        for j in range(3):

            ax[i,j].plot([tup[1] for tup in data[m]], zorder = 0)
            ax[i,j].errorbar([i for i in range(len(data[m]))], [tup[1] for tup in data[m]], yerr = [tup[2] for tup in data[m]], fmt = 'o', color='r', capsize = 4, zorder = 1)
            month = datetime.date(1900, m+1, 1).strftime('%B')
            ax[i,j].set_title(month)
            ax[i,j].set_ylim(396, 417)

            ax[i,j].set_xticklabels(['']+[year[:year.find('-')] for year in [tup[0] for tup in data[0]]])
            ax[i,j].set_yticks([400,405,410,415])

            m += 1

    plt.suptitle('{} Mean XCO2'.format(focus))
    plt.savefig(os.path.join(path, '../Plots/{}_XCO2.png').format(focus.replace(' ', '_')))

    record = open(os.path.join(path, '../Tables/{}_XCO2.csv').format(focus.replace(' ', '_')), 'w')
    record.write('Year,Num Obs,Mean XCO2,Min XCO2,Max XCO2\n')
    for k in range(len(data[0])):

        year = data[0][k][0][:data[0][k][0].find('-')]
        annual_mean = np.mean([data[j][k][1] for j in range(12)])
        annual_min = np.min([data[j][k][3] for j in range(12)])
        annual_max = np.max([data[j][k][4] for j in range(12)])
        annual_obs = sum([data[j][k][5] for j in range(12)])

        record.write('{},{},{},{},{}\n'.format(year, annual_obs, annual_mean, annual_min, annual_max))

    record.close()
