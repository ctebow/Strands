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


Revisions:

Game Logic: The rubric item description was "Issue with hint feature.
See code comment(s)." The code comment was as follows, by line 399 of the
src/strands file:

[Code Quality] implementation maintains the hint state even after it's
been used but should return "No hint yet" whenever the hint meter
is below the threshold, regardless of the current hint state.
The current implementation is giving precedence to the "Use your current hint"
message even when the hint meter is below the threshold.
The boolean flag used to maintain the hint state may not be
properly reset when strands are successfully
submitted. 

To fix this, we first added a conditional (see NEW LOGIC comment
at the start of use_hints that checks before performing
the use_hint logic if the current hint_word has already been guessed,
and, if so, resets the hint state. This ensures
the hint state is always reset, on top of what is already present
in submit_strands. Beyond this, below in use_hint,
(see other NEW LOGIC comment), I modify another conditional so that
"No hint yet" is read whenever the hint meter is below the threshold,
irrespective of the hint state, as desired. Along with a small GUI
fix (marked by NEW LOGIC) so that any h key press would trigger self.handle_hint_conditions()
instead of only ones above the hint threshold, this solves all the problems. 

GUI: This component received two S scores in Milestone 2.

TUI:

Art: This component received two S scores in Milestone 2. There was an instructor comment
on adding docstrings for various student-created functions and classes, which has been 
resolved by adding docstrings to functions where there were no docstrings previously. 

QA:
