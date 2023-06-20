from defs import Token, TokenType, Location

hard_macros = {
  "FLAGS_LESSEQ": "0",
  "FLAGS_EQUAL": "4",
}

class Lexer:
  cursor = 0; row = 0; col = 0
  stomach = []; tokens = []

  def __init__(self, file_path, text):
    self.file_path = file_path
    self.text = text
    for macro in hard_macros:
      self.text = self.text.replace(macro, hard_macros[macro])

  def eof(self):
    return self.cursor >= len(self.text)
  
  def incr(self, steps=1): # increment cursor while updating current row and col
    for _ in range(0, steps):
      if self.curchar() == "\n":
        self.col = 0
        self.row += 1
      else:
        self.col += 1
      self.cursor += 1

  def eat(self): # eat character and put in stomach
    character = self.text[self.cursor]
    self.stomach.append(character)
    self.incr()
    return character
  
  def digest(self): # digest current eaten characters
    token_string = "".join(self.stomach)
    self.stomach = []
    return token_string
  
  def curchar(self, offset=0):
    position = self.cursor + offset
    if position >= len(self.text):
      raise Exception("eof")
    return self.text[position]
  
  def append(self, token):
    self.tokens.append(token)

  def get_location(self):
    return Location(self.file_path, self.row, self.col)
  
  def lex(self):
    sym_tokens = { # map for cleaner code 
      ",": TokenType.COMMA, "[": TokenType.OBRACK, "]": TokenType.CBRACK, 
      ".": TokenType.DOT, ":": TokenType.COLON,
    }
    while not self.eof():
      # print(self.curchar())
      for sym in sym_tokens.keys():
        if self.curchar() == sym: # one character tokens (see sym_tokens)
          self.append(Token(sym_tokens[sym], sym, self.get_location()))
          self.incr()
          if self.eof():
            return
      if self.curchar().isspace():
        self.incr()
        continue
      if self.curchar().isalpha(): # names
        loc = self.get_location()
        self.eat()
        while not self.eof() and (self.curchar().isalnum() or self.curchar() == "_"):
          self.eat()
        digest = self.digest()
        self.append(Token(TokenType.NAME, digest, loc))
      if self.curchar() == "#": # comments
        while not self.eof() and self.curchar() != "\n":
          self.incr()
      if self.curchar() == "\"": # string literals
        loc = self.get_location()
        self.incr()
        while not self.eof() and self.curchar() != "\"":
          self.eat()
        digest = self.digest()
        self.append(Token(TokenType.STRLIT, digest, loc))
        self.incr()
      if self.curchar().isnumeric(): # number literals (5, 0b101, 0x5)
        loc = self.get_location()
        self.eat()
        while not self.eof() and (self.curchar().isnumeric() or self.curchar() in ["b", "x", "a", "c", "d", "e", "f"]):
          self.eat()
        digest = self.digest()
        self.append(Token(TokenType.NUMLIT, digest, loc))
      