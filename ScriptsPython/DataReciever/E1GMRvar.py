#Auteur : Yesid BELLO
#Date : 30/09/2021
#Programme qui permet de récupérer, à partir d'une adresse de départ et d'arrivée, les coordonnées du départ et de l'arrivée, le trajet, la vitesse et la pente de la route.
# Modifie par: Yesid BELLO

##Initialisation
import time
StartMessure = time.time()

#Librairies
import os
import json
import csv
import pyjsonviewer
import requests
import polyline
from math import *
import numpy
import time
import googlemaps
import ssl
import time
import statistics
import math
import pandas as pd
import folium
import statistics
import webbrowser
import urllib.request
import matplotlib.pyplot as plt

plt.close('all')

#Chemin du dossier contenant le programme
os.chdir('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/EnergieComparisson')

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
# arrival_adress = '32, chemin des 2 écoles, 95490 Vauréal'
arrival_adress = 'Piscine Montbauron, 7 Rue Léon Gatin, 78000 Versailles'

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

def RouteData1(Coordonees):
    body = {
        "coordinates":Coordonees,
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

def ElevationVectorData(CoordoneesCompletes):
    # VectLatLong = new_geometryORM[0]
    print("API request route: sending request ...")
    body = {
      "format_in": "polyline",
      "format_out": "polyline",
      "geometry": CoordoneesCompletes[0:2000]
        }
    headers = {
        'Authorization': ORS_key,
    }
    Elevation_raw = requests.post('https://api.openrouteservice.org/elevation/line',json=body,headers=headers)
    print("API request route: OK\n")
    Elevation = Elevation_raw.text
    Elevation = json.loads(Elevation)

    return Elevation


EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time imports: '+str(CalculMesure))

#https://openrouteservice.org/dev/#/api-docs/v2/directions/{profile}/geojson/post
# item=1
# getDistance(route['geometry']['coordinates'][item][1],route['geometry']['coordinates'][item][2],route['geometry']['coordinates'][item+1][1],route['geometry']['coordinates'][item+1][2])

##Main

##-Récupération des coordonnées du départ et de l'arrivée

# start = time.process_time()
StartMessure = time.time()

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

EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time coordonees: '+str(CalculMesure))

## Coordenates externes

# fields = ['Long', 'Lat', 'Alt']
# df = pd.read_csv('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/DataReciever/Coordenates.csv', sep=';', skipinitialspace=True, usecols=fields)
#
# LatSichr = df.Lat
# LonSichr = df.Long
# elev_list = df.Alt
#
# DownSample = math.ceil(len(LatSichr)/40) # 50 Puntos Maximo
#
# Coordonees = []
# for i in range(len(LatSichr)):
#     if math.remainder(i,DownSample)==0:
#         Coordonees.append([LatSichr[i],LonSichr[i]])

##-Récupération du trajet

StartMessure = time.time()

flag=1
while flag:
    try:
        route = RouteData(departure_long,departure_lat,arrival_long,arrival_lat)
        # route = RouteData1(Coordonees)
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
        print('Error in route Data, sleeping 1 secs\n')
        time.sleep(1)

EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time route: '+str(CalculMesure))

## Coordenates externes

# fields = ['Long', 'Lat', 'Alt']
# df = pd.read_csv('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/DataReciever/Coordenates.csv', sep=';', skipinitialspace=True, usecols=fields)
#
# LatSichr = df.Lat
# LonSichr = df.Long
# elev_list = df.Alt
# geometry = []
# for i in range(len(df.Alt)):
#     geometry.append([df.Lat[i],df.Long[i]])


##Altitude
#https://www.geodose.com/2018/03/create-elevation-profile-generator-python.html

StartMessure = time.time()
StartMessureInt = time.time()

KeyPoints = len(route['properties']['segments'][0]['steps'])
KeySegments = len(route['properties']['segments'])
KeyPointsTemp = 0
KeySegmentsTemp = 0
TotalDist = 0
j = 0

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

EndMessureInt = time.time()
CalculMesureInt= EndMessureInt - StartMessureInt
print('Time Add points: '+str(CalculMesureInt))

# new_geometryORM = []
# for i in range(len(LatSichr)):
#     new_geometryORM.append([LonSichr[i],LatSichr[i]])
#
#
#
# #API ORS VECTOR altitudes ------------------------
#
# CoordoneesCompletes = []
# for i in range(len(LatSichr)):
#     CoordoneesCompletes.append([LonSichr[i],LatSichr[i]])
#
# elevationsORS = []
# #Découpage en requêtes de 500 points (max de l'api)
# for i in range(ceil(len(CoordoneesCompletes)/2000)):
#     try:
#         if((i+1)*2000<=len(CoordoneesCompletes)):
#             elevations_resultORS = ElevationVectorData(CoordoneesCompletes[i*2000:(i+1)*2000])
#         else:
#             elevations_resultORS = ElevationVectorData(CoordoneesCompletes[i*2000:])
#         for j in range(len(elevations_resultORS)):
#             elevationsORS.append(elevations_resultORS['geometry'][j])
#     except:
#         print('Error: '+elevations_resultORS['error'])
#         break
#
# elev_list_ORS = []
#
# for i in range(len(elevationsORS)):
#     elev_list_ORS.append(elevationsORS[i][2])

#API Google Map altitudes -------------------------------
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

EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time altitude: '+str(CalculMesure))

## Coordenates externes Imposéee

# fields = ['Long', 'Lat', 'Alt']
# df = pd.read_csv('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/DataReciever/Coordenates.csv', sep=';', skipinitialspace=True, usecols=fields)
#
# LatSichr = df.Long
# LonSichr = df.Lat
# elev_list = df.Alt
#
# df.Lat

##Pente

StartMessure = time.time()


DistNodesV = []
DiffaltV  = [0]
Pente = [0]
DistCum = [0]
DistInit = 0
VarTemp = 0

for i in range(len(LatSichr)-1):
    DistNodes=getDistance(LatSichr[i],LonSichr[i],LatSichr[i+1],LonSichr[i+1])
    DiffAlt = (elev_list[i+1]-elev_list[i])
    DistNodesV.append(DistNodes)
    DistCum.append(DistInit+DistNodes)
    DistInit=DistInit+DistNodes
    if (abs(DiffAlt/DistNodes))>0.5:
        VarTemp = VarTemp
        DiffaltV.append(DiffAlt)
        Pente.append(math.asin(VarTemp)) #Radians
    else:
        VarTemp = DiffAlt/DistNodes
        DiffaltV.append(DiffAlt)
        Pente.append(math.asin(VarTemp)) #Radians
    print(' ')
    # print(DiffAlt)
    # print(DistNodes)
    # print(DiffAlt/DistNodes)
    # input("Press Enter to continue...")

EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time pente: '+str(CalculMesure))

##Vittesse
# https://giscience.github.io/openrouteservice/documentation/travel-speeds/Travel-Speeds.html

StartMessure = time.time()


MaxSpeed = []
DistKeyPoints = route['properties']['segments'][0]['steps'][0]['distance']
# DistKeyPointsVect = []
# DistTempVect = []
KeyPoints = len(route['properties']['segments'][0]['steps'])
KeySegments = len(route['properties']['segments'])
KeyPointsTemp = 0
KeySegmentsTemp = 0

TotalDist = 0
i = 0
# for i in range(len(LatSichr)-1):
DistNoeuds = []
for i in range(len(route['properties']['segments'])):
    for j in range(len(route['properties']['segments'][i]['steps'])):
        DistNoeuds.append(route['properties']['segments'][i]['steps'][j]['distance'])
        print(route['properties']['segments'][i]['steps'][j]['distance'])

plt.figure(figsize=(10,4))
plt.plot(range(len(DistNoeuds)),DistNoeuds)
plt.xlabel("Noeuds (-)")
plt.ylabel("Distance (m)")
plt.grid()
plt.show()

while 1 :
    DistTemp = route['properties']['segments'][KeySegmentsTemp]['steps'][KeyPointsTemp]['distance']
    DuraTemp = route['properties']['segments'][KeySegmentsTemp]['steps'][KeyPointsTemp]['duration']

    if(DuraTemp==0):
        KeyPointsTemp = KeyPointsTemp + 1
        # DistKeyPointsVect.append(DistKeyPoints)
        # DistTempVect.append(DistTemp)
    else:
        MaxSpeedTemp = (DistTemp/DuraTemp)
        MaxSpeed.append(MaxSpeedTemp)

        if(DistCum[i]>=DistKeyPoints+TotalDist):
            TotalDist = TotalDist+DistKeyPoints
            KeyPointsTemp = KeyPointsTemp + 1
            DistKeyPoints = DistKeyPoints + route['properties']['segments'][KeySegmentsTemp]['steps'][KeyPointsTemp]['distance']
            # DistKeyPointsVect.append(DistKeyPoints)
            # DistTempVect.append(DistTemp)

        i=i+1

    if(KeyPointsTemp==KeyPoints):
        KeyPointsTemp = 0
        KeySegmentsTemp = KeySegmentsTemp+1
        KeyPoints = len(route['properties']['segments'][KeySegmentsTemp]['steps'])

    if (len(MaxSpeed)==len(LatSichr)) :
        break


EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time vitesse: '+str(CalculMesure))


# end = time.process_time()
# CalculTime = end - start

print(' Recuperation des donnees fini')
print(' ')
print('departure :'+departure['formatted_address'])
print('Arrival :'+arrival['formatted_address'])
print(' ')
print('Distance total: [m]')
print(round(DistCum[len(DistCum)-1]))
print('Nom de point: [-]')
print(len(Pente))
print('Temps de calcule: [s]')
print(CalculTime)

# DistKeyPoints = 0
# for i in range(len(route['properties']['segments'][0]['steps'])-1):
#     DistKeyPoints= DistKeyPoints + (route['properties']['segments'][0]['steps'][i]['distance'])
#     print(DistKeyPoints)

## Analyse

if(len(elev_list)==len(elev_list_ORS)):
    ErreurAltitude=[]
    for i in range(len(elev_list)):
        ErreurAltitude.append(elev_list[i]-elev_list_ORS[i])

## Plots

if DevelopperMode:
    plt.figure(figsize=(10,4))
    plt.plot(range(len(DistNodesV)),DistNodesV)
    plt.fill_between(range(len(DistNodesV)),DistNodesV,alpha=0.1)
    plt.xlabel("Nodes")
    plt.ylabel("Distance (m)")
    plt.grid()
    plt.show()

    plt.figure(figsize=(10,4))
    plt.plot(range(len(MaxSpeed)),MaxSpeed)
    plt.fill_between(range(len(MaxSpeed)),MaxSpeed,alpha=0.1)
    plt.xlabel("Nodes (-)")
    plt.ylabel("Vitesse Max (m/s)")
    plt.grid()
    plt.show()

    plt.figure(figsize=(10,4))
    plt.plot(DistCum,elev_list)
    if(len(elev_list)==len(elev_list_ORS)):
        plt.plot(DistCum,elev_list_ORS)
    plt.fill_between(DistCum,elev_list,alpha=0.1)
    plt.xlabel("Distance (m)")
    plt.ylabel("Altura (m)")
    if(len(elev_list)==len(elev_list_ORS)):
        plt.legend(['GM','ORS'])
    plt.grid()
    plt.show()

    if(len(elev_list)==len(elev_list_ORS)):
        plt.figure(figsize=(10,4))
        plt.plot(DistCum,ErreurAltitude)
        plt.fill_between(DistCum,ErreurAltitude,alpha=0.1)
        plt.xlabel("Distance (m)")
        plt.ylabel("Erreur GM-ORS (m)")
        plt.legend(['Moy: '+str(round(statistics.mean(ErreurAltitude),2))+'\n'+'Max: '+str(round(max(ErreurAltitude),2))+'\n'+'Min: '+str(round(min(ErreurAltitude),2))])
        plt.grid()
        plt.show()

    plt.figure(figsize=(10,4))
    plt.plot(DistCum,DiffaltV)
    plt.fill_between(DistCum,DiffaltV,alpha=0.1)
    plt.xlabel("Distance (m)")
    plt.ylabel("Diff Altura (m)")
    plt.grid()
    plt.show()

    plt.figure(figsize=(10,4))
    plt.plot(DistCum,Pente)
    plt.fill_between(DistCum,Pente,alpha=0.1)
    plt.xlabel("Distance (m)")
    plt.ylabel("Pente (°)")
    plt.grid()
    plt.show()

StartMessure = time.time()

DataFinal = []

for i in range(len(LatSichr)-1):
    DataFinal.append([i,LatSichr[i],LonSichr[i],DistCum[i],MaxSpeed[i],Pente[i],elev_list[i],duration])

DataFinal.insert(0,['Num','Lat','Lng','Dist (m)','MaxSpeed (m/s)','Slope (rad)','Altitude (m)','Duree (s)'])
writeCsv(DataFinal,"dataResol1_GMaps_38KmRvarVitR1TEST")

EndMessure = time.time()
CalculMesure= EndMessure - StartMessure
print('Time sauvegardement: '+str(CalculMesure))

points = []
for i in range(len(LatSichr)-1):
    points.append(tuple([LatSichr[i], LonSichr[i]]))

map = folium.Map(location=[statistics.mean(LatSichr), statistics.mean(LonSichr)], default_zoom_start=15)

folium.Marker(
    location=[LatSichr[1], LonSichr[1]],
    popup='Point de depart</b>',
    tooltip = "Point de depart"
    ).add_to(map)

folium.Marker(
    location=[LatSichr[len(LatSichr)-1], LonSichr[len(LonSichr)-1]],
    popup='Point d"arrive'+'Distance: '+str(round(DistCum[len(DistCum)-1],2)),
    tooltip = "Point d'arrive"+'Distance: '+str(round(DistCum[len(DistCum)-1],2))
    ).add_to(map)

folium.PolyLine(
    points, color="red",
    weight=2.5,
    opacity=1
    ).add_to(map)

map.save('mymap.html')
output_file = "mymap.html"

webbrowser.open(output_file, new=2)  # open in new tab



















