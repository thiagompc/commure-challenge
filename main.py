from lichess import LiChess

def print_top_50_classical_players(top_players: list) -> None:
    for user in top_players:
        print(user['username'])

def print_last_30_day_rating_for_top_player(top_classical_player: str, history_dict:dict) -> None:
  print(f'{top_classical_player}, {history_dict}')

if __name__ == '__main__':
    api = LiChess()

    # Warmup: List the top 50 classical chess players. Just print their usernames.
    top_players = api.get_top_50_classical_players(50)
    print_top_50_classical_players(top_players)

    # Part 2: Print the rating history for the top chess player in classical chess for the last 30 calendar days.
    top_classical_player, history_dict = api.get_last_30_day_rating_for_top_player(top_players[0]['username'])
    print_last_30_day_rating_for_top_player(top_classical_player, history_dict)

    # Part 3: Create a CSV that shows the rating history for each of these 50 players, for thelast 30 days.
    api.generate_rating_csv_for_top_50_classical_players(top_players)