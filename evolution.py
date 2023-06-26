from car import Car
import numpy as np
import random
import sys

class Evolution:
    def __init__(self):
        self.__initial_population = 5
        self.__cross_number = 2
        self.__max_population = self.__initial_population + self.__cross_number
        self.__mutation_rate = 0.05
        self.__population = []
        self.__generation = 0

    def __selection(self):
        population = self.__population
        for item in population:
            car = item["car"]
            distance = car.get_distance()
            back_score = -10000 if car.went_backwards() else 0
            forward_first_score = -10000 if car.went_forward_first() else 0
            forward_only_score = -10000 if car.went_forward_only() else 0
            #quiero que vaya para adelante y no sea solo un camino recto
            score = forward_first_score + distance
            item["score"] = score

        population_ordered = sorted(population, key=lambda d: d["score"], reverse=True)
        self.__population = population_ordered

        #parent1 = population_ordered[0]
        #parent2 = random.choice(population_ordered)
        #parents = [parent1, parent2]

        max_parent = 2*self.__cross_number
        parents = population_ordered[0:max_parent]

        random.shuffle(parents)

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

        self.__population = population