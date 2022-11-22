from command import Command

class CodeWriter:
  def __init__(self, output_file=None, stream=None):
    if not (output_file or stream):
      raise ValueError("Output file or a write stream must be provided.")
    
    if output_file:
      self.stream = open(output_file, "w")
    else:
      if stream.mode != "w":
        raise ValueError(f"File opened not opened in 'w' mode instead is open in {stream.mode}")
      
      self.stream = stream
  
    self.arithmetic_fns = {
      "add": self.__write_add,
      "sub": self.__write_sub,
      "neg": self.__write_neg,
      "eq": self.__write_eq,
      "gt": self.__write_gt,
      "lt": self.__write_lt,
      "and": self.__write_and,
      "or": self.__write_or,
      "not": self.__write_not
    }
    
    self.instruction_written_count = 0
    
    self.segment_addresses = {
      "temp": "5",
      "local": "LCL",
      "argument": "ARG",
      "this": "THIS",
      "that": "THAT"
    }
  
  def __write_instructions(self, instructions):
    for instruction in instructions:
      self.stream.write(f"{instruction}\n")
    self.instruction_written_count += len(instructions)
  
  def __write_and(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "M=D&M"
    ]
    self.__write_instructions(instructions)
  
  def __write_or(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "M=D|M"
    ]
    self.__write_instructions(instructions)
  
  def __write_not(self):
    instructions = [
      "@SP",
      "A=M-1",
      "M=!M"
    ]
    self.__write_instructions(instructions)
  
  def __write_add(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "M=M+D"
    ]
    self.__write_instructions(instructions)
    
  def __write_sub(self):
    instructions = [
      "@SP",
      "M=M-1",
      "A=M-1",
      "D=M",
      "A=A+1",
      "D=D-M",
      "A=A-1",
      "M=D"
    ]
    self.__write_instructions(instructions)
    
  def __write_neg(self):
    instructions = [
      "@SP",
      "A=M-1",
      "M=-M"
    ]
    self.__write_instructions(instructions)
  
  def __write_eq(self):
    jump_pos = self.instruction_written_count + 23
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "D=M-D",
      f"@EQUAL{jump_pos}",
      "D;JEQ",
      f"@NOTEQUAL{jump_pos}",
      "0;JMP",
      f"(EQUAL{jump_pos})",
      " @SP",
      " A=M-1",
      " M=-1",
      f" @EQEND{jump_pos}",
      " 0;JMP",
      f"(NOTEQUAL{jump_pos})",
      " @SP",
      " A=M-1",
      " M=0",
      f" @EQEND{jump_pos}",
      " 0;JMP",
      f"(EQEND{jump_pos})",
      " 0",
    ]
    self.__write_instructions(instructions)
  
  def __write_gt(self):
    jump_pos = self.instruction_written_count + 23
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "D=D-M",
      f"@GREATERTHAN{jump_pos}",
      "D;JLT",
      f"@NOTGREATERTHAN{jump_pos}",
      "0;JMP",
      f"(GREATERTHAN{jump_pos})",
      " @SP",
      " A=M-1",
      " M=-1",
      f" @EQEND{jump_pos}",
      " 0;JMP",
      f"(NOTGREATERTHAN{jump_pos})",
      " @SP",
      " A=M-1",
      " M=0",
      f" @EQEND{jump_pos}",
      " 0;JMP",
      f"(EQEND{jump_pos})",
      " 0"
    ]
    self.__write_instructions(instructions)
  
  def __write_lt(self):
    jump_pos = self.instruction_written_count + 23
    instructions = [
      "@SP",
      "M=M-1",
      "A=M",
      "D=M",
      "A=A-1",
      "D=D-M",
      f"@LESSTHAN{jump_pos}",
      "D;JGT",
      f"@NOTLESSTHAN{jump_pos}",
      "0;JMP",
      f"(LESSTHAN{jump_pos})",
      " @SP",
      " A=M-1",
      " M=-1",
      f" @LTEND{jump_pos}",
      " 0;JMP",
      f"(NOTLESSTHAN{jump_pos})",
      " @SP",
      " A=M-1",
      " M=0",
      f" @LTEND{jump_pos}",
      " 0;JMP",
      f"(LTEND{jump_pos})",
      "0"
    ]
    self.__write_instructions(instructions)
    
  def writeArithmetic(self, command: str):
    self.arithmetic_fns[command]()
  
  def writePushPop(self, command: Command, segment: str, index: int):
    if command == Command.C_PUSH:
      self.__push_cmd(segment, index)
    elif command == Command.C_POP:
      self.__pop_cmd(segment, index)
  
  def __push_cmd(self, segment: str, index: int):
    if segment in self.segment_addresses:
      addr = self.segment_addresses[segment]
      instructions = [
        f"@{index}",
        "D=A",
        f"@{addr}",
        "A=D+M",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
      ]
    elif segment == "constant":
      instructions = [
        f"@{index}",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
      ]
    self.__write_instructions(instructions)
  
  def __pop_cmd(self, segment: str, index: int):
    if segment in self.segment_addresses:
      addr = self.segment_addresses[segment]
      instructions = [
        f"@{index}",
        "D=A",
        f"@{addr}",
        "A=D+M",
        "D=A",
        "@addr",
        "M=D",
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@addr",
        "A=M",
        "M=D"
      ]
    self.__write_instructions(instructions)    
  
  def close(self):
    instructions = [
      "@END",
      "0;JMP",
      "(END)",
      " @END",
      " 0;JMP"
    ]
    self.__write_instructions(instructions)
    self.stream.close()
