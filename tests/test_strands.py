import pytest

from src.strands import Pos, Strand, Board, StrandsGame
from base import Step, PosBase, StrandBase, BoardBase, StrandsGameBase
from fakes import StrandFake, BoardFake, StrandsGameFake 


def test_inheritance() -> None:
    assert issubclass(Pos, PosBase)
    assert issubclass(StrandFake, StrandBase)
    assert issubclass(BoardFake, BoardBase)
    assert issubclass(StrandsGameFake, StrandsGameBase)


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
    strand_n = StrandFake(Pos(4, 2), [Step.N, Step.N, Step.N])
    strand_s = StrandFake(Pos(0, 2), [Step.S, Step.S, Step.S])
    strand_e = StrandFake(Pos(2, 0), [Step.E, Step.E, Step.E])
    strand_w = StrandFake(Pos(2, 4), [Step.W, Step.W, Step.W])

    assert strand_n.positions() == [Pos(4, 2), Pos(3, 2), Pos(2, 2), Pos(1, 2)]
    assert strand_s.positions() == [Pos(0, 2), Pos(1, 2), Pos(2, 2), Pos(3, 2)]
    assert strand_e.positions() == [Pos(2, 0), Pos(2, 1), Pos(2, 2), Pos(2, 3)]
    assert strand_w.positions() == [Pos(2, 4), Pos(2, 3), Pos(2, 2), Pos(2, 1)]



def test_strand_positions_straight_intercardinal() -> None:
    strand_ne = StrandFake(Pos(3, 0), [Step.NE, Step.NE, Step.NE])
    strand_nw = StrandFake(Pos(3, 4), [Step.NW, Step.NW, Step.NW])
    strand_se = StrandFake(Pos(0, 0), [Step.SE, Step.SE, Step.SE])
    strand_sw = StrandFake(Pos(0, 4), [Step.SW, Step.SW, Step.SW])

    assert strand_ne.positions() == [Pos(3, 0), Pos(2, 1), Pos(1, 2), Pos(0, 3)]
    assert strand_nw.positions() == [Pos(3, 4), Pos(2, 3), Pos(1, 2), Pos(0, 1)]
    assert strand_se.positions() == [Pos(0, 0), Pos(1, 1), Pos(2, 2), Pos(3, 3)]
    assert strand_sw.positions() == [Pos(0, 4), Pos(1, 3), Pos(2, 2), Pos(3, 1)]


def test_strand_positions_long_folded_vs_unfolded() -> None:
    unfolded = StrandFake(
        Pos(1, 1),
        [Step.E, Step.SE, Step.S, Step.SW, Step.W, Step.NW, Step.N, Step.NE],
    )
    folded = StrandFake(
        Pos(0, 0), [Step.S, Step.S, Step.E, Step.E, Step.N, Step.W, Step.N, Step.W]
    )

    assert not unfolded.is_folded()
    assert folded.is_folded()

def test_load_game_cs_142_txt() -> None:
    game = StrandsGameFake("boards/cs-142.txt")
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
        game = StrandsGameFake(txt.strip().splitlines())
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
            StrandsGameFake(txt.splitlines())

def test_play_game_cs_142_once() -> None:
    game = StrandsGameFake("boards/cs-142.txt")
    assert game.submit_strand(StrandFake(Pos(0, 3), [])) == ("cmsc", True)
    assert game.submit_strand(StrandFake(Pos(1, 0), [])) == ("one", True)
    assert game.submit_strand(StrandFake(Pos(1, 1), [])) == ("forty", True)
    assert game.submit_strand(StrandFake(Pos(2, 4), [])) == ("two", True)
    assert game.game_over()


def test_play_game_cs_142_twice() -> None:
    game = StrandsGameFake("boards/cs-142.txt")
    game.submit_strand(StrandFake(Pos(1, 1), []))
    game.submit_strand(StrandFake(Pos(2, 4), []))
    game.submit_strand(StrandFake(Pos(0, 3), []))
    game.submit_strand(StrandFake(Pos(1, 0), []))
    assert game.game_over()


def test_play_game_cs_142_more() -> None:
    game = StrandsGameFake("boards/cs-142.txt")
    assert game.use_hint() == (0, False)
    assert game.use_hint() == (0, True)
    assert game.use_hint() == "Use your current hint"
    assert game.submit_strand(StrandFake(Pos(0, 3), [])) == ("cmsc", True)
    assert game.submit_strand(StrandFake(Pos(1, 0), [])) == ("one", True)
    assert game.use_hint() == (2, False)
    assert game.submit_strand(StrandFake(Pos(1, 1), [])) == ("forty", True)
    assert game.submit_strand(StrandFake(Pos(2, 4), [])) == ("two", True)
    assert game.game_over()
