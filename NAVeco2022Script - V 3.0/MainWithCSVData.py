"""
    Auteur : Anis SALHI
    Date : 06/2022

    Programme qui :
        * Récupere les données du trajet, avec adresse de départ et d arrivée + les parametres de l'algo génétique (ps, pm,..)
        * Lance l'algo génétique
        * Sortie : La meilleur profil vitesse trouvé (chromosome) + plot de ce profil

    Modifie par: Anis SALHI
"""
#==============================================================================
import sys

sys.path.append('C:/Users/crybelloceferin/Documents/MATLAB/Anis/VersionYesid/')

import fonctions as fct
import random
import time
import statistics
from aDataRecovery import aDataRecovery

#TODO: Ranger les parametres


# Données :
Population_size = 150
limit_generation  = 150
Selection_probability = 0.5
Mutation_probability = 0.2

acceleration_max = 2.5 # en m/s²

# Criteres d'arret
gain = 0.01 # en kWh
limit_identical_best = 10

# pour les resultats finaux. Pour chaque trajet (Vmax, Pente)
DataRoute = []
DataFinal = [] # pour ecrire les resultats dans un fichier csv

plot_best_solution = True

#==============================================================================

# Données :


departure_adress = 'Vanves, France'
arrival_adress = 'Montparnasse Paris, France'
DevelopperMode = False
data = aDataRecovery(departure_adress,arrival_adress,DevelopperMode)

comienzo = time.time()
#Trajet réel
data = data[1:]
#[['Num', 'Lat', 'Lng', 'Dist (m)', 'MaxSpeed (m/s)', 'Slope (rad)', 'Altitude (m)', 'Duree (s)']]
DistSpeed = []
DistSlope = []
for point in data:
    DistSpeed.append( [ float(point[3]) , float(point[4]) ] )
    DistSlope.append( [ float(point[3]) , float(point[5]) ] )


#==============================================================================

cut , spd , dist_segment_speed = fct.speed_and_dist_cut(DistSpeed)
print("-----------------------------------------------------------")

vect_accel, vect_speed = fct.split_speed_and_acceleration(-acceleration_max , acceleration_max , spd)

print("-----------------------------------------------------------")

#====================== 1) Chromosome a duree min ===============================================

# pour avoir la durée min possible
chromosome_duraion_min = []

chromosome_duraion_min.append( acceleration_max )
chromosome_duraion_min.append( spd[0] )

for i in range( 1, len(spd) ):

    if(spd[i] > spd[i-1]):
        chromosome_duraion_min.append(acceleration_max)
    elif( spd[i] < spd[i-1] ):
        chromosome_duraion_min.append(-acceleration_max)
    else:
        chromosome_duraion_min.append( 0 )

    chromosome_duraion_min.append( spd[i] )


chromosome_duraion_min.append(-acceleration_max)
chromosome_duraion_min.append( 0 )
#------------------------------------------------------------------------------------------
duration_raw_per_phase, duration_per_phase, distance_per_phase, distance_raw_per_phase = fct.calculate_durations(chromosome_duraion_min, dist_segment_speed, cut, spd)

cumulative_raw_distance, energy_consumed_metre, times_metre, vts_metre,tps   = fct.evaluate(chromosome_duraion_min ,duration_raw_per_phase, distance_raw_per_phase, DistSlope )
duration_min = times_metre[-1]

crom_min_lst = [ chromosome_duraion_min,  sum(energy_consumed_metre), times_metre[-1]]


#====================== 2) Chromosome a duree max ===============================================

# pour avoir la durée max

chromosome_duraion_max = []

min_spd = []
for s in spd :

    # si au dessous de 30 kmh ==> vts min = 20
    if s <= 8.33 and s >= 7: # >= 5.55
        min_spd.append(5.55)
    # si au dessous de 50 kmh ==> vts min = 30
    elif s <= 13.88 and s >= 10: # >= 8.33
        min_spd.append(8.33)
    # si au dessous de 90 kmh ==> vts min = 50
    elif  s <= 25 and s >= 15: # >= 13.88
        min_spd.append(13.88)
    # si > 90 kmh ==> vts min = 80
    elif s >= 25:
        min_spd.append(22.22)
    # si les limitations de vitesse sont "trop petite"
    else:
        min_spd.append( s*0.75 )
        #min_spd.append( min(spd) )



chromosome_duraion_max.append( (acceleration_max + 0)/2  )
chromosome_duraion_max.append( min_spd[0] )

for i in range(0, len(min_spd)-1):

    if min_spd[i] < min_spd[i+1] :
        chromosome_duraion_max.append( (acceleration_max + 0)/2  )
        chromosome_duraion_max.append( min_spd[i+1] )

    elif min_spd[i] > min_spd[i+1] :
        chromosome_duraion_max.append( -(acceleration_max + 0)/2  )
        chromosome_duraion_max.append( min_spd[i+1] )

    else :
        chromosome_duraion_max.append( 0  )
        chromosome_duraion_max.append( min_spd[i+1] )

