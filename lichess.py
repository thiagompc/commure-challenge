import csv
import requests
from datetime import datetime, timedelta

class LiChess:
    def __init__(self):
        self.lichess_url = 'https://lichess.org/api'

    def get_top_50_classical_players(self, num: int) -> list:
        """Returns the top 50 classical chess players from the Lichess API."""
        response = requests.get(f'{self.lichess_url}/player/top/{num}/classical')
        response.raise_for_status()
        players_data = response.json()
        return players_data['users']

    def get_player_rating_history(self, player: str) -> list:
        """Fetches the rating history for a given player."""
        response = requests.get(f'{self.lichess_url}/user/{player}/rating-history')
        response.raise_for_status()
        return response.json()

    def extract_classical_history(self, rating_history: list) -> list:
        """Extracts the classical rating history from the given rating history."""
        return next(item['points'] for item in rating_history if item['name'] == 'Classical')

    def generate_30_day_rating_history(self, classical_history: list) -> dict:
        """Generates the last 30 days of ratings from the classical history."""
        history_dict = {}
        now = datetime.now()
        last_valid_value = None
        first_valid_value_day = None
        first_valid_value_index = None

        for day in range(29, -1, -1):
            current_date = now - timedelta(days=day)
            current_date_list = [current_date.year, current_date.month-1, current_date.day]

            result = next(((index, item) for index, item in enumerate(classical_history) if item[:-1] == current_date_list), None)
            if result:
                index, date_record = result
                if first_valid_value_index is None:
                    first_valid_value_index = index
                    first_valid_value_day = current_date_list
                last_valid_value = date_record[-1]

                history_dict[current_date.strftime('%d-%b')] = date_record[-1]
            else:
                history_dict[current_date.strftime('%d-%b')] = last_valid_value
        
        if first_valid_value_day and first_valid_value_index:
            self.fill_missing_ratings(classical_history, first_valid_value_day, first_valid_value_index, history_dict)
        else:
            self.handle_not_recent_ratings(classical_history, history_dict)
        return history_dict
    
    def handle_not_recent_ratings(self, classical_history: list, history_dict: dict):
        """Handles the case where the player hasn't played in the last 30 days."""
        last_rating = classical_history[-1][-1]
        for key in history_dict:
            if history_dict[key] is None:
                history_dict[key] = last_rating

    def fill_missing_ratings(self, classical_history: list, first_valid_value_day: list, first_valid_value_index: int, history_dict: dict):
        """Fills missing ratings for days where the player didn't play."""
        if first_valid_value_day != [datetime.now().year, datetime.now().month-1, datetime.now().day]:
            first_date_record = None
            for i, item in enumerate(reversed(classical_history[:first_valid_value_index]), start=first_valid_value_index):
                first_date_record = item
                break
            for key in history_dict:
                if history_dict[key] is None:
                    history_dict[key] = first_date_record[-1] if first_date_record else 0

    def get_last_30_day_rating_for_top_player(self, top_classical_player: str) -> tuple:
        """Returns the last 30 days of classical ratings for a given player."""
        rating_history = self.get_player_rating_history(top_classical_player)
        classical_history = self.extract_classical_history(rating_history)
        history_dict = self.generate_30_day_rating_history(classical_history)

        return (top_classical_player, history_dict)

    def generate_rating_csv_for_top_50_classical_players(self, top_50_classical: list, title: str) -> None:
        """Generates a CSV file with the last 30 days of ratings for the top 50 classical players."""
        csv_data = []
        for username in top_50_classical:
            csv_data.append(self.get_last_30_day_rating_for_top_player(username['username']))
        dates = list(csv_data[0][1].keys())
        with open(f'{title}.csv', 'w', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)
            
            # Write the header row (username followed by all dates)
            writer.writerow(['username'] + dates)
            
            # Write the data for each user
            for username, ratings in csv_data:
                row = [username] + [ratings.get(date, None) for date in dates]
                writer.writerow(row)
        print(f'{title}.csv created successfully')