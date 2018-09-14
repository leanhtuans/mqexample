#!/usr/bin/python3
# Buu Tran March 24, 2017, generate LLD from source code
# STEP 1: generate data structures, enum and external signals for module
# -->we do NOT generate constants for module here, only generate constants in internal modules
# -->for enum, we do generate enum for module, but do NOT for internal modules
# STEP 2: generate data structures, constants, internal signals and operations for internal modules
# Only In signal!!!
# Scripts works fine with Rose RT code, but may miss something in free-style user code

import os
import os.path
import sys
import xlsxwriter
#import re

if not os.path.isfile("vcp20/src/RTSystem/vcp.cpp"):
    print("Run the script only from vcp20-master folder!")
    exit(0)

if len(sys.argv) < 2:
    print("Missing argument: module name is required")
    print("Example: ../../tools/lldgen.py logmgr tuan1.le")
    exit(0)

module = sys.argv[1]

if len(sys.argv) == 3:
    pic = sys.argv[2]
else:
    pic = "tuan1.le"

signal_count = 0
neversent_signal_count = 0
#neverhandled_signal_count = 0
include_orphan_signal = False

if len(sys.argv) == 4 and "orphan" == sys.argv[3]:
    include_orphan_signal = True
if len(sys.argv) == 5 and "orphan" == sys.argv[4]:
    include_orphan_signal = True

def correct_module_name(name):
    # correct the module name
    if name.lower().startswith("obn"):
        name = "OBN" + name[3:]
    else:
        if name.lower().startswith("bt"):
            name = "BT" + name[2:]
        else:
            if "ecallapp" == name.lower():
                name = "ECallApp"
            else:
                if "odimgr" == name.lower():
                    name = "ODIMgr"
                else:
                    if name.lower() == "usl":
                        name = "USLMgr"
                    else:
                        if name.lower().startswith("sms"):
                            name = "SMS" + name[3:]
                        else:
                            if name.lower().startswith("rvs"):
                                name = "RVS" + name[3:]
                            else:
                                if name.lower().startswith("ui"):
                                    name = "UI" + name[2:]
                                else:
                                    if name.lower().startswith("onstar"):
                                        name = "OnStar" + name[6:]
                                    else:
                                        if name.lower().startswith("occreq"):
                                            name = "OCCReq" + name[6:]
                                        else:
                                            if name.lower().startswith("hwio"):
                                                name = "HWIO" + name[4:]
                                            else:
                                                if name.lower().startswith("locmask"):
                                                    name = "LocMask" + name[7:]
                                                else:
                                                    if not name.lower().startswith("vtim"):
                                                        name = name.title()
    name = name.replace("app", "App")
    name = name.replace("mgr", "Mgr")

    if "AppMgr" == name:
        name = "AppMgrVcp"
    if "AudioMgr" == name:
        name = "AudioMgrVCP"
    if "BillMgr" == name:
        name = "billMgrVcp"
    if "uslmgr" == name.lower():
        name = "USLMgrVcp"
    if "adaapp" == name.lower():
        name = "ADAApp"
    if "omaapp" == name.lower():
        name = "OMAApp"
    if "scruiseapp" == name.lower():
        name = "SCruiseApp"
    if "vtimapp" == name.lower():
        name = "vtimApp"
    if "calibifmgr" == name.lower():
        name = "CalibIfMgr"
    if "diagifmgr" == name.lower():
        name = "DiagIfMgr"
    if "dtcmgr" == name.lower():
        name = "DTCMgr"
    if "vifmgr" == name.lower():
        name = "VIFMgr"
    return name

def real_code(line, checksemicolon = True):
    line = remove_comment(line)
    line = line.strip(' \t\n\r')
    #if line.startswith("//") or not line:
    if not line:
        return 0
    if checksemicolon and not line.endswith(";"):
        return 0
    return 1
###
def remove_comment(line):
    parts = line.split("//", 1)
    return parts[0]
###
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

###extract enum and write to worksheet
def write_enum(worksheetEnum, row, f, n):
    global enum_txt

    with open(f, 'r', errors="ignore") as file:
        lines = file.readlines()
        # extract enum declaration
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            lines[i] = remove_comment(lines[i])
            name = ""
            if lines[i].startswith("enum ") or lines[i].startswith("enum{") or lines[i].startswith("typedef enum"):

                #if "AnalysisCmdC" in f:
                #    print(lines[i])

                enum_decl = ""
                while i in range(len(lines)):
                    if real_code(lines[i], False):
                        enum_decl += lines[i]
                    if lines[i].rstrip().endswith(";"):
                        break
                    i += 1

                #if "AnalysisCmdC" in f:
                #    print(enum_decl)

                if not enum_decl:
                    continue
                #if "IOnStarControlListE" in enum_decl:
                 #   print(enum_decl)
                parts = enum_decl.split("{")
                if len(parts) != 2:
                    continue
                name = parts[0]
                name = name.replace('enum', '')
                name = name.replace('typedef', '')
                name = name.strip()

                #if "AnalysisCmdC" in f:
                #    print(name)

                parts = parts[1].split("}")
                if len(parts) != 2:
                    continue
                if not name:
                    name = parts[1]
                    name = name.replace('enum', '')
                    name = name.replace('typedef', '')
                    name = name.replace(';', '')
                    name = name.strip()

                #if "AnalysisCmdC" in f:
                #    print(name)

                if not name:
                    name = "Constants"
                #print(name)
                enum_parts = parts[0].split(',')

                #if "AnalysisCmdC" in f:
                #    print(enum_parts)

                worksheetEnum.write('B' + str(row), 'Should have')
                worksheetEnum.write('C' + str(row), name, format[n+3])
                worksheetEnum.write('D' + str(row), 'New')
                worksheetEnum.write('E' + str(row), pic)

                #print(enum_txt[name])
                if name not in enum_txt:
                    enum_txt[name] = "This is an enum for ..."
                #print(name)
                #print(enum_txt[name])

                desc = "__Description__\n\n" + enum_txt[name] + "\n\n__Syntax__\n\n" + "[{ColorCode syntax=\'c\'\n\n"
                desc += enum_decl
                desc += "}]\n\n__Enumeration__\n\n[{Table\n\n||%%(color:#000000;)Name%!\n||%%(color:#000000;)Description%!\n\n"
                for line in enum_parts:
                    line = line.strip()
                    line = line.strip(',')
                    parts = line.strip().split(" = ")
                    if not line or len(parts) > 2:
                        continue
                    desc += "|" + parts[0] + "\n"

                    if name + "::" + parts[0] not in enum_txt:
                        enum_txt[name + "::" + parts[0]] = " "
                    desc += "|" + enum_txt[name + "::" + parts[0]] + "\n\n"
                desc += "}]\n"
                worksheetEnum.write('F' + str(row), desc)
                row += 1
    return row

