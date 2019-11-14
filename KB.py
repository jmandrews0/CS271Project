class Term:
    name = ""
    neg = False

    def __init__(self, name, neg = False):
        self.name = name
        self.neg = neg
        
    def __eq__(self, other):
        return self.name == other.name and self.neg == other.neg

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        string = ""
        if self.neg:
            string += "!"
        string += self.name
        return string

    def negate(self):
        self.neg = not self.neg

class Clause:
    neg = False
    c = set()

    def __init__(self, terms, neg = False):
        self.neg = neg
        self.c = set(terms)

    def __eq__(self, other):
        return other.c == self.c

    def __hash__(self):
        string = ""
        for t in self.c:
            string += t.name
        return hash(string)

    def __str__(self):
        string = "( "
        for term in self.c:
            string += str(term) + " "
        string += ")"
        return string

    def add(self, term):
        self.c.add(term)

    def negate(self):
        if len(self.c) == 1:
            for term in self.c:
                term.negate()
        else:
            self.neg = not self.neg


class KB:
    # a set of CNF clauses
    kb = set()

    def tell(self, clause):
        self.kb.add(clause)

    def ask(self, clause):
        # add the negation of the clause to the kb
        clauses = set([i for i in self.kb])
        clause.negate()
        clauses.add(clause)
        new = set()
        
        while True:
            print(len(clauses))
            for i in clauses:
                for j in clauses:
                    resolvent = self.resolve(i.c,j.c)
                    if len(resolvent) == 1:
                        if len(resolvent[0].c) == 0:
                            return True
                        else:
                            new.add(resolvent[0])
            if new.issubset(clauses):
                return False
            clauses = clauses.union(new)

    def resolve(self, c1, c2):
        count = 0
        n1 = set([i for i in c1])
        n2 = set([i for i in c2])
                  
        for t1 in c1:
            for t2 in c2:
                if t1.name == t2.name and t1.neg ^ t2.neg:
                    count += 1
                    n1.remove(t1)
                    n2.remove(t2)
        if count == 1:
            return [Clause(n1.union(n2))]
        else:
            return []

# --------------------------------TEST EXAMPLE---------------------------------------
if __name__ == "__main__":
    kb = KB()
    kb.tell(Clause([Term("A"), Term("B")]))
    kb.tell(Clause([Term("B",True), Term("C"), Term("D",True)]))
    kb.tell(Clause([Term("C"), Term("D")]))
    kb.tell(Clause([Term("A",True)]))

    print( kb.ask(Clause([Term("C")])) )
        
