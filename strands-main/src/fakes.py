"""
Game logic for Milestone 1:
Pos, StrandFake, BoardFake, StrandsGameFake
"""
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step

class Pos(PosBase):
    
    def take_step(self, step: Step) -> "Pos":

        c = self.c
        r = self.r

        if "w" in step:
            c -= 1
        if "n" in step:
            r -= 1
        if "s" in step:
            r += 1
        if "e" in step:
            c += 1

        return Pos(r, c)

    def step_to(self, other: "Pos") -> Step:

        if self == other:
            raise ValueError

        r_dist = self.r - other.r
        c_dist = self.c - other.c

        if abs(r_dist) < 2 and abs(c_dist) < 2: # instructions said two steps??
                                                # i think they mean like NW or SE
            step = ""

            if r_dist == -1:
                step += "s"
            else:
                step += "n"
            if c_dist == -1:
                step += "e"
            else:
                step += "w"
        
            return step

        else:
            raise ValueError
    
    def is_adjacent_to(self, other: "Pos") -> bool:

        r_dist = self.r - other.r
        c_dist = self.c - other.c

        if abs(r_dist) == 1 or abs(c_dist) == 1:
            return True
        else:
            return False
        
class StrandFake(StrandBase):
    
    def positions(self) -> list[Pos]:

        stack = []
        stack.append(self.start)
        position_list = []

        for step in self.steps:
            pos = stack.pop().take_step(step)
            stack.append(pos)
            position_list.append(pos)
        
        return position_list
    
    def is_cyclic(self) -> bool:
        raise NotImplementedError
    
    def is_folded(self) -> bool:
        raise NotImplementedError

class BoardFake(BoardBase):

    # milestone one said to not check if letters is valid,
    # didn't see until after I added this, we could take 
    # the checking part out if its unecessary for now
    def __init__(self, letters: list[list[str]]):

        row_size = len(letters[0])

        # check row size
        for row in letters:
            if len(row) != row_size:
                raise ValueError
            # check letter formatting
            for letter in row:
                if len(letter) != 1:
                    raise ValueError
                if not letter.isalpha() or not letter.islower():
                    raise ValueError
        
        self.letters = letters

    # make properties?      
    def num_rows(self) -> int:
        return len(self.letters)
    
    def num_cols(self) -> int:
        return len(self.letters[0])
    
    def get_letter(self, pos: Pos) -> str:
        
        if pos.r > self.num_rows() or pos.c > self.num_cols():
            raise ValueError
        
        return self.letters[pos.r][pos.c]
    
    def evaluate_strand(self, strand: StrandFake) -> str:
        raise NotImplementedError

class StrandsGameFake(StrandsGameBase):
    ...
    

# TODO: Define these four classes