def get_signal_source_external(signal, destination_module):
    sources  = ""
    for f in os.listdir("vcp20/src"):
        if not f.endswith("C.nocomment.cpp") or not os.path.isfile("vcp20/src/" + f):
            continue
        if "scruise" in f.lower():
            continue
        with open("vcp20/src/" + f, 'r', errors="ignore") as file:
            first_line = file.readline().lower()

            if0 = False
            for line in file:
                if line.startswith("#if 0"):
                    if0 = True
                    continue

                if if0 and line.startswith("#endif"):
                    if0 = False
                    continue

                if if0:
                    continue

                if "." + signal + "(" in line:
                    parts = first_line.split("::applayer::")
                    if len(parts) == 1:
                        parts = first_line.split("::midlayer::")
                    parts = parts[1].split("::", 1)
                    #print(correct_module_name(parts[0]))
                    name = correct_module_name(parts[0])
                    if destination_module.lower() != name.lower() and not name in sources:
                        if sources:
                            sources += "\n"
                        sources += name
                    break

    return sources

def get_signal_source_internal(signal, destination_capsule, capsules):
    sources  = ""
    for capsule in capsules:
        if capsule == destination_capsule:
            continue
        f = "vcp20/src/" + capsule + ".nocomment.cpp"
        if not os.path.isfile(f):
            continue
        with open(f, 'r', errors="ignore") as file:
            if0 = False
            for line in file:
                if line.startswith("#if 0"):
                    if0 = True
                    continue

                if if0 and line.startswith("#endif"):
                    if0 = False
                    continue

                if if0:
                    continue

                if "." + signal + "(" in line and not line.lstrip().startswith("//"):
                    if not capsule in sources:
                        if sources:
                            sources += "\n"
                        sources += capsule
                    break

    # if "AnalysisCmdC" == destination_capsule:  #
    #     print(destination_capsule, signal, "sources:", sources)  #
    return sources

def get_mapped_functions(signal, capsules): #, external=True
    #print(signal)
    functions = ""
    for capsule in capsules:
        with open("vcp20/src/" + capsule + ".cpp", 'r', errors="ignore") as file:
            #print("vcp20/src/" + capsule + ".cpp")
            lines = file.readlines()
            #if "chkPosValidReq" in signal:
             #   print("case " + signal)
            for i in range(len(lines)):
                # if "chkPosValidReq" in lines[i]:
                #     print(capsule)
                #     print(lines[i-1])
                #     print(lines[i])
                if lines[i].strip().startswith("case " + signal):
                    #print(signal)
                    #if external:
                    j = i -1
                    while j:
                        if "{\n" != lines[j]:
                            j -= 1
                            continue
                        #print(lines[j-1])
                        #print(lines[j])
                        if lines[j-1].startswith("INLINE_METHODS "):
                            parts = lines[j-1].split("::transition", 1)
                            if len(parts) != 2:
                                break
                            parts = parts[1].split("_", 1)
                            parts = parts[1].split("(", 1)
                            if parts[0] not in functions:
                                if functions:
                                    #functions += "\n"
                                    functions += "\\"  # force line break?
                                functions += parts[0]
                            i = len(lines)
                        break
                    #print("functions", functions)
                    # else:#internal signal, not tested yet
                    #     # if next line is chain
                    #     if lines[i+1].lstrip().startswith("chain") and lines[i+1].endswith(");\n"):
                    #         parts = lines[i+1].split("_", 1)
                    #         parts = parts[1].split("(", 1)
                    #         if parts[0] not in functions:
                    #             if functions:
                    #                 #functions += ", "
                    #                 functions += "\\"  # force line break?
                    #             functions += parts[0]
                    #         break
    # if "startOBNReq" in signal:
    #     print(functions)
    return functions

