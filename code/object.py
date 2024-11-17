from sympy import symbols, Eq, cos, sin, solve, pi, sqrt


class Relation:
    def __init__(self, id, flag, Mf, rf, vf, expf, cost):
        self.id = id
        self.flag = flag
        self.Mf = Mf
        self.rf = rf
        self.vf = vf
        self.expf = expf
        self.cost = cost
        self.expf = self.parse_expf(expf)

    def parse_expf(self, expf):
        # Loại bỏ ký tự backtick và tạo phương trình sympy
        expf = expf.strip("`").strip()
        expf = expf.replace("^", "**")
        left, right = expf.split("=")

        variables = {str(var): var for var in self.Mf}

        if "Pi" in expf:
            variables.update({"Pi": pi})
        if "cos" in expf:
            variables.update({"cos": cos})
        if "sin" in expf:
            variables.update({"sin": sin})
        if "sqrt" in expf:
            variables.update({"sqrt": sqrt})

        left = eval(
            left.strip(), {}, variables
        )  # Biến đổi phần trái thành biểu thức sympy

        right = eval(
            right.strip(), {}, variables
        )  # Biến đổi phần phải thành biểu thức sympy

        # self.expf = Eq(left, right)
        return Eq(left, right)

    def print_relation(self):
        print(f"\nrelation: {self.id}")
        print(f"\tflag: {self.flag}")
        print(f"\tMf: {self.Mf}")
        print(f"\t\ttype: {type(self.Mf)}")
        # for mf in self.Mf:
        #     print(f"\t\t{mf} - {type(mf)}")
        print(f"\trf: {self.rf}")
        print(f"\tvf: {self.vf}")
        print(f"\texpf: {self.expf}")
        print(f"\t\ttype: {type(self.expf)}")

        print(f"\tcost: {self.cost}")


class Object:
    def __init__(self, name):
        self.name = name
        self.variables = {}
        self.relations = []

    def init_variables(self, line):
        # print("\tcurrent line: ", line)
        if ":" in line:
            left, right = line.split(":", 1)
            # print(f"\t\tleft: {left}")
            # print(f"\t\tright: {right}")

            left = symbols(left)
            definition = {left: right}
            self.variables.update(definition)
        elif "=" in line:
            left, right = line.split("=", 1)
            # print(f"\t\tleft: {left}")
            # print(f"\t\tright: {right}")

            left = symbols(left)
            definition = {left: right}
            self.variables.update(definition)

    def get_variables(self, output=False):
        if output:
            for var in self.variables:
                print(f"{var}: {self.variables[var]}")
        return self.variables

    def get_relations(self, output=False):
        if output:
            for rel in self.relations:
                rel.print_relation()
        return self.relations
