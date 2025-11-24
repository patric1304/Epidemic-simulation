"""
Epidemic Simulation (SIR Model) - Project Option 2
An agent-based simulation modeling the spread of an infectious disease using the SIR model.
"""

import pygame
import random
import math

from collections import deque
from enum import Enum

# Screen dimensions
WIDTH, HEIGHT = 1200, 700
GRAPH_HEIGHT = 250

# Colors
BACKGROUND_COLOR = (30, 30, 40)
SUSCEPTIBLE_COLOR = (100, 200, 255)  # Blue
INFECTED_COLOR = (255, 100, 100)     # Red
RECOVERED_COLOR = (100, 255, 100)    # Green
IMMUNE_COLOR = (255, 200, 50)        # Yellow
QUARANTINE_COLOR = (150, 150, 150)   # Gray
TEXT_COLOR = (200, 200, 200)

# Simulation parameters
INITIAL_POPULATION = 200
INITIAL_INFECTED = 5
INFECTION_RADIUS = 15
BASE_INFECTION_PROB = 0.02  # Per frame when in contact
RECOVERY_TIME = 300  # Frames (5 seconds at 60 FPS)
RECOVERY_PROB = 0.7  # 70% chance to recover, 30% to die
VACCINATION_RATE = 0.3  # 30% of population gets vaccinated
VACCINATION_SUCCESS_RATE = 0.9  # 90% success rate
MOVEMENT_SPEED = 2

class AgentState(Enum):
    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    IMMUNE = 4  # Vaccinated and immune

class Agent:
    def __init__(self, state=AgentState.SUSCEPTIBLE):
        self.position = pygame.math.Vector2(random.uniform(50, WIDTH - 50), random.uniform(50, HEIGHT - GRAPH_HEIGHT - 50))
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = MOVEMENT_SPEED
        self.state = state
        self.infection_time = 0  # Time since infection
        self.contact_time = {}  # Track contact time with infected agents
        self.in_quarantine = False
        self.quarantine_position = None
        
    def update(self, agents, quarantine_zones, enable_quarantine):
        """Update agent position and state"""
        if self.state == AgentState.INFECTED:
            self.infection_time += 1
            
            # Check for recovery or death
            if self.infection_time >= RECOVERY_TIME:
                if random.random() < RECOVERY_PROB:
                    self.state = AgentState.RECOVERED
                    self.in_quarantine = False
                else:
                    return False  # Agent dies
            
            # Move to quarantine if enabled and not already there
            if enable_quarantine and not self.in_quarantine:
                for zone in quarantine_zones:
                    if zone.has_space():
                        self.in_quarantine = True
                        self.quarantine_position = zone.get_position()
                        break
        
        # Update position
        if self.in_quarantine and self.quarantine_position:
            # Move slowly towards quarantine zone
            direction = (self.quarantine_position - self.position)
            if direction.length() > 2:
                self.position += direction.normalize() * self.speed * 0.5
            else:
                # Random movement within quarantine zone
                self.position += self.velocity * self.speed * 0.3
                if random.random() < 0.05:
                    angle = random.uniform(0, 2 * math.pi)
                    self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        else:
            # Normal movement
            self.position += self.velocity * self.speed
            
            # Temporary grouping behavior (social behavior)
            if random.random() < 0.01:
                nearby_agents = [a for a in agents if a != self and self.position.distance_to(a.position) < 50]
                if nearby_agents:
                    # Move towards nearby agent
                    target = random.choice(nearby_agents)
                    direction = (target.position - self.position).normalize()
                    self.velocity = direction
        
        # Bounce off edges
        if self.position.x < 0 or self.position.x > WIDTH:
            self.velocity.x *= -1
        if self.position.y < 0 or self.position.y > HEIGHT - GRAPH_HEIGHT:
            self.velocity.y *= -1
        
        # Keep within bounds
        self.position.x = max(0, min(self.position.x, WIDTH))
        self.position.y = max(0, min(self.position.y, HEIGHT - GRAPH_HEIGHT))
        
        # Random direction change
        if random.random() < 0.02:
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        
        return True  # Agent survives
    
    def check_infection(self, agents):
        """Check if agent gets infected through contact"""
        if self.state != AgentState.SUSCEPTIBLE:
            return
        
        for agent in agents:
            if agent.state == AgentState.INFECTED and agent != self:
                distance = self.position.distance_to(agent.position)
                if distance < INFECTION_RADIUS:
                    # Track contact time
                    agent_id = id(agent)
                    if agent_id not in self.contact_time:
                        self.contact_time[agent_id] = 0
                    self.contact_time[agent_id] += 1
                    
                    # Infection probability increases with contact duration
                    infection_chance = BASE_INFECTION_PROB * (1 + self.contact_time[agent_id] * 0.01)
                    if random.random() < infection_chance:
                        self.state = AgentState.INFECTED
                        self.infection_time = 0
                        return
                else:
                    # Reset contact time if not in contact
                    agent_id = id(agent)
                    if agent_id in self.contact_time:
                        del self.contact_time[agent_id]
    
    def vaccinate(self):
        """Attempt to vaccinate the agent"""
        if self.state == AgentState.SUSCEPTIBLE:
            if random.random() < VACCINATION_SUCCESS_RATE:
                self.state = AgentState.IMMUNE
                return True
        return False
    
    def get_color(self):
        """Get the color based on agent state"""
        if self.state == AgentState.SUSCEPTIBLE:
            return SUSCEPTIBLE_COLOR
        elif self.state == AgentState.INFECTED:
            return INFECTED_COLOR
        elif self.state == AgentState.RECOVERED:
            return RECOVERED_COLOR
        elif self.state == AgentState.IMMUNE:
            return IMMUNE_COLOR
    
    def draw(self, screen):
        """Draw the agent"""
        color = self.get_color()
        radius = 5 if self.state != AgentState.INFECTED else 6
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), radius)
        
        # Draw infection radius for infected agents
        if self.state == AgentState.INFECTED:
            pygame.draw.circle(screen, (*INFECTED_COLOR, 30), (int(self.position.x), int(self.position.y)), 
                             INFECTION_RADIUS, 1)