def export_signal(p, type, worksheetSig, row, dst, capsules, formatH, formatC, external=True):
    #in the case of external signal, dst must be module, otherwise capsule
    global signal_txt
    signals = []
    data = []
    source = []
    resp = []
    function = []
    out_signals = [] #used to find resp
    global signal_count
    global neversent_signal_count
    #global neverhandled_signal_count

    f = "vcp20/src/" + p + ".h"
    with open(f, 'r', errors="ignore") as file:
        lines = file.readlines()
        start = 0
        for line in lines:
            if "sysinfo" in line.lower():
                continue
            #if "\tclass " + type + " : public RTRootProtocol\n" == line: #this does not work for derived protocols
            if line.startswith("\tclass " + type + " : public "):
                start = 1
            else:
                if not start:
                    continue
            if line.startswith("\t\tinline RTInSignal "):
                parts = line.split("RTInSignal ", 1)
                parts = parts[1].split("(", 1)
                signals.append(parts[0])
                # search all cpp file to find potential source of this signal
                #buuth slow function, comment it for testing
                if external:
                    source.append(get_signal_source_external(parts[0], dst))
                else:
                    source.append(get_signal_source_internal(parts[0], dst, capsules))

                #if "AnalysisCmdC" == dst and source:#
                #    print(dst, parts[0], "sources:", source)#
                # search mapped functions
                function.append(get_mapped_functions(p + "::" + type + "::rti_" + parts[0], capsules))
                # signal data
                #print(parts[1])
                parts = parts[1].split(")")
                data.append(parts[0].strip().replace("RTTypedValue_", ""))
            if line.startswith("\t\tinline RTOutSignal "):
                parts = line.split("RTOutSignal ", 1)
                parts = parts[1].split("(", 1)
                out_signals.append(parts[0])

            if "\t};\n" == line and signals:
                break
        #if "LogOdiCmdP" == p:
         #   print(out_signals)
        # check if resp exist and fill resp
        for signal in signals:
            resp_clue = signal.replace("Req", "Resp").lower()
            found_resp = False
            for out_signal in out_signals:
                if out_signal.lower().endswith(resp_clue):
                    found_resp = True
                    resp.append(out_signal)
                    break
            if not found_resp:
                resp.append("")
        # if "ThreeBtnIfP" == p:
        #     print("Dst:", dst)
        #     print("ThreeBtnIfP, type:", type)
        #     print(signals)
        #     print("out signals", out_signals)
        #     print(data)
        #     print(source)
        #     print(function)
        #     print("resp:", resp)
    if not signals:
        return row

    if external:
        print("External protocol", p)
    else:
        print("Internal protocol", p)
    source_items = []
    for i in range(len(source)):
        #ignore if no mapped functions
        if not function[i]:
            continue
        parts = source[i].split("\n")
        for part in parts:
            if not part.strip() in source_items and part.strip():
                source_items.append(part.strip())

    best_item = ""
    if not source_items:
        return row
    if not ''.join(function):
        return row

    for item in source_items:
        exist_in_all_source = True
        for i in range(len(source)):
            if function[i] and not item in source[i]:
                exist_in_all_source = False
                break
        if exist_in_all_source:
            best_item = item
            break

    # if "LogNadRptP" == p:
    #     print(source_items)
    #     print("Best source:", best_item)

    worksheetSig.write('B' + str(row), 'Should have')
    if best_item:
        worksheetSig.write('C' + str(row), p + " (" + best_item + " to " + dst + ")", formatH)
    else:
        if len(source_items) == 1:
            worksheetSig.write('C' + str(row), p + " (" + source_items[0] + " to " + dst + ")", formatH)
        else:
            worksheetSig.write('C' + str(row), p, formatH)
    #worksheetSig.write('C' + str(row), p, formatH)
    worksheetSig.write('D' + str(row), 'New')
    worksheetSig.write('E' + str(row), pic)
    worksheetSig.write('F' + str(row), '')
    row += 1
    for i in range(len(signals)):
        #signal_count += 1
        # ignore if no mapped functions
        if not function[i]:
            #neverhandled_signal_count += 1
            continue
        signal_count += 1
        if not source[i]:
            neversent_signal_count += 1
        if not include_orphan_signal and not source[i]:
            continue

        worksheetSig.write('B' + str(row), 'Should have')
        worksheetSig.write('C' + str(row), signals[i], formatC)
        worksheetSig.write('D' + str(row), 'New')
        worksheetSig.write('E' + str(row), pic)
        desc = "[{Table\n\n||Signal Name\n|" + signals[i] + "\n\n||Parameter\n|" + data[i] + "\n\n||Source\n|"

        if p + "::" + signals[i] not in signal_txt:
            signal_txt[p + "::" + signals[i]] = " "
            if include_orphan_signal and not source[i]:
                signal_txt[p + "::" + signals[i]] = "orphan"

        if best_item:
            desc += best_item + "\n\n||Destination\n|" + dst + "\n\n||Description\n|" + signal_txt[p + "::" + signals[i]] + "\n\n||Response\n|"
        else:
            str_source = source[i].replace("\n", "\\\\")
            desc += str_source + "\n\n||Destination\n|" + dst + "\n\n||Description\n|" + signal_txt[p + "::" + signals[i]] + "\n\n||Response\n|"
        desc += resp[i] + "\n\n||Mapped Function\n|" + function[i].replace("\n", "\\\\") + "\n\n}]"
        worksheetSig.write('F' + str(row), desc)
        row += 1
    return row

def export_capsule_structures(syntax, members, worksheet, row, add_data_structures_row, n):
    global data_txt

    if add_data_structures_row:
        worksheet.write('B' + str(row), 'Should have')
        worksheet.write('C' + str(row), "Data Structures", format[n+2])
        worksheet.write('D' + str(row), 'New')
        worksheet.write('E' + str(row), pic)
        worksheet.write('F' + str(row), '')
        row += 1

    worksheet.write('B' + str(row), 'Should have')
    parts = syntax.split(":", 1)
    if len(parts) == 1:
        parts = syntax.split("{", 1)
    parts = parts[0].strip().rsplit(" ", 1)
    name = parts[1]
    #parts[1] : structure name


    worksheet.write('C' + str(row), name, format[n+3])
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)

    if name not in data_txt:
        if name.strip().endswith("_Actor"):
            data_txt[name] = " is an active class (capsule) for ..."
        else:
            data_txt[name] = " is a class/ structure for ..."

    desc = "__Description__\n\n" + name + data_txt[name] + "\n\n__Syntax__\n\n" + "[{ColorCode syntax=\'c\'\n\n"

    desc += syntax
    desc += "}]\n\n__Members__\n\n[{Table\n\n||%%(color:#000000;)Name%!\n||%%(color:#000000;)Type%!\n||%%(color:#000000;)Description%!\n\n"
    for line in members:
        line = line.strip().rstrip(";")
        line = line.replace("[ ", "[")
        line = line.replace(" ]", "]")
        line = line.replace("[ ", "[")
        line = line.replace(" ]", "]")
        line = line.split("=")[0].strip()
        brackets = ""
        if line.endswith("]"):
            result = remove_text_inside_brackets(line)
            #print(line)#
            #print(result)#
            line = result[0]
            if len(result) == 2:
                brackets = result[1]
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        if "CDebug" == parts[0]:
            continue
        #print(parts[0] + brackets)#
        #[] is not imported correctly by CodeBeamer
        #brackets = brackets.replace("[", "<").replace("]", ">")
        desc += "|" + parts[1] + "\n"
        if not brackets:
            desc += "|" + parts[0] + "\n"
        else:
            desc += "|[{ColorCode syntax=\'c\'\n\n" + parts[0] + brackets + "\n}]\n"
        if name + "::" + parts[1] not in data_member_txt:
            data_member_txt[name + "::" + parts[1]] = ""
        desc += "|" + data_member_txt[name + "::" + parts[1]] + " \n\n"


    desc += "}]\n"
    #print(desc)
    worksheet.write('F' + str(row), desc)
    row += 1

    return row

