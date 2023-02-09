import random as rdm
import math
import numpy as np
import matplotlib.pyplot as plt
#---------------------------------------------------------------------------------------------------


"""  Entrée : Tableau 2 dimensions : [ Distance (m), Vmax (m/s) ] ( Sortie de la segmentation.csv) 
     Sortie : retourne 3 vecteurs: 
        * un pour les points où on coupe, ie: où la vitesse change 
        * un 2eme vecteur de toutes les vitesses sur notre trajet 
        * un 3eme pour les distances des differents segments où V est constant ==> il aura donc la meme 
            taille que le vecteur précédent 
"""        

def speed_and_dist_cut(_dist_and_speed):
    
    _speeds = []
    dist_segment_speed = []
    cut_points = []
 
    # premiere vitesse max
    V = _dist_and_speed[0][1] 
    _speeds.append(V)
    
    for i in range(1, len(_dist_and_speed)):
            if(_dist_and_speed[i][1] != V):
                cut_points.append(i)
                V = _dist_and_speed[i][1]
                _speeds.append(V)     
                # ajouter la distance du segment (la où v = cst)
                if(len(dist_segment_speed) > 0):
                    dist_segment_speed.append(_dist_and_speed[i-1][0] - _dist_and_speed[cut_points[-2]-1][0] )  
                else:
                    dist_segment_speed.append(_dist_and_speed[i-1][0]) 
   
    #ajouter la distance du dernier segment s'il y'a plus de 2 limitations de vitesse
    if len(_speeds) > 1:    
        dist_segment_speed.append(_dist_and_speed[len(_dist_and_speed)-1][0] - _dist_and_speed[cut_points[-1]-1][0] ) 
    
    # s'il y aune seule vitesse limite la distance du segment == la distance totale 
    else: # cad : len(dist_segment_speed) == 0 :
        dist_segment_speed.append(_dist_and_speed[-1][0]) 
        
           
    return cut_points, _speeds, dist_segment_speed


#---------------------------------------------------------------------------------------------------

"""
    Entrée :  [Amin (m), Amax (m/s), [Vmax]]    
    Sortie :  2 tableaux: 
    *un vecteur pour les accelerations possibles, avec le 'pas' qu'on a choisi et les 
        limites 'a_min' et 'a_max 
    * une matrice qui contient la vitesse min et vitesse max pour tout le trajet [ [Vmin_1, Vmax_1],
                                                                                   [Vmin_2, Vmax_2],
                                                                                   ...] en (m/s)
"""
def split_speed_and_acceleration(_Acceleration_min, _Acceleration_max, _speeds):
    
    vectors_speeds = []    
    
    subdivision_acceleration = 50
    step_acceleration = (_Acceleration_max - _Acceleration_min)/subdivision_acceleration
    
    vector_acceleration = [ i*step_acceleration for i in range(-round(subdivision_acceleration/2) , round(subdivision_acceleration/2) +1 ) ]
    
    for i in range(0, len(_speeds)):
        #===============================================================================    
        # initialisation des vitesses min a avoir en fonction des limitations de vitesse
        if _speeds[i] <= 8.33 and _speeds[i] >= 7: # >= 5.55: # 30 kmh --> Vmin = 20 kmh
            tmp = [5.55]        
        elif _speeds[i] <= 13.88 and _speeds[i] >= 10: # >= 8.33 # 50 kmh --> Vmin = 30 kmh
            tmp = [8.33]
        elif _speeds[i] <= 25 and _speeds[i] >= 15: # >= 13.88  # 90 kmh --> Vmin = 50 kmh
            tmp = [13.88]
        elif _speeds[i] > 25 :   # 110 ou 130 kmh --> Vmin = 80 kmh
            tmp = [22.22]    
        else:
            tmp = [ _speeds[i]/4 ] # si une limitation de vitesse est "trop petite" (on met Vmin = Vmax/4 kmh)
        if( _speeds[i] not in tmp ):
            tmp.append( _speeds[i] )
        #i += 1 
        vectors_speeds.append( tmp ) 
    
        

    return vector_acceleration, vectors_speeds

#=======================================================================================

