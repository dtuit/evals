from typing import List, Tuple
import string
import os
import random
import json
from dataclasses import dataclass
import numpy as np

COLORS = ["Red", "Green", "Yellow", "Blue", "Purple", "Orange", "Black", "White", "Brown", "Pink"]
ANIMALS = ["Dog", "Cat", "Bird", "Fish", "Rabbit", "Horse", "Cow", "Pig", "Sheep", "Chicken"]
COUNTRIES = ["USA", "Canada", "Mexico", "Brazil", "Argentina", "Chile", "Peru", "Colombia", "Venezuela", "Ecuador"]

QUESTION_TEMPLATE="Demo {i}: {question} -> {answer}"
ANSWER_TEMPLATE="Example to predict: {question}"

SEPARATOR = ""
QUESTION_TEMPLATE="{question} -> {answer}"
ANSWER_TEMPLATE="{question} -> "

def joiner(seq, sep=SEPARATOR, alt_sep=" "):
    if not isinstance(seq, list):
        seq = list(seq)
    if isinstance(seq[0], int) and sep == "":
        sep = alt_sep
    
    return sep.join([str(x) for x in seq])


@dataclass
class PuzzleExample():
    question: List[int|str]
    answer: List[int|str]
    
    background: str = None
    
    
@dataclass
class Puzzle():
    example_set: List[PuzzleExample]
    additional_instructions: str = ""
    
    def answer(self):
        answer = joiner(self.example_set[-1].answer)
        # answer = joiner.join([str(x) for x in self.example_set[-1].answer])
        return answer
    
    def to_string(self,  
                  question_template=QUESTION_TEMPLATE,
                  answer_template=ANSWER_TEMPLATE
                  ):
        sample = ""
        for i, puzzle in enumerate(self.example_set[:-1]):
            question = joiner(puzzle.question)
            answer = joiner(puzzle.answer)
            sample += question_template.format(i=i+1, question=question, answer=answer) + "\n"
        
        question = joiner(self.example_set[-1].question)
        sample += answer_template.format(question=question)
        return sample

   
def generate_puzzle_colored_ordering(examplars=3, min_val=1, max_val=20, **kwargs):
    """
    Puzzle Description:
        Given a list of numbers and a list of colors, animals, or countries,
        the slected items are mapped to numbers in ascending order
    
    Example:
        17,9,7,12 -> Orange,Blue,Brown,Black
        20,1,4,13 -> Orange,Brown,Blue,Black
        1,6,19,12 -> Brown,Blue,Orange,Black
        13,11,3,5 ->
    """
    example_set = []
    num_elements = random.randint(4, 6)
    mapping_set = random.choice([COLORS, ANIMALS, COUNTRIES])
    selected_colors = random.sample(mapping_set, num_elements)

    for _ in range(examplars+1):
        puzzle = random.sample(range(min_val, max_val + 1), num_elements)
        sorted_puzzle = sorted(puzzle)
        color_mapping = {sorted_puzzle[i]: color for i, color in enumerate(selected_colors)}
        colors = [color_mapping[number] for number in puzzle]
        example_set.append(PuzzleExample(puzzle, colors))
    return Puzzle(example_set)


def generate_puzzle_incrementing_pattern(examplars=3, **kwargs):
    """
    Puzzle Description:
        Given a sequence of letters, predict the next letter in the sequence
        Sequences are generated by incrementing the letter by a random number.
        Letters with an integer value greater than 26 wrap around
    
    Example:
        C,E,G,I,K -> M
        I,K,M,O,Q -> S
        I,K,M,O,Q ->
    
    """
    def incrementing_pattern(start='A', length=5, n=1, **kwargs):
        result = []
        for i in range(length):
            new_char = chr(((ord(start) - ord("A") + i * n) % 26) + ord("A"))
            result.append(new_char)
        return ''.join(result)
    
    example_set = []
    length = random.randint(6, 10)
    n = random.randint(1, 5)
    for _ in range(examplars+1):
        start = random.choice(string.ascii_uppercase)
        pattern = incrementing_pattern(start=start, length=length, n=n, **kwargs)
        question, answer = pattern[:-1], pattern[-1]
        example_set.append(PuzzleExample(question, answer))
    return Puzzle(example_set)