def export_operations(operation, worksheet, row, capsule, formatH, formatC):
    global operation_txt
    global stats_by_method
    global stats_by_component
    TESTMOD = "ARHandlerVcpC"#"ARReqHandlerC"
    # if TESTMOD == capsule:
    #     print(operation, capsule)
    namesearch = ""
    if " transition" in operation:
        parts = operation.split(" transition", 1)
        namesearch = parts[1][:-2]
        operation = operation.replace("INLINE_METHODS ", "")
        parts = operation.split("_", 1)
        pref = parts[0].split("transition")
        operation = pref[0] + parts[1]
        # if TESTMOD == capsule:
        #     print(namesearch, operation)

    parts = operation.split("(", 1)
    if len(parts) < 2:
        return row
    params = parts[1].split(")", 1)
    params = params[0].strip().split(",")
    if len(params) == 2 and params[0].rstrip().endswith("rtdata") and params[1].rstrip().endswith("rtport"):
        params = []
        #print(operation)
        #print(params)
        #del params[-1]
        #print(params)
    #print(params)
    parts = parts[0].strip().rsplit(" ", 1)
    if len(parts) < 2:
        return row
    name = parts[1]
    if not namesearch:
        namesearch = name
    if TESTMOD == capsule and "openARResp" == name:
        print(operation)

    # get operation code
    codes = ""
    tab_to_strip = 0
    with open("vcp20/src/" + capsule + ".cpp", 'r', errors="ignore") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if namesearch in lines[i] and i > 0:
                j = 1
                while lines[i-j].startswith("#define "):
                    j += 1
                if not lines[i - j].startswith("// {{{RME transition ") and not lines[i - 1].startswith("// {{{RME operation "):
                    continue
                start = False
                block_comment = False
                if0 = False
                while i in range(len(lines) - 1):
                    i += 1
                    if not start and "\t// {{{USR\n" == lines[i]:
                        start = True
                        # if TESTMOD == capsule and "openARResp" == name:
                        #     print("Start:", lines[i])

                    if "/*" in lines[i] and not lines[i].lstrip().startswith("//"):
                        block_comment = True

                    if lines[i].startswith("#if 0"):
                        if0 = True

                    if start and "\t// }}}USR\n" == lines[i]:
                        # if "FeatStateVcpC" == capsule and "Trigger" == name:
                        #     print("End:", lines[i], i, len(lines))
                        i = len(lines)
                        start = False
                        break

                    if block_comment and "*/" in lines[i] and not lines[i].lstrip().startswith("//"):
                        block_comment = False
                        continue

                    if if0 and lines[i].startswith("#endif"):
                        if0 = False
                        continue

                    if start and real_code(lines[i], False) and not block_comment and not if0:
                        if not codes:
                            tab_to_strip = len(lines[i]) - len(lines[i].lstrip("\t"))
                        #convert to pseudocode
                        strcode = remove_comment(lines[i][tab_to_strip:])
                        strcode = strcode.rstrip() + "\n"
                        #print(strcode)
                        if "LOGGER(" in strcode and strcode.rstrip().endswith(";"):
                            strcode = ""
                        if "TRACE(" in strcode and strcode.rstrip().endswith(";"):
                            # if "RespBT" == name:
                            #     print("Skip TRACE", strcode)
                            strcode = ""

                        if "CATTComm::SendPacketToATT" in strcode:
                            strcode = strcode.replace("CATTComm::SendPacketToATT", "SENDS PACKET TO ATT ")
                        if "CATTComm::SendComPacketToATT" in strcode:
                            strcode = strcode.replace("CATTComm::SendComPacketToATT", "SENDS COM PACKET TO ATT ")
                        if ").send();" in strcode:
                            str2 = strcode.replace(".send();", "")
                            parts = str2.rsplit(".", 1)
                            if len(parts) == 2:
                                if parts[1].rstrip().endswith("()"):
                                    parts[1] = parts[1].replace("()", "")
                                strcode = parts[0] + " SENDS SIGNAL " + parts[1]
                        else:
                            if " strstr(" in strcode or "(strstr(" in strcode:
                                parts = strcode.split("strstr(", 1)
                                strcode = parts[0] + parts[1].replace(",", " CONTAINS ", 1)
                                parts = strcode.split("CONTAINS")
                                parts = parts[1].split(")", 1)
                                if parts[1].lstrip().startswith("!= NULL"):
                                    strcode = strcode.replace("!= NULL", "", 1)
                                else:
                                    if parts[1].lstrip().startswith("== NULL"):
                                        strcode = strcode.replace("CONTAINS", "NOT CONTAINS")
                            else:
                                if strcode.lstrip().startswith("printf("):
                                    strcode = ""
                        if strcode.lstrip().startswith("if(") or strcode.lstrip().startswith("if ("):
                            strcode = strcode.replace("if", "IF ", 1)
                        # if strcode.rstrip().endswith(";"):
                        #     parts = strcode.rsplit(";", 1)
                        #     strcode = parts[0] + parts[1]
                        if "strncmp(" in strcode:
                            strcode = strcode.replace("strncmp", "DIFFERENCE BETWEEN STRINGS")
                        if "strcmp(" in strcode:
                            strcode = strcode.replace("strcmp", "DIFFERENCE BETWEEN STRINGS")
                        if "memcpy(" in strcode:
                            strcode = strcode.replace("memcpy", "COPY MEMORY BLOCK")
                        if "memcmp(" in strcode:
                            strcode = strcode.replace("memcmp", "DIFFERENCE BETWEEN MEMORY BLOCKS")
                        if "strcpy(" in strcode:
                            strcode = strcode.replace("strcpy", "COPY STRING")
                        if "strncpy(" in strcode:
                            strcode = strcode.replace("strncpy", "COPY STRING")
                        if "memset(" in strcode:
                            strcode = strcode.replace("memset", "RESET MEMORY BLOCK")
                        if "fopen(" in strcode:
                            strcode = strcode.replace("fopen", "OPEN FILE")
                        if "fprintf(" in strcode:
                            strcode = strcode.replace("fprintf", "WRITE TO FILE")
                        if "fclose(" in strcode:
                            strcode = strcode.replace("fclose", "CLOSE FILE")
                        if "snprintf(" in strcode:
                            strcode = strcode.replace("snprintf", "PRINT TO BUFFER")
                        #codes += lines[i][tab_to_strip:]
                        #print("After:" , strcode)
                        codes += strcode
                        # if "FeatStateVcpC" == capsule and "Trigger" == name:
                        #     print("Code line:", lines[i])
                if i == len(lines):
                    break

    if len(params) == 1 and params[0].rstrip().endswith("* rtdata") and not "rtdata" in codes:
        params = []
    # if TESTMOD == capsule and "openARResp" == name:
    #     print("Operation:", operation)
    #     print(codes)

    codes_no_logger = ""
    lines = codes.split("\n")
    to_skip = False
    for i in range(len(lines)):
        if "LOGGER(" in lines[i] and not lines[i].rstrip().endswith(";"):
            # if "AnalyseMifReq" == name:
            #     print("Skip line", lines[i])
            to_skip = True
            continue
        if "TRACE(" in lines[i] and not lines[i].rstrip().endswith(";"):
            # if "RespBT" == name:
            #     print("Skip TRACE line", lines[i])
            to_skip = True
            continue
        if to_skip and lines[i].rstrip().endswith(";"):
            to_skip = False
            # if "AnalyseMifReq" == name:
            #     print("Skip line", lines[i])
            continue
        if to_skip:
            # if "AnalyseMifReq" == name:
            #     print("Skip line", lines[i])
            continue
        #print(i)
        if lines[i].startswith("#ifdef ") and i < len(lines) - 2 and lines[i+1].startswith("#endif"):
            continue
        if lines[i].startswith("#endif") and i > 0 - 2 and lines[i-1].startswith("#ifdef "):
            continue
        if i < len(lines):
            #print("add line number", i, "code line:", lines[i])
            if lines[i].rstrip().endswith(";"):
                codes_no_logger += lines[i].rstrip()[:-1] + "\n"
            else:
                codes_no_logger += lines[i] + "\n"

    if not codes:
        return row
    #codes = " \n" + codes

    #statistic
    stats_by_method[capsule + "::" + name] = 0
    if capsule not in stats_by_component:
        stats_by_component[capsule] = 0
    for l in codes.split("\n"):
        if l.strip():
            stats_by_method[capsule + "::" + name] += 1
    stats_by_component[capsule] += stats_by_method[capsule + "::" + name]
        # if("factoryALDL" == name):
        #     print(l, stats_by_method[capsule + "::" + name])

    # if "startlogmode" == name:
    #     print("Operation Code:")
    #     print(codes)
    #     print("Codes without logger:", codes_no_logger)

    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), name, formatH)
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)

    if capsule + "::" + name not in operation_txt:
        operation_txt[capsule + "::" + name] = "This is an operation for ..."

    desc = "__Description__\n\n" + operation_txt[capsule + "::" + name] + "\n\n__Syntax__\n\n" + "[{ColorCode syntax=\'c\'\n\n"
    desc += operation
    desc += "}]\n\n__Parameters__\n\n[{Table\n\n||%%(color:#000000;)Name%!\n||%%(color:#000000;)Type%!\n||%%(color:#000000;)Description%!\n\n"
    for line in params:
        line = line.replace("[ ", "[")
        line = line.replace(" ]", "]")
        line = line.replace("[ ", "[")
        line = line.replace(" ]", "]")
        line = line.split("=")[0].strip()
        brackets = ""
        if line.endswith("]"):
            result = remove_text_inside_brackets(line)
            # print(line)#
            # print(result)#
            line = result[0]
            if len(result) == 2:
                brackets = result[1]
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        if "CDebug" == parts[0]:
            continue
        # print(parts[0] + brackets)#
        # [] is not imported correctly by CodeBeamer
        # brackets = brackets.replace("[", "<").replace("]", ">")
        desc += "|" + parts[1] + "\n"
        if not brackets:
            desc += "|" + parts[0] + "\n"
        else:
            desc += "|[{ColorCode syntax=\'c\'\n\n" + parts[0] + brackets + "\n}]\n"
        if capsule + "::" + name + "::" + parts[1] not in operation_param_txt:
            operation_param_txt[capsule + "::" + name + "::" + parts[1]] = ""
        desc += "|" + operation_param_txt[capsule + "::" + name + "::" + parts[1]] + " \n\n"

    desc += "}]\n\n"
    desc += "__Return Value__\n\n \n"
    desc += "__Errors__\n\n \n"
    desc += "__Notes__\n\n \n"
    worksheet.write('F' + str(row), desc)
    row += 1

    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), name + " - Detail Logic", formatC)
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)
    desc = "__Pseudocode__\n\n" + "[{ColorCode syntax=\'c\'\n\n"
    #desc += codes
    desc += codes_no_logger
    desc += "}]\n\n"

    desc += "__Diagram__\n\n \n"
    # desc += "[{ VerticalGraph title=\'Class Hierarchy\'\n\n"
    # desc += "(BaseDao[Each Dao must extend this][:color:red]\n"
    # desc += "\t(EntityDao[Persists entities][:color:#009900][:background:#DDFFDD]\n"
    # desc += "\t\t(ArtifactDao[:color:#3C78B5][:background:#D8E4F1]\n"
    # desc += "\t\t\t(Documents[:color:#777777][:background:#DDDDDD])\n"
    # desc += "\t\t\t(Wiki pages[:color:#777777][:background:#DDDDDD])\n"
    # desc += "\t\t)\n"
    # desc += "\t\t(ProjectDao[:color:#3C78B5][:background:#D8E4F1])\n"
    # desc += "\t\t(UserDao[:color:#3C78B5][:background:#D8E4F1])\n"
    # desc += "\t)\n"
    # desc += "\t(TemporalDao[Persists timestamped entities][:color:#009900][:background:#DDFFDD]\n"
    # desc += "\t\t(ArtifactSample[:color:#3C78B5][:background:#D8E4F1])\n"
    # desc += "\t\t(IssueSample[:color:#3C78B5][:background:#D8E4F1])\n"
    # desc += "\t)\n"
    # desc += ")\n"
    # desc += "}]\n"
    #print(name)
    #print(desc)
    worksheet.write('F' + str(row), desc)
    row += 1

    return row

