from game import Game

player_names = ['Raj', 'Jay', 'Kasra', 'Scott', 'Ethan']

game = Game(player_names, 1, 2)

game.start_game_loop()

print(game.players)