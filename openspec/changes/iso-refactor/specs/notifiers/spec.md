## ADDED Requirements

### Requirement: Notifier Protocol definieert kanaal-agnostisch contract voor handoff

Het systeem SHALL een `Notifier` Protocol bieden in `src/iso_audit/notifiers/base.py` met:

- `naam: str` (uniek class-attribute, lowercase, kebab-case voor multi-woord, e.g. `"slack"`, `"email"`, `"teams"`, `"mcp-teams"`)
- `vraag_besluit(decision: Decision) -> str` (stuurt decision naar het kanaal, retourneert decision_id voor latere correlatie)
- `healthcheck() -> dict`

Een `Notifier` is een communicatiekanaal tussen pipeline (typisch IntegerMode) en menselijke auditor; het is bewust géén Sink omdat de semantiek anders is — Notifier vraagt om respons, Sink levert one-shot.

#### Scenario: Adapter implementeert volledige Notifier-contract

- **WHEN** een nieuwe notifier wordt toegevoegd in `src/iso_audit/notifiers/`
- **THEN** mypy `--strict` MUST geen fouten rapporteren op het Protocol-conformance check
- **AND** de notifier MUST een `naam` attribuut hebben dat uniek is binnen de geregistreerde set

#### Scenario: Notifier mist verplichte methode

- **WHEN** een notifier `healthcheck()` niet implementeert
- **THEN** mypy `--strict` MUST een Protocol-violation error geven
- **AND** CI MUST de PR blokkeren

### Requirement: DecisionResolver-protocol parseert kanaal-respons kanaal-agnostisch

Een aparte `DecisionResolver` Protocol SHALL bestaan in `src/iso_audit/notifiers/base.py` met:

- `resolve(decision_id: str, action: str, modified_payload: dict | None = None) -> None`

`action` SHALL één van zijn: `"approve"`, `"reject"`, `"modify"`, `"abort"`.

De resolver SHALL kanaal-agnostisch zijn: Slack-button-payloads, Email-magic-link-clicks, en Teams-card-actions leveren allemaal dezelfde `(decision_id, action, modified_payload)`-shape op aan de resolver.

De resolver SHALL de `decisions`-tabel updaten: `status="resolved"`, `besluit_json` afgeleid van `action` en `modified_payload`, `resolved_at` op huidige tijdstempel.

Wanneer `action="abort"` SHALL `status="cancelled"` worden gezet en de pipeline-thread afbreken zonder verdere stappen.

#### Scenario: Slack-button approve-click

- **WHEN** auditor klikt `Goedkeuren` in Slack Block Kit message
- **THEN** SlackNotifier handler MUST `resolver.resolve(decision_id, "approve", None)` aanroepen
- **AND** de `decisions`-rij MUST `status="resolved"` en `besluit_json` gelijk aan voorstel hebben

#### Scenario: Email-magic-link approve-click

- **WHEN** auditor klikt `Goedkeuren` op Flask-portaal-pagina
- **THEN** EmailNotifier handler MUST `resolver.resolve(decision_id, "approve", None)` aanroepen
- **AND** dezelfde `decisions`-rij-update MUST plaatsvinden als bij Slack-equivalent

#### Scenario: Resolver met onbekende action

- **WHEN** een notifier-handler `resolver.resolve(decision_id, "vague_action", None)` aanroept
- **THEN** de resolver MUST een `ValueError` werpen
- **AND** de `decisions`-rij MUST onveranderd blijven

### Requirement: Pipeline selecteert notifier via verplichte `--notifier` flag bij integer-modus

De CLI SHALL een `--notifier <naam>` flag accepteren. De flag SHALL verplicht zijn wanneer `--mode integer` is gekozen.

Wanneer `--mode autonoom` is gekozen SHALL `--notifier` genegeerd worden (autonoom doet geen handoff).

Wanneer `--mode integer` zonder `--notifier` en zonder `ISO_AUDIT_DEFAULT_NOTIFIER` SHALL de CLI exit-code 2 retourneren met een lijst van geregistreerde notifiers.

