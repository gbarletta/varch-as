opcodes = [
  "push",
  "mov_rp_r",
  "mov_rp_m",
  "mov_rp_c"
  "mov_r_r",
  "mov_r_m",
  "mov_r_c",
  "mov_r_rp",
  "sub_r_r",
  "sub_r_c",
  "add_r_r",
  "add_r_c",
  "cmp",
  "flg",
  "jnz",
  "jmp",
  "call",
  "pop",
  "ret",
]

registers = [
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
]

with open("hello.bin", "rb") as f:
  bin = bytearray(f.read())

offset = 0
while offset < len(bin):
  match bin[offset]:
    case 0:
      print(f"PUSH {bin[offset+1]}")