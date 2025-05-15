import pytest
import os

from strands import Pos, Strand, Board, StrandsGame
from base import Step, PosBase, StrandBase, BoardBase, StrandsGameBase
from fakes import StrandFake, BoardFake, StrandsGameFake 


def test_inheritance() -> None:
    assert issubclass(Pos, PosBase)
    assert issubclass(Strand, StrandBase)
    assert issubclass(Board, BoardBase)
    assert issubclass(StrandsGame, StrandsGameBase)


def test_take_pos_step() -> None:
    pos = Pos(0, 0)
    assert pos.take_step(Step.N) == Pos(-1, 0)
    assert pos.take_step(Step.S) == Pos(1, 0)
    assert pos.take_step(Step.E) == Pos(0, 1)
    assert pos.take_step(Step.W) == Pos(0, -1)
    assert pos.take_step(Step.NE)== Pos(-1, 1)
    assert pos.take_step(Step.NW) == Pos(-1, -1)
    assert pos.take_step(Step.SE) == Pos(1, 1)
    assert pos.take_step(Step.SW) == Pos(1, -1)

def test_pos_to_success() -> None:
    pos = Pos(0,0)
    directions = [
        (Step.N, Pos(-1, 0)),
        (Step.S, Pos(1, 0)),
        (Step.E, Pos(0, 1)),
        (Step.W, Pos(0, -1)),
        (Step.NW, Pos(-1, -1)),
        (Step.NE, Pos(-1, 1)),
        (Step.SW, Pos(1, -1)),
        (Step.SE, Pos(1,1)),
    ]
    for step, other in directions:
        assert pos.step_to(other) == step


def test_pos_to_failure() -> None:
    pos = Pos(0,0)
    invalids = [Pos(0,2), Pos(2, 0), Pos(2, 2), Pos(-2, -1)]
    for other in invalids:
        with pytest.raises(ValueError):
            pos.step_to(other)

def test_strand_position_straight_cardinal() -> None:
    strand_n = Strand(Pos(4, 2), [Step.N, Step.N, Step.N])
    strand_s = Strand(Pos(0, 2), [Step.S, Step.S, Step.S])
    strand_e = Strand(Pos(2, 0), [Step.E, Step.E, Step.E])
    strand_w = Strand(Pos(2, 4), [Step.W, Step.W, Step.W])

    assert strand_n.positions() == [Pos(4, 2), Pos(3, 2), Pos(2, 2), Pos(1, 2)]
    assert strand_s.positions() == [Pos(0, 2), Pos(1, 2), Pos(2, 2), Pos(3, 2)]
    assert strand_e.positions() == [Pos(2, 0), Pos(2, 1), Pos(2, 2), Pos(2, 3)]
    assert strand_w.positions() == [Pos(2, 4), Pos(2, 3), Pos(2, 2), Pos(2, 1)]



def test_strand_positions_straight_intercardinal() -> None:
    strand_ne = Strand(Pos(3, 0), [Step.NE, Step.NE, Step.NE])
    strand_nw = Strand(Pos(3, 4), [Step.NW, Step.NW, Step.NW])
    strand_se = Strand(Pos(0, 0), [Step.SE, Step.SE, Step.SE])
    strand_sw = Strand(Pos(0, 4), [Step.SW, Step.SW, Step.SW])

    assert strand_ne.positions() == [Pos(3, 0), Pos(2, 1), Pos(1, 2), Pos(0, 3)]
    assert strand_nw.positions() == [Pos(3, 4), Pos(2, 3), Pos(1, 2), Pos(0, 1)]
    assert strand_se.positions() == [Pos(0, 0), Pos(1, 1), Pos(2, 2), Pos(3, 3)]
    assert strand_sw.positions() == [Pos(0, 4), Pos(1, 3), Pos(2, 2), Pos(3, 1)]


def test_strand_positions_long_folded_vs_unfolded() -> None:
    unfolded = Strand(
        Pos(1, 1),
        [Step.E, Step.SE, Step.S, Step.SW, Step.W, Step.NW, Step.N, Step.NE],
    )
    folded = Strand(
        Pos(0, 0), [Step.S, Step.S, Step.E, Step.E, Step.N, Step.W, Step.N, Step.W]
    )

    assert not unfolded.is_folded()
    assert folded.is_folded()

def test_is_not_cyclic() -> None:
    strand1 = Strand(Pos(0,0), [Step.E, Step.E, Step.E])
    strand2 = Strand(Pos(1,1), [Step.SE, Step.NE, Step.W])
    strand3 = Strand(Pos(2,2), [Step.N, Step.NE, Step.E])
    strand4 = Strand(Pos(3,3), [Step.W, Step.S, Step.E])

    assert not strand1.is_cyclic()
    assert not strand2.is_cyclic()
    assert not strand3.is_cyclic()
    assert not strand4.is_cyclic()

