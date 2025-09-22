"""
Hotel Specialist Agent Package - A2A Protocol Enabled
"""

__version__ = "1.2.0"
__author__ = "TourWithEase Team"
__description__ = "A2A-enabled hotel specialist agent"

import logging
logger = logging.getLogger(__name__)

# === SAFE IMPORTS WITH DETAILED ERROR HANDLING ===

# Initialize all variables to None first
hotel_specialist_agent = None
agent = None
root_agent = None
app = None
a2a_app = None
hotel_search = None
hotel_price_analysis = None
location_db = None
AWS_TOOLS_AVAILABLE = False

# Try importing with detailed error reporting
try:
    print("🔄 Attempting to import from .agent...")
    
    # Import one by one to identify specific failures
    try:
        from .agent import hotel_specialist_agent
        print("✅ hotel_specialist_agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import hotel_specialist_agent: {e}")
    
    try:
        from .agent import agent
        print("✅ agent imported successfully") 
    except ImportError as e:
        print(f"❌ Failed to import agent: {e}")
        # If hotel_specialist_agent exists, use it as agent
        if hotel_specialist_agent is not None:
            agent = hotel_specialist_agent
            print("🔧 Using hotel_specialist_agent as agent")
    
    try:
        from .agent import root_agent
        print("✅ root_agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import root_agent: {e}")
        # Use agent as root_agent if available
        if agent is not None:
            root_agent = agent
            print("🔧 Using agent as root_agent")
    
    try:
        from .agent import app
        print("✅ app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
    
    try:
        from .agent import a2a_app
        print("✅ a2a_app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import a2a_app: {e}")
        # Use app as a2a_app if available
        if app is not None:
            a2a_app = app
            print("🔧 Using app as a2a_app")
    
    try:
        from .agent import hotel_search
        print("✅ hotel_search imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import hotel_search: {e}")
    
    try:
        from .agent import hotel_price_analysis
        print("✅ hotel_price_analysis imported successfully") 
    except ImportError as e:
        print(f"❌ Failed to import hotel_price_analysis: {e}")
    
    try:
        from .agent import location_db
        print("✅ location_db imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import location_db: {e}")
    
    try:
        from .agent import AWS_TOOLS_AVAILABLE
        print("✅ AWS_TOOLS_AVAILABLE imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AWS_TOOLS_AVAILABLE: {e}")
        AWS_TOOLS_AVAILABLE = False

except ImportError as e:
    print(f"❌ Major import failure from .agent: {e}")

# === PACKAGE STATUS ===

def get_import_status():
    """Get detailed import status for debugging"""
    return {
        "hotel_specialist_agent": hotel_specialist_agent is not None,
        "agent": agent is not None,
        "root_agent": root_agent is not None,
        "app": app is not None,
        "a2a_app": a2a_app is not None,
        "hotel_search": hotel_search is not None,
        "hotel_price_analysis": hotel_price_analysis is not None,
        "location_db": location_db is not None,
        "AWS_TOOLS_AVAILABLE": AWS_TOOLS_AVAILABLE
    }

# === DYNAMIC __all__ BASED ON SUCCESSFUL IMPORTS ===

__all__ = ["__version__", "__author__", "__description__", "get_import_status"]

# Add successfully imported items to __all__
for item_name in ["hotel_specialist_agent", "agent", "root_agent", "app", "a2a_app", 
                  "hotel_search", "hotel_price_analysis", "location_db", "AWS_TOOLS_AVAILABLE"]:
    if globals()[item_name] is not None:
        __all__.append(item_name)

# === FALLBACK FUNCTIONS ===

if app is None and a2a_app is None:
    print("🔧 Creating minimal fallback FastAPI app...")
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Hotel Specialist - Fallback Mode")
        a2a_app = app
        
        @app.get("/health")
        async def fallback_health():
            return {"status": "fallback_mode", "message": "Hotel specialist running in fallback mode"}
        
        @app.get("/.well-known/agent_card") 
        async def fallback_agent_card():
            return {
                "name": "hotel_specialist_agent",
                "status": "fallback_mode",
                "version": __version__,
                "message": "Agent running in fallback mode due to import issues"
            }
        
        __all__.extend(["app", "a2a_app"])
        print("✅ Fallback FastAPI app created")
    except ImportError:
        print("❌ Cannot create fallback app - FastAPI not available")

# Final status report
status = get_import_status()
success_count = sum(status.values())
total_count = len(status)

print(f"📦 Hotel Specialist Package Import Summary:")
print(f"   ✅ Successful: {success_count}/{total_count}")
print(f"   📋 Available exports: {len(__all__)} items")

if success_count < total_count:
    print(f"⚠️ Some components failed to import. Check agent.py file structure.")
    print(f"🔧 Debug status: {status}")

logger.info(f"Hotel Specialist Package initialized with {success_count}/{total_count} components")
