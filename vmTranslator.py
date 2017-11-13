###########
# imports #
###########

import sys
import os

from Parser import Parser
from translator import Translator

#############
# constants #
#############
PATH_POS = 1  # the arguments position for the file path
ASM_SUFFIX = "asm"
VM_SUFFIX = "vm"
WRITING_MODE = "w"
FILE_NAME_POSITION = -1


def translate_file(file_name):
    """
    The function gets a file name from asm type and assembles it to binary code. It creates a hack file with he same
    name in the same directory the contains the assembled binary code.
    :param file_name: the name of the asm file to be assembled
    """
    # opening the asm file
    with open(file_name) as input_file:
        # figuring the output file name- replacing vm suffix to asm
        output_file_name = file_name.replace(VM_SUFFIX, ASM_SUFFIX)
        # opening the output file in writing mode
        with open(output_file_name, WRITING_MODE) as output_file:
            # translating the file
            file_name_dirs = file_name.split(os.path.sep)  # split the path to its directories and the file name
            file_name = file_name_dirs[FILE_NAME_POSITION][:-len(VM_SUFFIX)-1]  # gets the file name only
            file_parser = Parser(file_name)
            file_translator = Translator(file_parser)

            for line in input_file:
                file_parser.set_command(line)  # setting the parser to the current line
                file_parser.parse()
                asm_command = file_translator.translate()
                output_file.write(asm_command)  # printing the asm code in the output file


def translate_directory(directory_name):
    """
    The function gets a directory name and assembles all the asm files in it. The function creates matching hack
    files in the directory with the assembled binary code
    :param directory_name: the name of the given directory
    """
    files_list = os.listdir(directory_name)  # list of all the files' name in the given directory
    for directory_file in files_list:
        if VM_SUFFIX == directory_file[-len(VM_SUFFIX):]:  # if the file is an VM file
            vm_file = os.path.join(directory_name, directory_file)  # creates a full path of the file name
            translate_file(vm_file)

# main part
if __name__ == '__main__':
    if len(sys.argv) < PATH_POS + 1:
        sys.exit()  # There is not an input

    # checks if the given path is a directory or a file
    path = sys.argv[PATH_POS]
    if os.path.isdir(path):
        translate_directory(path)  # translates all asm file in the directory
    else:
        translate_file(path)  # translates the given asm file
