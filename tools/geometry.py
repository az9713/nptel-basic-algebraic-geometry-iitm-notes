"""Generate a checked two-dimensional curve illustration, no source media."""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]


def main():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" role="img"><title>Cusp and nodal cubic over the real numbers</title><rect width="800" height="360" fill="#19212b"/>']
    residuals = {}
    for number, name in enumerate(['cusp', 'node']):
        offset = number * 400
        def X(x):
            return offset + 70 + (x + 1.1) * 85
        def Y(y):
            return 180 - 48 * y
        points = []
        max_residual = 0
        for i in range(301):
            t = -1.5 + i / 100
            x, y = (t*t, t*t*t) if name == 'cusp' else (t*t-1, t*(t*t-1))
            residual = y*y-x*x*x if name == 'cusp' else y*y-x*x*(x+1)
            max_residual = max(max_residual, abs(residual))
            points.append(f'{X(x):.3f},{Y(y):.3f}')
        assert max_residual < 1e-12
        residuals[name] = max_residual
        parts += [f'<line x1="{offset+30}" y1="180" x2="{offset+380}" y2="180" stroke="#617184"/>',
                  f'<line x1="{X(0)}" y1="30" x2="{X(0)}" y2="335" stroke="#617184"/>',
                  f'<polyline points="{" ".join(points)}" fill="none" stroke="#7ed9c5" stroke-width="2.5"/>',
                  f'<circle cx="{X(0)}" cy="{Y(0)}" r="5" fill="#f3c76d"/>',
                  f'<text x="{offset+24}" y="24" fill="#e3e8ef" font-family="serif" font-size="19">{name}</text>',
                  f'<text x="{offset+370}" y="202" fill="#e3e8ef" font-family="serif">x</text>',
                  f'<text x="{X(0)+9}" y="46" fill="#e3e8ef" font-family="serif">y</text>']
    parts.append('</svg>')
    (ROOT / 'assets/curves.svg').write_text(''.join(parts), encoding='utf8')
    result = {'status': 'passed', 'sampled_points_per_curve': 301, 'maximum_equation_residuals': residuals,
              'scope': 'real parametrized illustration; exact Jacobian checks in algebra_lab.py'}
    (ROOT / 'validation/geometry-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