def export_data_for_capsule(capsule, capsules, row, n=1, worksheet=None, data_structs = None):
    #n is level, if main capsule, it's 0; indent will be n + 1
    #if capsule is not in capsules, it's some user-defined non-capsule class
    constants = []  # search cpp file too
    operations = []
    if capsules and capsule in capsules:
        is_active_class = True
    else:
        is_active_class = False

    #data structures
    with open("vcp20/src/" + capsule + ".h", 'r', errors="ignore") as file:
        start = False
        members = []
        prev_line = ""
        syntax = ""

        #print("Add worksheet", capsule)
        if not worksheet:
            row = 1
            worksheet = workbook.add_worksheet(capsule)
            worksheet.write('A' + str(row), 'ID')
            worksheet.write('B' + str(row), 'Business Value')
            worksheet.write('C' + str(row), 'Summary')
            worksheet.write('D' + str(row), 'Status')
            worksheet.write('E' + str(row), 'Assigned to')
            worksheet.write('F' + str(row), 'Description')
            row += 1
        #print(row)

        worksheet.write('C' + str(row), capsule, format[n+1])
        worksheet.write('B' + str(row), 'Should have')
        worksheet.write('D' + str(row), 'New')
        worksheet.write('E' + str(row), pic)
        worksheet.write('F' + str(row), '')
        row += 1

        add_data_structures_row = True

        #for line in file:
        lines = file.readlines()
        for i in range(len(lines)):
            line = remove_comment(lines[i]).rstrip(" ")
            if i > 0:
                prev_line = lines[i-1]
            if not start and line.startswith("class ") and (" : " in line or not is_active_class) and not line.rstrip().endswith(";"):
                start = True
            if not start and not line.rstrip().endswith(";"):
                if line.startswith("struct ") or line.startswith("typedef struct "):
                    if not line.startswith("struct RTTypedValue_"):
                        start = True
            if not start:
                #prev_line = line
                continue
            if start and line.startswith("}"):
                start = False
                syntax += line
                #export here
                #print(syntax)
                row = export_capsule_structures(syntax, members, worksheet, row, add_data_structures_row, n)
                add_data_structures_row = False
                # if "ODIMgrC" == capsule:
                #     print(capsule)
                #     print(syntax, "\n")
                #     print("Members:")
                #     print(members, "\n")
                #     print("Operations:")
                #     print(operations, "\n")
                #     print("constants:")
                #     print(constants, "\n")
                #     print("\n\n")
                #print(data_txt)

                #reset everything
                members = []
                syntax = ""

                #prev_line = line
                continue

            if real_code(line, False):
                if "RTActor_class " in line or "RTStateId " in line or "RTPortDescriptor " in line:
                    #prev_line = line
                    continue
                if "// {{{RME port" in prev_line:
                    #ignore ports
                    #prev_line = line
                    continue
                # if "// {{{RME transition" in prev_line:
                #     #prev_line = line
                #     if "transition" in line and "(" in line:
                #         line = line.replace("INLINE_METHODS ", "")
                #         parts = line.split("_", 1)
                #         pref = parts[0].split("transition")
                #         line = pref[0] + parts[1]
                #         operations.append(line)
                #     continue
                if "// {{{RME operation" in prev_line:
                    #if "AnalysisCmdC" == capsule:
                     #   print(line)
                    if "(" in line and not "void unexpectedMessage(" in line:
                        if not line.endswith(";\n"):
                            operation = ""
                            while i in range(len(lines)):
                                l = remove_comment(lines[i])
                                if real_code(l):
                                    operation += l
                                if l.rstrip().endswith(";"):
                                    break
                                i += 1
                        else:
                            # if "transition" in line:
                            #     line = line.replace("INLINE_METHODS ", "")
                            #     parts = line.split("_", 1)
                            #     pref = parts[0].split("transition")
                            #     line = pref[0] + parts[1]
                            if "scruise" not in line.lower() and "sysinfo" not in line.lower():
                                #print(line)
                                operations.append(line)
                    #prev_line = line
                    continue
                if "// {{{RME transition " in prev_line and "guard" not in line:
                    if not "_Initial(" in line and real_code(line):
                        # if "transition" in line:
                        #     line = line.replace("INLINE_METHODS ", "")
                        #     parts = line.split("_", 1)
                        #     pref = parts[0].split("transition")
                        #     line = pref[0] + parts[1]
                        if "scruise" not in line.lower() and "sysinfo" not in line.lower():
                            #print(line)
                            operations.append(line)


                if "(" in line and ")" in line:
                    #prev_line = line
                    continue
                if line.strip().endswith(":") and line.strip().startswith("p"):
                    #prev_line = line
                    continue
                if line.strip().startswith("#define") and line.strip() != "#define SUPER RTActor":
                    constants.append(line.lstrip())
                    #prev_line = line
                    continue

                #
                if line.startswith("\tRTActorRef ") or line.startswith("\tstatic const RTComponentDescriptor "):
                    continue
                if "// {{{RME classAttribute" in prev_line:
                    members.append(line)
                if not ")" in line:
                    syntax += line
                    if line.strip().endswith(";") and not "}" in line and line not in members:
                        members.append(line)

    #external data structure
    if data_structs:
        for data_struct in data_structs:
            row = export_data_for_capsule(data_struct, None, row, 2, worksheet)

    #Enumerations
    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), 'Enumerations', format[n+2])
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)
    worksheet.write('F' + str(row), '')
    row += 1

    row = write_enum(worksheet, row, "vcp20/src/" + capsule + ".h", n)
    row = write_enum(worksheet, row, "vcp20/src/" + capsule + ".cpp", n)
    with open("vcp20/src/" + capsule + ".cpp", 'r', errors="ignore") as file:
        # update constants with those in .cpp file
        for line in file:
            if real_code(line, False) and line.strip().startswith("#define") and line.strip() != "#define SUPER RTActor":
                constants.append(line.lstrip())

    #Constants
    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), 'Constants', format[n+2])
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)
    #print(capsule)
    #if "AnalysisCmdC" == capsule:
    #    print(constants)
    str_constants = ""
    for constant in constants:
        if not str_constants:
            str_constants = "[{ColorCode syntax=\'c\'\n\n" + constant
        else:
            #str_constants += '\\\\' + constant
            str_constants += constant
    if str_constants:
        str_constants += "}]\n\n"
    #print(str_constants)
    worksheet.write('F' + str(row), str_constants)
    row += 1

    #print(capsule)

    if is_active_class: #only for capsules, not class/ struct
        #Signals
        base_list = []  # base ports protocol
        conjugate_list = []  # conjugate ports protocol
        with open("vcp20/src/" + capsule + ".cpp", 'r', errors="ignore") as file:
            # make base_list and conjugate_list
            for line in file:
                if "scruise" in line.lower():
                    continue
                if line.endswith("::Base::rt_class\n"):
                    parts = line.split('&')
                    if len(parts) != 2:
                        continue
                    parts = parts[1].split("::", 1)
                    if not parts[0] in base_list:
                        base_list.append(parts[0])
                if line.endswith("::Conjugate::rt_class\n"):
                    parts = line.split('&')
                    if len(parts) != 2:
                        continue
                    parts = parts[1].split("::", 1)
                    if not parts[0] in conjugate_list:
                        conjugate_list.append(parts[0])
                if line.startswith("static RTActor * new_"):
                    break
        # print(capsule)
        # print(base_list)
        # print(conjugate_list)

        if base_list or conjugate_list:
            worksheet.write('B' + str(row), 'Should have')
            worksheet.write('C' + str(row), 'Signals', format[n+2])
            worksheet.write('D' + str(row), 'New')
            worksheet.write('E' + str(row), pic)
            worksheet.write('F' + str(row), '')
            row += 1

            for p in base_list:
                row = export_signal(p, "Base", worksheet, row, capsule, capsules, format[n+3], format[n+4], n)
            for p in conjugate_list:
                row = export_signal(p, "Conjugate", worksheet, row, capsule, capsules, format[n+3], format[n+4], n)

    #export operations
    #print(operations)
    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), 'Operations', format[n+2])
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)
    worksheet.write('F' + str(row), '')
    row += 1

    # if "ARHandlerVcpC" == capsule:
    #     print(capsule)
    #     print(operations)

    for operation in operations:
        row = export_operations(operation, worksheet, row, capsule, format[n+3], format[n+4])

    return row