"""
    Entrée :  [[Amin (m), Amax (m/s)], [Vmin, Vmax]]    
    Sortie :  [chromosome]
* Cette méthode de génération, génére des valeurs de gauche à droite du chromosome, en commancant par a_1 ensuite V_1, a_2, V_2, ...
* C'est la méthode utilisée'
"""
def generate_chromosome(vector_acceleration, vectors_speeds):
    
    acceptable = True
    chromosome_table = []
    
    vector_acceleration_positive = [i for i in vector_acceleration if i > 0] # pour a_0
    vector_acceleration_negative = [j for j in vector_acceleration if j < 0] # pour a_final 
    
    # ajouter la premiere acceleration (positive) et non NULLE
    acceleration_random = round(rdm.random()*max(vector_acceleration_positive)  ,2)
    while acceleration_random == 0:
        acceleration_random = round(rdm.random()*max(vector_acceleration_positive)  ,2)
    
    chromosome_table.append( acceleration_random ) # acceleration de depart
    i = 0
    while( i < len(vectors_speeds)-1  ):
        if(i == 0):
              speed_random = rdm.random()*(vectors_speeds[i][-1] - vectors_speeds[i][0]) + vectors_speeds[i][0]  
              chromosome_table.append( speed_random ) 
              
              acceleration_random = rdm.random()*vector_acceleration[-1]*rdm.choice([-1,1])  
              chromosome_table.append( acceleration_random )
              i = i + 1           
        else:
            
            if(acceleration_random < 0):
                
                # si on deccelere alors il faudra que la prochaine vitesse minimale 'vectors_speeds[i][0]' 
                # soit strictement inferieure a la vitesse actuelle, cad 'speed_random'
                if speed_random <= vectors_speeds[i][0]: 
                    acceptable = False
                    break
                    
                spd_random = rdm.random()*( min( vectors_speeds[i][-1], speed_random) - vectors_speeds[i][0] ) + vectors_speeds[i][0]  
                # il faut qu'elle soit STRICTEMENT inferieure a la vitesse precedente car a < 0
                while spd_random == speed_random:
                    spd_random = rdm.random()*( min( vectors_speeds[i][-1], speed_random) - vectors_speeds[i][0] ) + vectors_speeds[i][0]  
                    # print(str(spd_random) + " =======  "+str(speed_random) )
                speed_random = spd_random
                chromosome_table.append( speed_random ) 
                
            elif(acceleration_random > 0):
                if vectors_speeds[i][-1] <= speed_random :
                    acceptable = False
                    break;
                
                spd_random = rdm.random()*(vectors_speeds[i][-1] - vectors_speeds[i][0]) + vectors_speeds[i][0]  
                # il faut qu'elle soit STRICTEMENT superieure a la vitesse precedente car a < 0
                while spd_random == speed_random:
                    spd_random = rdm.random()*(vectors_speeds[i][-1] - vectors_speeds[i][0]) + vectors_speeds[i][0] 
                speed_random = spd_random
                chromosome_table.append( speed_random ) 
                   
            else :       
                # si a == 0 alors on garde la meme vitesse. deja stockée dans la derniere valeur 'speed_random'
                # et verifier que si on garde la meme vts qu'avant, qu'elle soit 
                # tjrs inferieure a la limitte max de la vts d'apres et superieure a
                # la vitesse min d'apres
                if( (speed_random <= vectors_speeds[i][-1]) and (speed_random >= vectors_speeds[i][0]) ): 
                    chromosome_table.append( speed_random ) 
                else:#
                    acceptable = False #
                    break #
            
            
            acceleration_random = round(rdm.random()*vector_acceleration[-1],2)*rdm.choice([-1,1])   
            #acceleration_random = rdm.choice( vector_acceleration )
            chromosome_table.append( acceleration_random )
            i = i + 1             

#=======================================================================================
    
    # car s'il y a une seule limitation de vitesse alors ca rentre meme pas dans la boucle d'au dessus, 
    # donc aacelerarion_random et ... ne sont pas définies     
    if len(vectors_speeds) > 1 :
        
        # ajoutée pour le soucis de a == 0 en dernier
        if(acceleration_random < 0):
            
            # verifier que la vitesse min d'apres soit inferieure strictement, sinon ce n'est pas possible de 
            # deccelerer vers une vitesse plus grande que soi, ou égale
            if speed_random <= vectors_speeds[i][0]: 
                acceptable = False
                
            else:    
                spd_random = rdm.random()*( min( vectors_speeds[i][-1], speed_random) - vectors_speeds[i][0] ) + vectors_speeds[i][0]  
                # il faut qu'elle soit STRICTEMENT inferieure a la vitesse precedente car a < 0
                while spd_random == speed_random:
                    spd_random = rdm.random()*( min( vectors_speeds[i][-1], speed_random) - vectors_speeds[i][0] ) + vectors_speeds[i][0] 
                    
                speed_random = spd_random
                chromosome_table.append( speed_random ) 
            
        elif(acceleration_random > 0):
               
            if vectors_speeds[i][-1] <= speed_random :
                acceptable = False
                
            else:    
                spd_random = rdm.random()*(vectors_speeds[i][-1] - vectors_speeds[i][0]) + vectors_speeds[i][0] 
                # il faut qu'elle soit STRICTEMENT superieure a la vitesse precedente car a < 0
                while spd_random == speed_random:
                    spd_random = rdm.random()*(vectors_speeds[i][-1] - vectors_speeds[i][0]) + vectors_speeds[i][0]  
                   
                speed_random = spd_random
                chromosome_table.append( speed_random ) 
           #=======================================================================================
        else: # a == 0    #
            # on verifie qu'on depasse pas la limite en gardant la mm vts
            if( (speed_random <= vectors_speeds[i][-1]) and (speed_random >= vectors_speeds[i][0]) ): 
                # ajouter l'avant derniere vitesse
                chromosome_table.append( speed_random ) 
            else:#
                acceptable = False #
                   
    # sinon, il a une seule limitation de vitesse ==> on ajoute juste le random vitesse, car la premiere 
    # acceleration y est deja (au debut) 
    else: 
        
        speed_random = rdm.random()*(vectors_speeds[i][-1] - vectors_speeds[i][0]) + vectors_speeds[i][0] 
        chromosome_table.append( speed_random ) 
    
    acceleration_random = rdm.random()*min(vector_acceleration_negative) 
    while acceleration_random == 0:
        acceleration_random = rdm.random()*min(vector_acceleration_negative) 
    
    #ajouter la derniere decceleration et la derniere vitesse v=0
    chromosome_table.append( acceleration_random ) # decceleration finale (vers V=0)
    chromosome_table.append( 0 ) # vitesse finale = 0
    i = i + 1           
    # print("je suis laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+str(acceptable))
    return acceptable, chromosome_table

  
