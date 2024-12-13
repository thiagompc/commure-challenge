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

    def get_last_30_day_rating_for_top_player(self, top_classical_player: str) -> list:
        """Returns the last 30 days of classical ratings for a given player."""
        response = requests.get(f'{self.lichess_url}/user/{top_classical_player}/rating-history')
        response.raise_for_status()
        user_rating_history = response.json()

        # Extract the classical rating history
        classical_history = next(item['points'] for item in user_rating_history if item['name'] == 'Classical')

        # Initialize variables to keep track of the last and the first valid value
        last_valid_value = None
        first_valid_value_index = None
        first_valid_value_day = None

        history_dict = {}
        now = datetime.now()

        # Iterate over the last 30 days
        for day in range(29, -1, -1):
            current_date = now - timedelta(days=day)
            current_date_list = [current_date.year, current_date.month-1, current_date.day]

            # Check if the target date exists in the classical history
            result = next(((index, item) for index, item in enumerate(classical_history) if item[:-1] == current_date_list), None)
            if result:
                index, date_record = result
                if first_valid_value_index is None:
                    first_valid_value_index = index 
                    first_valid_value_day = current_date_list
                last_valid_value = date_record[-1]
                    
                history_dict[current_date.strftime('%d-%b')] = date_record[-1]
            else:
                # Keep same score if user didn't play that day
                history_dict[current_date.strftime('%d-%b')] = last_valid_value

        # Gets the first rating if the player doesn't have a rating for the first day
        current_date = now - timedelta(days=29)
        if first_valid_value_day != [current_date.year, current_date.month-1, current_date.day]:
            first_date_record = None
            for i, item in enumerate(reversed(classical_history[:first_valid_value_index]), start=index):
                first_date_record = item
                break
            for key in history_dict:
                if history_dict[key] is None:
                    history_dict[key] = first_date_record[-1] if first_date_record else 0

        return (top_classical_player, history_dict)

    def generate_rating_csv_for_top_50_classical_players(self, top_50_classical: list) -> None:
        """Generates a CSV file with the last 30 days of ratings for the top 50 classical players."""
        csv_data = []
        for username in top_50_classical:
            csv_data.append(self.get_last_30_day_rating_for_top_player(username['username']))
        dates = list(csv_data[0][1].keys())
        with open('user_ratings.csv', 'w', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)
            
            # Write the header row (username followed by all dates)
            writer.writerow(['username'] + dates)
            
            # Write the data for each user
            for username, ratings in csv_data:
                row = [username] + [ratings.get(date, None) for date in dates]
                writer.writerow(row)
        print("users_ratings.csv created successfully")