import Parser

#############
# constants #
#############
END_OF_LINE_MARK = "\n"
GO_TO_REGISTER_M = "A=M" + END_OF_LINE_MARK
GO_TO_PREVIOUS_REGISTER_M = "AM=M-1" + END_OF_LINE_MARK
GO_TO_REGISTER_D = "A=D" + END_OF_LINE_MARK
GETTING_REGISTER_VALUE = "D=M" + END_OF_LINE_MARK
GETTING_ADDRESS_VALUE = "D=A" + END_OF_LINE_MARK
REDUCE_MEMORY = "M=M-1" + END_OF_LINE_MARK
INCREMENT_MEMORY = "M=M+1" + END_OF_LINE_MARK
UPDATE_MEMORY_TO_D = "M=D" + END_OF_LINE_MARK
ADDING_D_TO_MEMORY = "M=D+M" + END_OF_LINE_MARK
SUBTRACTION_D_FROM_M_TO_M = "M=M-D" + END_OF_LINE_MARK
SUBTRACTION_M_FROM_D_TO_D = "D=D-M" + END_OF_LINE_MARK
NEGATION_MEMORY = "M=-M" + END_OF_LINE_MARK
NOT_MEMORY = "M=!M" + END_OF_LINE_MARK
OR_D_MEMORY = "M=M|D" + END_OF_LINE_MARK
AND_D_MEMORY = "M=M&D" + END_OF_LINE_MARK
ADD_A_TO_D = "D=D+A" + END_OF_LINE_MARK
FALSE_INTO_MEMORY = "M=0" + END_OF_LINE_MARK
TRUE_INTO_MEMORY = "M=-1" + END_OF_LINE_MARK
LABELS_TRANSLATOR = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
POINTER_ADDRESS_TRANSLATOR = {"0": "THIS", "1": "THAT"}
STACK = "SP"
STATIC_SEGMENT = "static"
POINTER_SEGMENT = "pointer"
TEMP_SEGMENT = "temp"
CONSTANT_SEGMENT = "constant"
A_PREFIX = "@"
TEMP_MEMORY = "5"
ADDR_STORE_REGISTER = "R13"
COMPARE_TEMP_REGISTER = "R14"
JUMP_ON_D = "D;"
REGULAR_MINUS_LABEL = "REGULAR_MINUS_L"
TRUE_LABEL = "TRUE_L"
FALSE_LABEL = "FALSE_L"
NEXT_COMMAND_LABEL = "CONTINUE_L"
JUMP_NOT_NEGATIVE = "JGE"
JUMP_NOT_POSITIVE = "JLE"
JUMP_EQUAL = "JEQ"
JUMP_ALWAYS_OPERATION = "0;JMP" + END_OF_LINE_MARK
JUMP_POSITIVE = "JGT"
JUMP_NEGATIVE = "JLT"
LABEL_PREFIX = "("
LABEL_SUFFIX = ")"
EMPTY_COMMAND = ""
COMMENT_SIGN = "//"
ADD_OPERATION = "add"
SUB_OPERATION = "sub"
NEGATION_OPERATION = "neg"
EQUAL_OPERATION = "eq"
GREATER_OPERATION = "gt"
LOWER_OPERATION = "lt"
AND_OPERATION = "and"
OR_OPERATION = "or"
NOT_OPERATION = "not"


