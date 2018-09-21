#!/usr/bin/python3
#tuan1.le@lge.com


import os
import os.path
import sys
import xlsxwriter

module = "progmgr"
pic = "tuan1.le"
source_dir = "src"
header_dir = "include"
function_number_total = 0


def real_code(line, checksemicolon = True):
    line = remove_comment(line)
    line = line.strip(' \t\n\r')
    if not line:
        return ""
    if checksemicolon and not line.endswith(";"):
        return ""
    return line

def remove_comment(line):
    parts = line.split("//", 1)
    if line.find("/*") != -1 and line.find("*/") != -1:
        parts = line.split("/*", 1)
        parts2 = line.split("*/")
        return parts[0] + parts2[len(parts2)-1]
    return parts[0]

def remove_text_inside_brackets(text, brackets="[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    saved_brackets = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0
                saved_brackets.append(character)
                break
        else: # character is not a bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    result = []
    result.append(''.join(saved_chars).rstrip())
    result.append(''.join(saved_brackets))
    return result

def convert_to_pseudocode(function_code):
    function_pseudocode = ""

    function_pseudocode += function_code
    #    while i in range(len(lines) - 1):
    #        i += 1
    #        if not start and "\t// {{{USR\n" == lines[i]:
    #            start = True
    #            # if TESTMOD == capsule and "openARResp" == name:
    #            #     print("Start:", lines[i])
    #
    #        if "/*" in lines[i] and not lines[i].lstrip().startswith("//"):
    #            block_comment = True
    #
    #        if lines[i].startswith("#if 0"):
    #            if0 = True
    #
    #        if start and "\t// }}}USR\n" == lines[i]:
    #            # if "FeatStateVcpC" == capsule and "Trigger" == name:
    #            #     print("End:", lines[i], i, len(lines))
    #            i = len(lines)
    #            start = False
    #            break
    #
    #        if block_comment and "*/" in lines[i] and not lines[i].lstrip().startswith("//"):
    #            block_comment = False
    #            continue
    #
    #        if if0 and lines[i].startswith("#endif"):
    #            if0 = False
    #            continue
    #
    #        if start and real_code(lines[i], False) and not block_comment and not if0:
    #            if not codes:
    #                tab_to_strip = len(lines[i]) - len(lines[i].lstrip("\t"))
    #            #convert to pseudocode
    #            strcode = remove_comment(lines[i][tab_to_strip:])
    #            strcode = strcode.rstrip() + "\n"
    #            #print(strcode)
    #            if "LOGGER(" in strcode and strcode.rstrip().endswith(";"):
    #                strcode = ""
    #            if "TRACE(" in strcode and strcode.rstrip().endswith(";"):
    #                # if "RespBT" == name:
    #                #     print("Skip TRACE", strcode)
    #                strcode = ""
    #
    #            if "CATTComm::SendPacketToATT" in strcode:
    #                strcode = strcode.replace("CATTComm::SendPacketToATT", "SENDS PACKET TO ATT ")
    #            if "CATTComm::SendComPacketToATT" in strcode:
    #                strcode = strcode.replace("CATTComm::SendComPacketToATT", "SENDS COM PACKET TO ATT ")
    #            if ").send();" in strcode:
    #                str2 = strcode.replace(".send();", "")
    #                parts = str2.rsplit(".", 1)
    #                if len(parts) == 2:
    #                    if parts[1].rstrip().endswith("()"):
    #                        parts[1] = parts[1].replace("()", "")
    #                    strcode = parts[0] + " SENDS SIGNAL " + parts[1]
    #            else:
    #                if " strstr(" in strcode or "(strstr(" in strcode:
    #                    parts = strcode.split("strstr(", 1)
    #                    strcode = parts[0] + parts[1].replace(",", " CONTAINS ", 1)
    #                    parts = strcode.split("CONTAINS")
    #                    parts = parts[1].split(")", 1)
    #                    if parts[1].lstrip().startswith("!= NULL"):
    #                        strcode = strcode.replace("!= NULL", "", 1)
    #                    else:
    #                        if parts[1].lstrip().startswith("== NULL"):
    #                            strcode = strcode.replace("CONTAINS", "NOT CONTAINS")
    #                else:
    #                    if strcode.lstrip().startswith("printf("):
    #                        strcode = ""
    #            if strcode.lstrip().startswith("if(") or strcode.lstrip().startswith("if ("):
    #                strcode = strcode.replace("if", "IF ", 1)
    #            # if strcode.rstrip().endswith(";"):
    #            #     parts = strcode.rsplit(";", 1)
    #            #     strcode = parts[0] + parts[1]
    #            if "strncmp(" in strcode:
    #                strcode = strcode.replace("strncmp", "DIFFERENCE BETWEEN STRINGS")
    #            if "strcmp(" in strcode:
    #                strcode = strcode.replace("strcmp", "DIFFERENCE BETWEEN STRINGS")
    #            if "memcpy(" in strcode:
    #                strcode = strcode.replace("memcpy", "COPY MEMORY BLOCK")
    #            if "memcmp(" in strcode:
    #                strcode = strcode.replace("memcmp", "DIFFERENCE BETWEEN MEMORY BLOCKS")
    #            if "strcpy(" in strcode:
    #                strcode = strcode.replace("strcpy", "COPY STRING")
    #            if "strncpy(" in strcode:
    #                strcode = strcode.replace("strncpy", "COPY STRING")
    #            if "memset(" in strcode:
    #                strcode = strcode.replace("memset", "RESET MEMORY BLOCK")
    #            if "fopen(" in strcode:
    #                strcode = strcode.replace("fopen", "OPEN FILE")
    #            if "fprintf(" in strcode:
    #                strcode = strcode.replace("fprintf", "WRITE TO FILE")
    #            if "fclose(" in strcode:
    #                strcode = strcode.replace("fclose", "CLOSE FILE")
    #            if "snprintf(" in strcode:
    #                strcode = strcode.replace("snprintf", "PRINT TO BUFFER")
    #            #codes += lines[i][tab_to_strip:]
    #            #print("After:" , strcode)
    #            codes += strcode
    #            # if "FeatStateVcpC" == capsule and "Trigger" == name:
    #            #     print("Code line:", lines[i])
    #    if i == len(lines):
    #        break

    return function_pseudocode

def export_operations(file, function_text, row, worksheet=None, indentH=2, indentC=3):
    global operation_txt
    global stats_by_method
    global stats_by_component
    #lines = function_text.strip().split('\n')
    lines = function_text.strip().split('\n', 1)
    if len(lines) < 2:
        return row

    #for i in range(len(lines)):
    if True:
        function_prototype = lines[0]
        function_code = lines[1].strip("{} \n\t")
        parts = function_prototype.split("(")
        if len(parts) < 2:
            return row

        function_params = parts[1].split(")", 1)
        function_params = function_params[0].strip().split(",")
        
        parts = parts[0].split(' ')
        function_name = parts[len(parts)-1]

        worksheet.write('B' + str(row), 'Should have')
        worksheet.write('C' + str(row), function_name, format[indentH])
        worksheet.write('D' + str(row), 'New')
        worksheet.write('E' + str(row), pic)
        print(function_name)

        if function_name not in operation_txt:
            operation_txt[function_name] = "This is an operation for ..."

        desc = "__Description__\n\n" + operation_txt[function_name] + "\n\n__Syntax__\n\n" + "[{ColorCode syntax=\'c\'\n\n"
        desc += function_prototype
        desc += "}]\n\n__Parameters__\n\n[{Table\n\n||%%(color:#000000;)Name%!\n||%%(color:#000000;)Type%!\n||%%(color:#000000;)Description%!\n\n"
        for line in function_params:
            line = line.replace("[ ", "[")
            line = line.replace(" ]", "]")
            line = line.replace("[ ", "[")
            line = line.replace(" ]", "]")
            line = line.split("=")[0].strip()
            brackets = ""
            if line.endswith("]"):
                result = remove_text_inside_brackets(line)
                line = result[0]
                if len(result) == 2:
                    brackets = result[1]
            parts = line.rsplit(" ", 1)
            if len(parts) != 2:
                continue
            if "CDebug" == parts[0]:
                continue
            desc += "|" + parts[1] + "\n"
            if not brackets:
                desc += "|" + parts[0] + "\n"
            else:
                desc += "|[{ColorCode syntax=\'c\'\n\n" + parts[0] + brackets + "\n}]\n"
            #if capsule + "::" + name + "::" + parts[1] not in operation_param_txt:
                #operation_param_txt[capsule + "::" + name + "::" + parts[1]] = ""
            #desc += "|" + operation_param_txt[capsule + "::" + name + "::" + parts[1]] + " \n\n"
            desc += "|" + " \n\n"

        desc += "}]\n\n"
        desc += "__Return Value__\n\n \n"
        desc += "__Errors__\n\n \n"
        desc += "__Notes__\n\n \n"
        worksheet.write('F' + str(row), desc)
        worksheet.write('G' + str(row), 'Operations')
        worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
        row += 1

        worksheet.write('B' + str(row), 'Should have')
        worksheet.write('C' + str(row), function_name + " - Detail Logic", format[indentC])
        worksheet.write('D' + str(row), 'New')
        worksheet.write('E' + str(row), pic)

        desc = "__Pseudocode__\n\n" + "[{ColorCode syntax=\'c\'\n\n"
        desc += convert_to_pseudocode(function_code)
        desc += "}]\n\n"

        desc += "__Diagram__\n\n \n"

        worksheet.write('F' + str(row), desc)
        worksheet.write('G' + str(row), 'Operations - Detail Logic')
        worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
        row += 1

    return row

def export_data_for_c_file(file, row, indent=1, worksheet=None):
    with open(file, 'r', errors="ignore") as file:
        lines = file.readlines()

        block_comment = False
        if0 = False
        function_text = ""
        function_body = False
        function_number = 0

        for i in range(len(lines)):

            if "/*" in lines[i] and not "*/" in lines[i] and not lines[i].lstrip().startswith("//"):
                block_comment = True
                #mal-case line 58, util.h, #define DELTA_PATH				"/var/opt/progmgr/"     //* Change unzip path - hyuntae.bok 170302
                if lines[i].find("//") != -1 and lines[i].find("/*") > lines[i].find("//"):
                    lines[i] = str(lines[i].split("//")[0])
                    block_comment = False
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "block_comment =", block_comment)

            if lines[i].startswith("#if 0") or lines[i].startswith("#if\t0"):
                if0 = True
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "if0 =", if0)

            if block_comment:
                if "*/" in lines[i] and not lines[i].lstrip().startswith("//"):
                    block_comment = False
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "block_comment =", block_comment)
                continue

            if if0:
                if lines[i].startswith("#endif"):
                    if0 = False
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "if0 =", if0)
                continue

            #lines[i] = real_code(lines[i], False)
            #if not lines[i]:
                #continue

            #function is in one line.
            if '){' in lines[i] and ';}' in lines[i]:
                #function_prototype = lines[i]
                parts = lines[i].split("(")
                if len(parts) < 2:
                    return row
                #function_name = parts[0]
                #function_params = parts[1].split(")", 1)
                #function_params = function_params[0].strip().split(",")
                parts = parts[0].split(' ')
                if len(parts) >= 1 and parts[len(parts)-1]:
                    #function_name = parts[len(parts)-1]
                    #worksheet.write('C' + str(row), function_name, format[indent])
                    #worksheet.write('G' + str(row), 'Operations')
                    #worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                    #row += 1
                    function_text = real_code(lines[i], False).replace('{',"\n{\n")
                    function_text = function_text.replace(';',";\n")
                    function_number += 1
                    #function_number_total += 1
                    #print(function_text)
                    row = export_operations(file, function_text, row, worksheet, indent + 1, indent + 2)

            #function with function name is previous line and '{' is first character.
            if lines[i].startswith("{") and not function_body:
                function_body = True
                function_text = ""
                #function_prototype = lines[i-1]
                parts = lines[i-1].split("(")   #check if previous line is really an function prototype (need improvement)
                if len(parts) < 2:
                    continue
                #function_name = parts[0]
                parts = parts[0].split(' ')
                if len(parts) >= 1 and parts[len(parts)-1]:
                    #function_name = parts[len(parts)-1]
                    #worksheet.write('C' + str(row), function_name, format[indent])
                    #worksheet.write('G' + str(row), 'Operations')
                    #worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                    #row += 1
                    function_text += real_code(lines[i-1], False) + '\n' + real_code(lines[i], False) + '\n'
                    continue

            if function_body:
                function_text += real_code(lines[i], False) + '\n'
                if lines[i].startswith("}"):
                    function_body = False
                    function_number += 1
                    #function_number_total += 1
                    #print(function_number, str(file).split('\'')[1] + " " + str(i + 1) + '\n' + function_text)
                    row = export_operations(file, function_text, row, worksheet, indent + 1, indent + 2)

            #enum
            if "typedef enum" in lines[i] or "enum {" in lines[i]:
                worksheet.write('C' + str(row), lines[i], format[indent])
                worksheet.write('G' + str(row), 'Enumerations')
                worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                row += 1

            #constant
            if "#define" in lines[i]:
                worksheet.write('C' + str(row), lines[i], format[indent])
                worksheet.write('G' + str(row), 'Contants')
                worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                row += 1
                

            #data structure
            if "typedef struct" in lines[i]:
                worksheet.write('C' + str(row), lines[i], format[indent])
                worksheet.write('G' + str(row), 'Data Structures')
                worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                row += 1

