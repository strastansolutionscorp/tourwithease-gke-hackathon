# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import remote_a2a_agent

# Trip Orchestrator Remote Agent
trip_orchestrator_remote = RemoteA2aAgent(
    name="trip_orchestrator_agent",
    description=(
        "Master travel coordinator orchestrating comprehensive trip planning "
        "by coordinating flights, hotels, context, pricing, and booking services across specialist agents."
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Context Specialist Remote Agent
context_specialist_remote = RemoteA2aAgent(
    name="context_specialist_agent",
    description=(
        "Travel context intelligence provider delivering weather forecasts, "
        "currency information, cultural insights, and destination-specific guidance."
    ),
    agent_card=f"http://localhost:8002/{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Flight Specialist Remote Agent
flight_specialist_remote = RemoteA2aAgent(
    name="flight_specialist_agent",
    description=(
        "Aviation and flight booking expert using AWS Lambda and Amadeus GDS "
        "for comprehensive flight searches, price analysis, and travel recommendations."
    ),
    agent_card=f"http://localhost:8003/{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Hotel Specialist Remote Agent
hotel_specialist_remote = RemoteA2aAgent(
    name="hotel_specialist_agent",
    description=(
        "Accommodation and hospitality expert using AWS Lambda and Amadeus GDS "
        "for hotel searches, price comparisons, and personalized lodging recommendations."
    ),
    agent_card=f"http://localhost:8004/{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Default root agent - Trip Orchestrator as the main entry point
root_agent = trip_orchestrator_remote
