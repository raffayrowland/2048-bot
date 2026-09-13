## 2048 Bot

This bot uses the expectimax algorithm to calculate future board positions, and then selects the move which maximises the expected
score. Note that the score it is maximising is not the game score, rather a function that takes a board position and outputs a number
that approximates a board's quality and potential for future success.

## Demo

This was one of the runs which reached the 8,192 tile, taking about 14 minutes and reaching a final score of 133,216

![gif](2048.gif)

### Board scoring function

The scoring function takes multiple factors in to account, such as the number of empty squares, the distances between high value 
tiles, and the 'snake score', which weights squares on the board differently, causing the bot to put high-value tiles on high-value 
squares, and vice versa. 

The parameters used by this function are trained using a genetic algorithm, using a population of 150 players running 10 episodes per
generation for 5 generations. The result can be found in the file params/best_ga_params.json. 

### Evaluation Metrics

Over 1000 games, the bot scored an average of 46,935 points, almost 2.5x higher than an average human. It reached the 2048 tile
in 89.3% of the games it played, and the 4096 tile in 39.8%. The highest tile it reached was 8,192, which it reached 11 times. 

## Running the bot yourself

Clone the repository and create an environment
```
git clone https://github.com/raffayrowland/2048-bot.git
cd 2048-bot
python3 -m venv venv
source venv/bin/activate
```

Run the bot with pretrained parameters
```
python expectimax.py
```
