import json
from subprocess import call
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai

from tqdm import trange

from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai

win, lose = 0, 0
number = 10
player1 = "base3"
player2 = "IWantToPass"

for i in trange(number):
    config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
    config.register_player(name=player1, algorithm=baseline3_ai())
    config.register_player(name=player2, algorithm=call_ai())

    ## Play in interactive mode if uncomment
    # config.register_player(name="me", algorithm=console_ai())
    game_result = start_poker(config, verbose=0)
    if game_result["players"][1]["stack"] > game_result["players"][0]["stack"]:
        win+=1
    elif game_result["players"][1]["stack"] < game_result["players"][0]["stack"]:
        lose+=1

print(f"Victory rate({player1} vs {player2})) = {1 - lose/number}%.")


# print(json.dumps(game_result, indent=4))