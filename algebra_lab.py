"""Exact symbolic checks for the original examples in the lecture notes.

Run: python algebra_lab.py
Requires SymPy. No network access and no mutation unless --output is provided.
These checks verify named finite examples, not the general mathematical theorems.
"""
import argparse
import json
from pathlib import Path
import sympy as sp


def checks():
    x, y, t, u, v, s = sp.symbols('x y t u v s')
    results = {}

    certificate = sp.expand(y * x - (x * y - 1))
    assert certificate == 1
    results['unit_ideal_certificate'] = str(certificate)

    basis = sp.groebner([x**2, y], x, y)
    remainder_x = basis.reduce(x)[1]
    remainder_square = basis.reduce(x**2)[1]
    assert remainder_x == x and remainder_square == 0
    results['nilpotent_example_remainders'] = [str(remainder_x), str(remainder_square)]

    components = sp.factor(x * y * (x - 1))
    assert sp.expand(components - x * y * (x - 1)) == 0
    results['three_component_polynomial'] = str(components)

    cusp = y**2 - x**3
    parametrization = {x: t**2, y: t**3}
    assert sp.expand(cusp.subs(parametrization)) == 0
    assert sp.cancel((y / x).subs(parametrization)) == t
    results['cusp_rational_inverse'] = 't (on t != 0)'

    forward = sp.Matrix([x, y + x**2])
    inverse = sp.Matrix([u, v - u**2])
    back = inverse.subs({u: forward[0], v: forward[1]}, simultaneous=True)
    there = forward.subs({x: inverse[0], y: inverse[1]}, simultaneous=True)
    assert sp.simplify(back - sp.Matrix([x, y])) == sp.zeros(2, 1)
    assert sp.simplify(there - sp.Matrix([u, v])) == sp.zeros(2, 1)
    determinant = sp.expand(forward.jacobian([x, y]).det())
    assert determinant == 1
    results['triangular_map_jacobian'] = str(determinant)

    quadric_relation = sp.expand((s**2) * (t**2) - (s * t)**2)
    assert quadric_relation == 0
    results['veronese_relation'] = str(quadric_relation)

    node = y**2 - x**2 * (x + 1)
    ranks = {}
    for name, equation in [('cusp', cusp), ('node', node)]:
        jacobian = sp.Matrix([[sp.diff(equation, x), sp.diff(equation, y)]])
        origin_rank = jacobian.subs({x: 0, y: 0}).rank()
        ranks[name + '_origin'] = {'rank': origin_rank, 'tangent_dimension': 2 - origin_rank}
        assert origin_rank == 0
    cusp_regular_rank = sp.Matrix([[sp.diff(cusp, x), sp.diff(cusp, y)]]).subs({x: 1, y: 1}).rank()
    assert cusp_regular_rank == 1
    ranks['cusp_at_1_1'] = {'rank': cusp_regular_rank, 'tangent_dimension': 2 - cusp_regular_rank}
    results['tangent_spaces_over_Q'] = ranks

    # Failure of a constant-Jacobian converse in characteristic p is elementary.
    prime = 5
    polynomial = t - t**prime
    derivative = sp.Poly(sp.diff(polynomial, t), t, modulus=prime)
    assert derivative == sp.Poly(1, t, modulus=prime)
    assert [int(polynomial.subs(t, a)) % prime for a in range(prime)] == [0] * prime
    results['characteristic_5_example'] = {'derivative': '1', 'five_inputs_same_output': True}

    # Homogenize y-x^2 at total degree 2; the new variable is z.
    z = sp.symbols('z')
    homogeneous = y * z - x**2
    assert homogeneous.subs(z, 1) == y - x**2
    scale = sp.symbols('lambda')
    scaled = homogeneous.subs({x: scale * x, y: scale * y, z: scale * z}, simultaneous=True)
    assert sp.expand(scaled - scale**2 * homogeneous) == 0
    results['homogenized_parabola'] = str(homogeneous)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'passed', 'checks': checks(), 'scope': 'exact finite examples; not proofs of general theorems'}
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
