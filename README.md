# Flappy Bird AI — NeuroEvolution with a Genetic Algorithm

This project is my version of Flappy Bird using Python and Pygame, where a population of birds
learns to play the game through evolution. This project doesn't use any machine learning libraries
or NEAT frameworks. The single-layer neural network and genetic algorithm are hand-implemented.

You can also jump in and play against the AI yourself, or just sit back and watch it train itself.

## How it works

- **The "brain":** each bird has a neural network made of 8 weighted inputs (its own
  height and velocity, the positions of the nearest pipe, and the positions of the
  *next* nearest pipes after that) which is then squashed through an `atan`-based
  activation function to decide whether or not to flap.
- **The "evolution":** After every generation, the birds that survive the longest are selected
  as parents. The next generation of birds is bred by mixing weights from multiple top performers
  (crossover) and nudging them slightly by a set mutation percentage. The single best bird from each
  generation is carried forward unchanged (elitism), so progress is never lost if mutations go south.
- **Checkpointing ("Hall of Fame" mode):** If the "HALL_OF_FAME" variable is set to true,
  the best bird's weights and score are saved to `best_bird.json`. Future runs can load that
  file and continue refining from where the previous run left off — letting you run several
   shorter training sessions with a shrinking mutation rate instead of one long one to refine further.
- **Human vs. AI:** press Space to jump in and play alongside the current AI
  generation. The high score of the best AI bird ever recorded is shown on screen.

## Controls

| Key | Action |
|---|---|
| `Space` / `W` / `Up Arrow` | Flap (as the human player) |
| `P` | Force the current generation to end early and start the next one |

## Running it

```bash
pip install pygame
python3 FlappyBirdAivPlayer.py
```

You'll need the sprite assets in the same folder as the script:
`flappybirdbg1.png`, `flappybirdbg.png`, `flappybirdai.png`, `flappybird_god.png`,
`flappybird.png`, `toppipe.png`, `bottompipe.png`.

## What I learned building this/Issues I faced

- Building a genetic algorithm from scratch: fitness, selection, crossover, and
  mutation.
- I learned why unnormalized inputs can saturate an activation function and stall
  learning, and how to normalize inputs to fix it.
- Debugging a hidden bug where a breeding-pool variable was being silently reset
  every frame while waiting for the next generation to spawn, discovered by instrumenting
  the code with print statements.

## Possible next steps

- Track average population fitness per generation (not just the top performer) and
  chart it over time.
- Add a hidden layer to the network instead of a single linear layer for increased complexity
