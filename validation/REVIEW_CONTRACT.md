# Independent chapter review records

Two reviewers other than a chapter's author read the actual complete HTML
fragment and use EDITOR_DOMAIN.md and the science-editor standard. A full review
checks statements, definitions, proof hinges, examples, exercises, limitations,
and lecture-topic fidelity against available evidence. The report explicitly
names what was not checked. No model or human identity is inferred beyond the
actual agent/context used.

Each reviewer writes validation/reviews/chNN-REVIEWER.md with original SHA-256,
verdict, located findings, repairs required and follow-up evidence.
After findings are resolved the reviewer confirms affected passages and writes
a companion JSON record with chapter, author, reviewer, original_sha256,
final_sha256, review_kind, status, report and limitations. Status is accepted
only when blockers are resolved. final_sha256 is the digest of the accepted
HTML fragment, not a predicted value.

An acceptance is an editorial judgment about the inspected manuscript. It does
not certify exhaustive audiovisual coverage, formal proof verification, human
review, or institutional endorsement. An author self-audit cannot count as
either independent review.
