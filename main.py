from sympy import *
import json
from object import Object, Relation


def ReadObjectw(filename):
    """
    - Read object from file
    @param filename: file name
    -> return object
    """
    with open(filename, "r") as file:
        lines = file.readlines()

    nameobject = None
    M = []
    F = []
    helpob = []
    i = 1
    f = []

    # Bỏ qua các dòng trống ban đầu
    lines = [line.strip() for line in lines if line.strip()]

    # for line in lines:
    #     print(f"line: {i}", line)
    #     i += 1

    if len(lines) == 0:
        print("File is empty")
        return None

    # Lấy tên đối tượng
    nameobject = lines[0]
    helpob.append(lines[0])
    ob = Object(nameobject)

    # Tìm các phần tử trong "variables"
    print("\n\n.............READING VARIABLES.............\n\n")
    i = 1
    while "variables" not in lines[i]:
        i += 1
    i += 1  # Skip "variables" line

    # Lấy các biến
    while "endvariables" not in lines[i]:
        ob.init_variables(lines[i])

        M.append(lines[i].split()[0])  # Phần tử đầu tiên là tên thuộc tính
        helpob.append(lines[i])
        i += 1

    # ob.get_variables(True)

    print("\n\n.............READING RELATIONS.............\n\n")

    # Xử lý phần còn lại
    i += 1  # Skip "endvariables" line
    current_rel = {}
    for line in lines[i:]:
        if "relation" in line:

            if current_rel:
                rel = Relation(**current_rel)
                # rel.print_relation()
                ob.relations.append(rel)  # Add relation to object

            current_rel = {}
            id = line.split()[1]
            current_rel["id"] = id
            current_rel["cost"] = 0
            i += 1
        elif "flag" in line:
            flag = int(line.split("=")[1])
            current_rel["flag"] = flag
            i += 1
        elif "Mf" in line:
            Mf = line.split("=")[-1].strip("{} ")
            symbols = Mf.strip().split(",")
            symbols = [Symbol(symbol.strip().replace(",", "")) for symbol in symbols]
            current_rel["Mf"] = symbols
            i += 1
        elif "rf" in line:
            rf = int(line.split("=")[-1].strip())
            current_rel["rf"] = rf
            i += 1
        elif "vf" in line:
            vf = line.split("=")[-1].strip("{} ")
            symbols = vf.strip().split(",")
            symbols = [Symbol(symbol.strip().replace(",", "")) for symbol in symbols]
            current_rel["vf"] = symbols
            i += 1
        elif "expf" in line:
            line = line.replace("`", "")
            # print(line)
            expf = line.split("=", 1)[1].strip("`")
            current_rel["expf"] = expf
            i += 1
        elif "cost" in line:
            cost = int(line.split("=")[-1].strip())
            current_rel["cost"] = cost

    if current_rel:
        rel = Relation(**current_rel)
        # rel.print_relation()
        ob.relations.append(rel)  # Add relation to object

    return ob


def Baodong(F, A):
    """
    - Find packs of elements that can be calculated from given elements
    @param F: set of relations
    @param A: set of given elements
    -> return set of elements that can be calculated from given elements
    """
    A1 = set([Symbol(a) for a in A])

    print("Input: ")
    for a in A1:
        print(f"\t{a}  type: {type(a)}")
    A2 = set()
    F1 = set(F.copy())
    used_relations = []
    get_ops = []

    while A1 != A2:
        A2 = A1.copy()
        ff = set()
        for f in F1:
            # print(f"relation: {f.id}")
            # if (f.flag == 0 and len(set(f.Mf) - set(A1) - set(f.vf)) == 0) or (
            #     f.flag == 1 and len(set(f.Mf) - set(A1)) <= f.rf
            # ):
            Mf = set(f.Mf)
            if Mf.issubset(A1) and len(Mf - A1 - set(f.vf)) == 0:
                continue
            if (len(Mf - A1) == 1) or (len(Mf - A1) <= f.rf):
                used_relations.append(f.id)
                old_A1 = A1.copy()
                A1 = A1.union(Mf)
                get_ops.append(A1 - old_A1)
                ff.add(f)
        F1 -= ff

    # remove lenght 0 symbols
    results = A1.copy()
    for a in A1:
        if len(str(a)) == 0:
            results.remove(a)

    print("\nUsed relations: new elements")
    for i in range(len(used_relations)):
        print(f"\t{used_relations[i]}: {get_ops[i]}")

    return results


def ApQuanhe(D, A, output=True):
    """
    - Apply relations D to set A
    @param D: set of relations
    @param A: set or list (auto convert to set) of elements
    @param output: print steps
    -> return Anew: set of elements after applying relations D to set A
    """
    for a in A:
        if type(a) != Symbol:
            a = Symbol(a)
    Anew = set(A)
    if output:
        print(f"\nApplying {[int(f.id) for f in D]}: on {A}, ", end="")
        print(f"\texpf: {[f.expf for f in D]}")
    for f in D:
        Mf = set(f.Mf)
        if Mf.issubset(Anew) and len(Mf - Anew - set(f.vf)) == 0:
            continue
        if (len(Mf - Anew) == 1) or (len(Mf - Anew) <= f.rf):
            old_A1 = Anew.copy()
            Anew = Anew.union(Mf)
    if output:
        print("get: ", Anew - set(A) if Anew != set(A) else "-")
    return Anew


def Solutionw(filename, start, end):
    """
    - Check if there is a solution for the problem
    @param filename: file name
    @param start: set of given elements
    @param end: set of wanted elements
    --> [True/False, list of relations used to solve the problem]
    """

    F = ReadObjectw(filename).relations
    sol = []
    Aold = set()
    start = set(Symbol(a) for a in start)
    sol_found = False
    end = set(Symbol(e) for e in end)
    old_start = start.copy()
    ops_at_step = []

    print(f"\n\n\tFINDING SOLUTION {end} FROM {start}\n\n")

    if end.issubset(start):
        return [True, []]
        sol_found = True

    while not sol_found and Aold != start:
        Aold = start.copy()
        start_copy = start.copy()
        for f in F:
            start = ApQuanhe([f], start)
            if start != Aold:
                sol.append(f)

                # start_copy is to find out what elements we get at each step
                ops_at_step.append(start - start_copy)
                start_copy = start.copy()

            if end.issubset(start):
                sol_found = True
                break

    print(start)

    if sol_found:
        # optimize solution
        final_rel = sol[-1]

        print("\n\nFinding optimizing solution ....")
        # filter out unused relations
        print("\n\nFiltering out used relations: ")
        needs = end.copy()
        had = old_start.copy()
        real_opt_sol = []

        while not (needs.issubset(had)):

            print(f"\tNeeds: {needs} - Had: {had}")
            for i in range(len(ops_at_step)):
                ops = ops_at_step[i]
                if ops == set():
                    continue
                if ops.issubset(needs):
                    print(f"\t    -Get {i+1}: {ops}")
                    rel_needs = set(sol[i].Mf).difference(had)
                    print(f"\t\tRel {i+1} needs: {rel_needs}")
                    if len(rel_needs) == 1:
                        had = had.union(rel_needs)
                        print("\t\t Get 1 more needs, add to had: ", had)
                        real_opt_sol.append(sol[i])
                    else:
                        needs = needs.union(rel_needs)
                    print(f"\t\t Add more to Needs: {needs}")
    if sol_found:
        return [True, real_opt_sol]
    else:
        return [False, []]


def Solve_(input_path):
    """
    - Solve the problem from input.json
    @param input_path: path to input.json
    -> return results (dict)
    """
    read_json = json.load(open(input_path, "r"))

    input = read_json["input"]
    output = set(read_json["output"])

    # find solutions for the problem
    relations = Solutionw("code/TAM_GIAC.txt", input, output)
    if not relations[0]:
        print("\n\nSolution not found")
        return
    print()
    for i in relations[1]:
        print(f"\tRelation id {i.id} - {i.Mf} - {i.expf}")

    # apply solution to get the result
    print("\n\n ....Calculating result....\n\n")
    print(f"input: {input}")
    print(f"output: {output}")

    variables = {}  # {var(symbols): value}
    packs = set()

    for key in input:
        variables[Symbol(key)] = input[key]
        packs.add(Symbol(key))
    print("variables: ", variables)
    print("packs: ", packs, "\n")

    for idx, rel in enumerate(relations[1]):
        found_element = set(rel.Mf).difference(packs)
        print(f"\n\tstep {idx+1}: packs = {packs} - found_elements = {found_element}")
        found_element_val = solve(rel.expf.subs(variables), found_element)
        if found_element_val[0] < 0:
            found_element_val[0] = abs(found_element_val[0])
        print(
            f"\t\trelation: {rel.expf} - result: {next(iter(found_element))}={found_element_val[0]}"
        )
        # add new elements to packs
        for element in found_element:
            packs.add(element)
        print("\t\tnew packs: ", packs)
        variables[list(found_element)[0]] = found_element_val[0]
        print("\t\tnew variables: ", variables)

    print("\n\nResult: ")
    for key in output:
        print(f"\t{key}: {variables[Symbol(key)]}")

    # return results dict
    answers = {}
    for key in output:
        answers[key] = variables[Symbol(key)]
    print("\nEnd Solve_")
    return answers


# CAll Solve_ function and solve the problem from input.json
Solve_("input.json")

print("\n\n\t\tEND")


"""test code, not in use"""
# tamgiac = ReadObjectw("code/TAM_GIAC.txt")

# # tamgiac.get_variables(True)
# tamgiac.get_relations(True)

# baodong = Baodong(tamgiac.relations, {"S", "r"})
# print("\n\nBao dong: ", baodong, " -> ", len(baodong))

# print("\tKet qua Ap quan he: ", ApQuanhe(tamgiac.relations[:15], {"r"}))

# solution = Solutionw("code/TAM_GIAC.txt", {"a", "b", "c"}, {"S", "r"})
# if solution[0]:
#     print("\n\nSolution found: ")
#     for i in solution[1]:
#         print(f"\t{i.id} - {i.Mf} - {i.expf}")
# else:
#     print("\n\nSolution not found")