class QuarantineZone:
    def __init__(self, x, y, width, height, capacity=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.capacity = capacity
        self.current_count = 0
    
    def has_space(self):
        return self.current_count < self.capacity
    
    def get_position(self):
        """Get a random position within the quarantine zone"""
        return pygame.math.Vector2(
            random.uniform(self.rect.x + 10, self.rect.x + self.rect.width - 10),
            random.uniform(self.rect.y + 10, self.rect.y + self.rect.height - 10)
        )
    
    def draw(self, screen):
        """Draw the quarantine zone"""
        pygame.draw.rect(screen, QUARANTINE_COLOR, self.rect, 2)
        font = pygame.font.SysFont(None, 20)
        text = font.render('QUARANTINE ZONE', True, QUARANTINE_COLOR)
        screen.blit(text, (self.rect.x + 10, self.rect.y + 5))

class Statistics:
    def __init__(self, max_history=500):
        self.max_history = max_history
        self.susceptible_history = deque(maxlen=max_history)
        self.infected_history = deque(maxlen=max_history)
        self.recovered_history = deque(maxlen=max_history)
        self.immune_history = deque(maxlen=max_history)
        self.infection_rate_history = deque(maxlen=max_history)
        self.recovery_rate_history = deque(maxlen=max_history)
        self.death_count = 0
        self.total_infections = 0
        self.total_recoveries = 0
        self.prev_infected = 0
        self.prev_recovered = 0
    
    def update(self, agents):
        """Update statistics"""
        susceptible = sum(1 for a in agents if a.state == AgentState.SUSCEPTIBLE)
        infected = sum(1 for a in agents if a.state == AgentState.INFECTED)
        recovered = sum(1 for a in agents if a.state == AgentState.RECOVERED)
        immune = sum(1 for a in agents if a.state == AgentState.IMMUNE)
        
        self.susceptible_history.append(susceptible)
        self.infected_history.append(infected)
        self.recovered_history.append(recovered)
        self.immune_history.append(immune)
        
        # Calculate rates
        new_infections = max(0, infected - self.prev_infected + (self.prev_recovered - recovered))
        new_recoveries = max(0, recovered - self.prev_recovered)
        
        infection_rate = new_infections / max(1, len(agents)) * 100
        recovery_rate = new_recoveries / max(1, infected) * 100 if infected > 0 else 0
        
        self.infection_rate_history.append(infection_rate)
        self.recovery_rate_history.append(recovery_rate)
        
        self.prev_infected = infected
        self.prev_recovered = recovered
        
        if new_infections > 0:
            self.total_infections += new_infections
        if new_recoveries > 0:
            self.total_recoveries += new_recoveries
    
    def draw_graphs(self, screen):
        """Draw graphs showing population and rates over time"""
        graph_y = HEIGHT - GRAPH_HEIGHT + 10
        graph_width = WIDTH // 2 - 20
        graph_height = GRAPH_HEIGHT - 20
        
        # Population graph
        self._draw_graph(screen, 10, graph_y, graph_width, graph_height, 
                        [self.susceptible_history, self.infected_history, 
                         self.recovered_history, self.immune_history],
                        [SUSCEPTIBLE_COLOR, INFECTED_COLOR, RECOVERED_COLOR, IMMUNE_COLOR],
                        "Population Over Time",
                        ["Susceptible", "Infected", "Recovered", "Immune"])
        
        # Rates graph
        self._draw_graph(screen, WIDTH // 2 + 10, graph_y, graph_width, graph_height,
                        [self.infection_rate_history, self.recovery_rate_history],
                        [INFECTED_COLOR, RECOVERED_COLOR],
                        "Infection & Recovery Rates (%)",
                        ["Infection Rate", "Recovery Rate"])
    
    def _draw_graph(self, screen, x, y, width, height, data_lists, colors, title, labels):
        """Helper method to draw a graph"""
        # Background
        pygame.draw.rect(screen, (20, 20, 30), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 1)
        
        # Title
        font = pygame.font.SysFont(None, 20)
        title_text = font.render(title, True, TEXT_COLOR)
        screen.blit(title_text, (x + 10, y + 5))
        
        # Legend
        legend_y = y + 25
        for i, (label, color) in enumerate(zip(labels, colors)):
            pygame.draw.circle(screen, color, (x + 10, legend_y + i * 15), 4)
            label_text = font.render(label, True, TEXT_COLOR)
            screen.blit(label_text, (x + 20, legend_y + i * 15 - 7))
        
        # Draw data
        if any(len(data) > 1 for data in data_lists):
            max_value = max(max(data) if data else 0 for data in data_lists)
            if max_value == 0:
                max_value = 1
            
            graph_x_start = x + 10
            graph_y_start = y + height - 10
            graph_draw_width = width - 20
            graph_draw_height = height - 80
            
            for data, color in zip(data_lists, colors):
                if len(data) > 1:
                    points = []
                    for i, value in enumerate(data):
                        px = graph_x_start + (i / len(data)) * graph_draw_width
                        py = graph_y_start - (value / max_value) * graph_draw_height
                        points.append((px, py))
                    
                    if len(points) > 1:
                        pygame.draw.lines(screen, color, False, points, 2)

class EpidemicSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Epidemic Simulation (SIR Model)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Initialize simulation
        self.agents = []
        self.statistics = Statistics()
        self.quarantine_zones = [
            QuarantineZone(WIDTH - 250, 50, 200, 200)
        ]
        
        # Simulation parameters (adjustable)
        self.infection_prob_multiplier = 1.0
        self.recovery_prob_multiplier = 1.0
        self.vaccination_rate_multiplier = 1.0
        self.enable_quarantine = True
        
        self.running = True
        self.paused = False
        self.frame_count = 0
        
        self.reset_simulation()
    
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.agents = []
        self.statistics = Statistics()
        self.frame_count = 0
        
        # Create susceptible agents
        for _ in range(INITIAL_POPULATION - INITIAL_INFECTED):
            self.agents.append(Agent(AgentState.SUSCEPTIBLE))
        
        # Create infected agents
        for _ in range(INITIAL_INFECTED):
            self.agents.append(Agent(AgentState.INFECTED))
        
        # Vaccinate a portion of the population
        if random.random() < self.vaccination_rate_multiplier:
            num_to_vaccinate = int(INITIAL_POPULATION * VACCINATION_RATE * self.vaccination_rate_multiplier)
            susceptible_agents = [a for a in self.agents if a.state == AgentState.SUSCEPTIBLE]
            for agent in random.sample(susceptible_agents, min(num_to_vaccinate, len(susceptible_agents))):
                agent.vaccinate()

    def load_scenario(self, scenario_id):
        """Load a specific simulation scenario"""
        self.reset_simulation()
        
        if scenario_id == 1:  # Extinction Scenario
            self.infection_prob_multiplier = 2.0
            self.recovery_prob_multiplier = 0.5
            self.vaccination_rate_multiplier = 0.0
            self.enable_quarantine = False
            print("Loaded Scenario 1: High Infection, Low Recovery (Extinction Risk)")
            
        elif scenario_id == 2:  # Survival Scenario
            self.infection_prob_multiplier = 0.8
            self.recovery_prob_multiplier = 1.5
            self.vaccination_rate_multiplier = 1.5
            self.enable_quarantine = True
            print("Loaded Scenario 2: Managed Outbreak (Survival)")
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_q:
                    self.enable_quarantine = not self.enable_quarantine
                elif event.key == pygame.K_UP:
                    self.infection_prob_multiplier = min(2.0, self.infection_prob_multiplier + 0.1)
                elif event.key == pygame.K_DOWN:
                    self.infection_prob_multiplier = max(0.1, self.infection_prob_multiplier - 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.recovery_prob_multiplier = min(2.0, self.recovery_prob_multiplier + 0.1)
                elif event.key == pygame.K_LEFT:
                    self.recovery_prob_multiplier = max(0.1, self.recovery_prob_multiplier - 0.1)
                elif event.key == pygame.K_w:
                    self.vaccination_rate_multiplier = min(2.0, self.vaccination_rate_multiplier + 0.1)
                elif event.key == pygame.K_s:
                    self.vaccination_rate_multiplier = max(0.0, self.vaccination_rate_multiplier - 0.1)
                elif event.key == pygame.K_1:
                    self.load_scenario(1)
                elif event.key == pygame.K_2:
                    self.load_scenario(2)
                elif event.key == pygame.K_v:
                    # Vaccinate remaining susceptible agents
                    susceptible = [a for a in self.agents if a.state == AgentState.SUSCEPTIBLE]
                    for agent in susceptible:
                        if random.random() < VACCINATION_RATE * self.vaccination_rate_multiplier:
                            agent.vaccinate()
    
    def update(self):
        """Update simulation state"""
        if self.paused:
            return
        
        self.frame_count += 1
        
        # Update infection probability based on multiplier
        global BASE_INFECTION_PROB, RECOVERY_PROB
        effective_infection_prob = BASE_INFECTION_PROB * self.infection_prob_multiplier
        effective_recovery_prob = min(0.99, RECOVERY_PROB * self.recovery_prob_multiplier)
        
        # Update all agents
        surviving_agents = []
        for agent in self.agents:
            # Temporarily modify recovery probability
            original_recovery = RECOVERY_PROB
            RECOVERY_PROB = effective_recovery_prob
            
            if agent.update(self.agents, self.quarantine_zones, self.enable_quarantine):
                surviving_agents.append(agent)
            else:
                self.statistics.death_count += 1
            
            RECOVERY_PROB = original_recovery
        
        self.agents = surviving_agents
        
        # Check for infections
        for agent in self.agents:
            agent.check_infection(self.agents)
        
        # Update statistics
        if self.frame_count % 5 == 0:  # Update every 5 frames
            self.statistics.update(self.agents)
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw quarantine zones
        if self.enable_quarantine:
            for zone in self.quarantine_zones:
                zone.draw(self.screen)
        
        # Draw agents
        for agent in self.agents:
            agent.draw(self.screen)
        
        # Draw statistics
        self.draw_stats()
        
        # Draw graphs
        self.statistics.draw_graphs(self.screen)
        
        # Draw controls
        self.draw_controls()
        
        pygame.display.flip()
    
    def draw_stats(self):
        """Draw statistics on screen"""
        susceptible = sum(1 for a in self.agents if a.state == AgentState.SUSCEPTIBLE)
        infected = sum(1 for a in self.agents if a.state == AgentState.INFECTED)
        recovered = sum(1 for a in self.agents if a.state == AgentState.RECOVERED)
        immune = sum(1 for a in self.agents if a.state == AgentState.IMMUNE)
        
        stats = [
            f"Population: {len(self.agents)}",
            f"Susceptible: {susceptible}",
            f"Infected: {infected}",
            f"Recovered: {recovered}",
            f"Immune: {immune}",
            f"Deaths: {self.statistics.death_count}",
            "",
            f"Infection Rate: x{self.infection_prob_multiplier:.1f}",
            f"Recovery Rate: x{self.recovery_prob_multiplier:.1f}",
            f"Vaccination Rate: x{self.vaccination_rate_multiplier:.1f}",
            f"Quarantine: {'ON' if self.enable_quarantine else 'OFF'}",
        ]
        
        y_offset = 10
        for stat in stats:
            if stat:
                text = self.small_font.render(stat, True, TEXT_COLOR)
                self.screen.blit(text, (10, y_offset))
            y_offset += 20
    
    def draw_controls(self):
        """Draw control instructions"""
        controls = [
            "SPACE: Pause/Resume",
            "R: Reset",
            "Q: Toggle Quarantine",
            "UP/DOWN: Adjust Infection Rate",
            "LEFT/RIGHT: Adjust Recovery Rate",
            "W/S: Adjust Vaccination Rate",
            "V: Vaccinate Population",
            "1: Extinction Scenario",
            "2: Survival Scenario"
        ]
        
        x_offset = WIDTH - 280
        y_offset = HEIGHT - GRAPH_HEIGHT - 160
        
        title = self.font.render("Controls:", True, TEXT_COLOR)
        self.screen.blit(title, (x_offset, y_offset))
        y_offset += 25
        
        for control in controls:
            text = self.small_font.render(control, True, TEXT_COLOR)
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += 20
        
        if self.paused:
            pause_text = self.font.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, (WIDTH // 2 - 40, 10))
    
    def run(self):
        """Main simulation loop"""
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    simulation = EpidemicSimulation()
    simulation.run()
