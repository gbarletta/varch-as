import lexer

class Assembler:
  current_line = 0

  def __init__(self, file_path):
    self.file_path = file_path
    try:
      with open(file_path, "r") as f:
        self.text = f.read()
    except:
      print(f"error: couldn't read file {file_path}")
  
  def assemble(self):
    lex = lexer.Lexer(self.file_path, self.text)
    lex.lex()
    for token in lex.tokens:
      print(token)