def generate_puzzle_sequence_completion(examplars=3):
    """
    Puzzle Description:
        Given a sequence of letters, predict the last N letters of the sequence
        Some letters are masked out with a '_' character
        masked out letters should be ignored
    
    Example:
        B,C,D,E,F,G,H,I,J,_,_,_,?,?,? -> N,O,P
        D,E,F,G,H,I,J,_,_,_,?,?,? -> N,O,P
        E,F,G,H,I,J,K,L,M,_,_,_,?,?,? ->
    
    """
    
    def sequence_completion(sequence, skips=3, predict=3, skip_char="_", predict_char="?"):
        if not isinstance(sequence, list):
            sequence = list(sequence)
        ans = sequence[-predict:]
        sequence[-(skips+predict): -predict] = [skip_char] * skips
        sequence[-predict:] = [predict_char] * predict
        return sequence, ans
    
    skips=3
    predict=3
    skip_char="*"
    predict_char="?"
    
    example_set = []
    for _ in range(examplars+1):
        length = random.randint(13, 16)
        start = random.randint(0, 6)
        sequence = string.ascii_uppercase[start:start+length] # TODO use other sequences
        pat, ans = sequence_completion(sequence, skips=skips, predict=predict, skip_char=skip_char, predict_char=predict_char)
        example_set.append(PuzzleExample(pat, ans))
    
    return Puzzle(example_set,
                  additional_instructions=(
                      "The question is a sequence of letters. "
                      f"The answer is the last {predict} letters of the sequence, "
                      f"The letters represented by a '{skip_char}' should be ignored."
                  )
    )

def generate_puzzle_repeating_symetry(examplars=3, **kwargs):
    """
    
    Example:
    
    
    
    """
    
    example_set = []
    
    repeats = random.randint(examplars-1, 4)
    for i in range(examplars+1):
        ans=[]
        n = random.randint(3, 5)
        chars = random.sample(string.ascii_uppercase, n)
        chars_reverse = chars[::-1]        
        for j in range(repeats):
            if j % 2 == 0:
                ans += chars
            else:
                ans += chars_reverse
        
        example_set.append(PuzzleExample(chars, ans))
    return Puzzle(example_set)
        

def generate_puzzle_string_dilation(examplars=3, **kwargs):
    """
    Puzzle Description:
        Given sequence of letters learn the rule for the sequence
        Each example uses the same rule
    
    Example:        
        *,*,*,*,P,*,*,*,*,* -> *,*,P,P,P,P,P,*,*,*
        x,x,x,V,x,x,x,x,x,x -> x,V,V,V,V,V,x,x,x,x
        x,x,x,x,x,O,x,x,x,x -> x,x,x,O,O,O,O,O,x,x
        x,x,R,x,x,x,x,x,x,x -> 
    
    """
    
    
    example_set = []
        
    morphological_element_length = random.randint(3, 5)
    seqlen = random.randint(8, 15)
    
    for _ in range(examplars+1):
        background_letter = random.choice("x+-*")
        target_letter = random.choice(string.ascii_uppercase)
        morphological_element = target_letter * morphological_element_length
        
        seq = [background_letter] * seqlen
        n = random.randint(0, seqlen-1)
        seq[n] = target_letter
        ans = string_dilation("".join(seq), morphological_element)
        example_set.append(PuzzleExample(seq, list(ans)))
    return Puzzle(example_set)