#END       for i in range(len(lines)):
    return row
    
def export_data_for_h_file(file, row, indent=1, worksheet=None):
    with open(file, 'r', errors="ignore") as file:
        lines = file.readlines()

        block_comment = False
        if0 = False

        for i in range(len(lines)):

            if "/*" in lines[i] and not "*/" in lines[i] and not lines[i].lstrip().startswith("//"):
                block_comment = True
                #mal-case line 58, util.h, #define DELTA_PATH				"/var/opt/progmgr/"     //* Change unzip path - hyuntae.bok 170302
                if lines[i].find("//") != -1 and lines[i].find("/*") > lines[i].find("//"):
                    lines[i] = str(lines[i].split("//")[0])
                    block_comment = False
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "block_comment =", block_comment)

            if lines[i].startswith("#if 0") or lines[i].startswith("#if\t0"):
                if0 = True
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "if0 =", if0)

            if block_comment:
                if "*/" in lines[i] and not lines[i].lstrip().startswith("//"):
                    block_comment = False
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "block_comment =", block_comment)
                continue

            if if0:
                if lines[i].startswith("#endif"):
                    if0 = False
                #print(lines[i].strip(), str(file).split('\'')[1] + " " + str(i + 1), "if0 =", if0)
                continue

            lines[i] = real_code(lines[i], False)
            if not lines[i]:
                continue

            #enum
            if "typedef enum" in lines[i] or "enum {" in lines[i]:
                worksheet.write('C' + str(row), lines[i], format[indent])
                worksheet.write('G' + str(row), 'Enumerations')
                worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                row += 1

            #constant
            if "#define" in lines[i]:
                worksheet.write('C' + str(row), lines[i], format[indent])
                worksheet.write('G' + str(row), 'Contants')
                worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                row += 1

            #data structure
            if "typedef struct" in lines[i]:
                worksheet.write('C' + str(row), lines[i], format[indent])
                worksheet.write('G' + str(row), 'Data Structures')
                worksheet.write('H' + str(row), str(file).split('\'')[1] + " " + str(i + 1))
                row += 1

    return row

