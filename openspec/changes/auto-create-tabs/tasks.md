## 1. Shared utility

- [x] 1.1 Add `ensure_tab_exists(spreadsheet_id, tab_name, env_fn)` function in `output/gws.py`: fetch sheet titles via `spreadsheets get --fields sheets.properties.title`, create tab via `batchUpdate addSheet` if missing

## 2. Wire up

- [x] 2.1 Call `ensure_tab_exists(SPREADSHEET_ID, TAB, _env)` at the start of `write_sheet` in `output/gws.py`
- [x] 2.2 Import and call `ensure_tab_exists` at the start of `write_sheet` in `output/business_gws.py`