def load_desc_txt():
    global data_txt
    global enum_txt
    global signal_txt
    global operation_txt
    global data_member_txt
    global operation_param_txt
    # load from module.data.txt
    if os.path.isfile("LLD/" + module + ".data.txt"):
        with open("LLD/" + module + ".data.txt", "r", errors="ignore") as file:
            for line in file:
                parts = line.split("\t\t\t|")
                if len(parts) != 2:
                    continue
                data_txt[parts[0]] = parts[1].rstrip("\n")
                #print(parts[0], data_txt[parts[0]])

    # load from enum.data.txt
    if os.path.isfile("LLD/" + module + ".enum.txt"):
        with open("LLD/" + module + ".enum.txt", "r", errors="ignore") as file:
            for line in file:
                parts = line.split("\t\t\t|")
                if len(parts) != 2:
                    continue
                enum_txt[parts[0]] = parts[1].rstrip("\n")
                #print(parts)

    # load from module.signal.txt
    if os.path.isfile("LLD/" + module + ".signal.txt"):
        with open("LLD/" + module + ".signal.txt", "r", errors="ignore") as file:
            for line in file:
                parts = line.split("\t\t\t|")
                if len(parts) != 2:
                    continue
                signal_txt[parts[0]] = parts[1].rstrip("\n")

    # load from module.operation.txt
    if os.path.isfile("LLD/" + module + ".operation.txt"):
        with open("LLD/" + module + ".operation.txt", "r", errors="ignore") as file:
            for line in file:
                parts = line.split("\t\t\t|")
                if len(parts) != 2:
                    continue
                operation_txt[parts[0]] = parts[1].rstrip("\n")

    # load from module.data.member.txt
    if os.path.isfile("LLD/" + module + ".data.member.txt"):
        with open("LLD/" + module + ".data.member.txt", "r", errors="ignore") as file:
            for line in file:
                parts = line.split("\t\t\t|")
                if len(parts) != 2:
                    continue
                data_member_txt[parts[0]] = parts[1].rstrip("\n")

    # load from module.operation.param.txt
    if os.path.isfile("LLD/" + module + ".operation.param.txt"):
        with open("LLD/" + module + ".operation.param.txt", "r", errors="ignore") as file:
            for line in file:
                parts = line.split("\t\t\t|")
                if len(parts) != 2:
                    continue
                operation_param_txt[parts[0]] = parts[1].rstrip("\n")

    return

