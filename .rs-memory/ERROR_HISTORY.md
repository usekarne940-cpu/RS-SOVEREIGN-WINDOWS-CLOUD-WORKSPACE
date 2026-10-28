# ERROR_HISTORY

Every error encountered during execution is recorded with root cause and fix. Zero-fake policy:
unresolved failures stay visible here and in reports/.

## Format
`[wave] ERROR -> root cause -> fix -> regression verification`

## Entries

- [W01] `curl https://pixeldrain.com/api/file/ZdPxkVmH` returned raw 7z bytes instead of JSON
  metadata -> pixeldrain serves file content unless JSON is explicitly negotiated
  -> fix: xlite_inspector.py sends `Accept: application/json` AND validates the response
  content-type/content sniff before JSON parsing (decision D-004)
  -> verification: unit tests cover metadata parsing; live probe re-run in Wave 11 with forced
  JSON negotiation.

- [W11] E-002: live metadata call hung until the 120 s command timeout
  -> root cause: the pixeldrain file endpoint serves the raw 2.55 GB archive content
  REGARDLESS of the Accept header; `resp.read()` was unbounded and the socket-level timeout
  never fires while the server keeps streaming
  -> fix: HEAD-first metadata (1-byte ranged-GET fallback on HTTP 405), JSON body fetch
  hard-capped at 1 MiB, every read size-capped, `/download` suffix removed (404 on this
  endpoint; the file endpoint itself serves content and honors Accept-Ranges)
  -> regression: live re-run 2026-10-28T18:55Z — metadata exit 0 (real name/size/date from
  headers), probe exit 0 (HTTP 206, 7z magic 377abcaf271c, reports/xlite-probe.json written).
  VERIFIED.

(No other unresolved errors — appended as they occur.)
