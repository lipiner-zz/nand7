###########
# imports #
###########
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
REDUCE_D = "D=D-1" + END_OF_LINE_MARK
UPDATE_MEMORY_TO_D = "M=D" + END_OF_LINE_MARK
UPDATE_MEMORY_TO_INCREMENTED_D = "M=D+1" + END_OF_LINE_MARK
ADDING_D_TO_MEMORY = "M=D+M" + END_OF_LINE_MARK
SUBTRACTION_D_FROM_M_TO_M = "M=M-D" + END_OF_LINE_MARK
SUBTRACTION_M_FROM_D_TO_D = "D=D-M" + END_OF_LINE_MARK
SUBTRACTION_D_FROM_M_TO_D = "D=M-D" + END_OF_LINE_MARK
SUBTRACTION_D_FROM_M_TO_A = "A=M-D" + END_OF_LINE_MARK
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
JUMP_NOT_EQUAL = "JNE"
LABEL_PREFIX = "("
LABEL_SUFFIX = ")"
EMPTY_COMMAND = ""
LABEL_FILENAME_SEPARATOR = "."
LABEL_SEP = "$"
LABEL_ALTER_SEP = "."  # alternative label separator for the vm translator usage
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
RETURN_LABEL = "ret."
LOCAL_KEYWORD = "LCL"
ARGUMENT_KEYWORD = "ARG"
THIS_KEYWORD = "THIS"
THAT_KEYWORD = "THAT"
DIST_TO_RET_ADDRESS = 5
LOOP_LABEL = "LOOP"
END_LOOP_LABEL = "ENDLOOP"
STACK_INITIAL_ADDRESS = 256
SYS_INIT_VM_COMMAND = "call Sys.init 0"
BOOTING_FILE_NAME = "Sys"