chromosome_duraion_max.append( -(acceleration_max + 0)/2  )
chromosome_duraion_max.append( 0 )

duration_raw_per_phase, duration_per_phase, distance_per_phase, distance_raw_per_phase = fct.calculate_durations(chromosome_duraion_max, dist_segment_speed, cut, spd)

cumulative_raw_distance, energy_consumed_metre, times_metre, vts_metre,tps   = fct.evaluate(chromosome_duraion_max ,duration_raw_per_phase, distance_raw_per_phase, DistSlope )

duration_max = times_metre[-1]
crom_max_lst = [ chromosome_duraion_max,  sum(energy_consumed_metre), times_metre[-1]]

#====================================== Chromosome 1 ======================================

#=================================== Launch Algo ==============================================================#


#start = time.time()

a = b = c = []

#================== Titre pour les plots des best solution ============================

plot_title = "meilleure solution trouvée"

#======================================


start_final = time.time()
stabilisation_time = 0

start = time.time()

#============================= 3) Generer une population initiale ========================
start = time.time()

execution_time = [0]

Population = []
Nbre_iteration = 2

Population.append( crom_max_lst )
Population.append( crom_min_lst )

# pour les exporter toutes les populations et voir leur evolution
data_by_population = []
data_by_generation = []

while ( Nbre_iteration < Population_size ):

    acceptable_chromosome = False
    acceptable_duration = False
    #acceptable_energie = False
    # or acceptable_energie != True (dans le while juste au dessous)
    while(acceptable_chromosome != True or acceptable_duration != True ):
        start_final = time.time()
        # generer un chromosome et verifier s'il est acceptable
        acceptable_chromosome, chromosome_1 = fct.generate_chromosome(vect_accel, vect_speed)
        a.append(time.time() - start_final)
        if acceptable_chromosome == False :
            break

        # calculer les differentes durees allouees
        duration_raw_per_phase, duration_per_phase, distance_per_phase, distance_raw_per_phase = fct.calculate_durations(chromosome_1, dist_segment_speed, cut, spd)
        b.append(time.time() - start_final - a[-1])
        # verifier qu'il n y a pas de duree negative (ca peut etre le cas juste qd la dist est trop petite)
        acceptable_duration = True
        s = 0
        for i in range(0, len(duration_raw_per_phase)):
            if duration_raw_per_phase[i] < 0 :
                acceptable_duration = False
                break
            else:
                s += duration_raw_per_phase[i]
        if acceptable_duration == False:
            break

        # verifier si la duree totale du chromosome (duree du trajet) est entre duree_min et duree_max
        if(s < duration_min or s > duration_max):
            acceptable_duration = False
            break
        cumulative_raw_distance, energy_consumed_metre, times_metre, vts_metre, tps   = fct.evaluate(chromosome_1 ,duration_raw_per_phase, distance_raw_per_phase, DistSlope )
        Population.append( [chromosome_1 , sum(energy_consumed_metre), times_metre[-1] ] )
        Nbre_iteration += 1
        c.append(time.time() - start_final - a[-1] - b[-1])
# afficher les temps de parcours et les energies consommees des chromosomes generees
# for crm in Population:
    #print(f'Ec = {crm.Fitness} ---- Tps = {crm.times_metre[-1]}')
    # print(f'Ec = {crm[1]} ---- Tps = {crm[2]}')

time_to_generate_population = time.time() - start
# print(f'creating population in {time_to_generate_population } (s)')
# print("")
# print(f'str(a) =  {sum(a)} (s)')
# print(f'str(b) =  {sum(b)} (s)')
# print(f'str(c) =  {sum(c)} (s)')

# pour avoir le meilleur de la population de depart et de le mttre dans le csv (en bas)
Population.sort( key=lambda x: x[1] , reverse = False )

#============================= 4)Tri et  Selection =============================

population_selected_Wheel = []
population_selected_Wheel = Population.copy()

#=========================================================================


start1 = time.time()
execution_time = []
#============================= 4) L'algorithme ===============================================

increment_identical_best = 0
increment_generation = 0
# Trier les chromosomes dans le sens croissant de l'energie consommee (ie: le premier est le 'best')
#population_selected_Wheel.sort( key=attrgetter('Fitness') , reverse = False )
population_selected_Wheel.sort( key=lambda x: x[1] , reverse = False )
# initialiser les meilleurs solutions connues et de generation
best_known_chromosome = population_selected_Wheel[0]
best_chromosome_of_generation = population_selected_Wheel[0]

new_generation = []

