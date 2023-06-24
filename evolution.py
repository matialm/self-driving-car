from car import Car

class Evolution:
    def __init__(self):
        self.__initial_population = 5
        self.__mutation_rate = 0.001
        self.__population = []
        self.__generation = 0

    def __selection(self):
        population = self.__population
        for item in population:
            car = item["car"]
            item["score"] = car.get_distance()

        population_ordered = sorted(population, key=lambda d: d["score"], reverse=True)
        self.__population = population_ordered
        
        return population_ordered[0:2]

    def __crossover(self, parent1, parent2):
        chromosome1 = parent1["car"].get_chromosome()
        chromosome2 = parent2["car"].get_chromosome()

        size = len(chromosome1)
        middle_point = int(size/2)

        child_chromosome = chromosome1[0:middle_point] + chromosome2[middle_point:size]
        child_car = Car()
        child_car.set_chromosome(child_chromosome)

        return child_car

    def __mutate(self, child_car):
        pass

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
        parent1, parent2 = self.__selection()
        child_car = self.__crossover(parent1, parent2)
        self.__mutate(child_car)

        new_population = self.__population[:-1]

        for item in new_population:
            item["car"].reset_state()

        new_population.append({
            "score": 0,
            "car": child_car
        })

        self.__population = new_population
        print(len(new_population))