def write_desc_txt():
    # write data to module.data.txt
    file = open("LLD/" + module + ".data.txt", "w", errors="ignore")
    if file:
        for key, value in data_txt.items():
            line = key + "\t\t\t|" + value + "\n"
            #print(line)
            file.write(line)
        file.close()

    # write enum to module.enum.txt
    file = open("LLD/" + module + ".enum.txt", "w", errors="ignore")
    if file:
        for key, value in enum_txt.items():
            line = key + "\t\t\t|" + value + "\n"
            file.write(line)
            #print(line)
        file.close()

    # write signal to module.signal.txt
    file = open("LLD/" + module + ".signal.txt", "w", errors="ignore")
    if file:
        for key, value in signal_txt.items():
            line = key + "\t\t\t|" + value + "\n"
            file.write(line)
        file.close()

    # write operation to module.operation.txt
    file = open("LLD/" + module + ".operation.txt", "w", errors="ignore")
    if file:
        for key, value in operation_txt.items():
            line = key + "\t\t\t|" + value + "\n"
            file.write(line)
        file.close()

    # write data member to module.data.member.txt
    file = open("LLD/" + module + ".data.member.txt", "w", errors="ignore")
    if file:
        for key, value in data_member_txt.items():
            line = key + "\t\t\t|" + value + "\n"
            # print(line)
            file.write(line)
        file.close()

    # write operation parameter to module.operation.param.txt
    file = open("LLD/" + module + ".operation.param.txt", "w", errors="ignore")
    if file:
        for key, value in operation_param_txt.items():
            line = key + "\t\t\t|" + value + "\n"
            file.write(line)
        file.close()

    # write module statistics
    file_stats = open("LLD/" + module + ".stats.txt", 'w')
    if file_stats:
        file_stats.write("User code by component:\n\n")
        for key, value in stats_by_component.items():
            line = key + "\t\t\t" + str(value) + " lines\n"
            file_stats.write(line)
        file_stats.write("\n")
        file_stats.write("User code by operation:\n\n")
        for key, value in stats_by_method.items():
            line = key + "\t\t\t" + str(value) + " lines\n"
            file_stats.write(line)
        file_stats.close()
    return

def main():
    # module_signature = "::" + module.lower() + "::"
#    module_signature = "::" + module.lower()
#    if module_signature.endswith("vcp"):
#        module_signature = module_signature[:-3]
    # classes in the modules, include none-active, but not P.h and D.h
    internal_modules = []

    # structs/ classes in D.h files
    data_structure = []
    enum = []

    print("Preparing c files without comments...")
    for f in os.listdir("src"):
        if f.endswith(".c") and not "nocomment" in f:
            nocommentfile = f[:-3] + "nocomment" + ".c"
            if os.path.isfile("src/" + nocommentfile):
                continue
            print("gcc -fpreprocessed -dD -E " + "vcp20/src/" + f + " >> vcp20/src/" + nocommentfile)
            os.system("gcc -fpreprocessed -dD -E " + "vcp20/src/" + f + " >> vcp20/src/" + nocommentfile)