execution_crossover = []
execution_creation_chrom = []
execution_sort = []
execution_boucle_for_class = []
execution_generation = []
execution_creation_chrom1 = []
execution_fonctions = []
data_by_step = []
data_by_generation = []
indices_cross_list = []
len_indices = []
Crossover_ameliorate = [0,0,0] # un tableau pour competer le nbre de fois que chaque croisment 1,2 ou 3 a AMLIORE la solution


#=======================================================================================================
                                    # DEBUT #
#=======================================================================================================

while(increment_identical_best < limit_identical_best and increment_generation < limit_generation):
    #le debut de time pour la construction d'une generation
    start_time_generation = time.time()
    Crossover_used_nbre = [0,0,0]

    # On crée une nouvelle génération
    # for i in range(0, len(population_selected_Wheel)-1 ) :
    #     for j in range(i+1 , len(population_selected_Wheel) ):

    while len(new_generation) != len(Population):

        # On prend 2 crom aleatoirement (differents) pour les croiser, et verifier
        # qu'ils n'ont pas été deja croisés
        rand_crom_1 = random.randint(0, len(Population)-1)
        rand_crom_2 = random.randint(0, len(Population)-1)
        while rand_crom_2 == rand_crom_1 or [rand_crom_1, rand_crom_2] in indices_cross_list or [rand_crom_2, rand_crom_1] in indices_cross_list:
            rand_crom_1 = random.randint(0, len(Population)-1)
            rand_crom_2 = random.randint(0, len(Population)-1)


        # on garde les indices des cromosomes croisés pour ne pas les re-croiser
        indices_cross_list.append( [rand_crom_1, rand_crom_2] )


        #rien.append([len(population_selected_Wheel),i,j])
        #==============================================================
        start = time.time()
        #==============================================================

        # générer un nouveau chromosome en croisant 2 parents selectionnes
        rand_crois = random.randint(1, 3)
        #rand_crois = 3
        start_cross = time.time()
        if( rand_crois == 1 ):
            chromosome_child = fct.crossover_speed_mean(population_selected_Wheel[rand_crom_1][0],
                                                          population_selected_Wheel[rand_crom_2][0])
        elif(rand_crois == 2 ) :
            chromosome_child = fct.crossover_speed_and_acceleration_mean(population_selected_Wheel[rand_crom_1][0],
                                                      population_selected_Wheel[rand_crom_2][0])
        else:
            chromosome_child, use_cross_3 = fct.crossover_exchange_one_point(population_selected_Wheel[rand_crom_1][0],
                                                      population_selected_Wheel[rand_crom_2][0])

        #==============================================================
        end_cross  = time.time()
        execution_crossover.append(end_cross - start_cross)
        #==============================================================

        mutation_bool = False
        # Mutation probable du fil
        if random.random() <= Mutation_probability:
            chromosome_child = fct.mutation_chromosome(chromosome_child)
            mutation_bool = True

        start_fonctions  = time.time()
        # calcul des caractéristiques du fils (et notamment l'Energie)
        duration_raw_per_phase, duration_per_phase, distance_per_phase, distance_raw_per_phase = fct.calculate_durations(chromosome_child, dist_segment_speed, cut, spd)

        # verifier s'il n ya pas de durée négative
        acceptable_duration  = True
        for k in range(0, len(duration_raw_per_phase)):
            if duration_raw_per_phase[k] < 0 :
                acceptable_duration = False
                break
        # if acceptable_duration == False :
        #     break

        cumulative_raw_distance, energy_consumed_metre, times_metre, vts_metre,tps = fct.evaluate(chromosome_child ,duration_raw_per_phase, distance_raw_per_phase, DistSlope )

        #==============================================================
        end_fonctions  = time.time()
        execution_fonctions.append(end_fonctions - start_fonctions)
        #==============================================================

        acceptable_time = True
        if times_metre[-1] > duration_max or times_metre[-1]  < duration_min :
            acceptable_time = False
            #break

        start_creation = time.time()
        # On crée le nouveau chromosome
        #crm_child = ch.chromosome(chromosome_child, duration_per_phase, duration_raw_per_phase, spd, distance_raw_per_phase, DistSlope)

        #crm_child.plot_chromosome()
        end_creation  = time.time()
        execution_creation_chrom.append(end_creation - start_creation)

        # # verifier si l'energie n'est pas negative
        # if( crm_child.Fitness > 0 ):

        acceptable_child = True
        if( sum(energy_consumed_metre) == best_chromosome_of_generation[1] and times_metre[-1] == best_chromosome_of_generation[2]):
            acceptable_child = False
            #break
        # verifier s'il est le meilleur de sa generation
        elif( sum(energy_consumed_metre) < best_chromosome_of_generation[1] and acceptable_child == True and acceptable_duration == True and acceptable_time == True):
            start_creation1 = time.time()

            best_chromosome_of_generation = [chromosome_child, sum(energy_consumed_metre), times_metre[-1]]
            end_creation1  = time.time()
            execution_creation_chrom1.append(end_creation1 - start_creation1)

            # ajouter le crossover utilisé pour trouver ce chromosome et s'il a été muté
            # ce 'if' cest pour garder le meilleur de la generation
            if len(data_by_step) > 0:
                data_by_step.clear()

            #data_by_step.append(sum(energy_consumed_metre))
            # Verifier que si c'est vraiment l'opérateur 3 qui ete utilise ou c'etait le 2
            if rand_crois == 3:
                if use_cross_3 == False:
                    rand_crois = 2

            data_by_step.append(rand_crois)

            data_by_step.append(mutation_bool)
            data_by_step.append(rand_crom_1)
            data_by_step.append(rand_crom_2)

        # l'injecter dans la nouvelle generation, s'il n'y est pas
        if( ([chromosome_child, sum(energy_consumed_metre), times_metre[-1]] not in new_generation) and acceptable_child == True and acceptable_duration == True and acceptable_time == True):

            new_generation.append( [chromosome_child, sum(energy_consumed_metre), times_metre[-1]] )

            # Enregistrer les opérateurs de croisement utilisés pour ajouter ce 'child' à la nouvelle génération
            # Verifier que si c'est vraiment l'opérateur 3 qui ete utilise ou c'etait le 2
            if rand_crois == 3:
                if use_cross_3 == False:
                    rand_crois = 2

            Crossover_used_nbre[rand_crois -1] += 1

        # print("  ")
        # print(f'acccccepte ON EST A --- {increment_generation} -- {len(new_generation)}')
        # print("  ")

        execution_time.append(time.time() -  start )

    len_indices.append(len(indices_cross_list))
    #vider la liste des indices croisés
    indices_cross_list.clear()

    start_boucle_for_class = time.time()
    # for a in new_generation:
        # print(a[0])
    end_boucle_for_class = time.time()
    execution_boucle_for_class.append(end_boucle_for_class - start_boucle_for_class)


    start_generation = time.time()
    # on met a jour la meilleur solution de connue

    #if( best_known_chromosome[1]/3600000  > best_chromosome_of_generation[1]/3600000  ):
    if( (best_known_chromosome[1]/3600000 - best_chromosome_of_generation[1]/3600000  >= gain) or
        (best_known_chromosome[1] == best_chromosome_of_generation[1] and best_known_chromosome[2] > best_chromosome_of_generation[2]) ):

        best_known_chromosome = best_chromosome_of_generation
        increment_identical_best = 0

        # on incremente la case du croisement utilisé pour avoir ce 'best_know'
        Crossover_ameliorate[ data_by_step[0]-1 ] += 1 # le rand_crois utilisé pour avoir ce best know

        # sauvegarder comment a t on obtenu ce best_know
        data_by_step.insert(0, best_chromosome_of_generation[1]/3600000) # energie du best generation
        data_by_step.insert(0, best_known_chromosome[1]/3600000) # energie consommee du best know
        data_by_step.insert(0, best_known_chromosome[2]) # tps de trajet
        data_by_step.insert(0, increment_generation+1) # num de generation
        data_by_step.append('Ameliorée') # Il ya amélioration de la solution globale (best know)
        stabilisation_time = time.time() - start_final
    else:
        increment_identical_best += 1

        # sauvegarder comment a t on obtenu ce best_know
        # verifier si cest le premier best_know, cad qu il na pas ete obtenu avec cross ou mut (best de depart)
        if len(data_by_step) == 0:
            data_by_step.append(best_chromosome_of_generation[1]/3600000)
            data_by_step.append('')
            data_by_step.append('')
            data_by_step.append('')
            data_by_step.append('')

            data_by_step.insert(0, best_known_chromosome[1]/3600000) # energie consommee
            data_by_step.insert(0, best_known_chromosome[2]) # tps de trajet
            data_by_step.insert(0, increment_generation+1) # num de generation
            data_by_step.append('') # pas d'amélioration de la solution globale
        # best generation n'est meilleure que best know, mais il existe une best generation
        else :
            # # on supprime ce qu'il ya car ce n'est pas meuilleure que best know, et donc ca ne sert
            # # a rien de garder les informations concernant best generation
            # data_by_step.clear()

            data_by_step.insert(0, best_chromosome_of_generation[1]/3600000)

            data_by_step.insert(0, best_known_chromosome[1]/3600000) # energie consommee
            data_by_step.insert(0, best_known_chromosome[2]) # tps de trajet
            data_by_step.insert(0, increment_generation+1) # num de generation
            data_by_step.append('') # pas d'amélioration de la solution globale

    # limite de generation
    increment_generation += 1


    # print(f'---------- increment_generation = {increment_generation} and increment_identical_best = {increment_identical_best} ----------------------------------------------------------------------------------------')

    # Trier notre generation dans l'odre decroissant de l'energie consommee
    #new_generation_tmp = new_generation.copy()
    new_generation.sort( key=lambda x: x[1] , reverse = True )

    # calculer la somme de toutes les energies consommees, pour former le determinateur
    sum_fitness = 0
    for crm in new_generation:
        sum_fitness += crm[1]

    # faire une copie de l'anciene generation pour completer la nouvelle selectionnee avec les meilleurs
    previous_generation = population_selected_Wheel.copy()
    population_selected_Wheel.clear()

    # Affecter une probabilite a chacun des chromosomes, en fct de leurs energies et les selectionner
    # selon la proba de selection donnée en entrée

    sum_iterate = 0
    for crm in new_generation:
        sum_iterate += crm[1]
        if sum_fitness == 0 :
            population_selected_Wheel = new_generation.copy()
            break
        elif( (sum_iterate/sum_fitness) >= Selection_probability ):
            population_selected_Wheel.append(crm)

    # La taille de la population selectionnée (l'ajouter aux data finaux)
    if increment_generation-1 > 0 :
        data_by_step.append( round(100*len(population_selected_Wheel)/float(Population_size),2) )
    else:
         data_by_step.append(100)  # a la premiere itération toute la population est selectionee


    start_sort = time.time()
    # completer la nouvelle selectionnee avec des chromosomes de l'ancienne generation (choisis aleatoirement)
    # jusuqu'a atteindre la taille de la population initiale
    previous_generation.sort( key=lambda x: x[1] , reverse = False)

    #==============================================================
    end_sort  = time.time()
    execution_crossover.append(end_sort - start_sort)
    #==============================================================

    k = 0
    while len(population_selected_Wheel) < len(Population) and k < len(previous_generation):
        #population_selected_Wheel.append(previous_generation.pop( random.randint( 0, len(previous_generation)-1 ) ) )
        if previous_generation[k] not in population_selected_Wheel :
            population_selected_Wheel.append(previous_generation[k])
        k += 1

    # si on trouve plus de chromosome de la generation precedente a rajouter, on en rajoute des random
    # while k == len(previous_generation) and len(population_selected_Wheel) < len(Population) :

    population_selected_Wheel.sort( key=lambda x: x[1] , reverse = False )

    # print(f'-------------------- taille de pop_wheel {len(population_selected_Wheel)} ---------')
    # on verifie que la nouvelle population selectionnee n'est pas reduite a 1 chrom ou rien
    # if( len(population_selected_Wheel) <= 1 ):
    #     break
    #==========================================================================================================

    # Ajouter le temps de consructtion d'une generation aux 'datas' de la generation
    end_time_generation = time.time()
    data_by_step.insert(2, end_time_generation - start_time_generation)

    # calcul de l'ecart-type de la generation et sa moyenne (en energie), et les ajouter aux donnees du csv
    standard_deviation_generation = statistics.pstdev([chld[1] for chld in new_generation ])
    mean_generation = statistics.mean([chld[1] for chld in new_generation ])
    data_by_step.append(standard_deviation_generation/3600000)
    data_by_step.append(mean_generation/3600000)

    # injecter ds les datas de chaque génération, le nbre de fois ou chaque croisment a creer un child 'realisable' pour la nvlle generation
    data_by_step.append(Crossover_used_nbre[0]) #
    data_by_step.append(Crossover_used_nbre[1])
    data_by_step.append(Crossover_used_nbre[2])


    # copier toutes les informations obtenues de cette génération, et l'injecter dans les datas finaux
    data_by_generation.append(data_by_step.copy())
    data_by_step.clear()


    #vider la liste new_generation et celle qui contient le nbre d'utilisation de chaque croisement
    new_generation.clear()
    Crossover_used_nbre.clear()

