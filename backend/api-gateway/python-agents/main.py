# main.py
import asyncio
import logging
import os
from messaging.a2a_bus import A2AMessageBus

# Import your agents
from agents.trip_orchestrator_agent.agent import TripOrchestrator
from agents.flight_specialist_agent.agent import FlightSpecialist
from agents.hotel_specialist_agent.agent import HotelSpecialist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

async def main():
    # Initialize Redis URL from environment or default
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Initialize the A2A message bus
    message_bus = A2AMessageBus(redis_url)
    await message_bus.initialize()

    # Instantiate agents
    trip_orchestrator = TripOrchestrator()
    flight_specialist = FlightSpecialist()
    hotel_specialist = HotelSpecialist()

    # Set the message bus for each agent
    trip_orchestrator.set_message_bus(message_bus)
    flight_specialist.set_message_bus(message_bus)
    hotel_specialist.set_message_bus(message_bus)

    # Initialize agents (register with message bus, etc.)
    await trip_orchestrator.initialize()
    await flight_specialist.initialize()
    await hotel_specialist.initialize()

    # Start listening for messages on the bus
    listen_task = await message_bus.start_listening()

    logging.info("All agents are running and connected via A2A message bus.")

    # Example: send a test request to the trip orchestrator
    test_request = {
        "message": "I want to plan a romantic trip to Paris next week",
        "conversation_id": "test-conversation-1"
    }
    logging.info(f"Sending test request: {test_request['message']}")
    response = await trip_orchestrator.process_request(test_request)
    logging.info(f"Received response: {response}")

    # Keep running until interrupted
    try:
        await listen_task
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        await message_bus.stop_listening()

if __name__ == "__main__":
    asyncio.run(main())
