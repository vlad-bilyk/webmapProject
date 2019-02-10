import folium
import geopy
import certifi
import ssl
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import random

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx
geolocator = Nominatim(user_agent="specify_your_app_name_here")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

year = str(input("Enter the year: "))

def reading_func(path):
    dct = dict()
    with open(path, errors='ignore') as file:
        lines = file.readlines()
    count = 0
    for line in lines:
        if "({}".format(year) in line:
            count += 1
            if count > 10000:
                break
            print(line)
            while "(" in line and ")" in line:
                ind1, ind2 = line.index("("), line.index(")")
                word = line[ind1:ind2 + 1]
                line = line.replace(word, "").strip()

            while "{" in line and "}" in line:
                ind1, ind2 = line.index("{"), line.index("}")
                word = line[ind1:ind2 + 1]
                line = line.replace(word, "").strip()
            try:
                name = line[:line.index("\t")]
            except:
                continue

            location = line.replace(name, "").strip().split(",")[0]

            if name not in dct:
                dct[name] = [location]
            elif location not in dct[name]:
                dct[name].append(location)


    return dct


def color_picker():
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
              'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
              'gray', 'black', 'lightgray']
    return random.choice(colors)


def map_builder(locations):
    map = folium.Map(location=[48.314775, 25.082925] ,zoom_start=2)
    fg_movies = folium.FeatureGroup(name="Movies filmed in {}. (Name, Location)".format(year))
    counter = 0

    for key in tqdm(locations.keys()):
        for value in locations[key]:
            if counter > 100:
                break
            try:
                location = geolocator.geocode(value)
                location_lst = [location.latitude, location.longitude]
                fg_movies.add_child(folium.Marker(location=location_lst,
                                                  popup="{}, {}".format(key, value),
                                                  icon=folium.Icon(color=color_picker())))
                counter += 1
            except:
                counter += 1
                continue

    fg_pp = folium.FeatureGroup(name="Population")
    fg_pp.add_child(folium.GeoJson(data=open('../docs/world.json', 'r',
                                             encoding='utf-8-sig').read(),
                                   style_function=lambda x: {'fillColor': 'green'
                                   if x['properties']['POP2005'] < 10000000
                                   else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
                                   else 'red'}))


    map.add_child(fg_pp)
    map.add_child(fg_movies)
    map.add_child(folium.LayerControl())
    map.save('Map_2.html')


locs = reading_func("../docs/locations.list")
print(map_builder(locs))