#---------------------------------------------------------------------------------------------------

"""
    Entrée :  [[Chromosome], [Dist de seg], [point], [Vmax]]    
    Sortie :  [Durée (s)]
Comme son nom l'indique, cette fonction calcule les différentes durrées en [s] pour 
les différentes phases du chromosome donné en entrée'
"""
def calculate_durations( chromosome, dist_segment_speed , cut_points, speeds):  
    
    # Pour avoir les données pour chaque phases, independemment des depassements  
    duration_brute_per_phase = []
    distance_raw_per_phase = []
    
    # Les distances et les durées des phases en detail (en separant les depassements ) 
    distance_per_phase = []            
    duration_per_phase = []
    
    dur_seg_tmp = []
    
    # Calculer les differentes durées brutes des diff phases (en cumulant des les durées mm s'il y a depassement)
    duration_raw_per_phase = []
    
    duration_segment = []
    i = 0
    j = 0  # and j<len(dist_segment_speed) dans le while ne sert a rien si tt va bien
    while(i < len(chromosome) ):
        
        if(i == 0):
            duration_1 = chromosome[i+1]/chromosome[i]
            distance_1 = duration_1*chromosome[i+1]/2 
             
            if(chromosome[i+2] == 0):
                
                duration_2 = 0
                distance_2 = duration_2*chromosome[i+1] + duration_2*(chromosome[i+3] - chromosome[i+1])/2 
                
                #sign_acceleration = abs(chromosome[i+2]) / chromosome[i+2] 
                dist_tmp = distance_1 + distance_2         
                distance_3 = dist_segment_speed[j] - dist_tmp
                
                duration_3 = distance_3/chromosome[i+1]

            elif(chromosome[i+2] > 0 and chromosome[i+3] > speeds[j] ):
                 
                 duration_2 = (speeds[j] - chromosome[i+1] )/chromosome[i+2] 
                 distance_2 = duration_2*chromosome[i+1] + duration_2*(speeds[j] - chromosome[i+1])/2
                
                 dist_tmp =  distance_1 + distance_2
                 distance_3 = dist_segment_speed[j] - dist_tmp
                 
                 duration_3 = distance_3/chromosome[i+1]
                 
            else:                  
                duration_2 = ( chromosome[i+3] - chromosome[i+1] )/chromosome[i+2] 
                distance_2 = duration_2*chromosome[i+1] + duration_2*(chromosome[i+3] - chromosome[i+1])/2
                
                #sign_acceleration = abs(chromosome[i+2]) / chromosome[i+2] 
                dist_tmp = distance_1 + distance_2   
                distance_3 = dist_segment_speed[j] - dist_tmp
                
                duration_3 = ( dist_segment_speed[j] - dist_tmp )/chromosome[i+1]
             
            duration_raw_per_phase.append( duration_1 )
            duration_raw_per_phase.append( duration_3 )
            duration_raw_per_phase.append( duration_2 )
             
            # mettre a jour la duree de tout le segement 
            duration_segment.append(duration_1 + duration_2 + duration_3)
            duration_per_phase.append([duration_1 , duration_3 , duration_2])
            distance_per_phase.append([distance_1 , distance_3 , distance_2])
            
           
            # pour avoir les distances 'brutes' par phases 
            distance_raw_per_phase.append(distance_1) 
            distance_raw_per_phase.append(distance_3)
            distance_raw_per_phase.append(distance_2) 
        
            i = i + 3
            j = j + 1
            
        else: # i >= 1 
            if(chromosome[i] == 0 ):
                # print(str(i) + " Fin")
                break
            
            if( chromosome[i] > speeds[j-1] ):
                 duration_1 = ( chromosome[i] - speeds[j-1] )/chromosome[i-1]  
                 distance_1 = duration_1*speeds[j-1]  +  duration_1*(chromosome[i]-speeds[j-1] )/2
                 
                 if(chromosome[i+1] == 0):  
                     duration_2 = 0 
                     
                     dist_tmp =  distance_1
                     #dist_tmp = duration_2*chromosome[i] + duration_2*(chromosome[i+2] - chromosome[i])/2
                     distance_3 = dist_segment_speed[j] - dist_tmp
                     
                     duration_3 = distance_3/chromosome[i]
                     
                 elif(chromosome[i+1] > 0 and chromosome[i+2] > speeds[j] ):
                     duration_2 = ( speeds[j] - chromosome[i] ) / chromosome[i+1]    
                     distance_2 = duration_2*chromosome[i] + duration_2*(speeds[j] - chromosome[i])/2
                     
                     dist_tmp = distance_1 + distance_2
                     distance_3 = dist_segment_speed[j] - dist_tmp
                     
                     duration_3 = distance_3/ chromosome[i]         
                     
                 else:
                     duration_2 = ( chromosome[i+2] - chromosome[i] )/chromosome[i+1]
                     distance_2 = duration_2*chromosome[i] + duration_2*(chromosome[i+2] - chromosome[i])/2
                     
                     dist_tmp = distance_1  + distance_2
                     distance_3 = dist_segment_speed[j] - dist_tmp
                     
                     duration_3 = distance_3/chromosome[i]
                 
                 duration_per_phase.append([duration_1 , duration_3,  duration_2])
                 # si on a une acceleration au debut du segment a prendre en
                 # compte ==> on rajoute sa duree a la duree de derniere acceleration du segment precedent
                 duration_raw_per_phase[-1] = duration_raw_per_phase[-1] + duration_1 
                 
                 duration_raw_per_phase.append( duration_3 )
                 duration_raw_per_phase.append( duration_2 )
                 
                 # mettre a jour la duree de tout le segement 
                 duration_segment.append(duration_1 + duration_2 + duration_3) 
                 distance_per_phase.append([distance_1 , distance_3 , distance_2])
                 
                 #=======================================================================================
                 # pour avoir les distances 'brutes' par phases 
                 distance_raw_per_phase[-1] = distance_raw_per_phase[-1] + distance_1
                 distance_raw_per_phase.append(distance_3) 
                 distance_raw_per_phase.append(distance_2)
                 #=======================================================================================
         
                 j = j + 1
                 i = i + 2
             
             #=======================================================================================
            else:
                duration_1 = 0  # y'avait pas de depassement avant 
                distance_1 = 0
                if(chromosome[i+1] == 0):
                    duration_2 = 0 
                    distance_2 = 0
                    
                    dist_tmp = distance_2
                    distance_3 = dist_segment_speed[j] - dist_tmp
                    
                    duration_3 = distance_3/chromosome[i]
                 
                elif(chromosome[i+1] > 0 and chromosome[i+2] > speeds[j] ):
                    duration_2 = ( speeds[j] - chromosome[i] ) / chromosome[i+1]  
                    distance_2 = duration_2*chromosome[i] + duration_2*(speeds[j] - chromosome[i])/2
                    
                    dist_tmp = distance_2
                    distance_3 = dist_segment_speed[j] - dist_tmp
                    
                    duration_3 = distance_3/ chromosome[i]       
                                                 
                else:
                    duration_2 = ( chromosome[i+2] - chromosome[i] )/chromosome[i+1] 
                    distance_2 = duration_2*chromosome[i] + duration_2*(chromosome[i+2] - chromosome[i])/2
                    
                    dist_tmp = distance_2
                    distance_3 = dist_segment_speed[j] - dist_tmp
                    
                    duration_3 = distance_3/ chromosome[i]
                                 
                duration_raw_per_phase.append( duration_3 )
                duration_raw_per_phase.append( duration_2 )
                
                duration_per_phase.append([duration_1 , duration_3,  duration_2])
                
                # mettre a jour la duree de tout le segement 
                duration_segment.append(duration_2 + duration_3) 
                distance_per_phase.append([distance_1 , distance_3 , distance_2])
                
                #########################################################
                # pour avoir les distances 'brutes' par phases 
                # distance_1 == 0    
                distance_raw_per_phase.append(distance_3) 
                distance_raw_per_phase.append(distance_2)
                #########################################################
                
                j = j + 1
                i = i + 2
             ####################################################

    return duration_raw_per_phase, duration_per_phase, distance_per_phase, distance_raw_per_phase 


