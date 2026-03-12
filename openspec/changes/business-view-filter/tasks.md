## 1. App Name Parsing

- [x] 1.1 Create `transform.py` with `_ENV_TOKENS` set and `_PRODUCT_MAP` dict (`nextcloud`, `react`/`reactfront`, `tilburg` → `tilburg-ui`)
- [x] 1.2 Implement `classify(app_name)` → returns canonical product type string or `None` if no match
- [x] 1.3 Implement `parse_app_name(app_name)` → returns `(customer, environment)` by scanning segments for first env token; fall back to `(namespace_customer, "")` if no token found
- [x] 1.4 Write unit tests for `classify` and `parse_app_name` covering: nextcloud, reactfront, tilburg-woo-ui, no-match, multi-segment customer, preprod

## 2. Business Pivot

- [x] 2.1 Implement `pivot(rows)` in `transform.py`: filter `[REMOVED]` apps, classify each, parse customer+env, group by `(customer, environment)`, produce dicts with boolean product columns
- [x] 2.2 Sort output by `customer_name` asc then `environment` asc
- [x] 2.3 Write unit tests for pivot: single product, multiple products same env, same product two envs, removed apps excluded

## 3. Business Output — Local

- [x] 3.1 Create `output/business_local.py`: read `BUSINESS_OUTPUT_PATH` env var, call `pivot()`, write xlsx with columns `customer_name`, `environment`, `nextcloud`, `react`, `tilburg-ui`
- [x] 3.2 No upsert needed — full rewrite on every run (business view is stateless)

## 4. Business Output — GWS

- [x] 4.1 Create `output/business_gws.py`: call `pivot()`, clear `Business` tab, write pivoted rows via `batchUpdate`
- [x] 4.2 Tab name constant `BUSINESS_TAB = "Business"` — separate from `Deployments`

## 5. Sync Entrypoint

- [x] 5.1 Add `business` case to `sync.sh` dispatching to `output/business_local.py` or `output/business_gws.py` based on a `BUSINESS_OUTPUT` env var (`local` or `gws`)
- [x] 5.2 Add `BUSINESS_OUTPUT` and `BUSINESS_OUTPUT_PATH` to `.env.example` with comments

## 6. Documentation

- [x] 6.1 Update `README.md` project structure to include `transform.py` and new output files
- [x] 6.2 Add `Business view` section to `README.md` describing the mode, env vars, and output columns
