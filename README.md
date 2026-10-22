# 7-Agent Crypto Paper Trading Lab — Starter

## What this is
A beginner-friendly Streamlit dashboard prototype. It includes a seven-agent architecture overview, a repeatable simulated paper-trading exercise, fee-aware trade journal, and basic performance metrics.

## Important limitations
- The prices are **synthetic demo prices**, not real crypto prices or historical data.
- Agent 3 explicitly abstains because live news is not connected.
- This is **not** a production autonomous AI system and it does not send exchange orders.
- It does not automatically run for 30 calendar days in the background. Keep a separate forward paper-trading service running for a genuine 30-day test before evaluating real-market performance.

## Run locally on a computer
1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open a terminal in the extracted folder.
4. Run:
   `pip install -r requirements.txt`
5. Run:
   `streamlit run app.py`
6. Open the local address shown in the terminal.

## Easiest Android route (cloud dashboard)
You can deploy this starter using GitHub and Streamlit Community Cloud:
1. Create/sign in to GitHub and create a **private** repository.
2. Upload `app.py` and `requirements.txt`.
3. Open https://share.streamlit.io/ and connect GitHub.
4. Choose the repository and `app.py` as the main file, then deploy.
5. Open the dashboard URL on your Android phone and use Chrome's **Add to Home screen** option if available.

Cloud providers and their terms may change. Never upload exchange secrets to GitHub or put secrets in the app source.

## How to interpret the dashboard
- Starting balance: fictional USDT balance.
- Final balance / return: result of the generated-price simulation only.
- Win rate: proportion of closed trades with positive net P&L.
- Profit factor: sum of winning net P&L divided by absolute losing net P&L.
- Fees: estimated entry and exit fees configured in the sidebar.
- CSV: downloadable simulated trade log.

## Proposed production architecture
Market data adapter -> agents 1–4 -> risk gate (agent 5) -> master coordinator (agent 7) -> paper execution engine -> persistent database -> journal/learning agent (agent 6) -> dashboard and alerts.

For a real 30-day forward test, add a continuously running worker, real public market data, database persistence, realistic fills/spread/slippage, alerting and daily backups. Use an exchange testnet/demo environment where supported. Do not enable real-money execution until independently reviewed and explicitly enabled by the user after paper evaluation.
