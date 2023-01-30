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

import math

import pandas as pd
import folium
import statistics
import webbrowser


import urllib.request
import math

plt.close('all')

#Chemin du dossier contenant le programme
os.chdir('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/TempsCalcule')

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

DevelopperMode = False

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
        "coordinates":[[departure_long,departure_lat],[arrival_long,arrival_lat]],
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

def Directions(Text):
    text = 'Vélodrome Montigny'
    print("API request route: sending request ...")
    # route_raw = requests.post(url_ORS+'geocode/autocomplete', json=body, headers=headers)
    route_raw = requests.post(url_ORS+'/geocode/search?api_key='+ORS_key+'&text='+text)
    print("API request route: OK\n")
    route = route_raw.text
    route = json.loads(route)
    for i in range(len(route['features'])):
        print(route['features'][i]['properties']['label'])
        print(route['features'][i]['geometry']['coordinates'])

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
    body = {
      "format_in": "polyline",
      "format_out": "polyline",
      "geometry": CoordoneesCompletes
        }
    headers = {
        'Authorization': ORS_key,
    }
    Elevation_raw = requests.post('https://api.openrouteservice.org/elevation/line',json=body,headers=headers)
    Elevation = Elevation_raw.text
    Elevation = json.loads(Elevation)

    return Elevation

#https://openrouteservice.org/dev/#/api-docs/v2/directions/{profile}/geojson/post
# item=1
# getDistance(route['geometry']['coordinates'][item][1],route['geometry']['coordinates'][item][2],route['geometry']['coordinates'][item+1][1],route['geometry']['coordinates'][item+1][2])

##Main

##-Récupération des coordonnées du départ et de l'arrivée
RouteTimeVector = []
TotalTimeVector = []
TotalDistanceVector = []
TotalNodesVector = []

arrival_adressVect = []
# arrival_adressVect.append('Compiègne, 60200') #105
# arrival_adressVect.append('Rhuis, 60410') #97
# arrival_adressVect.append('Noailles, 60430') #85
# arrival_adressVect.append('Dammartin-en-Goële, 77230') #75
# arrival_adressVect.append('Vemars, 7 rue de la Tour, ZA Les Portes de, 95470 Vémars') #65
# arrival_adressVect.append('Conseil Dep Medecin Seine St Denis, 2 Rue Adèle, 93250 Villemomble') #55
# arrival_adressVect.append('Hospital Center Sud Francilien, 40 Avenue Serge Dassault, 91100 Corbeil-Essonnes') #45
# arrival_adressVect.append('Valenton') #35
# arrival_adressVect.append('Rungis, 94150') #25
# arrival_adressVect.append('Bièvres, 91570') #15

arrival_adressVect.append('SQY Ouest Centre Commercial, 1 Av. de la Source de la Bièvre, 78180 Montigny-le-Bretonneux')#1
arrival_adressVect.append('EMITECH, ZA de l"Observatoire, 3 Av. des Coudriers, 78180 Montigny-le-Bretonneux')#2
arrival_adressVect.append('Communauté Emmaüs Trappes, 201 Av. des Bouleaux, 78190 Trappes')#3
arrival_adressVect.append('School Du Lac, Rue des 4 Vents, 78960 Voisins-le-Bretonneux')#4
arrival_adressVect.append('Lidl, 29 Rue des Tilleuls, 78960 Voisins-le-Bretonneux')#5
arrival_adressVect.append('🇫🇷 National Shooting Versailles, 2 Rte de Saint-Cyr, 78000 Versailles')#6
arrival_adressVect.append('JP Beltoise circuit, Av. des Frères Lumière, 78190 Trappes')#7
arrival_adressVect.append('Notre Dame du Grandchamp, 97 Rue Royale, 78000 Versailles')#8
arrival_adressVect.append('Versalles, 78000')#9
arrival_adressVect.append('Piscine Montbauron, 7 Rue Léon Gatin, 78000 Versailles')#10