#==================== Ecrire les data des generations ===========================
# calcul des 3 moyennes et ecart type du nbre d'utilisation des croisement dans chaque essai
mean_nbre_cross_1 =  statistics.mean( [ dt[-3] for dt in data_by_generation ] )
mean_nbre_cross_2 =  statistics.mean( [ dt[-2] for dt in data_by_generation ] )
mean_nbre_cross_3 =  statistics.mean( [ dt[-1] for dt in data_by_generation ] )

standard_deviation_use_cross_1_by_test = statistics.pstdev( [ dt[-3] for dt in data_by_generation ] )
standard_deviation_use_cross_2_by_test = statistics.pstdev( [ dt[-2] for dt in data_by_generation ] )
standard_deviation_use_cross_3_by_test = statistics.pstdev( [ dt[-1] for dt in data_by_generation ] )

# calcul de l'ecart-type de la population de depart et sa moyenne (de l'energie)
standard_deviation_starting_population = statistics.pstdev([p[1] for p in Population])
mean_starting_population = statistics.mean([p[1] for p in Population])

# On injecte les résultats dans un fichier csv
data_by_generation.insert(0,['Num generation','Tps trajet [s]','TC [s]', 'Ec globale [kWh]', 'Ec locale [kWh]',
                             'Cross ameliorate num','Mutation', 'Parent 1', 'Parent 2', 'Amélioration', '% de la population selectionée' , 'Ecart_type [kWh]' ,'Moy Ec [kWh]'
                             ,'cross 1 (speed mean)','cross 2 (speed + accel mean)','cross 3 (exchange)'])

