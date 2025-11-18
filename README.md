# Epidemic Simulation (SIR Model) - Project Option 2

An agent-based simulation modeling the spread of an infectious disease within a population using the SIR (Susceptible, Infected, Recovered) model.

## Features Implemented

### ✅ Agent States
- **Susceptible (Blue)**: Agents that can be infected
- **Infected (Red)**: Agents carrying the disease with visible infection radius
- **Recovered (Green)**: Agents that survived infection and gained immunity
- **Immune (Yellow)**: Vaccinated agents who cannot be infected

### ✅ State Transitions
- **Infection Mechanism**: 
  - Occurs when susceptible agents come within the infection radius of infected agents
  - Base infection probability: 2% per frame
  - Probability increases with duration of contact (proximity tracking)
  - Visual feedback with infection radius circles around infected agents

- **Recovery Mechanism**:
  - Agents remain infected for 300 frames (5 seconds at 60 FPS)
  - 70% chance to recover and become immune
  - 30% chance of death (agent removed from simulation)

### ✅ Movement Behaviors
- Agents move randomly within the environment
- Temporary social grouping behavior (agents occasionally move toward nearby agents)
- Smooth movement with velocity-based physics
- Boundary collision detection

### ✅ Quarantine Zones
- Visual quarantine zone in the top-right corner
- Infected agents automatically move to quarantine when enabled
- Limited capacity quarantine system
- Can be toggled on/off with 'Q' key

### ✅ Vaccination Strategies
- 30% of initial population eligible for vaccination
- 90% vaccination success rate
- Vaccinated agents become immune (yellow)
- Can trigger additional vaccination waves with 'V' key
- Vaccination rate affected by simulation parameters

### ✅ History Tracking
Two real-time graphs displayed at the bottom of the screen:

1. **Population Over Time**: 
   - Susceptible (Blue line)
   - Infected (Red line)
   - Recovered (Green line)
   - Immune (Yellow line)

2. **Infection & Recovery Rates**:
   - Infection Rate (Red line) - percentage of new infections
   - Recovery Rate (Green line) - percentage of recoveries

### ✅ User Interaction Controls
- **SPACE**: Pause/Resume simulation
- **R**: Reset simulation to initial state
- **Q**: Toggle quarantine zones on/off
- **UP/DOWN arrows**: Adjust infection rate (0.1x to 2.0x)
- **LEFT/RIGHT arrows**: Adjust recovery rate (0.1x to 2.0x)
- **V**: Trigger vaccination wave for remaining susceptible agents

## Installation

1. Make sure you have Python installed (3.7 or higher)
2. Install required dependencies:
```bash
pip install pygame matplotlib
```

## Running the Simulation

```bash
python epidemic_simulation.py
```

## Two Simulation Scenarios

### Scenario 1: Complete Extinction
To simulate a scenario where all agents die:
1. Run the simulation
2. Press **DOWN arrow** multiple times to reduce recovery rate to minimum (0.1x)
3. Press **UP arrow** to increase infection rate to maximum (2.0x)
4. Press **Q** to disable quarantine
5. Observe as the virus spreads rapidly and agents die without recovering

### Scenario 2: Survival and Virus Elimination
To simulate a scenario where the virus disappears and agents survive:
1. Run the simulation
2. Press **Q** to enable quarantine (if not already on)
3. Press **V** to vaccinate more of the population
4. Press **RIGHT arrow** to increase recovery rate
5. Press **DOWN arrow** to slightly decrease infection rate
6. Observe as infected agents recover, immune population grows, and virus eventually disappears

## Statistics Displayed

- **Population**: Total living agents
- **Susceptible**: Agents that can be infected
- **Infected**: Currently infected agents
- **Recovered**: Agents that survived infection
- **Immune**: Vaccinated agents
- **Deaths**: Total number of deaths
- **Infection Rate Multiplier**: Current infection rate adjustment
- **Recovery Rate Multiplier**: Current recovery rate adjustment
- **Quarantine Status**: Whether quarantine is enabled

## Implementation Details

### Key Classes

1. **Agent**: Represents individual agents with state, position, movement, and infection mechanics
2. **AgentState**: Enum defining the four possible states (SUSCEPTIBLE, INFECTED, RECOVERED, IMMUNE)
3. **QuarantineZone**: Manages quarantine areas for infected agents
4. **Statistics**: Tracks and stores historical data for graphing
5. **EpidemicSimulation**: Main simulation controller managing all components

### Infection Algorithm
- Proximity detection using distance calculation
- Contact duration tracking for each pair of agents
- Dynamic infection probability based on contact time
- Realistic spread pattern based on spatial proximity

### Visualization
- Color-coded agents for easy state identification
- Infection radius visualization for infected agents
- Real-time graphs with 500-frame history
- Quarantine zone boundaries
- Live statistics display

## Project Requirements Checklist

- ✅ Agent States: Susceptible, Infected, Recovered + Immune (bonus)
- ✅ Visualize each state with distinct colors
- ✅ Infection probabilities with proximity and duration mechanics
- ✅ Recovery after certain period with probability (or death)
- ✅ Movement with social behaviors (temporary grouping)
- ✅ Quarantine zones for infected individuals
- ✅ Vaccination with success rates and immunization
- ✅ Graphs showing population changes over time
- ✅ Graphs for infection rate and recovery rate
- ✅ Controls to adjust infection, recovery, and vaccination rates
- ✅ Two scenarios: complete extinction and survival

## Author
Created as part of MS Lab 6 - Project Option 2
