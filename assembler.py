###########
# imports #
###########

import sys
import os
from first_parse import FirstParse
from second_parse import SecondParse
from symbol_table import SymbolTable
from translator import Translator

#############
# constants #
#############
PATH_POS = 1  # the arguments position for the file path
HACK_SUFFIX = "hack"
ASM_SUFFIX = "asm"
WRITING_MODE = "w"
LINE_BREAK = "\n"


def assemble_file(file_name):
    """
    The function gets a file name from asm type and assembles it to binary code. It creates a hack file with he same
    name in the same directory the contains the assembled binary code.
    :param file_name: the name of the asm file to be assembled
    """
    # opening the asm file
    with open(file_name) as input_file:
        # figuring the output file name- replacing asm suffix to hack
        output_file_name = file_name.replace(ASM_SUFFIX, HACK_SUFFIX)
        # opening the output file in writing mode
        with open(output_file_name, WRITING_MODE) as output_file:
            # first parse of the file
            first_parser = FirstParse()  # creating a Parser for the first parse
            symbol_table = SymbolTable()  # creating the symbol table of the file
            for line in input_file:
                first_parser.set_command(line)  # setting the parser to the current line
                symbol_table.set_label(first_parser)  # creating the symbols of the labels

            # second parse of the file
            input_file.seek(0)  # setting the cursor to the beginning of the file
            second_parser = SecondParse()  # creating a Parser for the second parse
            for line in input_file:
                second_parser.set_command(line)  # setting the parser to the current line
                second_parser.parse()
                binary_line = Translator.translate(second_parser, symbol_table)  # translating to binary code
                if binary_line:
                    output_file.write(binary_line + LINE_BREAK)  # printing the binary code in the output file


def assemble_directory(directory_name):
    """
    The function gets a directory name and assembles all the asm files in it. The function creates matching hack
    files in the directory with the assembled binary code
    :param directory_name: the name of the given directory
    """
    files_list = os.listdir(directory_name)  # list of all the files' name in the given directory
    for directory_file in files_list:
        if ASM_SUFFIX == directory_file[-len(ASM_SUFFIX):]:  # if the file is an ASM file
            asm_file = os.path.join(directory_name, directory_file)  # creates a full path of the file name
            assemble_file(asm_file)

# main part
if __name__ == '__main__':
    if len(sys.argv) < PATH_POS + 1:
        sys.exit()  # There is not an input

    # checks if the given path is a directory or a file
    path = sys.argv[PATH_POS]
    if os.path.isdir(path):
        assemble_directory(path)  # assembles all asm file in the directory
    else:
        assemble_file(path)  # assembles the given asm file