# datas de la population de depart
data_by_generation.insert(1,[0,Population[0][2],time_to_generate_population,
                             Population[0][1]/3600000, Population[0][1]/3600000,
                             '','', '', '', '', '',
                             standard_deviation_starting_population/3600000, # pas la peine de convertir en kWh car cest le pourczntage qu'on cherche
                             mean_starting_population/3600000 , '', '', ''])

# fct.writeCsv_by_test(data_by_generation,"Trajet (par etape){Pop = "+str(Population_size)+
#                             ", PS = "+str(Selection_probability)+
#                             ", PM = "+str(Mutation_probability)+
#                             ", Generation = "+str(limit_generation)+
#                             " }" )
# vider les donnees de la generation, pour avoir celles de la prochaine
data_by_generation.clear()

#================================================================================

# print(" ")
# print(f'Fitness of best_chromosome_of_generation.Fitness = {best_chromosome_of_generation[1]}')
# print(" ")
# print(f'Fitness of best_known_chromosome = {best_known_chromosome[1]}')
# print("")
# print(" ")
# print(f'Duration of best_known_chromosome = {best_known_chromosome[2]}')
# print("The time used to execute this is given below")

end_final = time.time()

print(end_final - start_final)

# Recolter les resultat pour les Ecrire dans un fichier csv
DataFinal.append([Population_size, limit_generation ,Selection_probability , Mutation_probability,
                      end_final - start_final , float(best_known_chromosome[1])/3600000, float(limit_generation) - float(increment_identical_best)   ,
                      stabilisation_time ,float(best_known_chromosome[2]), Crossover_ameliorate[0], Crossover_ameliorate[1], Crossover_ameliorate[2],
                      best_known_chromosome[0],
                      mean_nbre_cross_1, mean_nbre_cross_2, mean_nbre_cross_3,
                      standard_deviation_use_cross_1_by_test,
                      standard_deviation_use_cross_2_by_test,
                      standard_deviation_use_cross_3_by_test,
                      '',
                      increment_generation, increment_identical_best, sum(execution_creation_chrom), sum(execution_fonctions)])



