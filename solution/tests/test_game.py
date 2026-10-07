import unittest
from random import Random

from game import Game


class GameTests(unittest.TestCase):
    def test_shuffle_and_countdown(self):
        for seed in range(50):
            game = Game()
            game.start(10, Random(seed))
            self.assertEqual(sorted(game.board), list(range(9)))
            self.assertNotEqual(game.board, list(range(9)))
            self.assertFalse(game.swap(0, 1, 12))
            self.assertEqual(game.elapsed(15), 2)

    def test_swap_validation_and_completion(self):
        game = Game()
        game.start(0)
        game.board = [1, 0, 2, 3, 4, 5, 6, 7, 8]
        for a, b in [(0, 0), (-1, 1), (0, 9), (True, 2), (1.5, 2)]:
            self.assertFalse(game.swap(a, b, 4))
        self.assertTrue(game.swap(0, 1, 5))
        self.assertEqual(game.phase, "solved")
        self.assertEqual(game.elapsed(100), 2)
        self.assertEqual(game.moves, 1)
        self.assertFalse(game.swap(0, 1, 101))

    def test_pause_resume_and_replay(self):
        game = Game()
        game.start(0)
        game.pause(5)
        self.assertEqual(game.elapsed(100), 2)
        game.resume(100)
        self.assertEqual(game.elapsed(102), 2)
        self.assertEqual(game.elapsed(105), 4)
        game.start(200)
        self.assertEqual(game.moves, 0)
        self.assertEqual(game.elapsed(201), 0)