def main():
    # structs/ classes in .h files, sometimes .c files also.
    data_structure = []
    enum = []

    print("Preparing c files without comments...")
    for f in os.listdir("src"):
        if f.endswith(".c") and not "nocomment" in f:
            nocommentfile = f[:-1] + "nocomment" + ".c"
            if os.path.isfile("src/" + nocommentfile):
                continue
            print("gcc -fpreprocessed -dD -E " + "src/" + f + " >> src/" + nocommentfile)
            os.system("gcc -fpreprocessed -dD -E " + "src/" + f + " >> src/" + nocommentfile)

    print("Preparing c files without comments... DONE")

    print("STEP 1: generate all functions of", module, "module")
    print("It takes a while to locate source, pls wait...")

    worksheet = workbook.add_worksheet(module)
    worksheet.write('A1', 'ID')
    worksheet.write('B1', 'Business Value')
    worksheet.write('C1', 'Summary')
    worksheet.write('D1', 'Status')
    worksheet.write('E1', 'Assigned to')
    worksheet.write('F1', 'Description')
    worksheet.write('G1', 'KieuDuLieu')
    worksheet.write('H1', 'TenFile')

    row = 2
    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), module, format[0])
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)
    worksheet.write('F' + str(row), '')
    worksheet.write('G' + str(row), '')
    worksheet.write('H' + str(row), '')
    row += 1

    for file in os.listdir(source_dir):
        if file.endswith(".nocomment.c"):
            row = export_data_for_c_file("src/" + file, row, 0, worksheet)

    for file in os.listdir(header_dir):
        if file.endswith(".h"):
            row = export_data_for_h_file("include/" + file, row, 0, worksheet)

    
    print("STEP 1 completed")

    print("Data exported to", "LLD/" + module + '-lld' + '.xlsx')
    return 0


#####################################################################################################################
if __name__ == "__main__":

    if not os.path.exists("LLD"):
        os.makedirs("LLD")
    workbook = xlsxwriter.Workbook("LLD/" + module + '-lld' + '.xlsx')

    format = []
    for i in range(8):
        ft = workbook.add_format()
        ft.set_indent(i)
        format.append(ft)

    data_txt = {}
    enum_txt = {}
    signal_txt = {}
    operation_txt = {}
    data_member_txt = {}
    operation_param_txt = {}

    stats_by_component = {}
    stats_by_method = {}

    main()
    workbook.close()

