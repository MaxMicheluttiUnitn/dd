"""Common tests for `autoref`, `cudd`, `cudd_zdd`."""
from nose.tools import assert_raises


class Tests(object):
    DD = None  # `autoref.BDD` or `cudd.BDD` or
        # `cudd_zdd.ZDD`

    def test_true_false(self):
        bdd = self.DD()
        true = bdd.true
        false = bdd.false
        assert false != true
        assert false == ~ true
        assert false == false & true
        assert true == true | false

    def test_add_var(self):
        bdd = self.DD()
        bdd.add_var('x')
        bdd.add_var('y')
        assert set(bdd.vars) == {'x', 'y'}, bdd.vars
        x = bdd.var('x')
        y = bdd.var('y')
        assert x != y, (x, y)

    def test_var_cofactor(self):
        bdd = self.DD()
        bdd.add_var('x')
        x = bdd.var('x')
        values = dict(x=False)
        u = bdd.let(values, x)
        assert u == bdd.false, u
        values = dict(x=True)
        u = bdd.let(values, x)
        assert u == bdd.true, u

    def test_richcmp(self):
        bdd = self.DD()
        assert bdd == bdd
        other = self.DD()
        assert bdd != other

    def test_len(self):
        bdd = self.DD()
        u = bdd.true
        assert len(bdd) == 1, len(bdd)

    def test_contains(self):
        bdd = self.DD()
        true = bdd.true
        assert true in bdd
        bdd.add_var('x')
        x = bdd.var('x')
        assert x in bdd
        # undefined `__contains__`
        other_bdd = self.DD()
        other_true = other_bdd.true
        with assert_raises(AssertionError):
            other_true in bdd

    def test_str(self):
        bdd = self.DD()
        s = str(bdd)
        s + 'must be a string'

    def test_levels(self):
        bdd = self.DD()
        bdd.add_var('x')
        bdd.add_var('y')
        bdd.add_var('z')
        ix = bdd.level_of_var('x')
        iy = bdd.level_of_var('y')
        iz = bdd.level_of_var('z')
        # before any reordering, levels are unchanged
        assert ix == 0, ix
        assert iy == 1, iy
        assert iz == 2, iz
        x = bdd.var_at_level(0)
        y = bdd.var_at_level(1)
        z = bdd.var_at_level(2)
        assert x == 'x', x
        assert y == 'y', y
        assert z == 'z', z

    def test_compose(self):
        bdd = self.DD()
        for var in ['x', 'y', 'z']:
            bdd.add_var(var)
        u = bdd.add_expr('x /\ ~ y')
        # x |-> y
        sub = dict(x=bdd.var('y'))
        v = bdd.let(sub, u)
        v_ = bdd.false
        assert v == v_, len(v)
        # x |-> y, y |-> x
        sub = dict(x=bdd.var('y'),
                   y=bdd.var('x'))
        v = bdd.let(sub, u)
        v_ = bdd.add_expr('y /\ ~ x')
        assert v == v_, v
        # x |-> z
        sub = dict(x=bdd.var('z'))
        v = bdd.let(sub, u)
        v_ = bdd.add_expr('z /\ ~ y')
        assert v == v_, v
        # x |-> z, y |-> x
        sub = dict(x=bdd.var('z'),
                   y=bdd.var('x'))
        v = bdd.let(sub, u)
        v_ = bdd.add_expr('z /\ ~ x')
        assert v == v_, v
        # x |-> (y \/ z)
        sub = dict(x=bdd.add_expr('y \/ z'))
        v = bdd.let(sub, u)
        v_ = bdd.add_expr('(y \/ z) /\ ~ y')
        assert v == v_, v

    def test_cofactor(self):
        bdd = self.DD()
        for var in ['x', 'y']:
            bdd.add_var(var)
        x = bdd.var('x')
        y = bdd.var('y')
        # x /\ y
        u = bdd.apply('and', x, y)
        r = bdd.let(dict(x=False, y=False), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=True, y=False), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=False, y=True), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=True, y=True), u)
        assert r == bdd.true, r
        # x /\ ~ y
        not_y = bdd.apply('not', y)
        u = bdd.apply('and', x, not_y)
        r = bdd.let(dict(x=False, y=False), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=True, y=False), u)
        assert r == bdd.true, r
        r = bdd.let(dict(x=False, y=True), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=True, y=True), u)
        assert r == bdd.false, r
        # ~ x \/ y
        not_x = bdd.apply('not', x)
        u = bdd.apply('or', not_x, y)
        r = bdd.let(dict(x=False, y=False), u)
        assert r == bdd.true, r
        r = bdd.let(dict(x=True, y=False), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=False, y=True), u)
        assert r == bdd.true, r
        r = bdd.let(dict(x=True, y=True), u)
        assert r == bdd.true, r

    def test_count(self):
        b = self.DD()
        b.add_var('x')
        u = b.add_expr('x')
        with assert_raises(AssertionError):
            b.count(u, 0)
        n = b.count(u, 1)
        assert n == 1, n
        n = b.count(u, 2)
        assert n == 2, n
        n = b.count(u, 3)
        assert n == 4, n
        b.add_var('y')
        u = b.add_expr('x /\ y')
        with assert_raises(AssertionError):
            b.count(u, 0)
        with assert_raises(AssertionError):
            b.count(u, 1)
        n = b.count(u, 2)
        assert n == 1, n
        n = b.count(u, 3)
        assert n == 2, n
        n = b.count(u, 5)
        assert n == 8, n

    def test_pick_iter(self):
        b = self.DD()
        b.add_var('x')
        b.add_var('y')
        # x /\ y
        s = '~ x /\ y'
        u = b.add_expr(s)
        g = b.pick_iter(u, care_vars=set())
        m = list(g)
        m_ = [dict(x=False, y=True)]
        assert m == m_, (m, m_)
        u = b.add_expr(s)
        g = b.pick_iter(u)
        m = list(g)
        assert m == m_, (m, m_)
        # x
        s = '~ y'
        u = b.add_expr(s)
        # partial
        g = b.pick_iter(u)
        m = list(g)
        m_ = [dict(y=False)]
        self.equal_list_contents(m, m_)
        # partial
        g = b.pick_iter(u, care_vars=['x', 'y'])
        m = list(g)
        m_ = [
            dict(x=True, y=False),
            dict(x=False, y=False)]
        self.equal_list_contents(m, m_)
        # care bits x, y
        b.add_var('z')
        s = 'x \/ y'
        u = b.add_expr(s)
        g = b.pick_iter(u, care_vars=['x', 'y'])
        m = list(g)
        m_ = [
            dict(x=True, y=False),
            dict(x=False, y=True),
            dict(x=True, y=True)]
        self.equal_list_contents(m, m_)

    def equal_list_contents(self, x, y):
        for u in x:
            assert u in y, (u, x, y)
        for u in y:
            assert u in x, (u, x, y)

    def test_apply(self):
        bdd = self.DD()
        for var in ['x', 'y', 'z']:
            bdd.add_var(var)
        x = bdd.var('x')
        y = bdd.var('y')
        z = bdd.var('z')
        # (x \/ ~ x) \equiv TRUE
        not_x = bdd.apply('not', x)
        true = bdd.apply('or', x, not_x)
        assert true == bdd.true, true
        # x /\ ~ x = 0
        false = bdd.apply('and', x, not_x)
        assert false == bdd.false, false
        # x /\ y = ~ (~ x \/ ~ y)
        u = bdd.apply('and', x, y)
        not_y = bdd.apply('not', y)
        v = bdd.apply('or', not_x, not_y)
        v = bdd.apply('not', v)
        assert u == v, (u, v)
        # xor
        u = bdd.apply('xor', x, y)
        r = bdd.let(dict(x=False, y=False), u)
        assert r == bdd.false, r
        r = bdd.let(dict(x=True, y=False), u)
        assert r == bdd.true, r
        r = bdd.let(dict(x=False, y=True), u)
        assert r == bdd.true, r
        r = bdd.let(dict(x=True, y=True), u)
        assert r == bdd.false, r
        # (z \/ ~ y) /\ x = (z /\ x) \/ (~ y /\ x)
        u = bdd.apply('or', z, not_y)
        u = bdd.apply('and', u, x)
        v = bdd.apply('and', z, x)
        w = bdd.apply('and', not_y, x)
        v = bdd.apply('or', v, w)
        assert u == v, (u, v)
        # symbols
        u = bdd.apply('and', x, y)
        v = bdd.apply('&', x, y)
        assert u == v, (u, v)
        u = bdd.apply('or', x, y)
        v = bdd.apply('|', x, y)
        assert u == v, (u, v)
        u = bdd.apply('not', x)
        v = bdd.apply('!', x)
        assert u == v, (u, v)
        u = bdd.apply('xor', x, y)
        v = bdd.apply('^', x, y)
        assert u == v, (u, v)

    def test_quantify(self):
        bdd = self.DD()
        for var in ['x', 'y']:
            bdd.add_var(var)
        x = bdd.var('x')
        # (\E x:  x) \equiv TRUE
        r = bdd.quantify(x, ['x'], forall=False)
        assert r == bdd.true, r
        # (\A x:  x) \equiv FALSE
        r = bdd.quantify(x, ['x'], forall=True)
        assert r == bdd.false, r
        # (\E y:  x) \equiv x
        r = bdd.quantify(x, ['y'], forall=False)
        assert r == x, (r, x)
        # (\A y:  x) \equiv x
        r = bdd.quantify(x, ['y'], forall=True)
        assert r == x, (r, x)
        # (\E x:  x /\ y) \equiv y
        y = bdd.var('y')
        u = bdd.apply('and', x, y)
        r = bdd.quantify(u, ['x'], forall=False)
        assert r == y, (r, y)
        assert r != x, (r, x)
        # (\A x:  x /\ y) \equiv FALSE
        r = bdd.quantify(u, ['x'], forall=True)
        assert r == bdd.false, r
        # (\A x:  ~ x \/ y) \equiv y
        not_x = bdd.apply('not', x)
        u = bdd.apply('or', not_x, y)
        r = bdd.quantify(u, ['x'], forall=True)
        assert r == y, (r, y)

    def test_cube(self):
        bdd = self.DD()
        for var in ['x', 'y', 'z']:
            bdd.add_var(var)
        # x
        x = bdd.var('x')
        c = bdd.cube(['x'])
        assert x == c, (x, c)
        # x /\ y
        y = bdd.var('y')
        u = bdd.apply('and', x, y)
        c = bdd.cube(['x', 'y'])
        assert u == c, (u, c)
        # x /\ ~ y
        not_y = bdd.apply('not', y)
        u = bdd.apply('and', x, not_y)
        d = dict(x=True, y=False)
        c = bdd.cube(d)
        assert u == c, (u, c)

    def test_add_expr(self):
        bdd = self.DD()
        for var in ['x', 'y']:
            bdd.add_var(var)
        # ((FALSE \/ TRUE) /\ x) \equiv x
        s = '(True \/ FALSE) /\ x'
        u = bdd.add_expr(s)
        x = bdd.var('x')
        assert u == x, (u, x)
        # ((x \/ ~ y) /\ x) \equiv x
        s = '(x \/ ~ y) /\ x'
        u = bdd.add_expr(s)
        assert u == x, (u, x)
        # x /\ y /\ z
        bdd.add_var('z')
        z = bdd.var('z')
        u = bdd.add_expr('x /\ y /\ z')
        u_ = bdd.cube(dict(x=True, y=True, z=True))
        assert u == u_, (u, u_)
        # x /\ ~ y /\ z
        u = bdd.add_expr('x /\ ~ y /\ z')
        u_ = bdd.cube(dict(x=True, y=False, z=True))
        assert u == u_, (u, u_)
        # (\E x:  x /\ y) \equiv y
        y = bdd.var('y')
        u = bdd.add_expr('\E x:  x /\ y')
        assert u == y, (str(u), str(y))
        # (\A x:  x \/ ~ x) \equiv TRUE
        u = bdd.add_expr('\A x:  ~ x \/ x')
        assert u == bdd.true, u

    def test_support(self):
        # signle var
        bdd = self.DD()
        # declared at the start, for ZDDs to work
        bdd.declare('x', 'y')
        x = bdd.var('x')
        supp = bdd.support(x)
        assert supp == set(['x']), supp
        # two vars
        y = bdd.var('y')
        x_and_y = bdd.apply('and', x, y)
        supp = bdd.support(x_and_y)
        assert supp == set(['x', 'y']), (supp, len(x_and_y))

    def test_rename(self):
        bdd = self.DD()
        bdd.declare('x', 'y', 'z', 'w')
        # x -> y
        x = bdd.var('x')
        supp = bdd.support(x)
        assert supp == set(['x']), supp
        d = dict(x='y')
        f = bdd.let(d, x)
        supp = bdd.support(f)
        assert supp == set(['y']), supp
        y = bdd.var('y')
        assert f == y, (f, y)
        # x, y -> z, w
        not_y = bdd.apply('not', y)
        u = bdd.apply('or', x, not_y)
        supp = bdd.support(u)
        assert supp == set(['x', 'y']), supp
        d = dict(x='z', y='w')
        f = bdd.let(d, u)
        supp = bdd.support(f)
        assert supp == set(['z', 'w']), supp
        z = bdd.var('z')
        w = bdd.var('w')
        not_w = bdd.apply('not', w)
        f_ = bdd.apply('or', z, not_w)
        assert f == f_, (f, f_)
        # ensure substitution, not swapping
        #
        # f == LET x == y
        #      IN x /\ y
        u = bdd.apply('and', x, y)
        # replace x with y, but leave y as is
        d = dict(x='y')
        f = bdd.let(d, u)
        # THEOREM f <=> y
        assert f == y, (f, y)
        # f == LET x == y
        #      IN x /\ ~ y
        u = bdd.apply('and', x, ~ y)
        d = dict(x='y')
        f = bdd.let(d, u)
        # THEOREM f <=> FALSE
        assert f == bdd.false, f
        # simultaneous substitution
        #
        # f == LET x == y1  (* x1, y1 correspond to *)
        #          y == x1  (* x, y after substitution *)
        #      IN x /\ ~ y
        u = bdd.apply('and', x, ~ y)
        # replace x with y, and simultaneously, y with x
        d = dict(x='y', y='x')
        f = bdd.let(d, u)
        f_ = bdd.apply('and', y, ~ x)
        # THEOREM f <=> (~ x /\ y)
        assert f == f_, (f, f_)
        del x, y, not_y, z, w, not_w, u, f, f_
        # as method
        x = bdd.var('x')
        y_ = bdd.var('y')
        d = dict(x='y')
        y = bdd.let(d, x)
        assert y == y_, (y, y_)
        del x, y, y_

    def test_ite(self):
        b = self.DD()
        for var in ['x', 'y', 'z']:
            b.add_var(var)
        x = b.var('x')
        u = b.ite(x, b.true, b.false)
        assert u == x, (u, x)
        u = b.ite(x, b.false, b.true)
        assert u == ~ x, (u, x)
        y = b.var('y')
        u = b.ite(x, y, b.false)
        u_ = b.add_expr('x /\ y')
        assert u == u_, (u, u_)

    def test_reorder(self):
        bdd = self.DD()
        dvars = ['x', 'y', 'z']
        for var in dvars:
            bdd.add_var(var)
        self._confirm_var_order(dvars, bdd)
        order = dict(y=0, z=1, x=2)
        bdd.reorder(order)
        for var in order:
            level_ = order[var]
            level = bdd.level_of_var(var)
            assert level == level_, (var, level, level_)
        # without args
        bdd = self.DD()
        # Figs. 6.24, 6.25 Baier 2008
        vrs = ['z1', 'z2', 'z3', 'y1', 'y2', 'y3']
        bdd.declare(*vrs)
        self._confirm_var_order(vrs, bdd)
        expr = '(z1 /\ y1) \/ (z2 /\ y2) \/ (z3 /\ y3)'
        u = bdd.add_expr(expr)
        bdd.reorder()
        levels = {var: bdd.level_of_var(var) for var in vrs}
        for i in range(1, 4):
            a = levels['z{i}'.format(i=i)]
            b = levels['y{i}'.format(i=i)]
            assert abs(a - b) == 1, levels

    def _confirm_var_order(self, vrs, bdd):
        for i, var in enumerate(vrs):
            level = bdd.level_of_var(var)
            assert level == i, (var, level, i)

    def test_function_support(self):
        bdd = self.DD()
        bdd.add_var('x')
        u = bdd.var('x')
        r = u.support
        assert r == {'x'}, r
        bdd.add_var('y')
        u = bdd.add_expr('y /\ x')
        r = u.support
        assert r == {'x', 'y'}, r