#-----------------------------------------------------------------------------------------------------


""" 
    Entrée :  [[Chromosome], [Durée (s)], [Dist de seg], [point], [Vmax]]    
    Sortie :  [Distance par m], [Durée par m], [Energie par m], [Vitt par m]
    Cette fonction calcule l'énergie consommée pour le chromosome donné en entrée,
    ainsi que le temps de trajet du même chromosome,  et les vitesses chaque 1 mètre
"""

def evaluate(chromosome ,duration_raw_per_phase, distance_raw_per_phase , _dist_and_slope):
    
    """ 0) les données du véhicule """ 
    m = 1100 # masse du véhicule 
    C_r = 0.01 # Coeff 
    g = 9.81 # gravitée
    Rw = 1.25 # 
    SC_x =0.609 # surface
    
    Motorization = 'Elect'
    #Motorization = 'Therm'
    
    if Motorization == 'Therm':
        Rdm_positive = 1/0.5
        Rdm_negative = 0
    else :     
        Rdm_positive = 1/0.8
        Rdm_negative = 0.2
    
    #---------------------------------------------------------------------------------
    
    """ 2) transformer la matrice des distances de chaque phase de chaque segement (en brute) en une liste 
        de distances cumulées (a la fin on aura la distance totale) 
        par exp: [1,3,2] ==> [1,4,6]  ( '1' la durée qu'on met pour la premiere phase, ...)"""

    
    cumulative_raw_distance = []
    distance_init = 0    
    
    for i in range( 0, len(distance_raw_per_phase) ) :       
            
            cumulative_raw_distance.append(distance_raw_per_phase[i] + distance_init)
            distance_init = distance_init + distance_raw_per_phase[i]
    
    #---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

    """ 3) parcourir la matrice de ditance_pente pour calculer la puissance """
    
    #Energie_consommée = 0
    #Ec_list = []
    
    i = 0 # pour parcourir le chromosome (les différentes phases)
    j = 1 # pour parcourir la liste dist_slope (pour récuperer les pentes chaque 1 m )
    k = 0 # pour les itérations des temps 
    
    times_metre = [0] 
    vts_metre = [0]
    energy_consumed_metre = [0]
    tps = []
    F_trac = 0
    
    while(i < len(chromosome) - 1  ): # -1 car on prend pas en compte le dernier V = 0 (ca ne consomme pas en +)
        
        if(i == 0): # car V_0 = 0
            
            while( j < len(_dist_and_slope)   and j  <= round(cumulative_raw_distance[i])   ):
                # temps pour chaque metre (au point j)
                times_metre.append( math.sqrt( j*2/chromosome[i] ) ) 
                #vts_metre.append( chromosome[i]*( times_metre[-1]-times_metre[-2] ) )
                vts_metre.append( chromosome[i]*( times_metre[-1] ) )
                
                #=====================================================================================================
                # calcul de F_trac = ma - Fa - Fr - Fw
                F_trac =   (m*chromosome[i] 
                            + m*g*math.cos( _dist_and_slope[j][1] )*C_r 
                            + m*g*math.sin( _dist_and_slope[j][1] ) 
                            + 0.5*Rw*SC_x 
                            *( 0 + chromosome[i]*times_metre[-1])**2  ) 
                #=====================================================================================================
                
                # Calucul de puissance en ce point j ( En = dt*V(t)*F*Randement )
                # quand i == 0 accel > 0 et donc ya un randement positif 
                if F_trac >= 0 :        
                    energy_consumed_metre.append(  ( times_metre[-1]-times_metre[-2] )*( 0 + chromosome[i]*times_metre[-1] )*( m*chromosome[i] + m*g*math.cos( _dist_and_slope[j][1] )*C_r + m*g*math.sin( _dist_and_slope[j][1] ) + 0.5*Rw*SC_x *( 0 + chromosome[i]*times_metre[-1])**2 )*Rdm_positive)  
                            
                    if energy_consumed_metre[-1] < 0 :
                        print(" Error !")
                                
                else:
                    #energy_consumed_metre.append(0)
                    energy_consumed_metre.append(  ( times_metre[-1]-times_metre[-2] )*( 0 + chromosome[i]*times_metre[-1] )*( m*chromosome[i] + m*g*math.cos( _dist_and_slope[j][1] )*C_r + m*g*math.sin( _dist_and_slope[j][1] ) + 0.5*Rw*SC_x *( 0 + chromosome[i]*times_metre[-1])**2 )*Rdm_negative)  
                    
                j += 1
            
            i += 1
            tps.append(times_metre[-1])
            
        else: 
            
            if(i%2 == 1): # a == 0 (Vitesse constante) et V_0 = chromosome[i] "c'est lui mm"
                
                while( j < len(_dist_and_slope) and j <= round(cumulative_raw_distance[i])   ):
                    
                    # temps pour chaque metre (au point j)
                    times_metre.append( (1/chromosome[i]) + times_metre[-1]  ) 
                    vts_metre.append( chromosome[i]  )
                    
                    #=====================================================================================================
                    # calcul de F_trac = ma - Fa - Fr - Fw
                    F_trac = (  m*g*math.cos( _dist_and_slope[j][1] )*C_r
                    + m*g*math.sin( _dist_and_slope[j][1] ) 
                    + 0.5*Rw*SC_x * (chromosome[i]**2) ) 
                    #=====================================================================================================
                    
                    # Calucul de puissance en ce point j ( En = dt*V(t)*F*Randement )
                    # quand  pente > 0 ==> ya un randement positif
                    # quand  pente <= 0 ==> ya pas de rendement ( dans le cas thermique )
                    # Energie = V_0*(ma-mgcos(alpha)*Cr - mgsin(alpha) - 0.5*ro*SCx * V_0**2)*Randement 
                    if F_trac >= 0 :                       
                        energy_consumed_metre.append(  ( times_metre[-1]-times_metre[-2] )  
                                                        *( chromosome[i] ) 
                                                        *(  m*g*math.cos( _dist_and_slope[j][1] )*C_r
                                                        + m*g*math.sin( _dist_and_slope[j][1] ) 
                                                        + 0.5*Rw*SC_x
                                                        * chromosome[i]**2  )
                                                        * Rdm_positive
                                                        #*(1 + ( abs(_dist_and_slope[j][1])/_dist_and_slope[j][1] ) )
                                                        )
                        
                        if energy_consumed_metre[-1] < 0 :
                            print(" Error !")
                        
                    else:
                        #energy_consumed_metre.append(0)
                        energy_consumed_metre.append(  ( times_metre[-1]-times_metre[-2] )  
                                                        *( chromosome[i] ) 
                                                        *(  m*g*math.cos( _dist_and_slope[j][1] )*C_r
                                                        + m*g*math.sin( _dist_and_slope[j][1] ) 
                                                        + 0.5*Rw*SC_x
                                                        * chromosome[i]**2  )
                                                        * Rdm_negative
                                                        #*(1 + ( abs(_dist_and_slope[j][1])/_dist_and_slope[j][1] ) )
                                                        )
                        
                    j += 1
            
                tps.append(times_metre[-1])
                #k = j-1
                
            else: #  V_0 = chromosome[i-1] "c'est la vitesse constante d'avant"
                
                last_time = times_metre[-1] # la derniere durée, à laquelle on va additionner les autres durées
                
                while( j < len(_dist_and_slope) and j < round(cumulative_raw_distance[i])  ):
                    
                    coeff = [0.5*chromosome[i] , chromosome[i-1] , -(j-k) ]         
                    possibles_solutions = [s for s in np.roots(coeff) if s > 0  ]
                    tps_for_metre =  min(possibles_solutions) 
                    
                    
                    times_metre.append( last_time + tps_for_metre ) 
                    vts_metre.append(  chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-last_time )  )  )
                    
                    #=====================================================================================================
                    # calcul de F_trac = ma - Fa - Fr - Fw
                    F_trac =   (m*chromosome[i]
                    + m*g*math.cos( _dist_and_slope[j][1] )*C_r
                    + m*g*math.sin( _dist_and_slope[j][1] ) 
                    + 0.5*Rw*SC_x * ( chromosome[i-1] +  chromosome[i]*( times_metre[-1]-last_time )  )**2)
                    #=====================================================================================================
                    
                    # vts_metre.append(  chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-times_metre[-2] )  )  )
                    
                    # Calucul de puissance en ce point j ( En = dt*V(t)*F*Randement )
                    # quand  pente > 0 ==> ya un randement positif
                    # quand  pente <= 0 ==> ya pas de rendement ( dans le cas thermique )
                    # Energie = V_0*(ma-mgcos(alpha)*Cr - mgsin(alpha) - 0.5*ro*SCx * V_0**2)*Randement 
                    if F_trac >= 0 :
                        energy_consumed_metre.append(  ( times_metre[-1]-times_metre[-2] )  
                                                        *( chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-last_time ) ) ) 
                                                        # *( chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-times_metre[-2] ) ) ) 
                                                        *( m*chromosome[i]
                                                        + m*g*math.cos( _dist_and_slope[j][1] )*C_r
                                                        + m*g*math.sin( _dist_and_slope[j][1] ) 
                                                        + 0.5*Rw*SC_x
                                                        *( chromosome[i-1] +  chromosome[i]*( times_metre[-1]-last_time )  )**2  )
                                                        # ( chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-times_metre[-2] ) ) ) **2  )
                                                        *Rdm_positive
                                                        #*(1 + ( abs(_dist_and_slope[j][1])/_dist_and_slope[j][1] ) )
                                                        )
                    
                        if energy_consumed_metre[-1] < 0 :
                            print(" Error !!!!")
                    
                    else:
                        #energy_consumed_metre.append(0)
                        energy_consumed_metre.append(  ( times_metre[-1]-times_metre[-2] )  
                                                        *( chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-last_time ) ) ) 
                                                        # *( chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-times_metre[-2] ) ) ) 
                                                        *( m*chromosome[i]
                                                        + m*g*math.cos( _dist_and_slope[j][1] )*C_r
                                                        + m*g*math.sin( _dist_and_slope[j][1] ) 
                                                        + 0.5*Rw*SC_x
                                                        *( chromosome[i-1] +  chromosome[i]*( times_metre[-1]-last_time )  )**2  )
                                                        # ( chromosome[i-1] + ( chromosome[i]*( times_metre[-1]-times_metre[-2] ) ) ) **2  )
                                                        *Rdm_negative
                                                        #*(1 + ( abs(_dist_and_slope[j][1])/_dist_and_slope[j][1] ) )
                                                        )

                    j += 1
            
                tps.append(times_metre[-1])
                #k = j-1
                
            k = j-1    
            i += 1
            
    return  cumulative_raw_distance, energy_consumed_metre, times_metre, vts_metre,tps   