#==============================================================
end_generation  = time.time()
execution_generation.append(end_generation - start_generation)
a.clear()
b.clear()
c.clear()

#====================== plot juste pour separere pour savoir quels plots appartiennt a un run ou pas

# plt.figure(figsize=(10,5))
# plt.plot(2*spd, 'black')
# plt.grid()
# plt.show()

#=================================================================

# calcul de moyenne d'energie, de temps pour que ca se stabilise et de génération pour stabilise
mean_energie = 0
mean_time_stabilisation = 0
mean_stabilisation_generation = 0
mean_use_crossover_1 = 0
mean_use_crossover_2 = 0
mean_use_crossover_3 = 0

for l in DataFinal:
    mean_energie  += l[5]
    mean_time_stabilisation += l[7]
    mean_stabilisation_generation += l[6]
    mean_use_crossover_1 += l[9]
    mean_use_crossover_2 += l[10]
    mean_use_crossover_3 += l[11]

mean_energie = mean_energie/len(DataFinal)
mean_time_stabilisation = mean_time_stabilisation/len(DataFinal)
mean_stabilisation_generation = mean_stabilisation_generation/len(DataFinal)
mean_use_crossover_1 = mean_use_crossover_1/len(DataFinal)
mean_use_crossover_2 = mean_use_crossover_2/len(DataFinal)
mean_use_crossover_3 = mean_use_crossover_3/len(DataFinal)


# calculer les ecarts type de ceux d'au dessus en pourcentage

Deviation_energie_lst = [d[5] for d in DataFinal]
Deviation_time_lst = [d[7] for d in DataFinal]
Deviation_generation_lst = [d[6] for d in DataFinal]

