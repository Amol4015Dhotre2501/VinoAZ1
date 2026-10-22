import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="7-Agent Crypto Paper Lab", page_icon="📊", layout="wide")
st.title("📊 7-Agent Crypto Paper Trading Lab")
st.caption("Starter prototype • simulated money only • no exchange orders are sent")

with st.sidebar:
    st.header("Simulation settings")
    starting_balance = st.number_input("Starting paper balance (USDT)", min_value=100.0, value=10000.0, step=500.0)
    days = st.slider("Simulation days", 7, 90, 30)
    fee_pct = st.number_input("Fee per side (%)", min_value=0.0, max_value=1.0, value=0.10, step=0.01) / 100
    risk_pct = st.slider("Risk budget per trade (%)", 0.1, 1.0, 0.5, 0.1) / 100
    seed = st.number_input("Repeatable demo seed", min_value=1, max_value=999999, value=42)
    run = st.button("Run paper simulation", type="primary", use_container_width=True)

agents = [
    ("Agent 1 — Trading Ideas", "Creates candidate setups from simulated price action."),
    ("Agent 2 — Technical Analyst", "Checks moving averages, RSI-like momentum and trend."),
    ("Agent 3 — News Analyst", "News is not connected in this prototype; it abstains rather than inventing headlines."),
    ("Agent 4 — Strategy Backtester", "Evaluates simple moving-average crossover signals."),
    ("Agent 5 — Risk Manager", "Limits per-trade risk and rejects trades without a defined stop."),
    ("Agent 6 — Journal Analyst", "Records simulated entries, exits, fees and outcomes."),
    ("Agent 7 — Master Coordinator", "Combines agent outputs and passes eligible signals to the paper engine.")
]
with st.expander("Meet the seven agents", expanded=True):
    for name, desc in agents:
        st.markdown(f"**{name}** — {desc}")

def simulate(days, start, fee, risk, seed):
    rng = np.random.default_rng(int(seed))
    n = days * 24
    # Synthetic prices are intentionally used: this is a demo, not actual crypto market data.
    returns = rng.normal(0.00005, 0.009, n)
    close = 60000 * np.exp(np.cumsum(returns))
    df = pd.DataFrame({"hour": np.arange(n), "close": close})
    df["fast"] = df.close.rolling(12).mean()
    df["slow"] = df.close.rolling(48).mean()
    df["signal"] = (df.fast > df.slow).astype(int)
    df["change"] = df.close.pct_change().fillna(0)
    balance = float(start)
    peak = balance
    rows = []
    position = None
    for i in range(49, len(df)):
        px = float(df.loc[i, "close"])
        sig = int(df.loc[i, "signal"])
        # Simple spot-style long/flat strategy. Stop and target are illustrative.
        if position is None and sig == 1 and int(df.loc[i-1, "signal"]) == 0:
            stop = px * 0.985
            target = px * 1.03
            risk_cash = balance * risk
            qty = risk_cash / max(px - stop, 1e-9)
            qty = min(qty, balance / px)
            entry_fee = qty * px * fee
            position = {"entry": px, "qty": qty, "stop": stop, "target": target, "entry_fee": entry_fee, "hour": i}
        elif position is not None:
            exit_reason = None
            if px <= position["stop"]:
                exit_reason = "Stop"
                exit_px = position["stop"]
            elif px >= position["target"]:
                exit_reason = "Target"
                exit_px = position["target"]
            elif sig == 0 and int(df.loc[i-1, "signal"]) == 1:
                exit_reason = "Signal exit"
                exit_px = px
            if exit_reason:
                gross = (exit_px - position["entry"]) * position["qty"]
                exit_fee = exit_px * position["qty"] * fee
                net = gross - position["entry_fee"] - exit_fee
                balance += net
                peak = max(peak, balance)
                rows.append({
                    "Entry hour": position["hour"], "Exit hour": i,
                    "Entry price": position["entry"], "Exit price": exit_px,
                    "Quantity": position["qty"], "Exit reason": exit_reason,
                    "Gross P&L (USDT)": gross, "Fees (USDT)": position["entry_fee"] + exit_fee,
                    "Net P&L (USDT)": net, "Result": "Win" if net > 0 else "Loss",
                    "Balance after trade": balance
                })
                position = None
    trades = pd.DataFrame(rows)
    return df, trades, balance

if run:
    prices, trades, final_balance = simulate(days, starting_balance, fee_pct, risk_pct, seed)
    st.session_state["results"] = (prices, trades, final_balance, starting_balance, days)
if "results" not in st.session_state:
    st.info("Choose settings on the left and tap **Run paper simulation**. This first version uses generated demo prices, not live market data.")
else:
    prices, trades, final_balance, starting_balance, days = st.session_state["results"]
    pnl = final_balance - starting_balance
    wins = int((trades["Net P&L (USDT)"] > 0).sum()) if len(trades) else 0
    losses = int((trades["Net P&L (USDT)"] <= 0).sum()) if len(trades) else 0
    win_rate = wins / len(trades) * 100 if len(trades) else 0
    gross_wins = trades.loc[trades["Net P&L (USDT)"] > 0, "Net P&L (USDT)"].sum() if len(trades) else 0
    gross_losses = abs(trades.loc[trades["Net P&L (USDT)"] < 0, "Net P&L (USDT)"].sum()) if len(trades) else 0
    pf = gross_wins / gross_losses if gross_losses else (float("inf") if gross_wins else 0)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Starting balance", f"${starting_balance:,.2f}")
    c2.metric("Final balance", f"${final_balance:,.2f}", f"{pnl:+,.2f} USDT")
    c3.metric("Return", f"{pnl/starting_balance*100:+.2f}%")
    c4.metric("Closed trades", len(trades))
    c5.metric("Win rate", f"{win_rate:.1f}%")
    st.subheader("Simulated price path")
    st.line_chart(prices.set_index("hour")["close"], height=240)
    left, right = st.columns(2)
    with left:
        st.subheader("Agent status")
        status = pd.DataFrame([
            {"Agent": n, "Status": "Demo active" if i not in (2,) else "Not connected / abstains"}
            for i,(n,_) in enumerate(agents)
        ])
        st.dataframe(status, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Risk and performance")
        st.metric("Profit factor", "∞" if pf == float("inf") else f"{pf:.2f}")
        st.metric("Winning trades", wins)
        st.metric("Losing trades", losses)
        st.metric("Total fees", f"${trades['Fees (USDT)'].sum():,.2f}" if len(trades) else "$0.00")
    st.subheader("Trade journal")
    if len(trades):
        st.dataframe(trades, use_container_width=True, hide_index=True)
        st.download_button("Download trade journal CSV", trades.to_csv(index=False).encode("utf-8"), "paper_trade_journal.csv", "text/csv")
    else:
        st.warning("No trades were closed in this simulation. Try another seed or longer period.")
    st.caption("This prototype uses synthetic prices and a basic moving-average strategy. Results are not real-market results and are not evidence of profitability.")

st.divider()
st.subheader("Before using real money")
st.markdown("""
- Do not add live trading keys to this prototype.
- Do not share exchange passwords, API secrets, recovery phrases or OTPs.
- A production version needs real market data, persistent storage, monitoring, tests, an exchange-specific paper/testnet connector, and an independent kill switch.
- Keep leverage and futures disabled during evaluation.
""")
