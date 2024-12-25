import pygame as pg
import sys
import math
import random

#GA Parameters
POPULATION_SIZE = 1000
GENOME_LENGTH = 40
MUTATION_RATE = 0.4
#CROSSOVER_RATE = 0.5
GENERATIONS = 200

#GA Functions
def create_genome():
    return sorted(random.randint(600, 11000) for _ in range(GENOME_LENGTH))

def mutate_genome(genome, fitness):
    """
    Mutate the genome by adding Gaussian noise to genes greater than the player's fitness.
    """
    return sorted(
        gene + (int(random.gauss(0, 100)) if gene > fitness and random.random() < MUTATION_RATE else 0)
        for gene in genome
    )

def tint_image(image, color):
    """Apply a color tint to an image."""
    tinted_image = image.copy()
    tint = pg.Surface(tinted_image.get_size()).convert_alpha()
    tint.fill(color)
    tinted_image.blit(tint, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return tinted_image

def crossover_genomes(parent1, parent2):
    """
    Perform blend crossover by interpolating values between the parents with a random factor.
    """
    child = []
    for g1, g2 in zip(parent1, parent2):
        alpha = random.uniform(0.4, 0.6)  # Blend factor between 0.4 and 0.6
        child_gene = int(alpha * g1 + (1 - alpha) * g2)
        child.append(child_gene)
    return sorted(child)

def select_parents(population):
    """
    Select parents using tournament selection.
    """
    tournament_size = 3
    tournament = random.sample(population, tournament_size)
    parent1 = max(tournament, key=lambda x: x[1])
    tournament = random.sample(population, tournament_size)
    parent2 = max(tournament, key=lambda x: x[1])
    return parent1, parent2

def preserve_elite(population, elite_count= math.ceil(POPULATION_SIZE/2)):
    """
    Preserve the top-performing individuals as elites to carry over to the next generation.
    """
    return sorted(population, key=lambda x: x[1], reverse=True)[:elite_count]

def evaluate_fitness(player, spikes, platforms):
    fitness = player.distance_traveled

    # Penalize collisions with spikes or spikebeds
    if pg.sprite.spritecollideany(player, spikes):
        fitness -= 100

    # Bonus for reaching further distances
    return max(fitness, 0)

def calculate_average_genome(population):
    """
    Calculate the average genome from a population of genomes.
    
    Parameters:
        population (list): A list of genomes, where each genome is a list of integers.
        
    Returns:
        list: A genome representing the average values of the input population.
    """
    if not population or not population[0][0]:
        return []

    genome_length = len(population[0][0])
    average_genome = [0] * genome_length

    for i in range(genome_length):
        gene_sum = sum(individual[0][i] for individual in population)  # Sum of ith gene across all genomes
        average_genome[i] = gene_sum // len(population)  # Average the sum

    return average_genome