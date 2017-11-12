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
    def __init__(self):
        """
        Creates new object of a parser.
        """
        self.__command = None
        self.__command_type = None
        self.__inner_command = None  # push/pop command
        self.__segment = None
        self.__dest_address = None
        self.__arithmetic_operation = None

    def set_command(self, command):
        """
        Sets the command in the parser. Clears the command from comments and extra white spaces and
        set the type
        :param command: the command to parse.
        """
        self.__command = command
        self.__clear()
        self.__command_type = self.__set_type()
        self.__inner_command = None
        self.__segment = None
        self.__dest_address = None
        self.__arithmetic_operation = None

    def __clear(self):
        """
        Reformat the command - removes comments and any white spaces
        """
        self.__command = self.__command.strip()  # removes white spaces from the beginning and the end
        comment_pos = self.__command.find(COMMENT_MARK)  # search for a comments chars "//"
        if comment_pos >= 0:
            self.__command = self.__command[:comment_pos]  # removes any comment if there is any
        print(self.__command)

    def __set_type(self):
        """
        Sets the type of the command: A-instruction / C-instruction / empty line / label
        """
        if len(self.__command) == 0:  # an empty command
            return EMPTY_COMMAND_TYPE
        # search for special symbol. If there aren't any then it is C-instruction
        if PUSH_COMMAND_MARK in self.__command:
            return PUSH_COMMAND_TYPE
        if POP_COMMAND_MARK in self.__command:
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
        command_parts = re.split(COMMANDS_SEPARATOR, self.__command)  # split the command based on white spaces
        command_parts = list(filter(lambda x: x != "", command_parts))  # removes empty parts resulted by extra spaces
        if self.get_type() == ARITHMETIC_COMMAND_TYPE:
            self.__arithmetic_operation = command_parts[ARITHMETIC_POS]
        elif self.get_type() == PUSH_COMMAND_TYPE:
            self.__inner_command = command_parts[COMMAND_POS]
            self.__segment = command_parts[SEGMENT_POS]
            self.__dest_address = command_parts[DEST_ADDRESS_POS]

    def get_operation(self):
        """
        :return: the dest part of the command in case of the command is a C-address. Otherwise, returns None
        """
        return self.__arithmetic_operation

    def get_command(self):
        """
        :return: the comp part of the command in case of the command is a C-address. Otherwise, returns None
        """
        return self.__inner_command

    def get_segment(self):
        """
        :return: the jump part of the command in case of the command is a C-address. The jump can be an empty
        string. If the command is not a C-instruction, returns None
        """
        return self.__segment

    def get_address(self):
        """
        :return: the address in the memory in the command in case of the command is a A-address. Otherwise, returns None
        """
        return self.__dest_address