def test_is_cyclic() -> None:
    strand1 = Strand(Pos(0,0), [Step.E, Step.W])
    strand2 = Strand(Pos(1,1), [Step.W, Step.S, Step.E, Step.N])
    strand3 = Strand(Pos(2,2), [Step.NE, Step.W, Step.W, Step.SW])
    strand4 = Strand(Pos(3,3), [Step.SW, Step.NW, Step.NE, Step.SE])

    assert strand1.is_cyclic()
    assert strand2.is_cyclic()
    assert strand3.is_cyclic()
    assert strand4.is_cyclic()


def test_load_game_cs_142_txt() -> None:
    game = StrandsGame("boards/cs-142.txt")
    assert game.theme() == '"CS 142"'
    assert game.board().num_rows() == 3
    assert game.board().num_cols() == 5


def test_load_game_cs_142_variations() -> None:
    variants = [
        """"CS 142"
C S M C T
O F O R Y
N E O W T
cmsc 1 4 w w w
one 2 1 s e
forty 2 2 e e ne s
two 3 5 w w
        """,
        """"CS 142"
  C S M C T  
  O F O R Y
  N E O W T
cmsc 1 4 w  w w
  one 2 1  s e
FORTY 2 2 e e ne s
TWO 3 5 w w
        """,
    ]
    for txt in variants:
        game = StrandsGame(txt.strip().splitlines())
        assert game.theme().lower() == '"cs 142"'
        assert game.board().num_rows() == 3
        assert game.board().num_cols() == 5
        assert len(game.answers()) == 4

def test_load_game_cs_142_invalid() -> None:
    bad_variants = [
        """"CS 142"
C S M C
O F O R Y
N E O W T
cmsc 1 4 w w w
        """,
        """"CS 142"
C S M C T
O F O R Y
N E O W T
cmsc 1 4 x x x
        """,
        """"CS 142"
C S M C T
O F O R Y
N E O W T
cmsc 2 4 w w w
        """,
    ]
    for txt in bad_variants:
        with pytest.raises(ValueError):
            StrandsGame(txt.splitlines())

def test_play_game_cs_142_once() -> None:
    game = StrandsGame("boards/cs-142.txt")
    assert game.submit_strand(Strand(Pos(0, 3), [])) == ("cmsc", True)
    assert game.submit_strand(Strand(Pos(1, 0), [])) == ("one", True)
    assert game.submit_strand(Strand(Pos(1, 1), [])) == ("forty", True)
    assert game.submit_strand(Strand(Pos(2, 4), [])) == ("two", True)
    assert game.game_over()


def test_play_game_cs_142_twice() -> None:
    game = StrandsGame("boards/cs-142.txt")
    game.submit_strand(Strand(Pos(1, 1), []))
    game.submit_strand(Strand(Pos(2, 4), []))
    game.submit_strand(Strand(Pos(0, 3), []))
    game.submit_strand(Strand(Pos(1, 0), []))
    assert game.game_over()


def test_play_game_cs_142_more() -> None:
    game = StrandsGame("boards/cs-142.txt")
    assert game.use_hint() == (0, False)
    assert game.use_hint() == (0, True)
    assert game.use_hint() == "Use your current hint"
    assert game.submit_strand(Strand(Pos(0, 3), [])) == ("cmsc", True)
    assert game.submit_strand(Strand(Pos(1, 0), [])) == ("one", True)
    assert game.use_hint() == (2, False)
    assert game.submit_strand(Strand(Pos(1, 1), [])) == ("forty", True)
    assert game.submit_strand(Strand(Pos(2, 4), [])) == ("two", True)
    assert game.game_over()

def test_overlapping() -> None:
   game1 = StrandsGame("boards/cs-142.txt")
   game2 = StrandsGame("boards/cs-142.txt")
   
   strand1 = Strand(Pos(1,1), [Step.E, Step.E, Step.NE, Step.S])
   strand2 = Strand(Pos(1,1), [Step.E, Step.E, Step.SE, Step.N])
   
   result1 = game1.submit_strand(strand1)
   result2 = game2.submit_strand(strand2)
   
   assert result1 == ("forty", True)
   assert result2 == ("forty", True)

def test_load_game_directions_file() -> None:
    game = StrandsGame("boards/directions.txt")
    assert game.theme() == '"Directions"'
    assert game.board().num_rows() == 7
    assert game.board().num_cols() == 4

def test_load_game_cs_142_variations() -> None:
    game1 = StrandsGame("boards/cs-142.txt")
    text_variant = [
        '"CS 142"',
        '',
        'C S M C T',
        'O F O R Y',
        'N E O W T',
        '',
        'cmsc 1 4 w w w',
        'one 2 1 s e',
        'forty 2 2 e e ne s',
        'two 3 5 w w',
    ]
    game2 = StrandsGame(text_variant)

    assert game1.theme() == game2.theme()
    assert game1.board().num_rows() == game2.board().num_rows()
    assert game1.board().num_cols() == game2.board().num_cols()
    assert {word for word, _ in game1.answers()} == {word for word, _ in game2.answers()}

