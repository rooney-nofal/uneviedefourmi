# Une vie de fourmi

This version deliberately keeps the same algorithm and the same order of operations as the original code.

Only one real split was made to match the exercise structure:
- `main.py` keeps the data, graph creation, time-expanded graph, maximum-flow search, output and animation.
- `ants.py` contains the original STEP 3 and STEP 4 blocks: reconstructing one path per ant and creating the E1, E2, E3... movement lists.

The code identifiers and comments are translated into English, but the algorithm is not redesigned.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Change `name = "zero"` in `main.py` to test:
`zero`, `un`, `deux`, `trois`, `quatre`, `cinq`, `3D`, `mort`, `at-ant`.