def generate_puzzle_string_dilation2(examplars=3, **kwargs):
    """
    Puzzle Description: 
    
    Example:
        -,-,-,Q,Q,-,Q,- -> -,-,R,Q,Q,R,Q,-
        -,W,W,-,W,W,-,- -> -,W,W,X,W,W,X,- # BUG Here the answer is wrong
        G,*,G,G,*,*,*,* -> G,H,G,G,H,*,*,*
        +,U,+,U,U,+,+,U -> 
    
    """
    example_set = []
    
    seqlen = random.randint(8, 15)
    for _ in range(examplars+1):
        background_letter = random.choice("x+-*")
        target_letter = random.choice(string.ascii_uppercase[:-1]) # exclude Z
        surround_letter = chr(ord(target_letter) + 1)
        surround_element = [surround_letter, target_letter, target_letter, surround_letter]
        
        seq = [background_letter] * seqlen
        
        n_singles = random.randint(0, 3)
        for _ in range(n_singles):
            n = random.randint(0, seqlen-1)
            seq[n] = target_letter
        
        surround_idx = random.randint(0, seqlen-1-len(surround_element))
        seq[surround_idx:surround_idx+len(surround_element)] = surround_element
        
        ans = seq[::]
        qry = [background_letter if x == surround_letter else x for x in seq]
        
        example_set.append(PuzzleExample(qry, ans))
    return Puzzle(example_set)


def valid_placements(seq: List, 
                     element: List, 
                     background_letter: str):
    """
    Find all valid placements of element in seq
    A valid placement is one where the element can be placed 
    without overlapping any non-background letters 
    """
    placements = []
    i = 0
    while i < len(seq)-len(element) + 1:
        for j in range(len(element)):
            if seq[i+j] != background_letter:
                i += j+1
                break
        else:
            placements.append(i)
        i += 1
    return placements

def randomly_place_element(seq: List,
                           element: List, 
                           background_letter: str,
                           check_valid=True):
    """
    Place element in seq at a random valid location
    """
    seq = seq[:]
    if check_valid:
        placements = valid_placements(seq, element, background_letter)
    else:
        placements = range(len(seq)-len(element))
    
    if len(placements) == 0:
        return seq, False
    else:
        idx = random.choice(placements)
        seq[idx:idx+len(element)] = element
        return seq, True
    

def replace(seq, toreplace, replacement):
    """
    Replace all instances of toreplace with replacement
    """
    return [x if x != toreplace else replacement for x in seq]

def subtract(seq1, seq2, background_letter='-'):
    """
    Subtract seq2 from seq1
    """
    assert len(seq1) == len(seq2)
    return [x if x != y else background_letter for x, y in zip(seq1, seq2)]

def add(seq1, seq2, background_letter='-'):
    """
    Add seq2 to seq1
    """
    assert len(seq1) == len(seq2)
    return [x if x != background_letter else y for x, y in zip(seq1, seq2)]

def generate_puzzle_string_dilation3(examplars=3, **kwargs):
    """
    Example:
        xxNxRRDRxxxNxx -> RRxRxxxxxRRxRx
        +++LWLL+I+++++ -> +++++++L+LL+++
        xxOxxxxxxxPAPP -> xPxPPxxxxxxxxx
        --C--BHBB----- -> 
    """    
    example_set = []
    
    kernel_size = random.randint(2,3) + 1
    seqlen = random.randint(3*kernel_size-1, 15)
    for _ in range(examplars+1):
        background_letter = random.choice("x+-*")     
        knl_letter, qry_letter, tgt_letter = random.sample(string.ascii_uppercase, 3)
            
        kernel_q = [qry_letter] + [knl_letter] * (kernel_size - 1)
        random.shuffle(kernel_q)
                
        bak = [background_letter] * seqlen
        qry, _ = randomly_place_element(bak, kernel_q, background_letter)               
        
        ans = qry[:]
        for _ in range(random.randint(1,2)):
            ans, success = randomly_place_element(ans, kernel_q, background_letter)
        ans = subtract(ans, qry, background_letter)
        
        tgt_letter_seq = [tgt_letter if x == qry_letter else background_letter for x in ans]
        qry = add(qry, tgt_letter_seq, background_letter)
        
        ans = replace(ans, qry_letter, background_letter)
                
        example_set.append(PuzzleExample(qry, ans))
    return Puzzle(example_set)


def string_dilation(input_string, morphological_element, match_threshold=1):
    result = list(input_string)
    for i in range(0, len(input_string)-len(morphological_element)+1):
        match = 0
        for j in range(len(morphological_element)):
            if i+j >= len(input_string):
                break
            if morphological_element[j] == input_string[i+j]:
                match += 1
        if match >= match_threshold:
            result[i:i+len(morphological_element)] = morphological_element
            
    return "".join(result)


