# Strategy Overview  
**Objective:** The VolTrendReturnAlpha seeks to capture short‑term directional moves by going long when recent 100‑day returns are positive and realized volatility is subdued, and going short when returns are negative and volatility is elevated. It filters out high‑vol regimes to lower risk while exploiting the tendency of returns to persist within low‑vol environments.  

**In one sentence:** Buy when returns are up and volatility is below its 20‑day average, sell when returns are down and volatility is above its 20‑day average, and exit via time or P&L limits.  

**Core signal logic:**  
- `returns_100 > 0` and `rs_vol_50 < sma(rs_vol_50, 20)` → long entry  
- `returns_100 < 0` and `rs_vol_50 > sma(rs_vol_50, 20)` → short entry  

**Quick interpretation:**  
- **Longs:** Positive recent returns + volatility lower than its 20‑day moving average.  
- **Shorts:** Negative recent returns + volatility higher than its 20‑day moving average.  
- **Risk controls:** Position size scales inversely with volatility; exits trigger on a 10‑day max holding, a 1 % stop loss, or a 2 % profit target.  

---  

# Long Entry Logic  
**Intuition:** In calmer markets, price trends tend to continue; a positive 100‑day return signal combined with low realized volatility suggests a stable upward move that can be safely ridden.  

**Conditions explained:**  
- `returns_100 > 0` – the asset has generated positive returns over the past 100 days.  
- `rs_vol_50 < sma(rs_vol_50, 20)` – current 50‑day realized volatility is below its 20‑day average, indicating a low‑vol regime.  

**Mathematical form:** ` (returns_100 > 0) and (rs_vol_50 < sma(rs_vol_50, 20)) `  

**Why it works:** Low volatility reduces the likelihood of abrupt reversals, allowing the positive return momentum to persist and generate incremental gains.  

---  

# Short Entry Logic  
**Intuition:** When markets are volatile and recent returns are negative, bearish pressure is reinforced; shorting in such high‑vol, down‑trend environments captures the downside while the volatility premium compensates for risk.  

**Conditions explained:**  
- `returns_100 < 0` – the asset has posted negative returns over the past 100 days.  
- `rs_vol_50 > sma(rs_vol_50, 20)` – current 50‑day realized volatility exceeds its 20‑day average, flagging a high‑vol regime.  

**Mathematical form:** ` (returns_100 < 0) and (rs_vol_50 > sma(rs_vol_50, 20)) `  

**Why it works:** Elevated volatility often accompanies accelerating price moves; coupling it with a negative return trend improves the odds that the down‑trend will continue, delivering short‑side profit.  

---  

# Exit Logic  
**Purpose:** To bound exposure time and lock in modest gains while preventing large losses.  

**Components:**  
- Time‑based exit after a maximum of 10 days (`days_since_entry >= max_duration`).  
- Stop‑loss exit when cumulative P&L falls to –1 % (`pnl_since_entry <= -stop_loss`).  
- Take‑profit exit when cumulative P&L reaches +2 % (`pnl_since_entry >= take_profit`).  

**Mathematical rule:** ` days_since_entry >= max_duration or pnl_since_entry <= -stop_loss or pnl_since_entry >= take_profit `  

**Lifecycle:** Most trades close within a few days as the 1 % loss or 2 % gain thresholds are hit; the 10‑day cap prevents lingering positions when the signal fades, ensuring a tight risk profile.  

---  

# Position Sizing  
**Rule:** ` base_risk_fraction * (0.02 / rs_vol_50) `  

**Intuition:** Position size is inversely proportional to current realized volatility; higher volatility shrinks the allocation, preserving the targeted risk budget.  

**Practical effect:** In low‑vol periods the denominator is small, so the multiplier approaches the upper bound (capped by `max_per_asset = 0.06`). In spikes of volatility the allocation contracts sharply, keeping exposure modest.  

---  

# Expected Behavior and Regime Sensitivity  
**Favorable regimes:**  
- Sustained low‑vol environments with positive return drift.  
- Persistent high‑vol environments paired with negative return drift.  

**Challenging regimes:**  
- Regime switches where volatility rapidly oscillates around its 20‑day average, causing frequent signal flips.  
- Sideways markets where returns hover near zero, generating false entries.  

**Insight:** Because volatility exhibits clustering, the 20‑day SMA filter tends to smooth short‑term spikes, allowing the strategy to stay in the “right” volatility regime longer and reduce whipsaw risk.  

---  

# Factor Style Interpretation  
**Primary exposure:** Trend‑following (return momentum).  

**Secondary exposures:** Realized‑volatility scaling (low‑vol tilt) and a modest short‑bias in high‑vol periods.  

**Interpretation:** The alpha behaves like a classic momentum factor but tempers exposure with a volatility‑adjusted risk budget, giving it a hybrid style that blends trend premium with a volatility‑managed overlay.  

---  

# Expected Trade Profile  
**Holding time:** Typically 2–5 days; capped at 10 days by the time‑based exit.  

**Drawdown pattern:** Limited to the 1 % stop‑loss per trade; occasional clustered losses may appear during abrupt regime shifts.  

**Filter activity:** The volatility filter blocks entries roughly 30‑40 % of the time in markets with frequent volatility spikes, reducing turnover in turbulent periods.  

---  

# Risk Diagnostics  
**Sensitivity:**  
- Model noise in `returns_100` and `rs_vol_50` can generate spurious signals.  
- Sudden regime changes may breach the volatility filter before the SMA catches up.  
- Execution slippage is modest due to the modest position sizes but can be amplified in thinly traded assets.  

**Structural risks:**  
- Prolonged low‑vol environments where the strategy stays long but market direction stalls, eroding returns.  
- Extreme volatility spikes that force rapid position scaling down, potentially missing upside moves.  

---  

# Assumptions and Limitations  
- Realized volatility (`rs_vol_50`) is a reliable proxy for near‑term risk.  
- The 20‑day SMA of volatility adequately separates low‑ and high‑vol regimes.  
- Linear scaling of position size captures the true risk‑return trade‑off.  
- Limitations: sensitivity to the look‑back windows (100‑day returns, 50‑day vol), potential lag in the SMA filter, and reliance on daily data granularity.  

---  

# Source Alphas  
- **volatility_trend_momentum_20251121_101502.yaml** – provides the `returns_100` momentum component.  
- **volatility_regime_shift_indicator_20251121_101532.yaml** – informs the volatility regime filter (`rs_vol_50` vs. `sma`).  
- **low‑volatility_trend_persistence_20251121_102707.yaml** – reinforces the low‑vol long bias.  
- **regime‑dependent_volatility_indicator_20251121_101348.yaml** – contributes to the dynamic sizing logic.  
- **trend_following_volatility_20251124_134933.yaml** – underpins the combined trend‑and‑volatility signal architecture.  
- Remaining alphas (e.g., volatility_momentum, trend_persistence_alpha) support the robustness of the momentum and volatility measurements used throughout the strategy.