class Translator:
    """
    A translator class translates an instruction in hack language to binary code. Consists on static methods that
    translate a line when given a Parser object that parsed the line
    """

    def __init__(self, parser):
        """
        initializes the Translator object the translates vm commands to asm commands
        :param parser: a parser that is set to a certain line of vm file
        """
        self.__parser = parser
        self.__label_counter = 0  # counts label for comparison operations

    def translate(self):
        """
        translates the command of the inner parser to asm code
        :return: the asm code matching the parser operation
        """
        line_type = self.__parser.get_type()
        # returns a comment of the full command for the understandability of the asm file
        line_comment = COMMENT_SIGN + self.__parser.get_command() + END_OF_LINE_MARK
        if line_type == Parser.ARITHMETIC_COMMAND_TYPE:
            return line_comment + self.__translate_arithmetic()
        elif line_type == Parser.PUSH_COMMAND_TYPE or line_type == Parser.POP_COMMAND_TYPE:
            return line_comment + self.__translate_push_pop()
        else:
            return EMPTY_COMMAND

    def __translate_arithmetic(self):
        """
        translate an arithmetic operation to asm
        :return: the asm command matching the arithmetic operation
        """
        operation = self.__parser.get_operation()
        if operation == ADD_OPERATION:
            trans = Translator.__translate_add()
        elif operation == SUB_OPERATION:
            trans = Translator.__translate_sub()
        elif operation == NEGATION_OPERATION:
            trans = Translator.__translate_neg()
        elif operation == EQUAL_OPERATION:
            trans = self.__translate_eq()
        elif operation == GREATER_OPERATION:
            trans = self.__translate_gt()
        elif operation == LOWER_OPERATION:
            trans = self.__translate_lt()
        elif operation == AND_OPERATION:
            trans = Translator.__translate_and()
        elif operation == OR_OPERATION:
            trans = Translator.__translate_or()
        else:  # not operation
            trans = Translator.__translate_not()
        return trans + Translator.__increment_stack()

    @staticmethod
    def __reduce_stack():
        """
        @SP
        M=M-1
        :return: the asm code of reducing the stack
        """
        return Translator.__get_A_instruction(STACK) + REDUCE_MEMORY

    @staticmethod
    def __increment_stack():
        """
        @SP
        M=M+1
        :return: the asm code of reducing the stack
        """
        return Translator.__get_A_instruction(STACK) + INCREMENT_MEMORY

    @staticmethod
    def __operate_on_top_stack_value(operation):
        """
        @SP
        A=M
        operation
        :param operation: the operation on the top stack value (M)
        :return: the asm code fot getting the stack register into A
        """
        return Translator.__get_A_instruction(STACK) + GO_TO_PREVIOUS_REGISTER_M + operation

    @staticmethod
    def __operate_on_stack(operation):
        """
        @SP
        A=M
        operation
        :param operation: the operation on the top stack value (M)
        :return: the asm code fot getting the stack register into A
        """
        return Translator.__get_A_instruction(STACK) + GO_TO_REGISTER_M + operation

    @staticmethod
    def __operate_on_two_top_stack_values(operation):
        """
        Inserts the top stack value into D and then the second top value into M and makes an operation on these
        2 values
        :param operation: the operation on the top stack value (D) and second (M)
        :return: the asm code for inserting the most top value in the stack into the A-register and the second
        top value into the memory M
        """
        return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + Translator.__get_A_instruction(STACK) + \
               GO_TO_PREVIOUS_REGISTER_M + operation

    @staticmethod
    def __jump_based_on_D(condition):
        """
        :param condition: the asm syntax for jump condition
        :return: the asm code for jumping based on the given condition and the value of D register
        """
        return JUMP_ON_D + condition + END_OF_LINE_MARK

    @staticmethod
    def __translate_add():
        """
        :return: The asm code for the adding operation
        """
        trans = Translator.__operate_on_two_top_stack_values(ADDING_D_TO_MEMORY)
        return trans

    @staticmethod
    def __translate_sub():
        """
        :return: The asm code for the subtraction operation
        """
        trans = Translator.__operate_on_two_top_stack_values(SUBTRACTION_D_FROM_M_TO_M)
        return trans

    @staticmethod
    def __translate_neg():
        """
        :return: The asm code for the negation operation
        """
        trans = Translator.__operate_on_top_stack_value(NEGATION_MEMORY)
        return trans

    def __compare(self, condition):
        """
        Computes the asm code for comparison between the 2 top values in the stack. The comparison condition is based
        on the given parameter
        :param: the comparison condition. The asm code of the jumping condition for true value. For example if the
        result should be true for the second_top_value > first_top_value the condition should be JGT
        :return: the comparison asm code
        """
        stack_value = Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE)
        temp_register_address = Translator.__get_A_instruction(COMPARE_TEMP_REGISTER)
        true_label_address = Translator.__get_A_instruction(TRUE_LABEL + str(self.__label_counter))
        false_label_address = Translator.__get_A_instruction(FALSE_LABEL + str(self.__label_counter))
        # gets the top stack value into a temp register
        first_value_into_temp = stack_value + temp_register_address + UPDATE_MEMORY_TO_D
        regular_minus_label_address = Translator.__get_A_instruction(REGULAR_MINUS_LABEL + str(self.__label_counter))
        jump_if_not_negative = Translator.__jump_based_on_D(JUMP_NOT_NEGATIVE)
        second_value = Translator.__reduce_stack() + GO_TO_REGISTER_M + GETTING_REGISTER_VALUE
        jump_if_not_positive = Translator.__jump_based_on_D(JUMP_NOT_POSITIVE)

        # set the result in case the top value is negative and the second is positive.
        # If the compare condition is greater than zero, then the result should be true now. For other conditions
        # the result should be false
        if condition == JUMP_POSITIVE:
            set_result = true_label_address + JUMP_ALWAYS_OPERATION
        else:
            set_result = false_label_address + JUMP_ALWAYS_OPERATION

        # regular_minus_content: no overflow risk on subtraction, so subtracting the 2 values and jump based on the
        # result to set the boolean value
        regular_minus_label_title = self.__create_label(REGULAR_MINUS_LABEL)
        regular_minus_content = stack_value + temp_register_address + SUBTRACTION_M_FROM_D_TO_D + true_label_address + \
                                Translator.__jump_based_on_D(condition)
        # the true and false labels - sets the stack value to the result of the comparison
        false_label_title = self.__create_label(FALSE_LABEL)
        false_label_content = Translator.__operate_on_stack(FALSE_INTO_MEMORY)
        jump_next = Translator.__get_A_instruction(NEXT_COMMAND_LABEL + str(self.__label_counter)) + JUMP_ALWAYS_OPERATION
        true_label_title = self.__create_label(TRUE_LABEL)
        true_label_content = Translator.__operate_on_stack(TRUE_INTO_MEMORY)
        next_command_label = self.__create_label(NEXT_COMMAND_LABEL)

        # combines all the comparison code
        trans = first_value_into_temp + regular_minus_label_address + jump_if_not_negative + second_value + \
                regular_minus_label_address + jump_if_not_positive + set_result + regular_minus_label_title + \
                regular_minus_content + false_label_title + false_label_content + jump_next + \
                true_label_title + true_label_content + next_command_label
        self.__label_counter += 1  # increment the label counter after this use
        return trans

    def __translate_eq(self):
        """
        :return: The asm code for the equal operation
        """
        return self.__compare(JUMP_EQUAL)

    def __translate_gt(self):
        """
        :return: The asm code for the grater than operation
        """
        return self.__compare(JUMP_POSITIVE)

    def __translate_lt(self):
        """
        :return: The asm code for the lower than operation
        """
        return self.__compare(JUMP_NEGATIVE)

    @staticmethod
    def __translate_and():
        """
        :return: The asm code for the and operation
        """
        trans = Translator.__operate_on_two_top_stack_values(AND_D_MEMORY)
        return trans

    @staticmethod
    def __translate_or():
        """
        :return: The asm code for the or operation
        """
        trans = Translator.__operate_on_two_top_stack_values(OR_D_MEMORY)
        return trans

    @staticmethod
    def __translate_not():
        """
        :return: The asm code for the not operation
        """
        trans = Translator.__operate_on_top_stack_value(NOT_MEMORY)
        return trans

    def __translate_push_pop(self):
        """
        :return: The asm code for the push/pop operation
        """
        segment = self.__parser.get_segment()
        address = self.__parser.get_address()
        command = self.__parser.get_type()

        if segment in LABELS_TRANSLATOR:  # local-like segments (local, argument, this, that)
            return Translator.__translate_local_push_pop(address, LABELS_TRANSLATOR[segment], command)
        elif segment == CONSTANT_SEGMENT:
            return Translator.__translate_constant_push_pop(address)
        elif segment == TEMP_SEGMENT:
            return Translator.__translate_temp_push_pop(address, command)
        elif segment == STATIC_SEGMENT:
            return self.__translate_static_push_pop(address, command)
        else:  # pointer segment
            return Translator.__translate_pointer_push_pop(address, command)

    @staticmethod
    def __translate_local_push_pop(address, segment_key, command):
        """
        translates local-like push and pop commands (local, argument, this, that) to asm code
        :param address: the address to access in the given segment
        :param segment_key: the segment asm representation
        :param command: the push/pop command
        :return: the asm code for the push/pop local operation
        """
        # push local
        if command == Parser.PUSH_COMMAND_TYPE:
            return Translator.__get_local_address(segment_key, address) + \
                   Translator.__put_address_content_in_stack() + Translator.__increment_stack()
        # pop local
        else:
            return Translator.__get_local_address(segment_key, address) + Translator.__reduce_stack() + \
                   Translator.__put_stack_content_in_address()

    @staticmethod
    def __translate_temp_push_pop(address, command):
        """
        translates temp push and pop commands to asm code
        :param address: the address to access in the temp segment
        :param command: the push/pop command
        :return: the asm code for the push/pop temp operation
        """
        # push static
        if command == Parser.PUSH_COMMAND_TYPE:
            return Translator.__get_temp_address(address) + Translator.__put_address_content_in_stack() + \
                   Translator.__increment_stack()
        # pop static
        else:
            return Translator.__get_temp_address(address) + Translator.__reduce_stack() + \
                   Translator.__put_stack_content_in_address()

    @staticmethod
    def __translate_constant_push_pop(address):
        """
        :param address: the address to access in the constant segment
        :return: the asm code for the push constant operation
        """
        return Translator.__put_address_in_stack(address) + Translator.__increment_stack()

    def __translate_static_push_pop(self, address, command):
        """
        translates static push and pop commands to asm code
        :param address: the address to access in the static segment
        :param command: the push/pop command
        :return: the asm code for the push/pop static operation
        """
        file_name = self.__parser.get_file_name()
        # push static
        if command == Parser.PUSH_COMMAND_TYPE:
            return Translator.__put_static_in_stack(file_name, address) + Translator.__increment_stack()
        # pop static
        else:
            return Translator.__reduce_stack() + Translator.__put_stack_content_in_static(file_name, address)

    @staticmethod
    def __translate_pointer_push_pop(address, command):
        """
        translates pointer push and pop commands to asm code
        :param address: the address to access in the pointer segment: 0 for this, 1 for that
        :param command: the push/pop command
        :return: the asm code for the push/pop pointer operation
        """
        # push pointer
        if command == Parser.PUSH_COMMAND_TYPE:
            return Translator.__get_A_instruction(POINTER_ADDRESS_TRANSLATOR[address]) + GETTING_REGISTER_VALUE + \
                   Translator.__operate_on_stack(UPDATE_MEMORY_TO_D) + Translator.__increment_stack()
        # pop pointer
        else:
            return Translator.__reduce_stack() + Translator.__operate_on_stack(UPDATE_MEMORY_TO_D) + \
                   Translator.__get_A_instruction(POINTER_ADDRESS_TRANSLATOR[address]) + UPDATE_MEMORY_TO_D

    @staticmethod
    def __get_local_address(segment, address):
        """
        D = segment + i
        :param segment: the given segment code (representing local, argument, this or that segments)
        :param address: the address to access in the given segment
        :return: the command for putting (segment base address + i) in D register
        """
        return Translator.__get_A_instruction(segment) + GETTING_REGISTER_VALUE + \
               Translator.__get_A_instruction(address) + ADD_A_TO_D

    @staticmethod
    def __get_temp_address(address):
        """
        D = 5 + i
        :param address: the address to access in the given segment
        :return: the command for putting (5 + i) in D register
        """
        return Translator.__get_A_instruction(TEMP_MEMORY) + GETTING_ADDRESS_VALUE + \
               Translator.__get_A_instruction(address) + ADD_A_TO_D

    @staticmethod
    def __put_address_content_in_stack():
        """
        *SP = *addr
        :return: the command for putting the content of the address in the stack
        """
        return GO_TO_REGISTER_D + GETTING_REGISTER_VALUE + Translator.__operate_on_stack(UPDATE_MEMORY_TO_D)

    @staticmethod
    def __put_stack_content_in_address():
        """
        *addr = *SP
        :return: the command for putting the content of the stack in the address
        """
        return Translator.__get_A_instruction(ADDR_STORE_REGISTER) + UPDATE_MEMORY_TO_D +\
               Translator.__operate_on_stack(GETTING_REGISTER_VALUE) + \
               Translator.__get_A_instruction(ADDR_STORE_REGISTER) + GO_TO_REGISTER_M + UPDATE_MEMORY_TO_D

    @staticmethod
    def __put_static_in_stack(file_name, address):
        """
        *SP = *filename.i
        :param file_name: the name of the vm file
        :param address: the address to access in the static segment
        :return: the command for putting the content of the static variable in the stack
        """
        return Translator.__get_A_instruction(file_name + "." + address) + GETTING_REGISTER_VALUE + \
               Translator.__operate_on_stack(UPDATE_MEMORY_TO_D)

    @staticmethod
    def __put_stack_content_in_static(file_name, address):
        """
        *filename.i=*SP
        :param file_name: the name of the vm file
        :param address: the address to access in the static segment
        :return: the command for putting the content of the stack in the static variable
        """
        return Translator.__operate_on_stack(GETTING_REGISTER_VALUE) + \
               Translator.__get_A_instruction(file_name + "." + address) + UPDATE_MEMORY_TO_D

    @staticmethod
    def __get_A_instruction(address_code):
        """
        @address_code
        :param address_code: the address to access
        :return: the A command for accessing the given address code
        """
        return A_PREFIX + address_code + END_OF_LINE_MARK

    @staticmethod
    def __put_address_in_stack(address):
        """
        *SP = address (for "push constant address" command)
        :param address: the address to put in the stack
        :return: the command for putting the given address in the stack
        """
        return Translator.__get_A_instruction(address) + GETTING_ADDRESS_VALUE + \
               Translator.__operate_on_stack(UPDATE_MEMORY_TO_D)

    def __create_label(self, label_name):
        """
        (label_name + INDEX)
        :param label_name: the label name
        :return: the label name format with the current label counter
        """
        return LABEL_PREFIX + label_name + str(self.__label_counter) + LABEL_SUFFIX + END_OF_LINE_MARK
