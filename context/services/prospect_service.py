from context.schemas.prospect import Prospect
from context.support.chadwick_register import ChadwickRegister

def prospect_info(prospect: Prospect):
    info = ChadwickRegister(**prospect.model_dump())

    player_id = info.search_player()

    if not player_id:
        raise ValueError(f"Prospect {prospect} not found")

    return player_id