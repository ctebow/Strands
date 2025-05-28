# src/tui.py
import os
import random
import click
from strands import StrandsGame
from ui import TUI
from stubs import ArtTUIStub
from art_tui import ART_FRAMES  # A dictionary that maps frame names (like "cat1") to frame classes

@click.command()
@click.option('--show', is_flag=True, help="Start the game in show mode (answers revealed).")
@click.option('-g', '--game', type=str, help="Pick a specific board to play (just the name, no .txt).")
@click.option('-h', '--hint', 'hint_threshold', type=int, default=3, help="How many correct strands before a hint becomes available.")
@click.option('-a', '--art', 'art_frame_name', type=str, default=None, help="Which art frame to use (e.g., cat1, cat4, trees).")
@click.option('-f', '--frame', 'frame_width', type=int, default=None, help="How thick the border/frame should be.")
@click.option('-w', '--width', 'interior_width', type=int, default=None, help="How wide the inside of the game area should be.")
@click.option('-e', '--height', 'interior_height', type=int, default=None, help="How tall the inside of the game area should be.")
def main(show: bool, game: str, hint_threshold: int, art_frame_name: str,
         frame_width: int, interior_width: int, interior_height: int) -> None:
    """
    Entry point for the Strands TUI. Launches a game with optional features like show mode,
    custom art frames, hint threshold, and size adjustments.
    """
    
    # Decide which game file to load. If the user doesn't pick one, we choose randomly.
    board_dir = "boards"
    if game is None:
        game_files = [f for f in os.listdir(board_dir) if f.endswith(".txt")]
        game_file = os.path.join(board_dir, random.choice(game_files))
    else:
        game_file = os.path.join(board_dir, f"{game}.txt")
        if not os.path.exists(game_file):
            print(f"Error: Game file '{game_file}' does not exist.")
            return

    # Try to create a StrandsGame instance with the chosen board and hint rule
    try:
        game = StrandsGame(game_file, hint_threshold=hint_threshold)
    except Exception as e:
        print(f"Error loading game: {e}")
        return

    # Figure out which frame to use. If user gave us a name, check if it's supported.
    art_cls = ArtTUIStub
    if art_frame_name is not None:
        art_cls = ART_FRAMES.get(art_frame_name)
        if art_cls is None:
            print(f"Error: Art frame '{art_frame_name}' is not supported.")
            return

    # Try to create the frame (art object) based on user's dimensions or fallback defaults
    try:
        if art_frame_name == "cat4":
            # cat4 has a fixed 8x6 board, so we don’t need user input
            interior_width = 8
            interior_height = 6
            frame_width = 2 if frame_width is None else frame_width
        else:
            # For all other frames, use default dimensions if not provided
            interior_width = interior_width or 24
            interior_height = interior_height or 14
            frame_width = frame_width or 2

        # Actually create the frame object
        art = art_cls(interior_width=interior_width, interior_height=interior_height, frame_width=frame_width)
    except Exception as e:
        print(f"Error initializing art frame: {e}")
        return

    # Finally, launch the text-based interface using everything we've set up
    tui = TUI(game, art, show=show)
    tui.run()

# This ensures the game launches if this script is run directly (like `python tui.py`)
if __name__ == "__main__":
    main()
