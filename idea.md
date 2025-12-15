# ROAMFIT

A multi-agentic fitness application designed to help users maintain their fitness routine while traveling.

## Architecture

Built using **Strands agents** with an orchestrator agent coordinating multiple specialized agents:

### Agents

- **Orchestrator Agent**: Coordinates workflow between all agents
- **Equipment Detection Agent**: Assesses available equipment from photos
- **Last Workout Summary Agent**: Tracks previous workouts and provides context for next sessions
- **Workout Generator Agent**: Creates personalized workouts based on available equipment and workout history
- **Graph and Trends Agent**: Visualizes progress through graphs and trend analysis
- **Location and Nearby Activity Agent**: Finds nearby gyms and running tracks using geolocation

