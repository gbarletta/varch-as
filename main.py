import os
import sys
import assembler

cwd = os.getcwd()
file_path = sys.argv[1]

asm = assembler.Assembler(cwd + '/' + file_path)
asm.assemble()
