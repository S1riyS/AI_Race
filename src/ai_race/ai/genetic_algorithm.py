"""
Based on https://github.com/kiecodes/genetic-algorithms/tree/master
"""

import typing as t
from random import choice, choices, randint, randrange, uniform

import numpy as np

from ai import NeuralNetwork


class Individual(t.NamedTuple):
    neural_network: NeuralNetwork
    fitness: float


Population = t.Sequence[Individual]
SortFunction = t.Callable[[Population], Population]
SelectionFunction = t.Callable[[Population], t.Annotated[t.List[Individual], 2]]
CrossoverFunction = t.Callable[[Individual, Individual], t.Tuple[Individual, Individual]]
MutationFunction = t.Callable[[Individual], Individual]


def _fitness_based_sort(population: Population) -> Population:
    """Sorts population by the fitness of the individual"""
    return sorted(population, key=lambda individual: individual.fitness, reverse=True)


def _fitness_based_selection(population: Population) -> t.Annotated[t.List[Individual], 2]:
    """Selects two random individuals from population based on their fitness"""
    return choices(
        population=population,
        weights=[individual.fitness for individual in population],
        k=2
    )


def _get_flatten_weights(weights: np.ndarray) -> t.Tuple[t.Tuple[int, ...], np.ndarray]:
    """Returns original shape of an array and its flatten version

    :param weights: numpy array with weight of neural network layer
    """
    original_shape = weights.shape
    flatten_weights = weights.flatten()
    return original_shape, flatten_weights


def _single_point_crossover(
        a: Individual,
        b: Individual,
        point: t.Optional[int] = None
) -> t.Tuple[Individual, Individual]:
    """Single Point Crossover is a form of crossover in which two-parent chromosome are
    selected and a random/given point is selected and the genes/data are
    interchanged between them after the given/selected point for example

    :param a: :class:`Individual` instance (father)
    :param b: :class:`Individual` instance (mother)
    :param point: Point after which weights will be interchanged, default = None

    :raises ValueError: If shapes of layers are different
    """
    for layer_a, layer_b in zip(a.neural_network.weighted_layers, b.neural_network.weighted_layers):
        weights_a = layer_a.weights
        weights_b = layer_b.weights

        if weights_a.shape != weights_b.shape:
            raise ValueError('Layers\' weights must have the same shape')

        shape, flatten_weights_a = _get_flatten_weights(weights_a)
        _, flatten_weights_b = _get_flatten_weights(weights_a)

        length = len(flatten_weights_a)
        if point is None:
            p = randint(1, length - 1)
        else:
            if 1 <= point <= length - 1:
                p = point
            else:
                p = randint(1, length - 1)

        reshaped_weights_a = np.concatenate([flatten_weights_a[:p], flatten_weights_b[p:]]).reshape(shape)
        reshaped_weights_b = np.concatenate([flatten_weights_b[:p], flatten_weights_a[p:]]).reshape(shape)

        layer_a.weights = reshaped_weights_a
        layer_b.weights = reshaped_weights_b

    return a, b


def _random_mutation(individual: Individual, num: int = 1, probability: float = 0.5) -> Individual:
    """Applies mutation to weights of neural network

    :param individual: :class:`Individual` class instance
    :param num: Number of mutations
    :param probability: Probability of mutation (from 0 to 1)
    """

    for _ in range(num):
        if uniform(0, 1) < probability:
            layer = choice(individual.neural_network.weighted_layers)
            shape, flatten_weights = _get_flatten_weights(layer.weights)

            index = randrange(len(flatten_weights))
            flatten_weights[index] = abs(flatten_weights[index] - uniform(-1, 1))
            layer.weights = flatten_weights.reshape(shape)

    return individual


def run_evolution(
        population: Population,
        sort_function: SortFunction = _fitness_based_sort,
        selection_function: SelectionFunction = _fitness_based_selection,
        crossover_function: CrossoverFunction = _single_point_crossover,
        mutation_function: MutationFunction = _random_mutation
) -> t.Sequence[NeuralNetwork]:
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

    # Extracting neural networks from all individuals of next generation
    next_generation_neural_networks = []
    for individual in next_generation:
        next_generation_neural_networks.append(individual.neural_network)

    return next_generation_neural_networks


def print_population(population: Population) -> None:
    population_size = len(population)
    fitness_list = [individual.fitness for individual in population]
    average_fitness = sum(fitness_list) / population_size
    max_fitness = max(fitness_list)
    print(f'Population size: {population_size}, Average fitness: {average_fitness}, Max fitness: {max_fitness}')
    print('-' * 20)
