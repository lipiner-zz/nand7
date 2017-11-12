import Parser

#############
# constants #
#############
END_OF_LINE_MARK = "\n"
GO_TO_REGISTER_M = "A=M" + END_OF_LINE_MARK
GO_TO_REGISTER_D = "A=D" + END_OF_LINE_MARK
GETTING_REGISTER_VALUE = "D=M" + END_OF_LINE_MARK
GETTING_ADDRESS_VALUE = "D=A" + END_OF_LINE_MARK
REDUCE_MEMORY = "M=M-1" + END_OF_LINE_MARK
INCREMENT_MEMORY = "M=M+1" + END_OF_LINE_MARK
UPDATE_MEMORY_TO_D = "M=D" + END_OF_LINE_MARK
ADDING_D_TO_MEMORY = "M=D+M" + END_OF_LINE_MARK
SUBTRACTION_D_FROM_MEMORY = "M=M-D" + END_OF_LINE_MARK
NEGATION_MEMORY = "M=-M" + END_OF_LINE_MARK
NOT_MEMORY = "M=!M" + END_OF_LINE_MARK
OR_D_MEMORY = "M=M|D" + END_OF_LINE_MARK
AND_D_MEMORY = "M=M&D" + END_OF_LINE_MARK
ADD_A_TO_D = "D=D+A" + END_OF_LINE_MARK
LABELS_TRANSLATOR = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
POINTER_ADDRESS_TRANSLATOR = {"0": "THIS", "1": "THAT"}
STACK = "SP"
STATIC_SEGMENT = "static"
POINTER_SEGMENT = "pointer"
TEMP_SEGMENT = "temp"
CONSTANT_SEGMENT = "constant"
A_PREFIX = "@"
TEMP_MEMORY = "5"
ADDR_STORE_REGISTER = "RAM13"


class Translator:
    """
    A translator class translates an instruction in hack language to binary code. Consists on static methods that
    translate a line when given a Parser object that parsed the line
    """

    def __init__(self, parser):
        self.__parser = parser
        self.__label_counter = 0

    def translate(self, parser):
        pass

    @staticmethod
    def __reduce_stack():
        """
        :return: the asm code of reducing the stack
        """
        return Translator.__get_A_instruction(STACK) + REDUCE_MEMORY

    @staticmethod
    def __increment_stack():
        """
        :return: the asm code of reducing the stack
        """
        return Translator.__get_A_instruction(STACK) + INCREMENT_MEMORY

    @staticmethod
    def __operate_on_top_stack_value(operation):
        """
        :return: the asm code fot getting the stack register into A
        """
        return Translator.__get_A_instruction(STACK) + GO_TO_REGISTER_M + operation

    # @staticmethod
    # def __get_top_stack_into_D():
    #     """
    #     :return: the asm code for getting the value in the top of the stack into the D-register
    #     """
    #     return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE)

    @staticmethod
    def __operate_on_two_top_stack_values(operation):
        """
        :return: the asm code for inserting the most top value in the stack into the A-register and the second
        top value into the memory M
        """
        return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + Translator.__reduce_stack() +\
               GO_TO_REGISTER_M + operation

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
        trans = Translator.__operate_on_two_top_stack_values(SUBTRACTION_D_FROM_MEMORY)
        return trans

    @staticmethod
    def __translate_neg():
        """
        :return: The asm code for the negation operation
        """
        trans = Translator.__operate_on_top_stack_value(NEGATION_MEMORY)
        return trans

    @staticmethod
    def __translate_eq():
        """
        :return: The asm code for the equal operation
        """
        pass

    @staticmethod
    def __translate_gt():
        """
        :return: The asm code for the grater than operation
        """
        pass

    @staticmethod
    def __translate_lt():
        """
        :return: The asm code for the lower than operation
        """
        pass

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
                   Translator.__operate_on_top_stack_value(UPDATE_MEMORY_TO_D) + Translator.__increment_stack()
        # pop pointer
        else:
            return Translator.__reduce_stack() + Translator.__operate_on_top_stack_value(UPDATE_MEMORY_TO_D) + \
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
        return GO_TO_REGISTER_D + GETTING_REGISTER_VALUE + Translator.__operate_on_top_stack_value(UPDATE_MEMORY_TO_D)

    @staticmethod
    def __put_stack_content_in_address():
        """
        *addr = *SP
        :return: the command for putting the content of the stack in the address
        """
        return Translator.__get_A_instruction(ADDR_STORE_REGISTER) + UPDATE_MEMORY_TO_D +\
               Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) +\
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
               Translator.__operate_on_top_stack_value(UPDATE_MEMORY_TO_D)

    @staticmethod
    def __put_stack_content_in_static(file_name, address):
        """
        *filename.i=*SP
        :param file_name: the name of the vm file
        :param address: the address to access in the static segment
        :return: the command for putting the content of the stack in the static variable
        """
        return Translator.__operate_on_top_stack_value(GETTING_REGISTER_VALUE) + \
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
               Translator.__operate_on_top_stack_value(UPDATE_MEMORY_TO_D)
