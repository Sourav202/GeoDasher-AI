import pygame as pg
import sys
import math
from classdefs import WIDTH, FPS, SCROLL_SPD, DEF_GROUND_LVL, BUFFER, COLORS, bg_img, screen
from classdefs import Player, Ground, Spike, Large_Platform, Small_Platform, SpikeBed, Block, ProgressBar, Goal
from GA import POPULATION_SIZE, GENERATIONS
from GA import create_genome, mutate_genome, crossover_genomes, select_parents, preserve_elite, calculate_average_genome

def is_colliding_with_spike(player, spike):
    """Check if the player collides with a triangular spike."""
    
    spike_left_face = ((spike.rect.left, spike.rect.bottom), (spike.rect.centerx, spike.rect.top))
    spike_right_face = ((spike.rect.centerx, spike.rect.top), (spike.rect.right, spike.rect.bottom))

    # Check if the player is clipping the triangle's faces
    if(player.rect.clipline(spike_left_face) or player.rect.clipline(spike_right_face)):
        return True
    return False

def check_collision(player, block):
    """
    Handles collision between the player and a block or a large platform.
    Safe if the player lands on top of the platform.
    Dies if the player touches the sides or bottom of the platform.
    """
    
    # Check if the player's rectangle collides with the platform's rectangle
    if player.rect.colliderect(block.rect):
        #print(player.rect.left, block.rect.right)
        # Top collision: Safe landing
        if player.velocity < 0:  # Player is jumping upward
            return False
        
        if (
            player.rect.bottom <= block.rect.top + BUFFER + 10 # Small buffer for landing
            and player.rect.right >= block.rect.left + BUFFER # Avoid left edge false positives
            and player.rect.left <= block.rect.right + BUFFER # Avoid right edge false positives
            and player.velocity >= 0
        ):
            # Correct the player's position and allow jumping
            player.rect.bottom = block.rect.top
            player.ground_level = block.rect.top
            player.velocity = 0
            player.is_jumping = False
            return False
        # Side or bottom collision: Death
        else:
            #print("Player hit the side or bottom of the platform!")
            return True  # Signal death
    #No collision
    return False

