#############
# constants #
#############
END_OF_LINE_MARK = "\n"
STACK = "@SP" + END_OF_LINE_MARK
GO_TO_REGISTER_M = "A=M" + END_OF_LINE_MARK
GO_TO_REGISTER_D = "A=D" + END_OF_LINE_MARK
GETTING_REGISTER_VALUE = "D=M" + END_OF_LINE_MARK
GETTING_ADDRESS_VALUE = "D=A" + END_OF_LINE_MARK
REDUCE_MEMORY = "M=M-1" + END_OF_LINE_MARK
INCREMENT_MEMORY = "M=M+1" + END_OF_LINE_MARK
UPDATE_MEMORY_TO_D = "M=D" + END_OF_LINE_MARK
ADDING_D_TO_MEMORY = "M=M+D" + END_OF_LINE_MARK
SUBTRACTION_D_FROM_MEMORY = "M=M-D" + END_OF_LINE_MARK
NEGATION_MEMORY = "M=-M" + END_OF_LINE_MARK
NOT_MEMORY = "M=!M" + END_OF_LINE_MARK
OR_D_MEMORY = "M=M|D" + END_OF_LINE_MARK
AND_D_MEMORY = "M=M&D" + END_OF_LINE_MARK
ADD_A_TO_D = "D=D+A" + END_OF_LINE_MARK
LABELS_TRANSLATOR = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
STATIC_SEGMENT = "static"
POINTER_SEGMENT = "pointer"
TEMP_SEGMENT = "temp"
CONSTANT_SEGMENT = "constant"
A_PREFIX = "@"
TEMP_MEMORY = "5"


class Translator:
    """
    A translator class translates an instruction in hack language to binary code. Consists on static methods that
    translate a line when given a Parser object that parsed the line
    """

    @staticmethod
    def translate(parser):
        pass

    @staticmethod
    def __reduce_stack():
        """
        :return: the asm code of reducing the stack
        """
        return STACK + REDUCE_MEMORY

    @staticmethod
    def __increment_stack():
        """
        :return: the asm code of reducing the stack
        """
        return STACK + INCREMENT_MEMORY

    @staticmethod
    def __operate_on_top_stack_value(operation):
        """
        :return: the asm code fot getting the stack register into A
        """
        return STACK + GO_TO_REGISTER_M + operation

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

    @staticmethod
    def __translate_push_pop(parser):
        """
        :return: The asm code for the push/pop operation
        """
        segment = parser.get_segment()
        address = parser.get_address()

        if segment in LABELS_TRANSLATOR.keys():
            return Translator.__translate_local_push_pop(address, LABELS_TRANSLATOR[segment])
        elif segment == CONSTANT_SEGMENT:
            return Translator.__translate_constant_push_pop(address)
        elif segment == TEMP_SEGMENT:
            return Translator.__translate_temp_push_pop(address)
        elif segment == STATIC_SEGMENT:
            return Translator.__translate_static_push_pop(parser)
        else:
            return Translator.__translate_pointer_push_pop(parser)

    @staticmethod
    def __translate_local_push_pop(address, segment_key):
        return Translator.__get_local_address(segment_key, address) + \
               Translator.__put_address_content_in_stack() + Translator.__increment_stack()

    @staticmethod
    def __translate_temp_push_pop(address):
        return Translator.__get_temp_address(address) + Translator.__put_address_content_in_stack() + \
               Translator.__increment_stack()

    @staticmethod
    def __translate_constant_push_pop(address):
        return Translator.__put_address_in_stack(address) + Translator.__increment_stack()

    @staticmethod
    def __translate_static_push_pop(parser):
        pass

    @staticmethod
    def __translate_pointer_push_pop(parser):
        pass

    @staticmethod
    def __get_local_address(segment, address):
        """
        putting addr + i in D register
        :param segment:
        :param address:
        :return:
        """
        return Translator.__get_A_instruction(segment) + GETTING_REGISTER_VALUE + \
               Translator.__get_A_instruction(address) + ADD_A_TO_D

    @staticmethod
    def __get_temp_address(address):
        """
        putting 5 + i in D register
        :param address:
        :return:
        """
        return Translator.__get_A_instruction(TEMP_MEMORY) + GETTING_ADDRESS_VALUE + \
               Translator.__get_A_instruction(address) + ADD_A_TO_D

    @staticmethod
    def __put_address_content_in_stack():
        """
        *SP = *addr
        :return:
        """
        return GO_TO_REGISTER_D + GETTING_REGISTER_VALUE + STACK + GO_TO_REGISTER_M + UPDATE_MEMORY_TO_D

    @staticmethod
    def __get_A_instruction(address_code):
        """
        @address_code
        :param address_code:
        :return:
        """
        return A_PREFIX + address_code + END_OF_LINE_MARK

    @staticmethod
    def __put_address_in_stack(address):
        return Translator.__get_A_instruction(address) + GETTING_ADDRESS_VALUE + STACK + \
               GO_TO_REGISTER_M + UPDATE_MEMORY_TO_D