standard_deviation_energie = statistics.pstdev( Deviation_energie_lst )
standard_deviation_time = statistics.pstdev( Deviation_time_lst )
standard_deviation_generation = statistics.pstdev( Deviation_generation_lst )
standard_deviation_cross_1 = statistics.pstdev( [d[9] for d in DataFinal] )
standard_deviation_cross_2 = statistics.pstdev( [d[10] for d in DataFinal] )
standard_deviation_cross_3 = statistics.pstdev( [d[11] for d in DataFinal] )

# % de l'ecart type de l'energie par rapport a la moyenne (coeff de variation)
if mean_energie != 0:
    standard_deviation_energie_percent = standard_deviation_energie*100/mean_energie
else:
    standard_deviation_energie_percent = 0

# % de l'ecart type du nbre de generation avant stabilisation par rapport a la moyenne (coeff de variation)
if mean_stabilisation_generation != 0:
    standard_deviation_generation_percent = standard_deviation_generation*100/mean_stabilisation_generation
else:
    standard_deviation_generation_percent = 0

# % de l'ecart type du temps de stabilisation par rapport a la moyenne (coeff de variation)
if mean_time_stabilisation != 0:
    standard_deviation_time_percent = standard_deviation_time*100/mean_time_stabilisation
else:
    standard_deviation_time_percent = 0

# % de l'ecart type de l'utilisation du 1e operateur de croisment par rapport a la moyenne
if mean_use_crossover_1 != 0:
    standard_deviation_cross_1_percent = standard_deviation_energie*100/mean_use_crossover_1
else:
    standard_deviation_cross_1_percent = 0

# % de l'ecart type de l'utilisation du 2e operateur de croisment par rapport a la moyenne
if mean_use_crossover_2 != 0:
    standard_deviation_cross_2_percent = standard_deviation_energie*100/mean_use_crossover_2
else:
    standard_deviation_cross_2_percent = 0

# % de l'ecart type de l'utilisation du 3e operateur de croisment par rapport a la moyenne
if mean_use_crossover_3 != 0:
    standard_deviation_cross_3_percent = standard_deviation_energie*100/mean_use_crossover_3
else:
    standard_deviation_cross_3_percent = 0

#===========================================================================================
# Calculer les moyennes et ecarts-type pour les resultats de chauque trajet
# cad: chaque essai a une moyenne d'utilisation de chaque croisement, nous calculons la moyenne des 5 essais
# (la moyenne des moyennes des essais)
mean_nbre_cross_1_by_route = statistics.mean(dr[-11] for dr in DataFinal)
mean_nbre_cross_2_by_route = statistics.mean(dr[-10] for dr in DataFinal)
mean_nbre_cross_3_by_route = statistics.mean(dr[-9] for dr in DataFinal)

standard_deviation_use_cross_1_by_route = statistics.pstdev(dr[-11] for dr in DataFinal)
standard_deviation_use_cross_2_by_route = statistics.pstdev(dr[-10] for dr in DataFinal)
standard_deviation_use_cross_3_by_route = statistics.pstdev(dr[-9] for dr in DataFinal)

# on ajoute 2 lignes vides pour séparer les infos :
DataFinal.append(['', '', '', '', '', '',  '', '', '','', '', '', '', '', '', '', ''])
DataFinal.append(['', '', '', '', '', '',  '', '', '','', '', '', '', '', '', '', ''])

DataFinal.append(['', '',  '', '', 'Moyenne: ',
                  mean_energie, mean_stabilisation_generation , mean_time_stabilisation ,
                  '', mean_use_crossover_1, mean_use_crossover_2, mean_use_crossover_3, ''])

DataFinal.append(['', '',  '', '', 'Ecart type: ',
                  standard_deviation_energie, standard_deviation_generation , standard_deviation_time ,
                  '', standard_deviation_cross_1, standard_deviation_cross_2 , standard_deviation_cross_3, ''])

# On injecte les résultats dans un fichier csv
DataFinal.insert(0,['Population', 'Génération', 'Selection proba ',
                    'Mutation proba', 'Time calc [s]', 'Energie cons [kWh]', 'Stabili_generation', 'Stabili_time [s]' ,
                    'duration travel [s]', 'Cross 1', 'Cross 2', 'Cross 3', 'Best chrom table' ,
                    'Mean use cross 1', 'Mean use cross 2', 'Mean use cross 3',
                    'Deviation use cross 1', 'Deviation use cross 2', 'Deviation use cross 3',
                    '' ,
                    'Increment gener','increment identical best', 'time call class [s]', 'time call fonctions [s]'])

# fct.writeCsv_all_Tets(DataFinal,"Trajet global {Pop = "+str(Population_size)+
#                             ", PS = "+str(Selection_probability)+
#                             ", PM = "+str(Mutation_probability)+
#                             ", Generation = "+str(limit_generation)+
#                             " }" )


#----------------------------- Data pour chaque trajet --------------------------------

