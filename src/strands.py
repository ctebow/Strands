from base import PosBase, StrandBase, BoardBase, StrandsGameBase


class Pos(PosBase):
    def take_step(self, step: Step) -> "PosBase":
        raise NotImplementedError
    
    def step_to(self, other: "PosBase") -> Step:
        raise NotImplementedError
    
    def is_adjacent_to(self, other: object) -> bool:
        raise NotImplementedError

class Strand(StrandBase):
    def positions(self) -> list[PosBase]:
        raise NotImplementedError
    
    def is_cycle(self) -> bool:
        raise NotImplementedError
    
    def is_folded(self) -> bool:
        raise NotImplementedError
    

class Board(BoardBase):
    def num_rows(self) -> int:
        raise NotImplementedError
    
    def num_cols(self) -> int:
        raise NotImplementedError

    def get_letter(self, pos: PosBase) -> str:
        raise NotImplementedError
    
    def evaluate_strand(self, strand: StrandBase) -> str:
        raise NotImplementedError

class StrandsGame(StrandsGameBase):
    def theme(self) -> str:
        raise NotImplementedError
    
    def board(self) -> BoardBase:
        raise NotImplementedError
    
    def answers(self) -> list[tuple[str, StrandBase]]:
        raise NotImplementedError
    
    def found_strands(self) -> list[StrandBase]:
        raise NotImplementedError
    
    def game_over(self) -> bool:
        raise NotImplementedError
    
    def hint_threshold(self) -> int:
        raise NotImplementedError
    
    def hint_meter(self) -> int:
        raise NotImplementedError

    def active_hint(self) -> None | tuple[int, bool]:
        raise NotImplementedError
        
    def submit_strand(self, strand: StrandBase) -> tuple[str, bool] | str:
        raise NotImplementedError
    
    def use_hint(self) -> tuple[int, bool] | str:
        raise NotImplementedError