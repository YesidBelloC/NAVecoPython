#Auteur : Yesid BELLO
#Date : 30/09/2021
#Programme qui permet de récupérer, à partir d'une adresse de départ et d'arrivée, les coordonnées du départ et de l'arrivée, le trajet, la vitesse et la pente de la route.
# Modifie par: Yesid BELLO

##Initialisation

#Librairies
import os
import json
import csv
import pyjsonviewer
import matplotlib.pyplot as plt
import requests
import polyline
from math import *
import numpy
import time
import googlemaps
import ssl
import time

import pandas as pd
import folium
import statistics
import webbrowser


import urllib.request
import math
import matplotlib.pyplot as plt

plt.close('all')

#Chemin du dossier contenant le programme
os.chdir('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid')

#Url des API utilisées
url_OSM = 'https://overpass-api.de/api/'
# Geometry Long Lat
url_ORS = 'https://api.openrouteservice.org/'

#API key for OpenRouteService
ORS_key = '5b3ce3597851110001cf62487778ecd1fca04f93a0099fa0b1a13240'

#API key for Gooogle Maps
GM_key = 'AIzaSyCKwpcYsXRObqXwtE_3RNt3P-OAuymL4Qs'
client = googlemaps.Client(key=GM_key)

##Paramètres

#Adresses
departure_adress = 'Expleo, Avenue des Prés, Montigny-le-Bretonneux'
arrival_adress = '32, chemin des 2 écoles, 95490 Vauréal'

#Résolution de la distance entre chaque point pour la récupération de l'altitude
distance_sample = 1

DevelopperMode = True

##Fonctions

#Sauvegarder,charger et afficher des données de type Json

def writeJson(jsonVar,jsonName):
    with open('./saved_data/'+jsonName+'.json', 'w') as json_file:
        json.dump(jsonVar, json_file)

def loadJson(jsonName):
    with open('./saved_data/'+jsonName+'.json', 'r') as json_file:
        return json.load(json_file)

def printJson(jsonVar,jsonParams):
    for param in jsonParams:
        print(jsonVar[0])

def jsonViewer(jsonName):
    pyjsonviewer.view_data(json_file='./saved_data/'+jsonName+'.json')

#Sauvegarder,charger des données de type CSV

