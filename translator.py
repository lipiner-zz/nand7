#############
# constants #
#############
A_INSTRUCTION_CODE = 'A'
C_INSTRUCTION_CODE = 'C'
EMPTY_TRANSLATION = ""
BINARY_TRANSLATION_CODE = "{0:b}"
ADDRESS_LENGTH = 15
BINARY_ZERO = "0"
BINARY_ONE = "1"
A_OPCODE = "0"
C_OPCODE = "1"
M_REGISTER = "M"
A_REGISTER = "A"
D_REGISTER = "D"
SHIFT_LEFT = "<<"
SHIFT_RIGHT = ">>"

# instructions translator directories
JUMP_TRANSLATOR = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
                   "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
COMP_TRANSLATOR = {"0": "101010", "1": "111111", "-1": "111010", "D": "001100", "A": "110000", "!D": "001101",
                   "!A": "110001", "-D": "001111", "-A": "110011", "D+1": "011111", "A+1": "110111", "D-1": "001110",
                   "A-1": "110010", "D+A": "000010", "D-A": "010011", "A-D": "000111", "D&A": "000000",
                   "D|A": "010101", "D<<": "110000", "D>>": "010000", "A<<": "100000", "A>>": "000000"}

LABELS_TRANSLATOR = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}


class Translator:
    """
    A translator class translates an instruction in hack language to binary code. Consists on static methods that
    translate a line when given a Parser object that parsed the line
    """

    @staticmethod
    def translate(parser, symbol_table):
        """
        When given a second_parser object of a line and a SymbolTable of the code file, translates the line to
        binary code
        :param parser: a second_parser object that was set to an instruction line from the asm file
        :param symbol_table: a SymbolTable object that represents the symbols of the current asm file
        :return: a string of 16 characters containing the assembled binary code of the line
        """
        instruction_type = parser.get_type()  # gets the type of the instruction
        if instruction_type == A_INSTRUCTION_CODE:
            return Translator.__translate_A(parser, symbol_table)
        elif instruction_type == C_INSTRUCTION_CODE:
            return Translator.__translate_C(parser)
        else:  # not A or C instruction, doesn't need to be translated
            return EMPTY_TRANSLATION

    @staticmethod
    def __translate_A(parser, symbol_table):
        """
        translates an A command to binary code
        :param parser: a second_parser object that was set to the A instruction
        :param symbol_table: a SymbolTable object that represents the symbols of the current asm file
        :return: a string of 16 characters containing the assembled binary code of the A command
        """
        address = parser.get_address()
        # checks if the address is a variable/label and replaces it with its address from the SymbolTable
        if not address.isdigit():
            address = symbol_table.find(address)
        # if the address contains only numbers- converting it to int
        else:
            address = int(address)

        # finding the binary representation of the address
        binary_repr = BINARY_TRANSLATION_CODE.format(address)
        # making sure the binary representation is 15 bits long by adding 0s to the start
        binary_repr = (ADDRESS_LENGTH - len(binary_repr))*BINARY_ZERO + binary_repr

        return A_OPCODE + binary_repr

    @staticmethod
    def __translate_C(parser):
        """
        translates a C command to binary code
        :param parser: a second_parser object that was set to the C instruction
        :return: a string of 16 characters containing the assembled binary code of the C command
        """
        # getting the instruction parts
        jump = parser.get_jump()
        dest = parser.get_dest()
        comp = parser.get_comp()

        # converting the instructions to binary codes
        jump_binary = Translator.__translate_jump(jump)
        comp_binary = Translator.__translate_comp(comp)
        dest_binary = Translator.__translate_dest(dest)
        shift_bit = Translator.__translate_shift(comp)

        return C_OPCODE + shift_bit + BINARY_ONE + comp_binary + dest_binary + jump_binary

    @staticmethod
    def __translate_jump(jump):
        """
        converts a jump instruction to the matching binary representation
        :param jump: a jump instruction
        :return: the binary code of the instruction
        """
        # returning the matching value from the translator dictionary
        return JUMP_TRANSLATOR[jump]

    @staticmethod
    def __translate_comp(comp):
        """
        converts a comp instruction to the matching binary representation
        :param comp: a jump instruction
        :return: the binary code of the instruction
        """
        # initializing the a bit to 0
        a = BINARY_ZERO
        # for M comp instructions: setting a to 1 and replacing M with A for figuring the comp instruction
        if M_REGISTER in comp:
            a = BINARY_ONE
            comp = comp.replace(M_REGISTER, A_REGISTER)

        # searching for the matching value from the translator dictionary
        comp_binary = COMP_TRANSLATOR[comp]

        return a + comp_binary

    @staticmethod
    def __translate_dest(dest):
        """
        converts a dest instruction to the matching binary representation
        :param dest: a jump instruction
        :return: the binary code of the instruction
        """
        # initializing d1, d2 and d3 to 0
        d1 = d2 = d3 = BINARY_ZERO
        # searching for A, D and M in the dest command, and updating the relevant bits to 1
        if A_REGISTER in dest:
            d1 = BINARY_ONE
        if D_REGISTER in dest:
            d2 = BINARY_ONE
        if M_REGISTER in dest:
            d3 = BINARY_ONE

        return d1 + d2 + d3

    @staticmethod
    def __translate_shift(comp):
        """
        determining the shift bit of the C instruction (the 14 bit)
        :param comp: the comp instruction
        :return: the shift bit
        """
        # if the comp command is s shift command- the 14 bit is 0
        if SHIFT_LEFT in comp or SHIFT_RIGHT in comp:
            return BINARY_ZERO

        return BINARY_ONE

    @staticmethod
    def __translate_add():
        """
        :return: The asm code for the adding operation
        """
        trans = "@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=D+M"
        return trans

    @staticmethod
    def __translate_sub():
        """
        :return: The asm code for the subtraction operation
        """
        trans = "@SP\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=M-D"
        return trans

    @staticmethod
    def __translate_neg():
        """
        :return: The asm code for the negation operation
        """
        trans = "@SP\nA=M\nM=-M"
        return trans

    @staticmethod
    def __translate_eq():
        pass

    @staticmethod
    def __translate_gt():
        pass

    @staticmethod
    def __translate_lt():
        pass

    @staticmethod
    def __translate_and():
        pass

    @staticmethod
    def __translate_or():
        pass

    @staticmethod
    def __translate_not():
        pass

    @staticmethod
    def __translate_push():
        pass

    @staticmethod
    def __translate_pop():
        pass