Wanneer `--notifier` een onbekende waarde heeft SHALL de CLI exit-code 2 retourneren met een lijst van geregistreerde notifiers.

#### Scenario: Integer-modus met onbekende notifier

- **WHEN** `iso-audit pipeline --source drive --mode integer --notifier xyz`
- **THEN** de CLI MUST exit-code 2 retourneren
- **AND** stderr MUST aangeven dat `xyz` geen geregistreerde notifier is

#### Scenario: Autonoom-modus met `--notifier` flag

- **WHEN** `iso-audit pipeline --source drive --mode autonoom --notifier slack`
- **THEN** de CLI MUST de notifier-flag negeren
- **AND** een WARNING-log MUST melden "notifier ignored in autonoom mode"

### Requirement: Slack-notifier implementeert Notifier Protocol via Block Kit

Een `SlackNotifier` SHALL bestaan in `src/iso_audit/notifiers/slack.py` die `Notifier` implementeert.

De notifier SHALL `naam = "slack"` hebben.

De notifier SHALL Slack Block Kit gebruiken voor structured messages met:
- Een header met het beslispunt en risico-niveau
- De context als formatted code-block (JSON, leesbaar)
- Het voorgesteld besluit als formatted code-block
- Action-buttons voor: `Goedkeuren`, `Afwijzen`, `Aanpassen`, `Afbreken` (Aanpassen opent een modal)
- Een unieke decision-id als button-value zodat de response-handler de juiste rij kan updaten

De handoff-channel SHALL configureerbaar zijn via env-var `SLACK_AUDIT_CHANNEL`.

De notifier SHALL een Slack-app-token-authenticatie gebruiken via env-var `SLACK_BOT_TOKEN`.

Button-callbacks SHALL via Slack Events API binnenkomen op een handler die `DecisionResolver.resolve()` aanroept met de geparseerde shape.

#### Scenario: Auditor klikt Goedkeuren

- **WHEN** de auditor op de `Goedkeuren`-button klikt
- **THEN** de handler MUST `DecisionResolver.resolve(decision_id, "approve", None)` aanroepen
- **AND** de pipeline-thread MUST hervatten met dat besluit

#### Scenario: Auditor klikt Aanpassen en submit modal

- **WHEN** de auditor op `Aanpassen` klikt en een gewijzigd besluit submit
- **THEN** de handler MUST `DecisionResolver.resolve(decision_id, "modify", modified_payload)` aanroepen
- **AND** de `decisions`-rij MUST `besluit_json` met de gewijzigde waarde hebben

#### Scenario: SlackNotifier healthcheck zonder token

- **WHEN** `healthcheck()` wordt aangeroepen zonder `SLACK_BOT_TOKEN`
- **THEN** de geretourneerde dict MUST `status: "fail"` bevatten
- **AND** een `reden`-veld dat naar de ontbrekende token verwijst

### Requirement: Email-notifier implementeert Notifier Protocol via SMTP en magic-link-portaal

Een `EmailNotifier` SHALL bestaan in `src/iso_audit/notifiers/email.py` die `Notifier` implementeert.

De notifier SHALL `naam = "email"` hebben.

De notifier SHALL SMTP gebruiken voor outbound mail via env-vars (`ISO_AUDIT_SMTP_HOST`, `ISO_AUDIT_SMTP_PORT`, `ISO_AUDIT_SMTP_USER`, `ISO_AUDIT_SMTP_PASS`, `ISO_AUDIT_SMTP_FROM`).

De notifier SHALL een lokaal Flask-mini-portaal draaien voor magic-link-respons (poort via env `ISO_AUDIT_PORTAL_PORT`, default `8765`).

Outbound e-mail SHALL bevatten:
- Het beslispunt en risico-niveau in subject en body
- De context en voorstel als formatted text in body
- Vier magic-links naar het lokale portaal: `/decision/<id>/approve`, `/reject`, `/modify`, `/abort`

Magic-link tokens SHALL single-use zijn en een expiratie hebben (default 24 uur, configureerbaar via `ISO_AUDIT_PORTAL_TOKEN_TTL_HOURS`).

Het Flask-portaal SHALL bij `/modify` een form-pagina serveren waar de auditor het besluit kan aanpassen vóór submit.

