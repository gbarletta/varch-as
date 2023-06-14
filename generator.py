import struct
from defs import Token, Symbol, TokenType, AssemblerError, token_names

opcodes = {
  "push": 0,
  "mov_rp_r": 1,
  "mov_rp_m": 2,
  "mov_rp_c": 3,
  "mov_r_r": 4,
  "mov_r_m": 5,
  "mov_r_c": 6,
  "mov_r_rp": 7,
  "sub_r_r": 8,
  "sub_r_c": 9,
  "add_r_r": 10,
  "add_r_c": 11,
  "cmp": 12,
  "flg": 13,
  "jnz": 14,
  "jmp": 15,
  "call": 16,
  "pop": 17,
  "ret": 18,
}

registers = {
  "rv": 15,
  "sf": 14,
  "sp": 13,
  "fl": 12,
  "r15": 15,
  "r14": 14,
  "r13": 13,
  "r12": 12,
  "r11": 11,
  "r10": 10,
  "r9": 9,
  "r8": 8,
  "r7": 7,
  "r6": 6,
  "r5": 5,
  "r4": 4,
  "r3": 3,
  "r2": 2,
  "r1": 1,
  "r0": 0,
}

def short(value):
  print(value)
  return struct.pack('>H', value)

class Generator:
  cursor = 0; current_memory_location = 0 
  symbols = {}; unresolved_symbols = []

  def __init__(self, file_path, tokens):
    self.file_path = file_path
    self.tokens = tokens
    self.executable = bytearray()
  
  def incr(self, offset=1):
    self.cursor += offset

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
  
  def expect_register(self, incr=True):
    token = self.peek()
    if not token.is_register:
      raise AssemblerError(self, f"expected register")
    if incr:
      self.incr()
    return token
  
  def expect_reg_or_num(self, incr=True):
    token = self.peek()
    if not token.is_register and token.type != TokenType.NUMLIT:
      raise AssemblerError(self, f"expected register or number literal")
    if incr:
      self.incr()
    return token
  
  def expect_number(self, incr=True):
    token = self.peek()
    if token.type != TokenType.NUMLIT:
      raise AssemblerError(self, f"expected register or number literal")
    if incr:
      self.incr()
    return token
  
  def get_current_location(self, offset=0):
    position = self.cursor + offset
    if position >= len(self.tokens):
      raise AssemblerError(self, "eof")
    return self.tokens[position].location
  
  def append(self, value):
    if isinstance(value, int):
      self.executable.append(value)
    else:
      self.executable += value

  def get_symbol(self, name):
    if name in self.symbols:
      return short(self.symbols[name])
    else:
      self.unresolved_symbols.append({"name": name, "offset": self.current_memory_location})
      return short(0x00)

  def generate(self):
    while not self.eof():
      match self.peek(0).type:
        case TokenType.DOT:
          self.incr()
          label_name = self.expect_token(TokenType.NAME)
          self.expect_token(TokenType.COLON)
          self.symbols[label_name.text] = self.current_memory_location
          continue
        case TokenType.PUSH:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          register = registers[self.expect_register().text]
          self.append(opcode)
          self.append(register)
          self.current_memory_location += 2
          continue
        case TokenType.POP:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          register = registers[self.expect_register().text]
          self.append(opcode)
          self.append(register)
          self.current_memory_location += 2
          continue
        case TokenType.MOV:
          self.incr()
          self.current_memory_location += 1
          opcode = None
          left = None; right = None
          left_type = None; right_type = None
          if self.peek(0).type == TokenType.OBRACK:
            self.incr()
            left = registers[self.expect_register().text]
            self.expect_token(TokenType.CBRACK)
            left_type = "regref"
          else:
            left = registers[self.expect_register().text]
            left_type = "reg"
          self.current_memory_location += 1
          self.expect_token(TokenType.COMMA)
          if self.peek(0).type == TokenType.OBRACK:
            self.incr()
            right = registers[self.expect_register().text]
            self.expect_token(TokenType.CBRACK)
            right_type = "regref"
            self.current_memory_location += 1
          else:
            right_token = self.peek()
            self.incr()
            if right_token.is_register:
              right = registers[right_token.text]
              right_type = "reg"
              self.current_memory_location += 1
            elif right_token.type == TokenType.NAME:
              right = self.get_symbol(right_token.text)
              right_type = "mem"
              self.current_memory_location += 2
            elif right_token.type == TokenType.NUMLIT:
              right = short(int(right_token.text))
              right_type = "num"
              self.current_memory_location += 2
          if left_type == "regref" and right_type == "reg":
            opcode = opcodes["mov_rp_r"]
          elif left_type == "regref" and right_type == "mem":
            opcode = opcodes["mov_rp_m"]
          elif left_type == "regref" and right_type == "num":
            opcode = opcodes["mov_rp_c"]
          elif left_type == "reg" and right_type == "reg":
            opcode = opcodes["mov_r_r"]
          elif left_type == "reg" and right_type == "mem":
            opcode = opcodes["mov_r_m"]
          elif left_type == "reg" and right_type == "num":
            opcode = opcodes["mov_r_c"]
          elif left_type == "reg" and right_type == "regref":
            opcode = opcodes["mov_r_rp"]
          self.append(opcode)
          self.append(left)
          self.append(right)
          continue
        case TokenType.SUB:
          self.incr()
          ra = registers[self.expect_register().text]
          self.current_memory_location += 2
          self.expect_token(TokenType.COMMA)
          right = self.expect_reg_or_num()
          if right.is_register:
            self.append(opcodes["sub_r_r"])
            self.append(ra)
            rb = registers[right.text]
            self.append(rb)
            self.current_memory_location += 1
          else:
            self.append(opcodes["sub_r_c"])
            self.append(ra)
            self.append(short(int(right.text)))
            self.current_memory_location += 2
          continue
        case TokenType.ADD:
          self.incr()
          ra = registers[self.expect_register().text]
          self.current_memory_location += 2
          self.expect_token(TokenType.COMMA)
          right = self.expect_reg_or_num()
          if right.is_register:
            self.append(opcodes["add_r_r"])
            self.append(ra)
            rb = registers[right.text]
            self.append(rb)
            self.current_memory_location += 1
          else:
            self.append(opcodes["add_r_c"])
            self.append(ra)
            self.append(short(int(right.text)))
            self.current_memory_location += 2
          continue
        case TokenType.CMP:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          ra = registers[self.expect_register().text]
          self.expect_token(TokenType.COMMA)
          rb = registers[self.expect_register().text]
          self.append(opcode)
          self.append(ra)
          self.append(rb)
          self.current_memory_location += 3
          continue
        case TokenType.FLG:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          ra = registers[self.expect_register().text]
          self.expect_token(TokenType.COMMA)
          num = int(self.expect_number().text)
          self.append(opcode)
          self.append(ra)
          self.append(num)
          self.current_memory_location += 3
          continue
        case TokenType.JNZ:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          ra = registers[self.expect_register().text]
          self.current_memory_location += 2
          self.expect_token(TokenType.COMMA)
          right_token = self.peek()
          if right_token.type == TokenType.NAME:
            self.incr()
            right = self.get_symbol(right_token.text)
          else:
            right = short(int(self.expect_number().text))
          self.current_memory_location += 2
          self.append(opcode)
          self.append(ra)
          self.append(right)
          continue
        case TokenType.JMP:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          self.current_memory_location += 1
          right_token = self.peek()
          if right_token.type == TokenType.NAME:
            self.incr()
            right = self.get_symbol(right_token.text)
          else:
            right = short(int(self.expect_number().text))
          self.current_memory_location += 2
          self.append(opcode)
          self.append(right)
          continue
        case TokenType.CALL:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          register = registers[self.expect_register().text]
          self.append(opcode)
          self.append(register)
          self.current_memory_location += 2
          continue
        case TokenType.RET:
          opcode = opcodes[self.peek(0).text]
          self.incr()
          self.append(opcode)
          self.current_memory_location += 1
          continue
      print(self.peek())
        

  