def generate_puzzle_fill_between(examplars=3, **kwargs):
    """
    Puzzle Description:
        If a letter occurs twice, fill between the two letters with the same letter
        if any other letter occurs between the two letters, do not change it.    
    
    Example:
        *,S,*,*,S,L,*,* -> *,S,S,S,S,L,*,*,*
        +,+,+,W,+,+,M,W -> +,+,+,W,W,W,M,W,+
        *,O,*,*,O,A,*,* -> *,O,O,O,O,A,*,*,*
        *,U,A,*,U,*,*,* ->
    
    """
    
    example_set = []
    
    seqlen = random.randint(8, 15)
    for _ in range(examplars+1):
        background_letter = random.choice("x+-*")
        target_letter = random.choice(string.ascii_uppercase)
        other_letter = random.choice(list(set(string.ascii_uppercase) - {target_letter}))

        target_len = random.randint(3, 6)
        target_start = random.randint(0, seqlen-target_len-1)
        target_indices = sorted([target_start, target_start+target_len])
        other_index = random.sample(set(range(seqlen-1)) - set(target_indices), 1)[0]
        
        background = [background_letter] * seqlen
                
        qry = background[::]
        qry[target_indices[0]] = target_letter
        qry[target_indices[1]] = target_letter
        qry[other_index] = other_letter

        ans = background[::]
        ans[target_indices[0]:target_indices[1]] = [target_letter] * (target_len +1)
        ans[other_index] = other_letter

        example_set.append(PuzzleExample(qry, ans))
    
    return Puzzle(example_set)
    

    

def generate_puzzle_set(generator, num_puzzles=5):
    puzzle_set = []
    for _ in range(num_puzzles):
        puzzle_set.append(generator())
    return puzzle_set


REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "../evals/registry")

YAML = """
sp_{task_name}:
  id: sp_{task_name}.dev.v0
  metrics: [accuracy]
sp_{task_name}.dev.v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: string_patterns/{task_name}/samples.v0.jsonl
""".strip()

TASK_MAPPING = {
    "colored_ordering": generate_puzzle_colored_ordering,
    "incrementing_pattern": generate_puzzle_incrementing_pattern,
    "sequence_completion": generate_puzzle_sequence_completion,
    "repeating_symetry": generate_puzzle_repeating_symetry,
    "string_dilation": generate_puzzle_string_dilation,
    "string_dilation2": generate_puzzle_string_dilation2,
    "string_dilation3": generate_puzzle_string_dilation3,
    "fill_between": generate_puzzle_fill_between,
}

INSTRUCTION = (
    "You are a pattern recognition bot, "
    "figure out the pattern and reply with just the solution, "
    "ensure that your reply starts with your solution."
)


if __name__ == "__main__":
    
    # generate_puzzle_string_dilation3()
    # exit()
    
    yaml_str = f"# This file is generated by {os.path.basename(__file__)}\n\n"
    for task_name, generator in TASK_MAPPING.items():
        task_path = f"string_patterns/{task_name}"
        output_path = f"evals/registry/data/{task_path}/samples.v0.jsonl"
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        puzzle_set = generate_puzzle_set(generator, 10)
        with open(output_path, "w") as f:
            for puzzle in puzzle_set:
                puzzle_text = INSTRUCTION + "\n"
                if puzzle.additional_instructions:
                    puzzle_text += puzzle.additional_instructions + "\n"
                puzzle_text += puzzle.to_string()
                
                print(puzzle_text + "\n\n")
                
                d = {
                    "input": [
                        {"role": "system", "content": "You are a pattern recognition bot, you only reply with the answer."},
                        {"role": "user", "content": puzzle_text},
                        ],
                    "ideal": puzzle.answer(),
                }
                f.write(json.dumps(d) + "\n")
        print(f"{len(puzzle_set)} lines written to {output_path}.")
        yaml_str += YAML.format(task_name=task_name, prompt_name=task_name, subject="sp") + "\n\n"
    
    yaml_file = f"{REGISTRY_PATH}/evals/string_patterns.yaml"
    with open(yaml_file, "w") as f:
        f.write(yaml_str)
    print(f"wrote {yaml_file}")