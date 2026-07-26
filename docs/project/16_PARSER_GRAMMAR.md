# Parser grammar and error taxonomy

This grammar is an implementation aid, not a replacement for the subject. Keep tokenization simple
and line-oriented; do not introduce a parser generator.

## Informal grammar

```ebnf
file            = ignored*, drone-count, ignored*, declaration*, ignored* ;
ignored         = blank-line | comment-line ;
drone-count     = "nb_drones:", positive-integer ;
declaration     = zone-line | connection-line ;
zone-line       = zone-prefix, name, integer, integer, metadata? ;
zone-prefix     = "start_hub:" | "end_hub:" | "hub:" ;
connection-line = "connection:", name, "-", name, metadata? ;
metadata        = "[", metadata-item, (whitespace, metadata-item)*, "]" ;
metadata-item   = key, "=", value ;
```

Because dash is the connection separator, zone names cannot contain it. Whitespace separates zone
fields and is prohibited inside names.

## Parsing stages

1. Preserve physical line number and original text.
2. Classify blank/comment/significant line.
3. Identify declaration prefix exactly.
4. Split metadata block from structural fields with balanced brackets.
5. Tokenize structural fields.
6. Parse metadata into unique key/value tokens.
7. Validate syntax/local values.
8. Build domain objects and validate cross-line constraints.

Keep lexical/syntax errors distinct from semantic/domain errors when useful, but expose one stable
user error shape.

## Stable error codes

| Code | Example |
| --- | --- |
| `MISSING_DRONE_COUNT` | First significant line is a hub |
| `INVALID_DRONE_COUNT` | zero, negative, non-integer |
| `UNKNOWN_DECLARATION` | unknown prefix |
| `INVALID_FIELD_COUNT` | missing coordinate/name |
| `INVALID_COORDINATE` | non-integer x/y |
| `INVALID_ZONE_NAME` | dash or whitespace |
| `DUPLICATE_ZONE` | repeated name |
| `DUPLICATE_START` / `DUPLICATE_END` | terminal repeated |
| `MISSING_START` / `MISSING_END` | end-of-file invariant |
| `MALFORMED_METADATA` | bracket or token syntax |
| `UNKNOWN_METADATA` | unsupported key |
| `DUPLICATE_METADATA` | repeated key |
| `INVALID_ZONE_TYPE` | not allowed enum |
| `INVALID_CAPACITY` | non-positive/non-integer |
| `UNKNOWN_CONNECTION_ZONE` | undefined/later endpoint |
| `DUPLICATE_CONNECTION` | same/reversed edge |
| `SELF_CONNECTION` | current self-loop policy |

Error messages include code, 1-based line, cause, and safe excerpt. Do not make tests depend on
every punctuation mark unless the CLI contract promises exact prose.

## Terminal capacity nuance

When `max_drones` appears on start/end, preserve its non-empty raw `key=value` token but do not
validate the value numerically. Fly-In 1.5 section VII.4 says the metadata is ignored and is not a
validation error. Effective terminal capacity is always unlimited.
