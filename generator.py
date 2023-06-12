from defs import Token, TokenType, AssemblerError, token_names

class Generator:
  cursor = 0
  current_memory_location = 0

  def eof(self):
    return self.cursor >= len(self.tokens)

  def peek(self, offset=0):
    position = self.cursor + offset
    if position >= len(self.tokens):
      raise AssemblerError(self, "eof")
    return self.tokens[position]
  
  def expect_token(self, token_type, incr=True):
    token = self.peek()
    if token.type != token_type:
      raise AssemblerError(self, f"expected \"{token_names[token_type]}\"")
    if incr:
      self.incr()
    return token
  
  def get_current_location(self, offset=0):
    position = self.cursor + offset
    if position >= len(self.tokens):
      raise AssemblerError(self, "eof")
    return self.tokens[position].location

  def __init__(self, file_path, tokens):
    self.file_path = file_path
    self.tokens = tokens

  def generate(self):
    while not self.eof():
      if self.peek(0).type == TokenType.DOT:
        pass
  
