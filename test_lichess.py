import csv
import unittest
from lichess import LiChess
from unittest.mock import patch, MagicMock

class TestLiChess(unittest.TestCase):
    def setUp(self):
        self.lichess = LiChess()

    def test_extract_classical_history_with_valid_data(self):
        rating_history = [
            {'name': 'Blitz', 'points': [1500, 1520, 1530]},
            {'name': 'Classical', 'points': [1600, 1620, 1640]},
            {'name': 'Bullet', 'points': [1400, 1420, 1440]}
        ]
        expected = [1600, 1620, 1640]
        result = self.lichess.extract_classical_history(rating_history)
        self.assertEqual(result, expected)

    def test_extract_classical_history_with_no_classical_data(self):
        rating_history = [
            {'name': 'Blitz', 'points': [1500, 1520, 1530]},
            {'name': 'Bullet', 'points': [1400, 1420, 1440]}
        ]
        with self.assertRaises(StopIteration):
            self.lichess.extract_classical_history(rating_history)

    def test_extract_classical_history_with_empty_data(self):
        rating_history = []
        with self.assertRaises(StopIteration):
            self.lichess.extract_classical_history(rating_history)

    @patch('lichess.requests.get')
    def test_get_top_50_classical_players(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'users': ['player1', 'player2']}
        mock_get.return_value = mock_response

        result = self.lichess.get_top_50_classical_players(50)
        self.assertEqual(result, ['player1', 'player2'])
        mock_get.assert_called_once_with('https://lichess.org/api/player/top/50/classical')

    @patch('lichess.requests.get')
    def test_get_player_rating_history(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{'name': 'Classical', 'points': [1600, 1620, 1640]}]
        mock_get.return_value = mock_response

        result = self.lichess.get_player_rating_history('player1')
        self.assertEqual(result, [{'name': 'Classical', 'points': [1600, 1620, 1640]}])
        mock_get.assert_called_once_with('https://lichess.org/api/user/player1/rating-history')

    def test_generate_30_day_rating_history(self):
        classical_history = [
            [2024, 9, 1, 1600],
            [2024, 9, 2, 1620],
            [2024, 9, 3, 1640]
        ]
        result = self.lichess.generate_30_day_rating_history(classical_history)
        self.assertIsInstance(result, dict)

    @patch('lichess.LiChess.get_player_rating_history')
    @patch('lichess.LiChess.extract_classical_history')
    @patch('lichess.LiChess.generate_30_day_rating_history')
    def test_get_last_30_day_rating_for_top_player(self, mock_generate, mock_extract, mock_get_history):
        mock_get_history.return_value = [{'name': 'Classical', 'points': [1600, 1620, 1640]}]
        mock_extract.return_value = [1600, 1620, 1640]
        mock_generate.return_value = {'01-Sep': 1600, '02-Sep': 1620, '03-Sep': 1640}

        result = self.lichess.get_last_30_day_rating_for_top_player('player1')
        self.assertEqual(result, ('player1', {'01-Sep': 1600, '02-Sep': 1620, '03-Sep': 1640}))

    @patch('lichess.LiChess.get_last_30_day_rating_for_top_player')
    def test_generate_rating_csv_for_top_50_classical_players(self, mock_get_last_30_day):
        mock_get_last_30_day.side_effect = [
            ('player1', {'01-Sep': 1600, '02-Sep': 1620, '03-Sep': 1640}),
            ('player2', {'01-Sep': 1500, '02-Sep': 1520, '03-Sep': 1540})
        ]
        top_50_classical = [{'username': 'player1'}, {'username': 'player2'}]

        self.lichess.generate_rating_csv_for_top_50_classical_players(top_50_classical, 'test_users_rating')

        with open('test_users_rating.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            self.assertEqual(rows[0], ['username', '01-Sep', '02-Sep', '03-Sep'])
            self.assertEqual(rows[1], ['player1', '1600', '1620', '1640'])
            self.assertEqual(rows[2], ['player2', '1500', '1520', '1540'])

if __name__ == '__main__':
    unittest.main()
