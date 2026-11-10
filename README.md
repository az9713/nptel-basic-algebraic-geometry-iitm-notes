# Basic Algebraic Geometry — NPTEL / IIT Madras

Independent study notes for T. E. Venkata Balaji's **42-recording NPTEL course**:
varieties, morphisms, local rings, function fields, and nonsingularity.

The reader has 15 topic chapters, developed proofs, worked examples, exercises
with complete solutions, a source map, a cumulative algebra laboratory, and an
interactive cusp/node illustration. It uses dark mode and bundled MathJax.

**[Read the lecture notes](https://az9713.github.io/nptel-basic-algebraic-geometry-iitm-notes/)**
· [Original playlist](https://www.youtube.com/playlist?list=PLbMVogVj5nJSNj24jdPGivlJtxbxua2by)
· [Official NPTEL course](https://nptel.ac.in/courses/111106097)

## Reading and scope

Open index.html locally or use the published reader. Begin with the study
guide if quotient rings, prime ideals, or induced topology need a refresher.
The notes assume mathematical maturity, not previous algebraic geometry.

The exposition is independently written, rather than a transcript. Official-label
English captions were acquired for all 42 recordings and retained privately.
The public manifest reports their actual cue bounds and hashes. Source review
depth varies by chapter; direct audio listening and blackboard-frame review were
not performed. There is no claim to reproduce every spoken detail or board
calculation. Recording-start links are navigation anchors, including where the
caption track begins later.

The mathematical statements retain hypotheses that abbreviated upload titles
can omit. The notes distinguish Euclidean from Zariski topology, bijective maps
from isomorphisms, local rings from function fields, and nonsingularity from a
manifold-boundary picture. Chapter 8 contains a separately dated November 2026
Jacobian-conjecture literature update, attributed to primary preprints without
claiming independent reproduction of their research proofs.

## Contents

1. Equations, topology, and the vanishing dictionary
2. Irreducibility and prime ideals
3. Noetherian spaces and irreducible components
4. Dimension, coordinate rings, and hypersurfaces
5. Recovering affine geometry from its ring
6. Basic open sets and localization
7. Quasi-compactness and regular functions
8. Affine morphisms, duality, and automorphisms
9. Projective space and affine gluing
10. Homogeneous geometry and degree-zero localization
11. Germs and local rings
12. Rational functions and function fields
13. Projective functions and Veronese embeddings
14. Local isomorphisms and birational geometry
15. Tangent spaces, nonsingularity, and smooth open sets

## Rebuild and verify

Python 3.13 was used for the recorded checks. The reader itself needs no Python
or network connection once downloaded.

    python -m pip install -r requirements.txt
    python algebra_lab.py --output validation/algebra-results.json
    python tools/geometry.py
    python tools/build.py
    python tools/review_index.py
    python tools/browser_check.py
    python tools/validate.py --output validation/package-results.json

The browser check uses an installed Google Chrome through Playwright. The other
checks run without a browser. The authored reader rebuild does not require the
private captions. Repeating provenance extraction does: tools/public_sources.py
expects private source metadata under ignored work/sources/.

The exact algebra program checks fixed polynomial examples, including a
unit-ideal certificate, a nilpotent quotient, a cusp's rational inverse, a
triangular polynomial automorphism, a Veronese relation, and Jacobian ranks.
These finite computations illustrate the theory; they are not proofs of the
general theorems.

## Review evidence

The validation/review-index.json file indexes two independent science-editor
reviews per chapter from agents other than its author. Reports are tied to actual
HTML fragment hashes, with targeted confirmation after repairs. These are
AI-agent editorial judgments, not human referee reports or formal proof certification.

The package-results.json, browser-results.json, algebra-results.json and
geometry-results.json reports in validation/ separate mechanical, rendering,
symbolic and plotted checks. The release validator rejects missing chapters,
unresolved source acquisition, broken local links, malformed mathematics, and
missing independent acceptances at the current content hash.

## Attribution and publication boundary

The original course remains the work of its lecturer and NPTEL/IIT Madras.
This independent edition has no institutional endorsement. The source map and
references link original recordings and primary mathematical sources.
MathJax's license is retained under assets/.

The workflow and reading structure draw on the inspected
[NPTEL Diffusion in Solids notes](https://github.com/az9713/nptel-diffusion-in-solids-notes)
and [Stanford CS229 notes](https://github.com/az9713/cs229-machine-learning-notes).
Their previous checks do not validate this edition.

Raw captions, media, private working captures, signed retrieval URLs, credentials,
and personal biographical instructions are excluded from the repository.