def initialize_objects(population):
    """
    Initializes all objects
    """
    grounds = pg.sprite.Group()
    players = [
    Player(genome, idx)
    for idx, (genome, _) in enumerate(population)
    ]
    player_group = pg.sprite.Group(players)
    spikes = pg.sprite.Group()
    blocks = pg.sprite.Group()
    small_platforms = pg.sprite.Group()
    large_platforms = pg.sprite.Group()
    spikebeds = pg.sprite.Group()
    goal = Goal(13250, 330)
    goal_group = pg.sprite.Group(goal)
    
    grounds.add(
        Ground(0, 430),
        Ground(WIDTH, 430)
    )
    
    spikes.add(
        Spike(1000, 380),
        Spike(1500, 380),
        Spike(1550, 380),
        Spike(2050, 380),
        Spike(2100, 380),
        Spike(3300, 380),
        Spike(3350, 380),
        Spike(4350, 330),
        Spike(5200, 280),
        Spike(7250, 230),
        Spike(7300, 230),
        Spike(7350, 230),
        Spike(7400, 230),
        Spike(7650, 230),
        Spike(7700, 230),
        Spike(7750, 230),
        Spike(7800, 230),
        Spike(8250, 188),
        Spike(8300, 188),
        Spike(8350, 188),
        Spike(8400, 188),
        Spike(8800, 230),
        Spike(8850, 330),
        Spike(9600, 330),
        Spike(10000, 380),
        Spike(11500, 130),
    )
    
    blocks.add(
        Block(2150, 380),
        Block(2350, 380),
        Block(2350, 330),
        Block(2550, 380),
        Block(2550, 330),
        Block(2550, 280),
    )
    
    large_platforms.add(
        Large_Platform(3600, 380, (350, 50)),
        Large_Platform(4100, 380, (550, 50)),
        Large_Platform(4800, 330, (800, 100)),
        Large_Platform(6950, 280, (1150, 320)),
        Large_Platform(8100, 330, (500, 270)),
        Large_Platform(8600, 280, (250, 320)),
        Large_Platform(8850, 380, (500, 220)),
        Large_Platform(11400, 380, (1900, 270)),
        Large_Platform(12100, 0, (250, 200)),
        Large_Platform(12350, 0, (700, 250)),
        Large_Platform(13050, 0, (250, 200)),
    )
    
    small_platforms.add(
        Small_Platform(5750, 290),
        Small_Platform(5970, 250),
        Small_Platform(6190, 210),
        Small_Platform(6410, 170),
        Small_Platform(6630, 130),
        Small_Platform(6850, 90),
        Small_Platform(7300, 58),
        Small_Platform(7350, 58),
        Small_Platform(7700, 58),
        Small_Platform(7750, 58),
        Small_Platform(8250, 108),
        Small_Platform(8300, 108),
        Small_Platform(8350, 108),
        Small_Platform(8400, 108),
        Small_Platform(9450, 380),
        Small_Platform(9500, 380),
        Small_Platform(9550, 380),
        Small_Platform(9600, 380),
        Small_Platform(9700, 430),
        Small_Platform(9750, 430),
        Small_Platform(9800, 430),
        Small_Platform(9850, 430),
        Small_Platform(9900, 430),
        Small_Platform(9950, 430),
        Small_Platform(10000, 430),
        Small_Platform(10100, 480),
        Small_Platform(10150, 480),
        Small_Platform(10200, 480),
        Small_Platform(10250, 480),
        Small_Platform(10300, 480),
        Small_Platform(10500, 430),
        Small_Platform(10700, 380),
        Small_Platform(10900, 330),
        Small_Platform(11100, 280),
        Small_Platform(11300, 230),
        Small_Platform(11500, 180),
    )
    
    spikebeds.add(
        SpikeBed(2200, 393, (150, 40)),
        SpikeBed(2400, 393, (150, 40)),
        SpikeBed(3950, 393, (150, 40)),
        SpikeBed(4650, 393, (150, 40)),
        SpikeBed(5600, 393, (1000, 40)),
        SpikeBed(6600, 393, (350, 40)),
        SpikeBed(9350, 521, (1000, 40)),
        SpikeBed(9450, 521, (1000, 40)),
        SpikeBed(10450, 521, (950, 40))
    )
    
    return grounds, players, player_group, spikes, blocks, small_platforms, large_platforms, spikebeds, goal_group

def is_jump_necessary(player, spikes, spikebeds, large_platforms, small_platforms, blocks):
    """Determine if a jump is necessary."""
    for spike in spikes:
        if player.rect.right + 50 >= spike.rect.left and player.rect.right + 50 <= spike.rect.right:
            return True
    for spikebed in spikebeds:
        if player.rect.right + 50 >= spikebed.rect.left and player.rect.right + 50 <= spikebed.rect.right:
            return True
    for platform in large_platforms:
        if player.rect.right + 50 >= platform.rect.left and player.rect.right + 50 <= platform.rect.right:
            return True
    for platform in small_platforms:
        if player.rect.right + 50 >= platform.rect.left and player.rect.right + 50 <= platform.rect.right:
            return True
    for block in blocks:
        if player.rect.right + 50 >= block.rect.left and player.rect.right + 50 <= block.rect.right:
            return True
    return False

