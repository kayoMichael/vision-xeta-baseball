from context.services.prospect_service import prospect_info
from context.schemas.prospect import Prospect
from context.main import mcp

@mcp.tool()
def prospect(body: Prospect):
    try:
        stat = prospect_info(body)
    except ValueError as e:
        raise e

    return stat
