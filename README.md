# TAMPA / Datanet PoC — README

Dit repository bevat een kleine proof‑of‑concept (PoC) voor een TAMPA‑gebaseerde verifier‑pipeline (Datanet). Recent zijn er extra configuratie‑ en hulpmiddelen toegevoegd om ChatGPT‑agenten veiliger en betrouwbaarder te gebruiken: strikte TAMPA prompts, parser‑instructies en een eenvoudige validator + tests.

Kort overzicht
- configs/tampa_prompt_v1.txt — strikte system prompt voor de ChatGPT/TAMPA agent (moet exact één JSON object teruggeven).
- configs/tampa_user_template.txt — user message template voor agent‑calls.
- configs/tampa_parser_instructions.txt — instructies voor de pipeline parser.
- configs/reviewer_assistant_prompt.txt — helper prompt voor menselijke reviewers.
- configs/canonicalizer_guidance.txt — richtlijnen voor canonicalize_v1.
- src/datanet/validate_tampa.py — eenvoudige validator die TAMPA JSON checkt tegen `canonical_text`.
- tests/test_chatgpt_validation.py — unit tests voor de validator.
- scripts/create_and_push_prompts.sh — script om de prompts in een feature branch te committen en een PR te openen (optioneel).

Belangrijke principes
- Modeloutput is niet automatisch betrouwbaar: alles moet gevalideerd worden.
- De ChatGPT‑prompt dwingt formaat af, maar je pipeline moet:
  - JSON parseen / substring‑extractie proberen,
  - validate_tampa_output draaien,
  - niet‑parseerbare of ongeldige outputs quarantaineren als `_raw` of `_invalid`,
  - menselijke review afdwingen voordat canonisatie plaatsvindt.

Snelstart (lokaal)
1. Vereisten
   - Python 3.9+
   - git
   - (optioneel) GitHub CLI `gh` voor automatische PR's

2. Installatie
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Server (development)
Voor een snelle lokale test (FastAPI/uvicorn):
```bash
uvicorn src.datanet.api:app --reload --port 8000
```
(Open http://localhost:8000/docs voor interactive API docs als FastAPI aanwezig is.)

4. Voorbeeld workflow (handmatig)
- Maak job (snapshot ingest):
  POST /jobs met JSON body:
  {
    "query": "...",
    "snapshot_html": "<html>...</html>"
  }
- Optioneel: run lokale tamparunner (POST /jobs maakt al `tampa_local`).
- Remote ChatGPT run:
  - Zonder OPENAI_API_KEY: gebruik POST /jobs/{jobId}/submit-agent om agent JSON handmatig te plakken.
  - Met OPENAI_API_KEY: POST /jobs/{jobId}/run-remote zal chatgpt_agent proberen aan te roepen en resultaat valideren en opslaan.

Repository‑scripts en automations
- scripts/create_and_push_prompts.sh — maakt branch `feat/add-tampa-prompts`, schrijft de promptbestanden, commit & pusht en opent een PR met de `gh` CLI (als aanwezig).
  Gebruik:
  ```bash
  chmod +x scripts/create_and_push_prompts.sh
  ./scripts/create_and_push_prompts.sh
  ```

PR handmatig aanmaken met gh
- Na commit/push:
```bash
gh pr create --base main --head feat/add-tampa-prompts --title "chore(configs): add TAMPA prompts and pipeline guidance" --body-file pr_body.txt
```

Tests
- Run unit tests:
```bash
pytest -q
```

Waar te kijken bij issues
- parse_failures: model geeft geen valide JSON — output wordt opgeslagen als `{agent_name}_raw`.
- validation failures: JSON bestaat maar faalt schema/index checks — opgeslagen als `{agent_name}_invalid` met reden.
- drhash mismatches: controleer canonicalize_v1 en drhash berekening.

Security & secrets
- NOOIT API‑sleutels of secrets in de repo committen.
- Gebruik environment variables of GitHub Secrets:
  - OPENAI_API_KEY (alleen nodig als je remote agent wilt gebruiken)
  - OPENAI_MODEL (optioneel)
- Voor CI automation gebruik het ingebouwde `GITHUB_TOKEN` of een GitHub App met beperkte scope.

Contributie & review
- Voeg kleine, gerichte PR's toe voor prompt‑tuning of validator‑verbeteringen.
- Versieer prompts: update `prompt_version` in de prompt en in agent outputs zodat audit mogelijk is.
- Voor productie: vervang/aanvul de eenvoudige validator met een JSON Schema / pydantic‑based validator en voeg metrics (parse_failures, validate_failures) toe.

Contact / hulp
- Als je hulp nodig hebt bij het toepassen van de patch, het uitvoeren van de script of fixen van CI‑fouten: plak hier de foutmelding en ik help je stap‑voor‑stap.

##### Function-calling: expanded schemas & handlers

This repo contains an expanded set of function schemas and simple server-side handler implementations to support richer model workflows:

- src/mcp/function_schemas.py — added fetch_full_mcp, annotate_span, export_result
- src/mcp/fncall_handlers.py — server-side handlers for the new functions
- tests/test_mcp_fncall.py — integration-style tests using the local data/ layout

Run the new tests:
```bash
pytest tests/test_mcp_fncall.py -q
```

Notes:
- These handlers are simple local implementations intended as examples. In production replace annotate_span/export_result with proper services (datastore, ticketing, object storage).

Einde
