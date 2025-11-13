from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BaseballCardMCP")

def load_endpoint():
    # Predict Endpoint
    import context.routes.predict

    # Card Prices Endpoint
    import context.routes.card_info

    # Card Prospect Endpoint
    import context.routes.prospect

if __name__ == "__main__":
    load_endpoint()
    mcp.run()
