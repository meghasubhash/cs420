# csce420-fall24

## How to Run
To run the program, use the following command from the terminal:

python blocksworld.py <filename> [-MAX_ITERS <int>]

## Example Commands
python blocksworld.py probA03.bwp
python blocksworld.py probA05.bwp -MAX_ITERS 200000

## Known Limitations
- The program performs efficiently on simpler Blocksworld problems with up to 7-10 moves.
- For larger problems, memory usage and performance may degrade due to the BFS's search nature.
- The default iteration limit is 100,000 but you can adjust this using the -MAX_ITERS flag.