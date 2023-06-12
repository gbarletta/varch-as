from enum import IntEnum
  
def gen_token_list():
  tokens = [
    "NAME", "DOT", "COLON",
    "COMMA", "OBRACK", "CBRACK",
    "STRLIT", "NUMLIT", "MOV",
    "PUSH", "POP", "RET",
    "ADD", "SUB", "CMP",
    "FLG", "JNZ", "JMP",
    "CALL", "SF", "SP",
    "RV",
  ]
  for i in range(16):
    tokens.append(f"R{i}")
  return tokens

def gen_token_names():
  names = [
    "Name", "Dot", "Colon",
    "Comma", "Open Bracket", "Close Bracket",
    "String Literal", "Number Literal", "Move",
    "Push", "Pop", "Ret",
    "Add", "Sub", "Compare",
    "Flag", "Jump Not Zero", "Jump",
    "Call", "Stack Frame", "Stack Pointer",
    "Return Value",
  ]
  for i in range(16):
    names.append(f"Register {i}")
  return names
  
TokenType = IntEnum("TokenType", gen_token_list(), start=0)
token_names = gen_token_names()

reserved_names = [
  ("mov", TokenType.MOV),
  ("push", TokenType.PUSH),
  ("pop", TokenType.POP),
  ("ret", TokenType.RET),
  ("add", TokenType.ADD),
  ("sub", TokenType.SUB),
  ("cmp", TokenType.CMP),
  ("flg", TokenType.FLG),
  ("jnz", TokenType.JNZ),
  ("jmp", TokenType.JMP),
  ("call", TokenType.CALL),
  ("sf", TokenType.SF),
  ("sp", TokenType.SP),
  ("rv", TokenType.RV),
  ("r0", TokenType.R0),
  ("r1", TokenType.R1),
  ("r2", TokenType.R2),
  ("r3", TokenType.R3),
  ("r4", TokenType.R4),
  ("r5", TokenType.R5),
  ("r6", TokenType.R6),
  ("r7", TokenType.R7),
  ("r8", TokenType.R8),
  ("r9", TokenType.R9),
  ("r10", TokenType.R10),
  ("r11", TokenType.R11),
  ("r12", TokenType.R12),
  ("r13", TokenType.R13),
  ("r14", TokenType.R14),
  ("r15", TokenType.R15),
]

def get_token_by_text(text):
  for res in reserved_names:
    if res[0] == text:
      return res[1]
  return None

class Location:
  def __init__(self, file_path, row, col):
    self.file_path = file_path
    self.row = row + 1
    self.col = col + 1

  def __str__(self):
    return f"{self.file_path}:{self.row}:{self.col}"

class Token:
  is_register = False
  is_instruction = False

  def __init__(self, token_type, text, location):
    if token_type == TokenType.NAME:
      self.type = TokenType.NAME
      reserved = get_token_by_text(text)
      if reserved != None:
        self.type = reserved
        if TokenType.SF <= self.type <= TokenType.R15:
          self.is_register = True
        else:
          self.is_instruction = True
    else:
      self.type = token_type
    self.text = text
    self.location = location
  
  def __str__(self):
    return f"{self.location}: {token_names[self.type]} \"{self.text}\""

class AssemblerError(Exception):
  def __init__(self, gen, message, offset=0):
    self.location = gen.get_current_location(offset=offset)
    self.message = message
    super().__init__(self.message)

  def __str__(self):
    return f"{self.message} at {self.location}"