#------------------------------------------------------------------------------------------------
#---------------------------------  PLOT CHROMOSOMES -------------------------------------------------------
#------------------------------------------------------------------------------------------------
"""
    Entrée :  [[[Chromosome]], [Vmax], [Durée (s) jusq'u moitié de la phase d'accel], [Durée (s)], Title, ]    
    Sortie :  [Distance par m], [Durée par m], [Energie par m], [Vitt par m]
"""
def plot_chromosome(chromosome_table, spd, duration_per_phase, duration_raw_per_phase, title):
    
    #======================== pour le plot du Vmax   ====================================
    duration_Vmax_plot = [0]
    i=0
    while(i < len(duration_per_phase) ):
        if(i==0):
            duree = duration_per_phase[i][0]+ duration_per_phase[i][1] + duration_per_phase[i][2] 
            i = i + 1
        else:
            duree = duration_Vmax_plot[-1] + sum( duration_per_phase[i] )
            i = i + 1 
        
        duration_Vmax_plot.append(duree)   
        duration_Vmax_plot.append(duree)
            
    # print("duration_Vmax_plot " +str(duration_Vmax_plot) )
   
    #=======================================================================================
    speed_Vmax_plot = []
    for v in spd:
        speed_Vmax_plot.append(v)
        speed_Vmax_plot.append(v)
    speed_Vmax_plot.append(spd[-1])    
    # print(speed_Vmax_plot)    
    
    #====================================== plot pour le Vmin  =================================
    # on utilise le meme tableau de duree que pour le Vmax (au dessus)
    
    #calcul des vitesses Min 
    speed_Vmin_plot = []
    for v in spd:
       
        if v <= 13.88: # 50 kmh
            speed_Vmin_plot.append(8.33)
            speed_Vmin_plot.append(8.33)
        elif v <= 25:  # 90 kmh
            speed_Vmin_plot.append(13.88)
            speed_Vmin_plot.append(13.88)
        else:                   # 110 ou 130 kmh
            speed_Vmin_plot.append(22.22)  
            speed_Vmin_plot.append(22.22)
        
    speed_Vmin_plot.append(speed_Vmin_plot[-1])   
        
    #=======================================================================================
    duration_plot = [0]
    for duree in duration_raw_per_phase:
        duration_plot.append(duree+ duration_plot[-1])
    #print(duration_plot)

    vitesses = [0]
    for i in range(0, len(chromosome_table)-1):
        if(i%2 == 1):
            vitesses.append(chromosome_table[i])
            vitesses.append(chromosome_table[i])
    vitesses.append(0)
    #print(vitesses)

    #-------------------- Plot -------------------------------------------------
    plt.figure(figsize=(10,5))
    plt.plot(duration_plot,vitesses)
    
    plt.plot(duration_Vmax_plot,speed_Vmax_plot)
    #plt.plot(duration_Vmax_plot,speed_Vmin_plot)
    #plt.fill_between(duration_Vmax_plot,speed_Vmax_plot,alpha=0.1)

    plt.plot(duration_plot, vitesses, 'o')
    plt.xlabel("Time(s)")
    plt.ylabel("Speed (m/s)")
    plt.legend(['Speed','Speed Max'])
    plt.title(str(title))
    #plt.legend(['Speed','Speed Max', 'Speed min'])
    plt.fill_between(duration_plot,vitesses,alpha=0.1)
    plt.grid()
    plt.show()        