Bij click op een magic-link SHALL het portaal `DecisionResolver.resolve()` aanroepen met de juiste `(decision_id, action, modified_payload)`-shape.

Het Flask-portaal MAY in MVP HTTP zonder TLS draaien omdat het lokaal op pipeline-host draait en tokens single-use + tijd-gelimiteerd zijn. Bij multi-host-deployment SHALL TLS via reverse-proxy verplicht worden — gedocumenteerd in `docs/notifiers/email.md`.

#### Scenario: Auditor klikt approve-magic-link

- **WHEN** de auditor klikt op `/decision/abc123/approve` magic-link in e-mail
- **THEN** het Flask-portaal MUST `DecisionResolver.resolve("abc123", "approve", None)` aanroepen
- **AND** een bevestigingspagina MUST tonen "Decision abc123 approved"
- **AND** de pipeline-thread MUST hervatten

#### Scenario: Auditor klikt approve-magic-link na expiratie

- **WHEN** de auditor klikt op een magic-link 25 uur na verzending (TTL=24)
- **THEN** het portaal MUST een 410 Gone response retourneren met "token expired"
- **AND** de `decisions`-rij MUST onveranderd blijven met `status="pending"`
- **AND** een log-entry MUST de expiratie registreren

#### Scenario: EmailNotifier healthcheck

- **WHEN** `healthcheck()` wordt aangeroepen
- **THEN** de geretourneerde dict MUST `status` bevatten gebaseerd op SMTP-connectivity-test
- **AND** een `portal_url`-veld met de lokale portaal-URL (bv. `http://localhost:8765`)

### Requirement: Contract-tests draaien tegen elke geregistreerde notifier

Een `tests/notifiers/test_protocol_contract.py` SHALL een fixture-set bevatten die identiek is voor alle notifiers.

Voor elke geregistreerde notifier SHALL pytest een parametrized test-suite draaien die:
- `vraag_besluit(decision)` retourneert een non-empty string (decision_id)
- `healthcheck()` retourneert een dict met minimaal de keys `status` en `naam`
- Bij identieke `Decision`-input, opeenvolgende calls genereren unieke decision_ids (geen collisions)

De tests SHALL mocking gebruiken voor externe systemen (Slack-API, SMTP-server, Flask-portaal); echte calls in CI SHALL geweigerd worden.

Een nieuwe notifier SHALL pas mergeable zijn wanneer alle contract-tests groen zijn.

#### Scenario: SlackNotifier passeert contract-tests

- **WHEN** `pytest tests/notifiers/test_protocol_contract.py -k slack` draait met gemockte Slack-API
- **THEN** alle parametrized tests MUST groen zijn

#### Scenario: EmailNotifier passeert contract-tests

- **WHEN** `pytest tests/notifiers/test_protocol_contract.py -k email` draait met gemockte SMTP en Flask-test-client
- **THEN** alle parametrized tests MUST groen zijn

### Requirement: NotifierRegistry beheert lifecycle van geregistreerde notifiers

Een `NotifierRegistry` SHALL bestaan in `src/iso_audit/notifiers/__init__.py` die:

- Notifiers registreert via een `@register` decorator of expliciete `register(notifier_class)` call
- `available()` methode biedt die een lijst van geregistreerde namen returnt
- `get(naam)` methode biedt die een geconfigureerde notifier-instance returnt of `KeyError` werpt

De registry SHALL idempotent zijn: dubbele registratie van dezelfde notifier-naam SHALL een `ValueError` werpen.

Het patroon SHALL identiek zijn aan `SourceRegistry` voor consistentie en uitlegbaarheid aan externe code-reviewers.

#### Scenario: Notifier wordt geregistreerd via decorator

- **WHEN** een notifier-class wordt voorzien van `@register`
- **THEN** `NotifierRegistry.available()` MUST de notifier-naam bevatten

#### Scenario: Dubbele registratie

- **WHEN** twee notifiers proberen dezelfde `naam` te registreren
- **THEN** de tweede registratie MUST een `ValueError` werpen
- **AND** de eerste registratie blijft actief
