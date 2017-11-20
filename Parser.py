###########
# imports #
###########
import re

#############
# constants #
#############
PUSH_COMMAND_TYPE = 'PU'
POP_COMMAND_TYPE = 'PO'
ARITHMETIC_COMMAND_TYPE = 'A'
EMPTY_COMMAND_TYPE = 'N'
LABEL_COMMAND_TYPE = 'L'
GOTO_COMMAND_TYPE = 'J'
IF_GOTO_COMMAND_TYPE = 'CJ'
RETURN_COMMAND_TYPE = 'R'
FUNCTION_COMMAND_TYPE = 'F'
CALL_COMMAND_TYPE = 'C'
PUSH_COMMAND_MARK = 'push'
POP_COMMAND_MARK = 'pop'
LABEL_COMMAND_MARK = 'label'
GOTO_COMMAND_MARK = 'goto'
IF_GOTO_COMMAND_MARK = 'if-goto'
RETURN_COMMAND_MARK = 'return'
FUNCTION_COMMAND_MARK = 'function'
CALL_COMMAND_MARK = 'call'
COMMENT_MARK = '//'
COMMANDS_SEPARATOR = "\s"
ARITHMETIC_POS = 0
COMMAND_POS = 0
SEGMENT_LABEL_POS = 1
DEST_ADDRESS_POS = 2
GOTO_ADDRESS_POS = 1
FUNCTION_NAME_POS = 1
FUNCTION_ARGS_VARS_POS = 2


class Parser:
    """
    A Parser object to parse the command to its parts.
    """
    def __init__(self, file_name):
        """
        Creates new object of a parser.
        """
        self.__command = None
        self.__command_type = None
        self.__cleared_command = None
        self.__segment_label = None  # the name of the segment or the label (depend on the command)
        self.__dest_address = None
        self.__arithmetic_operation = None
        self.__function_name = None
        self.__function_called_name = None  # the function name when calling a function
        self.__function_arg_var_num = None
        self.__file_name = file_name
        self.__functions_calls = {}  # stores all the called functions and its call number

    def set_command(self, command):
        """
        Sets the command in the parser. Clears the command from comments and extra white spaces and
        set the type
        :param command: the command to parse.
        """
        self.__command = command
        self.__clear()
        self.__command_type = self.__set_type()
        self.__segment_label = None
        self.__dest_address = None
        self.__arithmetic_operation = None
        self.__function_name = None
        self.__function_called_name = None
        self.__function_arg_var_num = None

    def __clear(self):
        """
        Reformat the command - removes comments and any white spaces
        """
        self.__command = self.__command.strip()  # removes white spaces from the beginning and the end
        self.__cleared_command = self.__command
        comment_pos = self.__cleared_command.find(COMMENT_MARK)  # search for a comments chars "//"
        if comment_pos >= 0:
            self.__cleared_command = self.__cleared_command[:comment_pos]  # removes any comment if there is any

    def __set_type(self):
        """
        Sets the type of the command: pop command / push command / arithmetic / empty line
        """
        if len(self.__cleared_command) == 0:  # an empty command
            return EMPTY_COMMAND_TYPE
        # search for command names
        if PUSH_COMMAND_MARK in self.__cleared_command:
            return PUSH_COMMAND_TYPE
        if POP_COMMAND_MARK in self.__cleared_command:
            return POP_COMMAND_TYPE
        if LABEL_COMMAND_MARK in self.__cleared_command:
            return LABEL_COMMAND_TYPE
        if RETURN_COMMAND_MARK in self.__cleared_command:
            return RETURN_COMMAND_TYPE
        if CALL_COMMAND_MARK in self.__cleared_command:
            return CALL_COMMAND_TYPE
        if FUNCTION_COMMAND_MARK in self.__cleared_command:
            return FUNCTION_COMMAND_TYPE
        if IF_GOTO_COMMAND_MARK in self.__cleared_command:  # first search for if-goto and only then for goto
            return IF_GOTO_COMMAND_MARK
        if GOTO_COMMAND_MARK in self.__cleared_command:
            return GOTO_COMMAND_TYPE
        return ARITHMETIC_COMMAND_TYPE

    def get_type(self):
        """
        :return: the command type: P for a push/pop command, A for an arithmetic command, N for empty line
        """
        return self.__command_type

    def parse(self):
        """
        Parse the command into its parts and set the command / segment / dest address / arithmetic command
        """
        command_parts = re.split(COMMANDS_SEPARATOR, self.__cleared_command)  # split the command based on white spaces
        command_parts = list(filter(lambda x: x != "", command_parts))  # removes empty parts resulted by extra spaces
        if self.__command_type == ARITHMETIC_COMMAND_TYPE:
            self.__arithmetic_operation = command_parts[ARITHMETIC_POS]
        elif self.__command_type == PUSH_COMMAND_TYPE or self.__command_type == POP_COMMAND_TYPE:
            self.__segment_label = command_parts[SEGMENT_LABEL_POS]
            self.__dest_address = command_parts[DEST_ADDRESS_POS]
        elif self.__command_type == GOTO_COMMAND_TYPE or self.__command_type == IF_GOTO_COMMAND_MARK:
            self.__dest_address = command_parts[GOTO_ADDRESS_POS]
        elif self.__command_type == LABEL_COMMAND_TYPE:
            self.__segment_label = command_parts[SEGMENT_LABEL_POS]
        elif self.__command_type == CALL_COMMAND_TYPE:
            self.__function_called_name = command_parts[FUNCTION_NAME_POS]
            self.__function_arg_var_num = command_parts[FUNCTION_ARGS_VARS_POS]
            if self.__function_called_name not in self.__functions_calls:
                self.__functions_calls[self.__function_called_name] = 0
            else:
                self.__functions_calls[self.__function_called_name] += 1
        elif self.__command_type == FUNCTION_COMMAND_TYPE:
            self.__function_name = command_parts[FUNCTION_NAME_POS]
            self.__function_arg_var_num = command_parts[FUNCTION_ARGS_VARS_POS]
        elif self.__command_type == RETURN_COMMAND_TYPE:
            self.__function_name = None

    def get_operation(self):
        """
        :return: the arithmetic operation (add, sub, eq...). If the command is not an arithmetic command, returns None
        """
        return self.__arithmetic_operation

    def get_command(self):
        """
        :return: the full VM original command
        """
        return self.__command

    def get_segment_label(self):
        """
        :return: the segment part of the command, in case the command is a push/pop command. Otherwise, returns None
        """
        return self.__segment_label

    def get_address(self):
        """
        :return: the destination address part of the command, in case the command is a push/pop command.
        Otherwise, returns None
        """
        return self.__dest_address

    def get_file_name(self):
        """
        :return: the VM file name
        """
        return self.__file_name

    def get_declared_function_name(self):
        """
        :return: the current function name. If it is current out of a function, returns None
        """
        return self.__function_name

    def get_called_function_name(self):
        """
        :return: the name of the called function on a call command
        """
        return self.__function_called_name

    def get_function_call_number(self):
        """
        :return: the number of the calls to the current function. If it is current out of a function, returns None
        """
        if self.__function_called_name is None:
            return None
        return self.__functions_calls[self.__function_called_name]

    def get_function_arg_var_num(self):
        """
        :return: the number of args when calling a function or the number of variables the function needs on declaration
        """
        return self.__function_arg_var_num