# pour les données finax. Cad: pour chaque trajet (Vmax, Slope)
DataRoute.append([
       Population_size, limit_generation ,Selection_probability ,
       Mutation_probability, mean_energie,
       mean_stabilisation_generation, mean_time_stabilisation,
       mean_use_crossover_1, mean_use_crossover_2, mean_use_crossover_3,
       standard_deviation_energie_percent, standard_deviation_generation_percent, standard_deviation_time_percent,
       standard_deviation_cross_1_percent, standard_deviation_cross_2_percent, standard_deviation_cross_3_percent,
       '',
       mean_nbre_cross_1_by_route, mean_nbre_cross_2_by_route, mean_nbre_cross_3_by_route,
       standard_deviation_use_cross_1_by_route,
       standard_deviation_use_cross_2_by_route,
       standard_deviation_use_cross_3_by_route
       ])

# print( ""  )
DataFinal.clear()

DataRoute.insert(0,['Population', 'Generation', 'Selection proba ',
                    'Mutation proba', 'Energie cons mean [kWh]', 'Stabili_generation mean', 'Stabili_time mean [s]' ,
                    'Cross 1 (speed mean)', 'Cross 2 (spd + accel mean)', 'Cross 3 ( one point exchange)',
                    'Deviation EC [%]', 'Deviation gener [%]', 'Deviation time stab [%]',
                    'Deviation cross 1 [%]', 'Deviation cross 2 [%]', 'Deviation cross 3 [%]',
                    '',
                    'Use cross 1 (speed mean)', 'Use cross 2 mean (speed + accel mean)', 'Use cross 3 mean (exchange)',
                    'Deviation use cross 1 (speed mean)',
                    'Deviation use cross 2 (speed + accel mean)',
                    'Deviation use cross 3 (exchange)',
                    ])

DataRoute.clear()

final_completo = time.time()
print(final_completo - comienzo)

#======================   Ploter la solution  =================================================

if plot_best_solution :
    import matplotlib.pyplot as plt

    #-------------------- Plot best solution found -------------------------------------------------

    duration_raw_per_phase, duration_per_phase, distance_per_phase, distance_raw_per_phase = fct.calculate_durations(best_known_chromosome[0] , dist_segment_speed, cut, spd)

    fct.plot_chromosome( best_known_chromosome[0] ,spd, duration_per_phase, duration_raw_per_phase, plot_title)

    #-------------------- Plot energie -------------------------------------------------

    Cumulative_energie = []
    tmp = 0
    for e in energy_consumed_metre:
        tmp+= e
        Cumulative_energie.append( tmp/3600 )


    plt.figure(figsize=(10,5))
    plt.plot(times_metre,Cumulative_energie)


    #plt.plot(duration_plot, vitesses, 'o')
    plt.xlabel("Time(s)")
    plt.ylabel("Eneegie ")
    plt.legend(['Energie'])
    #plt.legend(['Speed','Speed Max', 'Speed min'])
    #plt.fill_between(duration_plot,vitesses,alpha=0.1)
    plt.grid()
    plt.show()

    #-------------------- Plot vitesse -------------------------------------------------


    # plt.figure(figsize=(10,5))
    # plt.plot(times_metre,vts_metre)


    # #plt.plot(duration_plot, vitesses, 'o')
    # plt.xlabel("Time(s)")
    # plt.ylabel("Speed (m/s)")
    # plt.legend(['Speed'])
    # #plt.legend(['Speed','Speed Max', 'Speed min'])
    # #plt.fill_between(duration_plot,vitesses,alpha=0.1)
    # plt.grid()
    # plt.show()

    #-------------------- Plot Pente -------------------------------------------------

    plt.figure(figsize=(10,5))
    plt.plot(times_metre,[ d[1] for d in DistSlope[:len(times_metre)] ])


    #plt.plot(duration_plot, vitesses, 'o')
    plt.xlabel("Time(s)")
    plt.ylabel("Slope (m/s)")
    plt.legend(['Slope'])
    #plt.legend(['Speed','Speed Max', 'Speed min'])
    #plt.fill_between(duration_plot,vitesses,alpha=0.1)
    plt.grid()
    plt.show()

    #-------------------- Plot Distance -------------------------------------------------

    plt.figure(figsize=(10,5))
    plt.plot(times_metre,[ d[0] for d in DistSlope[:len(times_metre)] ])


    #plt.plot(duration_plot, vitesses, 'o')
    plt.xlabel("Time(s)")
    plt.ylabel("Distance (m/s)")
    plt.legend(['Distance [m]'])
    #plt.legend(['Speed','Speed Max', 'Speed min'])
    #plt.fill_between(duration_plot,vitesses,alpha=0.1)
    plt.grid()
    plt.show()


