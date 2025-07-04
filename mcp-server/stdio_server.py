import asyncio
from mcp.server.fastmcp import FastMCP
import sys

# ... (all the tool definitions from main.py) ...

if __name__ == "__main__":
    # This needs to run as a stdio server, not HTTP
    import nest_asyncio
    nest_asyncio.apply()
    
    # Create event loop and run forever
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mcp.run())
    loop.run_forever()  # Keep the process alive