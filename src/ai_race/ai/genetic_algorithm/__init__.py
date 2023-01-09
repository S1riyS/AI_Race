"""
Based on https://github.com/kiecodes/genetic-algorithms/tree/master
"""

import typing as t
from random import choice, choices, randrange, uniform

from ai.neural_network import NeuralNetwork
from .crossovers import uniform_crossover


class Individual(t.NamedTuple):
    neural_network: NeuralNetwork
    fitness: float = 0


Population = t.Sequence[Individual]
SortFunction = t.Callable[[Population], Population]
SelectionFunction = t.Callable[[Population], t.Annotated[t.List[Individual], 2]]
MutationFunction = t.Callable[[Individual], Individual]
CrossoverFunction = t.Callable[[Individual, Individual], t.Tuple[Individual, Individual]]


def _fitness_based_sort(population: Population) -> Population:
    """Sorts population by the fitness of the individual"""
    return sorted(population, key=lambda individual: individual.fitness, reverse=True)


def _fitness_based_selection(population: Population) -> t.Annotated[t.List[Individual], 2]:
    """Selects two random individuals from population based on their fitness"""
    min_fitness = min([individual.fitness for individual in population])
    return choices(
        population=population,
        weights=[individual.fitness - min_fitness for individual in population],
        k=2
    )


def _random_mutation(individual: Individual, num: int = 1, probability: float = 0.5) -> Individual:
    """Applies mutation to weights of neural network

    :param individual: :class:`Individual` class instance
    :param num: Number of mutations
    :param probability: Probability of mutation (from 0 to 1)
    """

    for _ in range(num):
        if uniform(0, 1) <= probability:
            layer = choice(individual.neural_network.weighted_layers)

            shape = layer.weights.shape
            flatten_weights = layer.weights.flatten()

            index = randrange(len(flatten_weights))
            flatten_weights[index] += uniform(-2.0, 2.0)
            layer.weights = flatten_weights.reshape(shape)

    return individual


def run_evolution(
        population: Population,
        sort_function: SortFunction = _fitness_based_sort,
        selection_function: SelectionFunction = _fitness_based_selection,
        crossover_function: CrossoverFunction = uniform_crossover,
        mutation_function: MutationFunction = _random_mutation
) -> Population:
    """
    Runs evolution of given population

    :param population: Population to evolve
    :param sort_function: Function of sorting population in a certain order
    :param selection_function: Function of selecting two individuals
    :param crossover_function: Function of crossing two individuals
    :param mutation_function: Mutation function of an individual
    :return: Sequence of neural networks from all individuals of the next generation
    """
    population = sort_function(population)
    population_size = len(population)

    next_generation = population[0:2 + (population_size % 2)]
    for j in range(int(population_size / 2) - 1):
        parents = selection_function(population)
        father = parents[0]
        mother = parents[1]

        offspring_a, offspring_b = crossover_function(father, mother)
        offspring_a = mutation_function(offspring_a)
        offspring_b = mutation_function(offspring_b)

        next_generation += [offspring_a, offspring_b]

    return next_generation


def print_population(population: Population) -> None:
    population_size = len(population)
    fitness_list = [individual.fitness for individual in population]
    average_fitness = sum(fitness_list) / population_size
    max_fitness = max(fitness_list)
    print(f'Population size: {population_size}, Average fitness: {average_fitness}, Max fitness: {max_fitness}')
    print('-' * 20)