for lieu in range(len(arrival_adressVect)):
    for rep in range(10):
        startAll = time.time()
        arrival_adress = arrival_adressVect[lieu]

        print(' ')
        print(' ')
        print('Compilation '+str(rep)+'/10 Lugar: '+str(lieu)+'/10')
        print(' ')
        print(' ')

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

        endAll = time.time()
        CalculTimeAll = endAll - startAll
        RouteTimeVector.append(CalculTimeAll)

        print(' Recuperation des donnees partial fini')
        print(' ')
        print('departure :'+departure['formatted_address'])
        print('Arrival :'+arrival['formatted_address'])
        print(' ')
        print('Temps de calcule (Recuperation du Trajet despuis les imports): [s]')
        print(CalculTimeAll)

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


        # # API ORS VECTOR altitudes 1 by 1 -----------------
        # new_geometry_Elev = ElevationVectorData(new_geometryORM[0:4])

        #API ORS Map altitudes
        # elevations = []
        # #Découpage en requêtes de 500 points (max de l'api)
        # for i in range(len(new_geometryORM)):
        #     elevations.append(ElevationData(new_geometryORM[i]))

        # elev_list = []
        # ResolHist = []
        # new_geometry_Final = []
        #
        # for i in range(len(elevations)):
        #     elev_list.append(elevations[i]['elevation'])
        #     ResolHist.append(elevations[i]['resolution'])
        #     new_geometry_Final.append([elevations[i]['location']['lat'],elevations[i]['location']['lng'],elevations[i]['elevation']])


        # # API ORS VECTOR altitudes Vector -----------------
        # CoordoneesCompletes = []
        # for i in range(len(LatSichr)):
        #     CoordoneesCompletes.append([LonSichr[i],LatSichr[i]])
        #
        # elevationsORS = []
        # #Découpage en requêtes de 500 points (max de l'api)
        # for i in range(ceil(len(CoordoneesCompletes)/2000)):
        #     try:
        #         if((i+1)*2000<=len(CoordoneesCompletes)):
        #             elevations_result = ElevationVectorData(CoordoneesCompletes[i*2000:(i+1)*2000])
        #         else:
        #             elevations_result = ElevationVectorData(CoordoneesCompletes[i*2000:])
        #         for j in range(len(elevations_result['geometry'])):
        #             elevationsORS.append(elevations_result['geometry'][j])
        #     except:
        #         print('Error: '+elevations_result['error'])
        #
        # elev_list_ORS = []
        #
        # for i in range(len(elevationsORS)):
        #     elev_list_ORS.append(elevationsORS[i][2])
        #
        # elev_list = elev_list_ORS

        # # #API Google Map altitudes ---------------------------
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

        ##Pente

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
            # print(' ')
            # print(DiffAlt)
            # print(DistNodes)
            # print(DiffAlt/DistNodes)
            # input("Press Enter to continue...")


        ##Vittesse
        # https://giscience.github.io/openrouteservice/documentation/travel-speeds/Travel-Speeds.html

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





        # end = time.process_time()
        endAll = time.time()
        CalculTimeAll = endAll - startAll
        TotalTimeVector.append(CalculTimeAll)
        TotalDistanceVector.append(round(DistCum[len(DistCum)-1]))
        TotalNodesVector.append(len(DistCum))

        print(' Recuperation des donnees fini')
        print(' ')
        print('departure :'+departure['formatted_address'])
        print('Arrival :'+arrival['formatted_address'])
        print(' ')
        print('Distance total: [Km]')
        print(round(DistCum[len(DistCum)-1])/1000)
        print('Nom de point: [-]')
        print(len(Pente))
        print('Temps de calcule (Recuperation du Trajet despuis les imports): [s]')
        print(CalculTimeAll)

        # DistKeyPoints = 0
        # for i in range(len(route['properties']['segments'][0]['steps'])-1):
        #     DistKeyPoints= DistKeyPoints + (route['properties']['segments'][0]['steps'][i]['distance'])
        #     print(DistKeyPoints)

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
            plt.fill_between(DistCum,elev_list,alpha=0.1)
            plt.xlabel("Distance (m)")
            plt.ylabel("Altura (m)")
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

        DataFinal = []

        for i in range(len(LatSichr)-1):
            DataFinal.append([i,LatSichr[i],LonSichr[i],DistCum[i],MaxSpeed[i],Pente[i],elev_list[i],duration])

        DataFinal.insert(0,['Num','Lat','Lng','Dist (m)','MaxSpeed (m/s)','Slope (rad)','Altitude (m)','Duree (s)'])
        writeCsv(DataFinal,"dataResol1_GMaps_38KmRvarVitR1")


        if DevelopperMode:
            points = []
            for i in range(len(LatSichr)-1):
                points.append(tuple([LatSichr[i], LonSichr[i]]))

            map = folium.Map(location=[statistics.mean(LatSichr), statistics.mean(LonSichr)], default_zoom_start=15)

            folium.Marker(
                location=[LatSichr[1], LonSichr[1]],
                popup='Point de depart</b>',
                tooltip = "Point de depart"
                ).add_to(map)

            folium.PolyLine(
                points, color="red",
                weight=2.5,
                opacity=1
                ).add_to(map)

            map.save('mymap.html')
            output_file = "mymap.html"

            webbrowser.open(output_file, new=2)  # open in new tab
        print('----------------- Algorithm ended --------------')