#=======================================================================================
################################################################## Crossovers + Mutations


""" croisement 1: la moyenne des vitesses en gardant les accelerations du parent 1 (meilleur parent)
    ainsi que les vitesses si la moyenne n'est pas possible """

def crossover_speed_mean(chromosome_1 , chromosome_2):
    chromosome_result = []
   
    for i in range(len(chromosome_1)):
        
        if(i%2 == 0): 
            chromosome_result.append(chromosome_1[i]) 
        
        else:
            if( i > 1 and ( chromosome_1[i-1] > 0 and chromosome_2[i-1] >= 0 ) and chromosome_result[i-2] < (chromosome_1[i] + chromosome_2[i])/2 ):
                if round((chromosome_1[i] + chromosome_2[i])/2  ,2 ) != 0 :
                    chromosome_result.append( round((chromosome_1[i] + chromosome_2[i])/2  ,2 ) )
                else:
                    chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2  )
            
            elif( i > 1 and ( chromosome_1[i-1] < 0 and chromosome_2[i-1] <= 0 ) and chromosome_result[i-2] > (chromosome_1[i] + chromosome_2[i])/2 ):   
                if round((chromosome_1[i] + chromosome_2[i])/2  ,2 ) != 0 :
                    chromosome_result.append( round((chromosome_1[i] + chromosome_2[i])/2  ,2 ) )
                else : 
                    chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2   )
                
            
            else:
                chromosome_result.append( chromosome_1[i] )
           
                     
    return chromosome_result 