#            file = open("vcp20/src/" + f, 'r', errors="ignore")
#            first_line = file.readline()
#            file.close()
#            file = open("vcp20/src/" + nocommentfile, 'r+', errors="ignore")
#            file.write(first_line)
#            file.close()

    load_desc_txt()
    print("STEP 1: generate data structures, enum and input signals for", module, "module")
    print("It takes a while to locate source of signals, pls wait...")

    for f in os.listdir("src"):
        if f.endswith(".h"):
            with open("src/" + f, 'r', errors="ignore") as file:
                first_line = file.readline().lower()
                if not module_signature in first_line:
                    continue
                # not generate protocol data yet
#                if f.endswith("P.h"):
                    #check if it's protocol
#                    is_protocol = False
#                    for i in range(30):
#                        line = file.readline()
#                        if not line:
#                            break
#                        if "public RTRootProtocol" in line:
#                            is_protocol = True
#                            break
#                    if is_protocol:
#                        continue
                # search for data outside
                lines = file.readlines()
                for line in lines:
                    if not real_code(line):
                        continue
                    parts = line.strip().split(" ")
                    # we extract only if actual data used. If class/ structure declared, but not use anywhere in module, just ignore it
                    if len(parts) == 2 and parts[0].endswith("D") and not parts[0] in data_structure:
                        data_structure.append(parts[0])
                        # print(line)
                if f.endswith("D.h"):
                    # parts = f.split(".")
                    # data_structure.append(parts[0])
                    continue
                # print(f)
                internal_modules.append(f)

        if f.endswith(".cpp"):
            with open("vcp20/src/" + f, 'r', errors="ignore") as file:
                first_line = file.readline().lower()
                if not module_signature in first_line:
                    continue

                lines = file.readlines()
                for line in lines:
                    if not real_code(line):
                        continue
                    parts = line.strip().split("::")
                    if len(parts) == 2 and parts[0] != "TraceD" and not "(" in parts[0] and not "." in parts[
                        0] and not " " in parts[0] and not "\t" in parts[0] and parts[0].endswith("D") and not parts[
                        0] in data_structure:
                        data_structure.append(parts[0])

    # print("internal_modules ", internal_modules, "data_structure ", data_structure)
    # return 0

    capsules = []       # all capsules in the module
    child_capsules = [] # except main capsule
    main_capsule = module + "C"
    if "theftapp" == module.lower():
        main_capsule = "TheftAppC80F"
    if "callmgr" == module.lower():
        main_capsule = "CallManagerC"
    if "rilmgr" == module.lower():
        main_capsule = "RILReadHandlerC"

    f = "vcp20/src/" + main_capsule + ".cpp"
    if not os.path.isfile(f):
        f = "vcp20/src/" + module + "VcpC.cpp"
    if not os.path.isfile(f):
        f = "vcp20/src/" + module + "VCPC.cpp"
    if os.path.isfile(f):
        with open(f, 'r', errors="ignore") as file:
            lines = file.readlines()
            #change to support derived capsule
            for line in lines:
                if line.startswith("extern const RTActorClass "):
                    parts = line.rsplit(" ", 1)
                    parts[1] = parts[1].strip().rstrip(";")
                    capsules.append(parts[1])
                    #check if capsule is derived user capsule
                    fchild = "vcp20/src/" + parts[1] + ".h"
                    with open(fchild, 'r', errors="ignore") as file2:
                        lines2 = file2.readlines()
                        for j in range(len(lines2)):
                            if lines2[j].startswith("extern const RTActorClass "):
                                if lines2[j+3].endswith("_Actor\n"):
                                    parts = lines2[j+3].split(" : public ")
                                    parts = parts[1].rsplit("_Actor", 1)
                                    capsules.append(parts[0])
                                break
                if "\n" == line and capsules:
                    break
            child_capsules.extend(capsules)
            #print(child_capsules)  # this is list of child capsules
            capsules.append(main_capsule)
            #print(child_capsules)  # this is list of child capsules
            #print(capsules)  # this is list of all capsules

    worksheet = workbook.add_worksheet(module)
    worksheet.write('A1', 'ID')
    worksheet.write('B1', 'Business Value')
    worksheet.write('C1', 'Summary')
    worksheet.write('D1', 'Status')
    worksheet.write('E1', 'Assigned to')
    worksheet.write('F1', 'Description')

    row = 2
    worksheet.write('B' + str(row), 'Should have')
    worksheet.write('C' + str(row), module, format[0])
    worksheet.write('D' + str(row), 'New')
    worksheet.write('E' + str(row), pic)
    worksheet.write('F' + str(row), '')
    row += 1

    row = export_data_for_capsule(main_capsule, capsules, row, 0, worksheet, data_structure)
    print("STEP 1 completed")

    # OK COMMENTED FOR TESTING
    print("STEP 2: generate data structures, constants, internal signals and operations for internal modules")
    ###
    for capsule in child_capsules:
        if len(sys.argv) == 4 and "s" == sys.argv[3]:
            row = export_data_for_capsule(capsule, capsules, row, 1) #uncomment this and comment above line to generate child capsules data to separate worksheet
        else:
            row = export_data_for_capsule(capsule, capsules, row, 1, worksheet)

    for mod in internal_modules:
        if mod[:-2] in capsules:
            continue
        row = export_data_for_capsule(mod[:-2], capsules, row, 0, worksheet)

    print("Total number of signals of all protocols used in the module:", signal_count)
    print("Signals handled, but never being sent:", neversent_signal_count)
    #print("Signals not used in the module:", neverhandled_signal_count)
    #print(data_txt)
    write_desc_txt()
    print("Data exported to", "LLD/" + module + '-lld' + '.xlsx')
    return 0


#####################################################################################################################
if __name__ == "__main__":
    module = correct_module_name(module)

    if "--help" == sys.argv[1]:
        print("Run lldgen.py only from vcp20-master folder")
        print("Usage    : ./lldgen.py module pic s orphan")
        print("module   : module name (e.g. LogMgr)")
        print("pic      : person-in-charge, e.g. buuth")
        print("s        : export data for each capsule to separate worksheet")
        print("orphan   : include orphan signals (signals that are handled in the module, but nobody ever sends)\n")
        print("Example 1: ./lldgen.py LogMgr buuth s")
        print("Command above generate LLD for each LogMgr capsule in separate worksheet, orphan signals excluded\n")
        print("Example 2: ./lldgen.py LogMgr buuth")
        print("Command above generate LLD for LogMgr in one worksheet, orphan signals excluded\n")
        print("Example 3: ./lldgen.py LogMgr buuth orphan")
        print("Command above generate LLD for LogMgr in one worksheet, inlcude all orphan signals\n")
        exit(0)

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

