# battleship

This project was part of course I took on human computer interaction with AI.
I wrote the battleship game from scratch using PyGame, and implemented an AI
that uses a bayesian model to find the most likely location of an enemies ship.
One can play against a human opponent, where the AI can offer hints with 
adaptive frequency based on user feedback, and rate your previous guess. The 
AI can also rate your setup before confirming it. Lastly, one can play against
the AI, and chose between three different difficulty levels:
1 - Random bot
2 - The AI difficulty adjusts to your own level of play
3 - The AI chooses the highest probability moves.

One can also access a heatmap of the AIs probability estimates using the 
options button. 

To play the game, run python3 battleship.py. The game window will open, 
allowing you to select an opponent and the level of difficulty if an AI 
opponent is selected. Then, each player will set up their ships, you can 
rotate the ships with the left and right arrow keys, as well as a right click.
Once all ships are places you can get a rating of their setup (note that this 
takes several minutes, as it's based on the AI playing multiple games against 
you). From there you can take turns guessing where your opponents ships are, 
and they guess the locations of yours. You can also get hints from the AI if 
you'd like, it doesn't use the true locations of the enemy ships, but a 
probabilistic model instead. The video below shows an example of starting 
the game, and using some of the features. 

Note: the mouse being flipped is a feature of the screen recording and does not actually happen in the game

[Screen recording 2022-10-06 2.43.09 PM.webm](https://user-images.githubusercontent.com/38572823/194654172-95943be2-4f8b-4175-a8dd-4c0b1881ff8d.webm)
