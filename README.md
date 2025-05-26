# CMSC 14200 Course Project

Team members:
- GUI: James Rosenberger (jmrosenberger)
- TUI: Anna Sokolova (annsok0l)
- Art: Caden Tebow (ctebow)
- QA:  Derrick Young (dvyoung)

Enhancements:

1) GUI-SOUND: For testing the game with sounds, use the optional
command-line parameter --sounds in addition to all the other normal
Play or Show mode command-line arguments. Note the Play mode sounds
are more extensive. I've added sounds
from https://kenney.nl/assets/category:Audio?search=&sort=update
for starting the game, quitting/exiting, clicking, clearing by
hitting escape, submitting a too short, non-dictionary, or repeated word,
and for both submitting a new dictionary and new
strand word. Enjoy!

2) DICTIONARY-WORDS: For testing this functionality, use the optional
command-line parameter --words in addition to all the other normal
PLay or Show mode command-line arguments. Doing so will create
a new GAME.with-words.txt file in the assets/ directory from the original
file specified by -g game in the command-line. This newly created file, if
made, is NOT used by the Game Logic, as this addition was optional. Enjoy!

3) SOLVER: For testing this functionality, run <src/solver.py -g boards/GAMEFILE>.
For testing out the general solver, which is incomplete, run
<src/solver.py -g boards/GAMEFILE --type general>. The working solver works by
assuming that it is given the game answers as only strings, without knowing
their starting positions or steps. It then "completes" the game file, by filling in
the missing starts and steps. The general solver assumes that it only
knows the game theme and gameboard. More info about the general solver can be found in
the file, but right now it is able to find about 3-4 of the answers on each board. 