#Chemin du dossier contenant le programme
fields = ['RouteTimeVector','TotalTimeVector','TotalDistanceVector','TotalNodesVector']
df = pd.read_csv('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E1Yesid/TempsCalcule/dataTempsCompil.csv', sep=';', skipinitialspace=True, usecols=fields)
rep = 9

RouteTimeVector = df.RouteTimeVector
TotalTimeVector = df.TotalTimeVector
TotalDistanceVector = df.TotalDistanceVector
TotalNodesVector = df.TotalNodesVector

RouteTimeVectorMean = []
TotalTimeVectorMean = []
TotalDistanceVectorMean = []
TotalNodesVectorMean = []

for i in range(int(len(RouteTimeVector)/10)):
    RouteTimeVectorMean.append(sum(RouteTimeVector[i*(rep+1):(i+1)*(rep+1)-1])/len(RouteTimeVector[i*(rep+1):(i+1)*(rep+1)-1]))
    TotalTimeVectorMean.append(sum(TotalTimeVector[i*(rep+1):(i+1)*(rep+1)-1])/len(TotalTimeVector[i*(rep+1):(i+1)*(rep+1)-1]))
    TotalDistanceVectorMean.append(sum(TotalDistanceVector[i*(rep+1):(i+1)*(rep+1)-1])/len(TotalDistanceVector[i*(rep+1):(i+1)*(rep+1)-1]))
    TotalNodesVectorMean.append(sum(TotalNodesVector[i*(rep+1):(i+1)*(rep+1)-1])/len(TotalNodesVector[i*(rep+1):(i+1)*(rep+1)-1]))

plt.figure(figsize=(10,4))
plt.plot(TotalDistanceVector,TotalTimeVector,'o')
plt.plot(TotalDistanceVectorMean,TotalTimeVectorMean,'o')
plt.plot(TotalDistanceVectorMean,TotalTimeVectorMean)
plt.fill_between(TotalDistanceVector,TotalTimeVector,alpha=0.1)
plt.xlabel("Distance [m]")
plt.ylabel("Temps total (s)")
plt.grid()
plt.show()

plt.figure(figsize=(10,4))
plt.plot(TotalDistanceVector,RouteTimeVector,'o')
plt.plot(TotalDistanceVectorMean,RouteTimeVectorMean,'o')
plt.plot(TotalDistanceVectorMean,RouteTimeVectorMean)
plt.fill_between(TotalDistanceVector,RouteTimeVector,alpha=0.1)
plt.xlabel("Distance [m]")
plt.ylabel("Temps route (s)")
plt.grid()
plt.show()

plt.figure(figsize=(10,4))
plt.plot(TotalNodesVector,TotalTimeVector,'o')
plt.fill_between(TotalNodesVector,TotalTimeVector,alpha=0.1)
plt.xlabel("Nodes")
plt.ylabel("Temps total (s)")
plt.grid()
plt.show()

plt.figure(figsize=(10,4))
plt.plot(TotalNodesVector,RouteTimeVector,'o')
plt.fill_between(TotalNodesVector,RouteTimeVector,alpha=0.1)
plt.xlabel("Nodes")
plt.ylabel("Temps route (s)")
plt.grid()
plt.show()


DataFinalTemp = []

for l in range(len(RouteTimeVector)):
    DataFinalTemp.append([RouteTimeVector[l],TotalTimeVector[l],TotalDistanceVector[l],TotalNodesVector[l]])

DataFinalTemp.insert(0,['RouteTimeVector','TotalTimeVector','TotalDistanceVector','TotalNodesVector'])
writeCsv(DataFinalTemp,"dataTempsCompilCourt")