""" croisement 2: la moyenne des vitesses et des accelerations en gardant les accelerations et les vitesses
    du parent 1 si la moyenne n'est pas possible """
    # en gardant ceux du "MEILLEUR" parent

def crossover_speed_and_acceleration_mean(chromosome_1 , chromosome_2):
    chromosome_result = []
    
    for i in range(len(chromosome_1)):
        if (i == 0): # accel et vitesse de la premiere phase (tjrs les memes qlq le chrom) 
            chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2  )
            chromosome_result.append( (chromosome_1[i+1] + chromosome_2[i+1])/2  )
                
        elif(i%2 == 0): 
            
            if( ( chromosome_1[i] > 0 and chromosome_2[i] >= 0 ) and chromosome_result[i-1] < (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                chromosome_result.append( (chromosome_1[i+1] + chromosome_2[i+1])/2 )
            
            elif( ( chromosome_1[i] < 0 and chromosome_2[i] <= 0 ) and chromosome_result[i-1] > (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                chromosome_result.append( (chromosome_1[i+1] + chromosome_2[i+1])/2 )
            
            elif( ( chromosome_1[i] < 0 and chromosome_2[i] <= 0 ) and chromosome_result[i-1] <= (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                chromosome_result.append( chromosome_1[i+1] )
                
            elif( ( chromosome_1[i] > 0 and chromosome_2[i] >= 0 ) and chromosome_result[i-1] >= (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                chromosome_result.append( chromosome_1[i+1]  )
                
            # on garde ceux du parent 1 (le meilleur)    
            elif( chromosome_1[i] == 0) :  
                chromosome_result.append( chromosome_1[i] )   
                chromosome_result.append( chromosome_result[i-1] )                                 
            else:
                chromosome_result.append( chromosome_1[i] )   
                chromosome_result.append( chromosome_1[i+1] )   
                
    return chromosome_result 


"""
    Entrée :  [Chromosome], [Chromosome]    
    Sortie :  [Chromosome], bool use_this_one_point_crossover (Operation used?)
"""
""" croisement 3: echange en un point random, cad qu'avant ce point random on garde la prtie du parent 1
    et apres, la partie du parent 2. Si ce n'est pas possible on applique le croisement 2 (juste au dessus) """
    

def crossover_exchange_one_point(chromosome_1 , chromosome_2):
    chromosome_result = []
    rand_cut_point = rdm.randint(2, len(chromosome_1)-2 )
    use_this_one_point_crossover = True
    
    # On tombe sur une acceleration
    if( 
        ( rand_cut_point%2 == 0 and chromosome_1[rand_cut_point] > 0 and chromosome_2[rand_cut_point] > 0 
        and chromosome_2[rand_cut_point+1] > chromosome_1[rand_cut_point-1])
        or
        (rand_cut_point%2 == 0 and chromosome_1[rand_cut_point] < 0 and chromosome_2[rand_cut_point] < 0 
        and chromosome_2[rand_cut_point+1] < chromosome_1[rand_cut_point-1])      
      )  : 
        
        for i in range(len(chromosome_1)):
            
            if i < rand_cut_point :
                chromosome_result.append( chromosome_1[i] )
            else:
                chromosome_result.append( chromosome_2[i] )       
                           
    # On tombe sur une vitesse
    elif(
        (rand_cut_point%2 == 1 and chromosome_1[rand_cut_point-1] > 0  
        and chromosome_2[rand_cut_point] > chromosome_1[rand_cut_point-2])
        or
        (rand_cut_point%2 == 1 and chromosome_1[rand_cut_point-1] < 0  
        and chromosome_2[rand_cut_point] < chromosome_1[rand_cut_point-2])            
       ) : # vitesse
        
        for i in range(len(chromosome_1)):
            
            if i < rand_cut_point :
                chromosome_result.append( chromosome_1[i] )
            else:
                chromosome_result.append( chromosome_2[i] )          
                            
    else :
        use_this_one_point_crossover = False 
        for i in range(len(chromosome_1)):
 
            if (i == 0): # accel et vitesse de la premiere phase (tjrs les memes qlq le chrom) 
                chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                chromosome_result.append(  (chromosome_1[i+1] + chromosome_2[i+1])/2 )
                    
            elif(i%2 == 0): 
                
                if( ( chromosome_1[i] > 0 and chromosome_2[i] >= 0 ) and chromosome_result[i-1] < (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                    chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                    chromosome_result.append( (chromosome_1[i+1] + chromosome_2[i+1])/2 )
                
                elif( ( chromosome_1[i] < 0 and chromosome_2[i] <= 0 ) and chromosome_result[i-1] > (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                    chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                    chromosome_result.append( (chromosome_1[i+1] + chromosome_2[i+1])/2 )
                
                elif( ( chromosome_1[i] < 0 and chromosome_2[i] <= 0 ) and chromosome_result[i-1] <= (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                    chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                    chromosome_result.append( chromosome_1[i+1]  )
                    
                elif( ( chromosome_1[i] > 0 and chromosome_2[i] >= 0 ) and chromosome_result[i-1] >= (chromosome_1[i+1] + chromosome_2[i+1])/2 ):
                    chromosome_result.append( (chromosome_1[i] + chromosome_2[i])/2 )
                    chromosome_result.append( chromosome_1[i+1]  )
                    
                # on garde ceux du parent 1 (le meilleur)    
                else:                
                    if chromosome_1[i] == 0 :
                        chromosome_result.append( chromosome_1[i] )   
                        chromosome_result.append( chromosome_result[i-1] )                                 
                    else:
                        chromosome_result.append( chromosome_1[i] )   
                        chromosome_result.append( chromosome_1[i+1] )   
    
    return chromosome_result, use_this_one_point_crossover 

""" Mutation : on prend une des accelerations du chromosome et on lui donne la plus grande valeur de toutes 
    les accelations possibles (cad: si c une accel negative on lui donne la plus petite et si c une 
                               accel positive on lui donne la plus grande accel PARMIS LES ACCEL DU CHROM)"""

def mutation_chromosome(chromosome_1):
   
    chromosome_result = chromosome_1.copy()
    
    # prendre une acceleration aléatoirement
    gene = rdm.randrange(0, len(chromosome_1)-1,2)

    # si l'acceleration prise est negative ==> on la remplace avec la plus petite accel du chrom
    if chromosome_result[gene] < 0 :
        # parmis toutes les accel negatives de ce chromosome
        chromosome_result[gene]  = min([i for i in chromosome_result[0:len(chromosome_result):2]])
    
    # si l'acceleration prise est positive ==> on la remplace avec la plus grosse accel du chrom
    elif chromosome_result[gene] > 0 :
        # parmis toutes les accel positives de ce chromosome
        chromosome_result[gene]  = max([i for i in chromosome_result[0:len(chromosome_result):2]])
                   
    return chromosome_result 

#========================================== FIN ===========================================