# Main game loop
def game_loop(screen, clock, population, generation):
    bg = bg_img
    bg_scroll = 0
    tiles = math.ceil(WIDTH/bg.get_width()) + 1   
    
    grounds, players, player_group, spikes, blocks, small_platforms, large_platforms, spikebeds, goal_group = initialize_objects(population)
    
    font = pg.font.Font(None, 36)
    progress_bar = ProgressBar(13000)
    running = True
    distance_covered = 0
    distance_lowered = 0
    fitness = 0
    active_players = [True] * len(players)
    while running:
        for i in range(tiles):
            screen.blit(bg, (bg.get_width() * i + bg_scroll, 0))
        bg_scroll -= 3
        if abs(bg_scroll) > bg.get_width():
            bg_scroll = 0
            
        for event in pg.event.get():
            if event.type == pg.QUIT:
                small_platforms.empty()
                large_platforms.empty()
                spikes.empty()
                blocks.empty()
                running = False
                pg.quit()
                sys.exit()
 
        # Update entities
        grounds.update()
        #player_group.update()
        spikes.update()
        blocks.update()
        large_platforms.update()
        small_platforms.update()
        spikebeds.update()
        goal_group.update()
        
        for i, player in enumerate(players):
            if not active_players[i]:  # Skip inactive players
                continue
            
            player.update()
            if player.current_jump < len(player.genome):
                if distance_covered >= player.genome[player.current_jump] and not player.is_jumping:
                    if not is_jump_necessary(player, spikes, spikebeds, large_platforms, small_platforms, blocks):
                        #player.penalty += 500
                        if(distance_covered < 2000):
                            player.penalty += 500  # Add penalty for unnecessary jump
                        if(distance_covered >= 2000 and distance_covered < 4000):
                            player.penalty += 700
                        if(distance_covered >= 6000 and distance_covered < 8000):
                            player.penalty += 900
                        if(distance_covered >= 8000 and distance_covered < 10000):
                            player.penalty += 1100
                        if(distance_covered > 10000):
                            player.penalty += 1300
                    player.jump()
                    player.current_jump += 1
            
            if(distance_covered < 5600):
                player.ground_level = DEF_GROUND_LVL
            # Collision detection
            for platform in large_platforms:
                if check_collision(player, platform):
                    #print(f"Player: {player} died from LARGE PLATFORM!")
                    active_players[i] = False
                    player.kill()
                    player.penalty += 200 
            if(distance_covered < 5600):
                player.ground_level = DEF_GROUND_LVL
            
            for platform in small_platforms:
                if check_collision(player, platform):
                    #print(f"Player: {player} died from SMALL PLATFORM!")
                    active_players[i] = False
                    player.kill()
                    player.penalty += 200 
            if(distance_covered < 5600):
                player.ground_level = DEF_GROUND_LVL
            
            # Check collisions with all blocks
            for block in blocks:
                if check_collision(player, block):
                    #print(f"Player: {player} died from BLOCK!")
                    active_players[i] = False
                    player.kill()
                    player.penalty += 200 
            if(distance_covered < 5600):
                player.ground_level = DEF_GROUND_LVL
            
            #Higher penalties for hitting spike beds
            for spikebed in spikebeds:
                if player.rect.colliderect(spikebed.rect):
                    #print(f"Player: {player} died from SPIKEBED!")
                    active_players[i] = False
                    player.kill()
                    player.penalty += 200 
    
            # Spike collision
            for spike in spikes:
                if is_colliding_with_spike(player, spike):
                    #print(f"Player: {player} died from SPIKE!")
                    active_players[i] = False
                    player.kill()
                    player.penalty += 300 
                    
            if distance_covered >= 5600:
                player.ground_level = 600
            
            # Update progress
            if active_players[i]:
                fitness = max(distance_covered - player.penalty, 0)  # Calculate penalized fitness
                population[i][1] = fitness

        # Update progress
        distance_covered += SCROLL_SPD
        progress_bar.update(distance_covered)
        if distance_covered >= progress_bar.total_length or not any(active_players):
            running = False
        
        #Distance based events
        if distance_covered > 5600 and distance_covered < 6500:  # Adjust threshold as needed
            player.ground_level = 600
            distance_lowered += 1
            for ground in grounds:
                ground.rect.y += 1  # Set a positive drop speed for downward motion
            for sprite in small_platforms:
                sprite.rect.y += 1
            for sprite in spikebeds:
                sprite.rect.y += 1

        if distance_covered >= 8200 and distance_covered <= 8206:
            for sprite in spikebeds:
                sprite.rect.y -= distance_lowered

        if distance_covered >= 8450 and distance_covered <= 8456:
            for sprite in small_platforms:
                sprite.rect.y -= distance_lowered
            
        if distance_covered > 10300 and distance_covered < 10700:
            for ground in grounds:
                ground.rect.y += 1
            for sprite in spikes:
                sprite.rect.y += 1
            for sprite in small_platforms:
                sprite.rect.y += 1
            for sprite in spikebeds:
                sprite.rect.y += 1

        # Check level completion
        if distance_covered >= progress_bar.total_length:
            print("Level Complete!")
            running = False
            small_platforms.empty()
            large_platforms.empty()
            spikes.empty()
            blocks.empty()
            
        # Draw everything
        grounds.draw(screen)
        player_group.draw(screen)
        spikes.draw(screen)
        blocks.draw(screen)
        large_platforms.draw(screen)
        small_platforms.draw(screen)
        spikebeds.draw(screen)
        progress_bar.draw(screen)
        goal_group.draw(screen)
        # Display text
        fitness_values = [fitness for _, fitness in population]
        highest_fitness = max(fitness_values)
        alive_count = sum(active_players)
        fitness_text = font.render(f"Current Fitness: {highest_fitness}", True, COLORS["White"])
        alive_text = font.render(f"Alive: {alive_count}/{len(population)}", True, COLORS["White"])
        generation_text = font.render(f"Generation: {generation}", True, COLORS["White"])
        # Draw text in the top-left corner
        screen.blit(fitness_text, (10, 10))
        screen.blit(alive_text, (10, 50))
        screen.blit(generation_text, (10, 90))
        
        pg.display.flip()
        clock.tick(FPS)
    return [fitness for _, fitness in population]

