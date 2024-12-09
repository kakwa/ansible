def decode_utf16_variable(variable_name):
    """
    Decodes a UTF-16 (char16_t) string from a variable of type pcsz
    and prints it as a UTF-8 string.
    """
    # Parse the variable
    value = gdb.parse_and_eval(variable_name)

    wchar_t_ptr_type = gdb.lookup_type("char16_t").pointer()
    const_wchar_t_ptr_type = wchar_t_ptr_type.const()
    pointer = value.cast(const_wchar_t_ptr_type)
    print(pointer.string())

class DecodeUTF16VariableCommand(gdb.Command):
    """Decode a UTF-16 string stored in a variable containing octal escape sequences."""

    def __init__(self):
        super(DecodeUTF16VariableCommand, self).__init__("print_utf16_var", gdb.COMMAND_USER)

    def invoke(self, argument, from_tty):
        decode_utf16_variable(argument.strip())

DecodeUTF16VariableCommand()