def writeCsv(csvVar,csvName):
    with open('./'+csvName+'.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file,delimiter=';')
        csv_writer.writerows(csvVar)

def loadCsv(csvName):
    csv_list = []
    with open('./'+csvName+'.csv', 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', quotechar='|')
        for row in csv_reader:
            csv_list.append(row)
        return csv_list

#Obtenir la distance entre deux coordonnées

def getDistance(lat1,lon1,lat2,lon2):
    R = 6371000
    phi1 = lat1*pi/180
    phi2 = lat2*pi/180
    dlat = (lat2-lat1)*pi/180
    dlon = (lon2-lon1)*pi/180

    a = sin(dlat/2)*sin(dlat/2)+cos(phi1)*cos(phi2)*sin(dlon/2)*sin(dlon/2)
    c = 2*atan2(sqrt(a), sqrt(1-a))

    return R * c

def RouteData(departure_long,departure_lat,arrival_long,arrival_lat):
    body = {
        "coordinates":[[departure_long,departure_lat],[2.06307,48.78879],[1.95808,48.80403],[arrival_long,arrival_lat]],
        "language":"fr-fr",
        "units":"m",
        "geometry":"True",
        "elevation":"true",
        "extra_info":["waytype","waycategory"],
        "geometry_simplify":"false",
    }

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': ORS_key,
        'Content-Type': 'application/json; charset=utf-8'
    }
    print("API request route: sending request ...")
    route_raw = requests.post(url_ORS+'v2/directions/driving-car/geojson', json=body, headers=headers)
    print("API request route: OK\n")
    route = route_raw.text
    route = json.loads(route)
    #Sauvegarde du trajet
    #writeJson(route,'route')

    return route['features'][0]

def ElevationData(DataLongLat):
    # print("API request route: sending request ...")
    body = {"format_in":"point","dataset":"srtm","geometry":DataLongLat}
    headers = {
        'Authorization': ORS_key,
    }
    Elevation_raw = requests.post('https://api.openrouteservice.org/elevation/point',json=body,headers=headers)
    # print("API request route: OK\n")
    Elevation = Elevation_raw.text
    Elevation = json.loads(Elevation)

    return Elevation['geometry']['coordinates'][2]

def ElevationVectorData(VectLongLat):
    VectLatLong = [[13.349762, 38.112952],
                   [12.638397, 37.645772]]
    # VectLatLong = new_geometryORM[0]
    print("API request route: sending request ...")
    body = {
      "format_in": "polyline",
      "format_out": "polyline",
      "geometry": VectLongLat
        }
    Elevation_raw = requests.post('https://api.openrouteservice.org/elevation/line',json=body,headers=headers)
    print("API request route: OK\n")
    Elevation = Elevation_raw.text
    Elevation = json.loads(Elevation)

    return Elevation['geometry']

#https://openrouteservice.org/dev/#/api-docs/v2/directions/{profile}/geojson/post
# item=1
# getDistance(route['geometry']['coordinates'][item][1],route['geometry']['coordinates'][item][2],route['geometry']['coordinates'][item+1][1],route['geometry']['coordinates'][item+1][2])

##Main

##-Récupération des coordonnées du départ et de l'arrivée

start = time.process_time()

#Récupération et sauvegarde des coordonnées du départ
print("API request geocode departure: sending request ...")
departure = client.geocode(departure_adress)[0]
print("API request geocode departure: OK")
#writeJson(departure,"departure")
#Récupération et sauvegarde des coordonnées de l'arrivée
print("API request geocode departure: sending request ...")
arrival = client.geocode(arrival_adress)[0]
print("API request geocode departure: OK\n")
#writeJson(arrival,"arrival")


# departure_name = departure['formatted_address']
# departure_long = 48.62713594546965
# departure_lat = 2.247859424399466
#
# arrival_name = arrival['formatted_address']
# arrival_long = 48.625395125545666
# arrival_lat = 2.2483400652800216

departure_name = departure['formatted_address']
departure_long = departure['geometry']['location']['lng']
departure_lat = departure['geometry']['location']['lat']

arrival_name = arrival['formatted_address']
arrival_long = arrival['geometry']['location']['lng']
arrival_lat = arrival['geometry']['location']['lat']

geometry = []

geometry.append([departure_lat,departure_long]);
geometry.append([arrival_lat, arrival_long]);

##-Récupération du trajet

flag=1
while flag:
    try:
        route = RouteData(departure_long,departure_lat,arrival_long,arrival_lat)
        distance = route['properties']['summary']['distance']
        duration = route['properties']['summary']['duration']
        geometry = route['geometry']['coordinates']

        flag=0
        if DevelopperMode:
            print('Meassure correct:')
            print('Distance: '+distance)
            print('Duration: '+duration)
            # print(geometry);
    except:
        #pass
        print('Error in route Data, sleeping 5 secs\n')
        time.sleep(5)

## Coordenates externes

# fields = ['Long', 'Lat', 'Alt']
# df = pd.read_csv('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/Coordenates.csv', sep=';', skipinitialspace=True, usecols=fields)
#
# LatSichr = df.Lat
# LonSichr = df.Long
# elev_list = df.Alt
# geometry = []
# for i in range(len(df.Alt)):
#     geometry.append([df.Lat[i],df.Long[i]])


##Altitude
#https://www.geodose.com/2018/03/create-elevation-profile-generator-python.html
LatSichr = []
LonSichr = []


for i in range(len(geometry)):
    if i == len(geometry)-1:
        n = 0
    else:
        DistTemp = getDistance(geometry[i][1],geometry[i][0],geometry[i+1][1],geometry[i+1][0])
        n = ceil(DistTemp/distance_sample)
    LatSichr.append(geometry[i][1])
    LonSichr.append(geometry[i][0])
    if n>1:
        for j in range(1,n):
            LatSichr.append(geometry[i][1]+(geometry[i+1][1]-geometry[i][1])/n*j)
            LonSichr.append(geometry[i][0]+(geometry[i+1][0]-geometry[i][0])/n*j)

new_geometry = []
for i in range(len(LatSichr)):
    new_geometry.append([LatSichr[i],LonSichr[i]])

new_geometryORM = []
for i in range(len(LatSichr)):
    new_geometryORM.append([LonSichr[i],LatSichr[i]])

#API Google Map altitudes
elevations = []
#Découpage en requêtes de 500 points (max de l'api)
for i in range(ceil(len(new_geometry)/500)):
    if((i+1)*500<=len(new_geometry)):
        elevations_result = client.elevation(new_geometry[i*500:(i+1)*500])
    else:
        elevations_result = client.elevation(new_geometry[i*500:])
    elevations += elevations_result

elev_list = []
ResolHist = []
new_geometry_Final = []

for i in range(len(elevations)):
    elev_list.append(elevations[i]['elevation'])
    ResolHist.append(elevations[i]['resolution'])
    new_geometry_Final.append([elevations[i]['location']['lat'],elevations[i]['location']['lng'],elevations[i]['elevation']])



















