"""
AWS Tools Package for Hotel and Flight Search Integration

This package provides tools for interacting with AWS API Gateway endpoints
for Amadeus GDS hotel and flight search functionality.
"""

# Import all the tools from the aws_tools module
from .aws_tools import (
    AWSLambdaTool,
    HotelSearchTool,
    FlightSearchTool,
    FlightPricingOffersTool,
    PriceAnalysisTool
)

# Define what gets imported when someone does "from aws_tools import *"
__all__ = [
    "AWSLambdaTool",
    "HotelSearchTool",
    "FlightSearchTool", 
    "FlightPricingOffersTool",
    "PriceAnalysisTool"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "AWS Lambda tools for hotel and flight search via API Gateway"

# Optional: Add package-level logging configuration
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())