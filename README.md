# crossword
This project has two parts:
     1. It has a crossword puzzle visualizer / editor module made using pygame. I indend to change the package in the future away from pygame.
     2. It has a crossword puzzle auto-completion module that attempts to automatically fill in blank spaces in crossword puzzles generated in the editor module. It is currently highly inefficient, though I think it should be correct. There are at least some cases that yield a false negative still, which I am trying to figure out. The running time is heavily dependent on the size of the list of words input as viable options for the auto-completer to draw from. I think the running time should be significantly improved by partially filling in some desired words (such as the intended theme of the puzzle) before trying the auto-completer, though I haven't tested this out yet.
