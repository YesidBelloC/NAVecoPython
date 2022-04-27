##Initialisation

#Librairies
import os
from sys import argv
import json
import csv
import pyjsonviewer
import matplotlib.pyplot as plt
from math import *
import ast

plt.close('all')

#Chemin
os.chdir('C:/Users/crybelloceferin/Documents/MATLAB/Supun/E3Yesid/')

script, seg_speed_ext, seg_slope_ext, seg_slope_sample, constant_slope_ext, duration_user = argv

##Paramètres

# #Segmentation par vitesse
# seg_speed = True
if (seg_speed_ext=='True'):
    seg_speed = True
elif (seg_speed_ext=='False'):
    seg_speed = False

#
# #Segmentation par pente
# seg_slope = True
if (seg_slope_ext=='True'):
    seg_slope = True
elif (seg_slope_ext=='False'):
    seg_slope = False
#
# #Résolution de la segmentation par pente
# seg_slope_sample = 5 en degrees
seg_slope_sample=float(seg_slope_sample)
#
# #Pente constante(moyenne) sur chaque segment
# constant_slope = True
if (constant_slope_ext=='True'):
    constant_slope = True
elif (constant_slope_ext=='False'):
    constant_slope = False
#
# #Temps désirée par le conducteur
# duration_user = 1000
duration_user=float(duration_user)


##Fonctions

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

##Main

data = loadCsv("dataResolE3")
data = data[1:]
#[['Num', 'Lat', 'Lng', 'Dist (m)', 'MaxSpeed (m/s)', 'Slope (rad)', 'Altitude (m)', 'Duree (s)']]

##Segmentation

split_points = [0]

#Segmentation par pente
if(seg_slope):
    ref_slope = float(data[1][5])
    for i in range(2,len(data)):
        slope_temp = data[i][5]
        if (abs(float(slope_temp)-ref_slope)>=seg_slope_sample):
            split_points.append(i)
            ref_slope = float(slope_temp)


#Segmentation par vitesse
if(seg_speed):
    ref_speed = float(data[1][4])
    for i in range(2,len(data)):
        if (float(data[i][4])!=ref_speed):
            split_points.append(i)
            ref_speed = float(data[i][4])

# split_points.append(len(data))

#Segmentation
segmented_header = ['Num', 'Lat', 'Lng', 'Dist (m)', 'MaxSpeed (m/s)', 'Slope (rad)', 'Altitude (m)', 'Duree (s) T','MIN SPEED C','DistSeg','MIN DUREE C']
segmented_data = []
IndiceInit=1
DistInit=0
if(len(split_points)>1):
    #Découpage du trajet en segments
    split_points = list(set(split_points))
    split_points = sorted(split_points)
    for i in range(1,len(data)):
        segmented_data.append(data[i][:])
        if(i==split_points[IndiceInit]):
            if(IndiceInit!=(len(split_points)-1)):
                IndiceInit = IndiceInit+1
            DistInit = float(data[i-1][3])

        segmented_data[i-1][0]=IndiceInit
        if(IndiceInit!=len(split_points)-1):
            DiffDist=float(data[split_points[IndiceInit]-1][3])-DistInit
        else:
            DiffDist=float(data[len(data)-1][3])-DistInit

        if(float(segmented_data[i-1][4])*3.6>= 110):
            segmented_data[i-1].append(80/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(80/3.6))
        elif(float(segmented_data[i-1][4])*3.6>= 70):
            segmented_data[i-1].append(40/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(40/3.6))
        elif(float(segmented_data[i-1][4])*3.6>=50):
            segmented_data[i-1].append(25/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(25/3.6))
        else:
            segmented_data[i-1].append(10/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(10/3.6))
else:
    split_points.append(len(data))
    for i in range(1,len(data)):
        segmented_data.append(data[i][:])
        segmented_data[i-1][0]=IndiceInit
        DiffDist=float(data[len(data)-1][3])-DistInit

        if(float(segmented_data[i-1][4])*3.6>= 110):
            segmented_data[i-1].append(80/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(80/3.6))
        elif(float(segmented_data[i-1][4])*3.6>= 70):
            segmented_data[i-1].append(40/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(40/3.6))
        elif(float(segmented_data[i-1][4])*3.6>=50):
            segmented_data[i-1].append(25/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(25/3.6))
        else:
            segmented_data[i-1].append(10/3.6)
            segmented_data[i-1].append(DiffDist)
            segmented_data[i-1].append(DiffDist/(10/3.6))

segmented_data.insert(0,segmented_header)
writeCsv(segmented_data,"SegmentedData")