# Main function
def main():
    clock = pg.time.Clock()
    # Initialize population with random genomes and zero fitness
    population = [[create_genome(), 0] for _ in range(POPULATION_SIZE)]
    #print("Initial Population Genomes:")
    #for idx, individual in enumerate(population):
        #print(f"Individual {idx + 1}: Genome = {individual[0]}")

    best_genome = None
    best_fitness = 0
    completion_fitness = 12800

    for generation in range(GENERATIONS):
        print(f"\nStarting Generation {generation + 1}")

        # Run the game loop for the entire population
        fitness_scores = game_loop(screen, clock, population, generation)  # Evaluate all genomes simultaneously

        # Update the fitness values in the population
        for i in range(len(population)):
            population[i][1] = fitness_scores[i]

        # Sort population by fitness in descending order
        population.sort(key=lambda x: x[1], reverse=True)

        # Check for improvement
        if population[0][1] > best_fitness:
            best_fitness = population[0][1]
        
        """# Adjust mutation rate dynamically
        if generation - last_improvement > 50:  # Stagnant for 10 generations
            MUTATION_RATE = min(MUTATION_RATE + 0.1, 0.4)  # Gradually increase to a cap
        else:
            MUTATION_RATE = 0.2  # Reset to default when improvement occurs
        """
        # Preserve elites
        elites = preserve_elite(population)
        print(f"Ideal Genome: [650, 1200, 1778, 1967, 2156, 3024, 3248, 3696, 4032, 4410, 4893, 5356, 5552, 5769, 5986, 6203, 6430, 6633, 6958, 7357, 8260, 8477, 9058, 9303, 9702, 10108, 10297, 10507, 10717, 10906]")
        print(f"Best Genome: {population[0][0]} (Fitness: {population[0][1]})")
        #print(f"Genome Values: {population[0][0]}")
        #avg_genome = calculate_average_genome(population)
        print(f"Median Genome: {population[math.floor(POPULATION_SIZE/2)][0]} (Fitness: {population[math.floor(POPULATION_SIZE/2)][1]})")
        
        # Update best genome and fitness for tracking
        if population[0][1] > best_fitness:
            best_fitness = population[0][1]
            best_genome = population[0][0]

        # Generate the next population
        next_population = elites[:]
        while len(next_population) < POPULATION_SIZE:
            parent1, parent2 = select_parents(population)
            child1 = mutate_genome(crossover_genomes(parent1[0], parent2[0]), fitness=parent1[1])
            child2 = mutate_genome(crossover_genomes(parent2[0], parent1[0]), fitness=parent2[1])
            next_population.extend([[child1, 0], [child2, 0]])

        if population[0][1] >= completion_fitness:
            best_genome = population[0][0]
            break  # Exit the loop as the level is beaten
        
        # Replace the old population with the new one
        population = next_population

    print("\nTraining Complete!")
    print(f"Best Genome: {best_genome}, Fitness: {best_fitness}")
    

    # Play the final game using the best genome
    #game_loop(screen, clock, [[best_genome, 0]])
    
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()