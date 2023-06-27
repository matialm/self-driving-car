from car import Car
import numpy as np
import random
import sys

class Evolution:
    def __init__(self):
        self.__initial_population = 10
        self.__cross_number = 4
        self.__max_population = self.__initial_population + self.__cross_number
        self.__mutation_rate = 0.05
        self.__population = []
        self.__generation = 0

    def __selection(self):
        population = self.__population
        for item in population:
            car = item["car"]
            distance = car.get_distance()
            forward_first_score = -int(sys.maxsize/8) if not car.went_forward_first() else 0
            forward_only_score = -int(sys.maxsize/12) if car.went_forward_only() else 0
            ping_pong_score = -int(sys.maxsize/4) if car.ping_pong_at_least_one_time() else 0
            score = ping_pong_score + forward_first_score + forward_only_score + distance
            item["score"] = score

        population_ordered = sorted(population, key=lambda d: d["score"], reverse=True)
        self.__population = population_ordered

        #max_parent = 2*self.__cross_number
        #parents = population_ordered[0:max_parent]
        parents = None
        cross_number = self.__cross_number
        best_parents = population_ordered[0:cross_number]
        random_parents = random.sample(population_ordered[cross_number:], cross_number)

        if cross_number > 1:
            parents = []
            for i in range(len(best_parents)):
                parents.append(best_parents[i])
                parents.append(random_parents[i])
        else:
            parents = [best_parents, random_parents]

        return parents

    def __crossover(self, parents):
        children = []
        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[i+1]

            chromosome1 = parent1["car"].get_chromosome()
            chromosome2 = parent2["car"].get_chromosome()

            size = len(chromosome1)
            section_size = int(size/4)

            child_chromosome = chromosome1[0:section_size] + chromosome2[section_size:2*section_size] + chromosome1[2*section_size:3*section_size] + chromosome2[3*section_size:4*section_size]
            
            #if child_chromosome == chromosome1 or child_chromosome == chromosome2:
            #    random.shuffle(child_chromosome)

            child_car = Car()
            child_car.set_chromosome(child_chromosome)
            children.append(child_car)

        return children

    def __mutate(self, children):
        for child in children:
            random_value = random.random()

            if random_value <= self.__mutation_rate:
                chromosome = child.get_chromosome()

                size = len(chromosome)
                random_index1 = random.randrange(size)
                random_index2 = random.randrange(size)

                #chromosome[random_index1] = chromosome[random_index2]
                a = -sys.maxsize
                b = sys.maxsize
                chromosome[random_index1] = ((b - a) * np.random.random_sample(1) + a)[0]
                #chromosome[random_index2] = ((b - a) * np.random.random_sample(1) + a)[0]

                child.set_chromosome(chromosome)

    def get_population(self):
        cars = [item["car"] for item in self.__population]
        return cars

    def create_initial_population(self):
        for i in range(self.__initial_population):
            self.__population.append({
                "score": 0,
                "car": Car()
            })

    def create_next_generation(self):
        self.__generation += 1
        parents = self.__selection()
        children = self.__crossover(parents)
        self.__mutate(children)

        population = self.__population
        if len(population) > self.__max_population:
            population = population[:-self.__cross_number]

        for item in population:
            item["car"].reset_state()

        for child in children:
            population.append({
                "score": 0.0,
                "car": child
            })
        
        print(self.__population)
        self.__population = population