class Translator:
    """
    A translator class that translates an instruction in vm language to machine code. Has an internal Parser object
    that is set to a certain line and translates the current parsed line
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
        trans = line_comment
        if line_type == Parser.ARITHMETIC_COMMAND_TYPE:
            trans += self.__translate_arithmetic()
        elif line_type == Parser.PUSH_COMMAND_TYPE or line_type == Parser.POP_COMMAND_TYPE:
            trans += self.__translate_push_pop()
        elif line_type == Parser.LABEL_COMMAND_TYPE:
            trans += self.__create_label(self.__parser.get_segment_label(), LABEL_SEP)
        elif line_type == Parser.IF_GOTO_COMMAND_TYPE or line_type == Parser.GOTO_COMMAND_TYPE:
            trans += self.__translate_jumps()
        elif line_type == Parser.CALL_COMMAND_TYPE:
            trans += self.__translate_call()
        elif line_type == Parser.FUNCTION_COMMAND_TYPE:
            trans += self.__translate_function_declaration()
        elif line_type == Parser.RETURN_COMMAND_TYPE:
            trans += self.__translate_return()
        else:
            return EMPTY_COMMAND
        return trans

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

    def __translate_jumps(self):
        """
        translate a jump (goto or if-goto) command to asm
        :return: the asm command matching the branching operation
        """
        jump_label = self.__create_full_label_name(self.__parser.get_address(), LABEL_SEP)
        if self.__parser.get_type() == Parser.GOTO_COMMAND_TYPE:
            return Translator.__translate_goto(jump_label)
        else:  # if-goto command
            return Translator.__translate_if_goto(jump_label)

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
        M=M+1)
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
        return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + \
               Translator.__get_A_instruction(STACK) + GO_TO_PREVIOUS_REGISTER_M + operation

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
        true_label_address = Translator.__get_A_instruction(self.__create_full_label_name(TRUE_LABEL +
                                                                                          str(self.__label_counter),
                                                                                          LABEL_ALTER_SEP))
        false_label_address = Translator.__get_A_instruction(self.__create_full_label_name(FALSE_LABEL +
                                                                                           str(self.__label_counter),
                                                                                           LABEL_ALTER_SEP))
        # gets the top stack value into a temp register
        first_value_into_temp = stack_value + temp_register_address + UPDATE_MEMORY_TO_D
        regular_minus_label_address = Translator.__get_A_instruction(self.__create_full_label_name(REGULAR_MINUS_LABEL +
                                                                                                   str(self.__label_counter),
                                                                                                   LABEL_ALTER_SEP))
        jump_if_not_negative = Translator.__jump_based_on_D(JUMP_NOT_NEGATIVE)
        second_value = Translator.__get_A_instruction(STACK) + GO_TO_PREVIOUS_REGISTER_M + GETTING_REGISTER_VALUE
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
        regular_minus_label_title = self.__create_label(REGULAR_MINUS_LABEL + str(self.__label_counter), LABEL_ALTER_SEP)
        regular_minus_content = stack_value + temp_register_address + SUBTRACTION_M_FROM_D_TO_D + true_label_address + \
                                Translator.__jump_based_on_D(condition)
        # the true and false labels - sets the stack value to the result of the comparison
        false_label_title = self.__create_label(FALSE_LABEL + str(self.__label_counter), LABEL_ALTER_SEP)
        false_label_content = Translator.__operate_on_stack(FALSE_INTO_MEMORY)
        jump_next = Translator.__get_A_instruction(self.__create_full_label_name(NEXT_COMMAND_LABEL +
                                                                                 str(self.__label_counter),
                                                                                 LABEL_ALTER_SEP)) + \
                    JUMP_ALWAYS_OPERATION
        true_label_title = self.__create_label(TRUE_LABEL + str(self.__label_counter), LABEL_ALTER_SEP)
        true_label_content = Translator.__operate_on_stack(TRUE_INTO_MEMORY)
        next_command_label = self.__create_label(NEXT_COMMAND_LABEL + str(self.__label_counter), LABEL_ALTER_SEP)

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
        segment = self.__parser.get_segment_label()
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
            return Translator.__push_address_to_stack(POINTER_ADDRESS_TRANSLATOR[address])
        # pop pointer
        else:
            return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + \
                   Translator.__get_A_instruction(POINTER_ADDRESS_TRANSLATOR[address]) + UPDATE_MEMORY_TO_D

    @staticmethod
    def __push_address_to_stack(address):
        """
        returns the hack command for pushing the value in the given address to the stack
        :param address: the address that holds the value to be pushed into the stack
        :return: the matching hack command
        """
        return Translator.__get_A_instruction(address) + GETTING_REGISTER_VALUE + \
               Translator.__operate_on_stack(UPDATE_MEMORY_TO_D) + Translator.__increment_stack()

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
        return A_PREFIX + str(address_code) + END_OF_LINE_MARK

    @staticmethod
    def __put_address_in_stack(address):
        """
        *SP = address (for "push constant address" command)
        :param address: the address to put in the stack
        :return: the command for putting the given address in the stack
        """
        return Translator.__get_A_instruction(address) + GETTING_ADDRESS_VALUE + \
               Translator.__operate_on_stack(UPDATE_MEMORY_TO_D)

    def __create_label(self, label_name, label_sep):
        """
        (label_name + INDEX)
        :param label_name: the label name
        :param label_sep: the separator between the file name and function name and the label name
        :return: the label name format with the current label counter
        """
        return LABEL_PREFIX + self.__create_full_label_name(label_name, label_sep) + LABEL_SUFFIX + END_OF_LINE_MARK

    def __create_full_label_name(self, label_name, label_sep):
        """
        creates the full label name according to the convention
        :param label_name: the pure label name
        :param label_sep: the separator between the label prefix and the pure label name
        :return: the full label name
        """
        label_full_name = ""
        # if the label is created inside call command: adds the called function name
        if self.__parser.get_type() == Parser.CALL_COMMAND_TYPE:
            label_full_name += self.__parser.get_called_function_name()
        # if the label is inside a function: adds the outer function name
        elif self.__parser.get_declared_function_name():
            label_full_name += self.__parser.get_declared_function_name()
        label_full_name += label_sep + label_name
        return label_full_name

    @staticmethod
    def __translate_goto(address):
        """
        @address
        0;JMP
        :param: address: the address for the destination of the jump
        :return: The asm code for goto operation
        """
        return Translator.__get_A_instruction(address) + JUMP_ALWAYS_OPERATION

    @staticmethod
    def __translate_return():
        """
        :return: the machine hack commands for a vm return command
        """
        # stores the return address into a temp register
        stores_return_into_temp = Translator.__get_A_instruction(DIST_TO_RET_ADDRESS) + GETTING_ADDRESS_VALUE + \
            Translator.__get_A_instruction(LOCAL_KEYWORD) + SUBTRACTION_D_FROM_M_TO_A + \
            GETTING_REGISTER_VALUE + Translator.__get_A_instruction(ADDR_STORE_REGISTER) + UPDATE_MEMORY_TO_D
        # copies the return value into the argument address
        copies_return_val = Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + \
            Translator.__get_A_instruction(ARGUMENT_KEYWORD) + GO_TO_REGISTER_M + UPDATE_MEMORY_TO_D
        # clears the stack - set the stack address to be after the return value (after the argument address)
        clears_stack = Translator.__get_A_instruction(ARGUMENT_KEYWORD) + GETTING_REGISTER_VALUE + \
            Translator.__get_A_instruction(STACK) + UPDATE_MEMORY_TO_INCREMENTED_D
        # restores all the segments addresses
        restore_THAT = Translator.__restores_outer_function_segments(THAT_KEYWORD)
        restore_THIS = Translator.__restores_outer_function_segments(THIS_KEYWORD)
        restore_ARG = Translator.__restores_outer_function_segments(ARGUMENT_KEYWORD)
        restore_LCL = Translator.__restores_outer_function_segments(LOCAL_KEYWORD)
        jump_return = Translator.__get_A_instruction(ADDR_STORE_REGISTER) + GO_TO_REGISTER_M + JUMP_ALWAYS_OPERATION

        # combines all together
        return stores_return_into_temp + copies_return_val + clears_stack + restore_THAT + restore_THIS + \
               restore_ARG + restore_LCL + jump_return

    def translate_booting(self):
        """
        Creates the asm commands for calling the sys.init file and initializing the stack.
        :return: the machine hack commands
        """
        self.__parser.set_command(SYS_INIT_VM_COMMAND)
        self.__parser.parse()
        trans = Translator.__get_A_instruction(STACK_INITIAL_ADDRESS) + GETTING_ADDRESS_VALUE + \
            Translator.__get_A_instruction(STACK) + UPDATE_MEMORY_TO_D + \
                self.__translate_call()
        return trans

    def __translate_label(self):
        """
        translates label vm command to hack command
        :return: the matching hack command
        """
        return self.__create_label(self.__parser.get_segment_label, LABEL_SEP)

    @staticmethod
    def __translate_if_goto(address):
        """
        translates if-goto vm command to hack command
        :return: the matching hack command
        """
        return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + \
               Translator.__get_A_instruction(address) + JUMP_ON_D + JUMP_NOT_EQUAL + END_OF_LINE_MARK

    @staticmethod
    def __restores_outer_function_segments(dest_register):
        """
        @LCL
        AM=M-1
        D=M
        @dest_register
        A=M
        M=D
        :param dest_register: the register we want to restore its value
        :return: the matching hack command
        """
        return Translator.__get_A_instruction(LOCAL_KEYWORD) + GO_TO_PREVIOUS_REGISTER_M + \
               GETTING_REGISTER_VALUE + Translator.__get_A_instruction(dest_register) + UPDATE_MEMORY_TO_D

    def __translate_call(self):
        """
        translates function call vm command to hack command
        :return: the matching hack command
        """
        return_address = RETURN_LABEL + str(self.__parser.get_function_call_number())
        full_return_address = self.__create_full_label_name(return_address, LABEL_SEP)
        push_ret_address = Translator.__put_address_in_stack(full_return_address) + Translator.__increment_stack()
        push_LCL = Translator.__push_address_to_stack(LOCAL_KEYWORD)
        push_ARG = Translator.__push_address_to_stack(ARGUMENT_KEYWORD)
        push_THIS = Translator.__push_address_to_stack(THIS_KEYWORD)
        push_THAT = Translator.__push_address_to_stack(THAT_KEYWORD)
        repos_ARG = Translator.__get_A_instruction(DIST_TO_RET_ADDRESS) + GETTING_ADDRESS_VALUE + \
                    Translator.__get_A_instruction(self.__parser.get_function_arg_var_num()) + \
                    ADD_A_TO_D + Translator.__get_A_instruction(STACK) + SUBTRACTION_D_FROM_M_TO_D + \
                    Translator.__get_A_instruction(ARGUMENT_KEYWORD) + UPDATE_MEMORY_TO_D
        repos_LCL = Translator.__get_A_instruction(STACK) + GETTING_REGISTER_VALUE + \
                    Translator.__get_A_instruction(LOCAL_KEYWORD) + UPDATE_MEMORY_TO_D
        jump_to_func = Translator.__translate_goto(self.__parser.get_called_function_name())
        return_label = self.__create_label(return_address, LABEL_SEP)

        return push_ret_address + push_LCL + push_ARG + push_THIS + push_THAT + \
               repos_ARG + repos_LCL + jump_to_func + return_label

    def __translate_function_declaration(self):
        """
        translates function declaration vm command to hack command
        :return: the matching hack command
        """
        create_func_label = self.__create_label(EMPTY_COMMAND, EMPTY_COMMAND)
        push_vars = Translator.__get_A_instruction(self.__parser.get_function_arg_var_num()) + GETTING_ADDRESS_VALUE + \
                    self.__create_label(LOOP_LABEL, LABEL_ALTER_SEP) + \
                    Translator.__get_A_instruction(self.__create_full_label_name(END_LOOP_LABEL, LABEL_ALTER_SEP)) + \
                    Translator.__jump_based_on_D(JUMP_EQUAL) + Translator.__operate_on_stack(FALSE_INTO_MEMORY) + \
                    Translator.__increment_stack() + REDUCE_D + \
                    Translator.__translate_goto(self.__create_full_label_name(LOOP_LABEL, LABEL_ALTER_SEP)) + \
                    self.__create_label(END_LOOP_LABEL, LABEL_ALTER_SEP)

        return create_func_label + push_vars

