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
PUSH_COMMAND_MARK = 'push'
POP_COMMAND_MARK = 'pop'
COMMENT_MARK = '//'
COMMANDS_SEPARATOR = "\s"
ARITHMETIC_POS = 0
COMMAND_POS = 0
SEGMENT_POS = 1
DEST_ADDRESS_POS = 2


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
        self.__segment = None
        self.__dest_address = None
        self.__arithmetic_operation = None
        self.__file_name = file_name

    def set_command(self, command):
        """
        Sets the command in the parser. Clears the command from comments and extra white spaces and
        set the type
        :param command: the command to parse.
        """
        self.__command = command
        self.__clear()
        self.__command_type = self.__set_type()
        self.__segment = None
        self.__dest_address = None
        self.__arithmetic_operation = None

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
        if self.get_type() == ARITHMETIC_COMMAND_TYPE:
            self.__arithmetic_operation = command_parts[ARITHMETIC_POS]
        elif self.get_type() == PUSH_COMMAND_TYPE or self.get_type() == POP_COMMAND_TYPE:
            self.__segment = command_parts[SEGMENT_POS]
            self.__dest_address = command_parts[DEST_ADDRESS_POS]

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

    def get_segment(self):
        """
        :return: the segment part of the command, in case the command is a push/pop command. Otherwise, returns None
        """
        return self.__segment

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
