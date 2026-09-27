# Flappy Bird AI — NeuroEvolution with a Genetic Algorithm

A from-scratch Flappy Bird clone in Python/Pygame where a population of birds learns
to play the game through evolution — no machine learning libraries, no NEAT-style
frameworks. The neural network (a single-layer linear model) and the genetic algorithm
(selection, mutation, elitism, checkpointing) are both hand-implemented.

You can also jump in and play against the AI yourself once it's had generations to train.

## How it works

- **The "brain":** each bird has a tiny neural network — 8 weighted inputs (its own
  height and velocity, the position of the nearest pipe gap, and the position of the
  *next* pipe gap after that) squashed through an `atan`-based activation function to
  decide whether to flap.
- **The "evolution":** every generation, the birds that survive longest are selected
  as parents. New birds are bred by mixing weights from multiple top performers
  (crossover) and nudging them slightly (mutation). The single best bird from each
  generation is carried forward unchanged (elitism) so progress is never lost.
- **Checkpointing ("Hall of Fame" mode):** the best bird's weights and score are saved
  to `best_bird.json`. Future runs can load that file and continue refining from where
  the previous run left off — letting you run several shorter training sessions with a
  shrinking mutation rate instead of one long one.
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

## What I learned building this

- Building a genetic algorithm from scratch: fitness, selection, crossover, and
  mutation, before ever touching a game.
- Why raw, unnormalized inputs can saturate an activation function and silently stall
  learning — and how to normalize inputs to fix it.
- Debugging a subtle state bug where a breeding-pool variable was being silently reset
  every frame while waiting for the next generation to spawn, discovered by instrumenting
  the code with print statements rather than guessing.
- The importance of tracking fitness per-individual rather than relying on shared,
  global state, especially once a population starts dying and respawning dynamically.

## Possible next steps

- Track average population fitness per generation (not just the top performer) and
  chart it over time.
- Add a small hidden layer to the network instead of a single linear layer.
- Speciation (à la NEAT) so structurally different strategies aren't forced to compete
  head-to-head too early.