def test_game_directions_invalid() -> None:

    bad_variant1 = [
        '"Directions"',
        'E A S T',
        'T S E W',
        'S H D R',
        '',
        'east 1 1 z z'
    ]
    bad_variant2 = [
        '"Directions"',
        'E A S T',
        'T S E W',
        'S H D R',
        '',
        'east 9 9 e kw e'
    ]
    bad_variant3 = [
        '"Directions"',
        'E A S T',
        'T S E W',
        'S H D R',
        '',
        'east'
    ]

    for bad_variant in [bad_variant1, bad_variant2, bad_variant3]:
        with pytest.raises(Exception):
            StrandsGame(bad_variant)

def test_play_game_directions_once() -> None:
    game = StrandsGame("boards/directions.txt")

    result1 = game.submit_strand(Strand(Pos(0, 0), [Step.E, Step.E, Step.E]))
    result2 = game.submit_strand(Strand(Pos(1, 3), [Step.W, Step.W, Step.W]))
    result3 = game.submit_strand(Strand(Pos(2, 0), [Step.S, Step.S, Step.S, Step.S]))
    result4 = game.submit_strand(Strand(Pos(6, 1), [Step.N, Step.N, Step.N, Step.N]))

    assert result1 == ("east", True)
    assert result2 == ("west", True)
    assert result3 == ("south", True)
    assert result4 == ("north", True)

    found_words = {word for word, _ in game.answers()}
    assert found_words == {"directions", "east", "west", "south", "north"}

def test_play_game_directions_twice() -> None:
    game = StrandsGame("boards/directions.txt")

    assert game.submit_strand(Strand(Pos(0, 0), [Step.E, Step.E, Step.E])) == ("east", True)
    assert game.submit_strand(Strand(Pos(1, 3), [Step.W, Step.W, Step.W])) == ("west", True)

    assert game.submit_strand(Strand(Pos(0, 0), [Step.E, Step.E, Step.E])) == "Already found"
    assert game.submit_strand(Strand(Pos(1, 3), [Step.W, Step.W, Step.W])) == "Already found"

    found = {word for word, _ in game.answers()}
    assert found == {"directions", "north", "south", "east", "west"}

def test_play_game_directions_three_times() -> None:
   game = StrandsGame("boards/directions.txt")
   
   assert game.submit_strand(Strand(Pos(0, 0), [Step.E, Step.E, Step.E])) == ("east", True)
   assert game.submit_strand(Strand(Pos(1, 3), [Step.W, Step.W, Step.W])) == ("west", True)
   assert game.submit_strand(Strand(Pos(2, 0), [Step.S, Step.S, Step.S, Step.S])) == ("south", True)
   assert game.submit_strand(Strand(Pos(6, 1), [Step.N, Step.N, Step.N, Step.N])) == ("north", True)
   assert game.submit_strand(Strand(Pos(3, 3), [Step.S, Step.NE, Step.S, Step.S, Step.S, Step.NW, Step.S, Step.SE, Step.W])) == ("directions", True)
   
   found = {word for word, strand in game.answers()}
   assert "directions" in found

def test_play_game_directions_three_times() -> None:
    game = StrandsGame("boards/directions.txt")

    assert game.submit_strand(Strand(Pos(0, 0), [Step.E, Step.E, Step.E])) == ("east", True)
    assert game.submit_strand(Strand(Pos(1, 3), [Step.W, Step.W, Step.W])) == ("west", True)
    assert game.submit_strand(Strand(Pos(2, 0), [Step.S, Step.S, Step.S, Step.S])) == ("south", True)
    assert game.submit_strand(Strand(Pos(6, 1), [Step.N, Step.N, Step.N, Step.N])) == ("north", True)

    result = game.submit_strand(Strand(Pos(3, 3), [
        Step.S, Step.NE, Step.S, Step.S, Step.S,
        Step.NW, Step.S, Step.SE, Step.W
    ]))

    assert result == ("directions", True) or result == "Already found"

    found = {word for word, _ in game.answers()}
    assert "directions" in found

def test_play_game_directions_more() -> None:
    game = StrandsGame("boards/directions.txt")

    assert game.submit_strand(Strand(Pos(0, 0), [Step.E, Step.E, Step.E])) == ("east", True)
    assert game.submit_strand(Strand(Pos(1, 3), [Step.W, Step.W, Step.W])) == ("west", True)
    assert game.submit_strand(Strand(Pos(2, 0), [Step.S, Step.S, Step.S, Step.S])) == ("south", True)
    assert game.submit_strand(Strand(Pos(6, 1), [Step.N, Step.N, Step.N, Step.N])) == ("north", True)

    result = game.submit_strand(Strand(Pos(3, 3), [
        Step.S, Step.NE, Step.S, Step.S, Step.S,
        Step.NW, Step.S, Step.SE, Step.W
    ]))

    assert result == ("directions", True) or result == "Already found"

    found = {word for word, _ in game.answers()}
    assert found == {"east", "west", "south", "north", "directions"}

def test_valid_game_files() -> None:
    for filename in os.listdir("boards"):
        if filename.endswith(".txt"):
            filepath = f"boards/{filename}"
            try:
                StrandsGame(filepath)
            except Exception as e:
                raise AssertionError(f"Failed to load {filename}: {e}")