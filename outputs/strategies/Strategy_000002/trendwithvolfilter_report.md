# Strategy Overview  
**Objective:** The TrendWithVolFilter strategy seeks to capture short‑term directional moves while avoiding assets that have experienced recent extreme tail events. It exploits the tendency of positive (negative) short‑term price slopes and returns to persist, provided tail risk is subdued (elevated). The construction combines a trend filter, a return filter, and a tail‑risk filter to generate directional bets with volatility‑scaled sizing.  

**In one sentence:** The model goes long (short) when short‑term momentum and returns are positive (negative) and recent tail risk is low (high), then exits on time, loss, profit, or spikes in realized volatility.  

**Core signal logic:**  
- `linear_slope_100 > 0` (or `< 0` for shorts) – short‑term trend direction.  
- `returns_100 > 0` (or `< 0` for shorts) – recent price performance.  
- `tail_returns_200 < 0` (or `> 0` for shorts) – tail‑risk filter.  

**Quick interpretation:**  
- **Longs:** Positive slope + positive 100‑day return + negative 200‑day tail return.  
- **Shorts:** Negative slope + negative 100‑day return + positive 200‑day tail return.  
- **Risk controls:** Exit on max 10‑day holding, 2 % stop loss, 4 % take profit, or realized volatility z‑score > 2.  

---  

# Long Entry Logic  
**Intuition:** When a security is trending upward and has delivered positive returns, a low tail‑risk signal suggests the move is not driven by a recent extreme shock, increasing the likelihood of continuation.  

**Conditions explained:**  
- `linear_slope_100 > 0` – the 100‑day linear regression slope is upward.  
- `returns_100 > 0` – cumulative return over the past 100 days is positive.  
- `tail_returns_200 < 0` – the 200‑day tail‑risk metric is negative, indicating limited recent extreme downside moves.  

**Mathematical form:** ` (linear_slope_100 > 0) and (returns_100 > 0) and (tail_returns_200 < 0) `  

**Why it works:** Positive short‑term momentum combined with recent gains signals trend persistence, while a low tail‑risk reading filters out assets that may be primed for a reversal due to hidden stress.  

---  

# Short Entry Logic  
**Intuition:** A downward slope together with negative recent returns points to a weakening market, and a high tail‑risk reading implies recent extreme downside pressure that may continue, making a short position attractive.  

**Conditions explained:**  
- `linear_slope_100 < 0` – the 100‑day linear regression slope is downward.  
- `returns_100 < 0` – cumulative return over the past 100 days is negative.  
- `tail_returns_200 > 0` – the 200‑day tail‑risk metric is positive, flagging recent extreme downside moves.  

**Mathematical form:** ` (linear_slope_100 < 0) and (returns_100 < 0) and (tail_returns_200 > 0) `  

**Why it works:** Negative momentum and recent losses indicate a weakening price path; a high tail‑risk signal confirms that stress is present, increasing the probability that the downtrend will persist.  

---  

# Exit Logic  
**Purpose:** To limit exposure duration, lock in gains, cut losses, and protect against sudden volatility spikes.  

**Components:**  
- Time‑based exit after `max_duration` days (10 days).  
- Stop‑loss exit when `pnl_since_entry <= -stop_loss` (2 % loss).  
- Take‑profit exit when `pnl_since_entry >= take_profit` (4 % gain).  
- Volatility‑triggered exit when `zscore(rs_vol_50) > 2`.  

**Mathematical rule:** ` days_since_entry >= max_duration or pnl_since_entry <= -stop_loss or pnl_since_entry >= take_profit or zscore(rs_vol_50) > 2 `  

**Lifecycle:** Typical trades close within a few days to the 10‑day cap; loss exits prune adverse moves early, profit exits capture the bulk of the trend, and the volatility filter prevents holding positions into turbulent periods, thereby compressing tail risk.  

---  

# Position Sizing  
**Rule:** ` base_risk_fraction * (rs_vol_120 / rs_vol_50) `  

**Intuition:** The base risk (1 % of portfolio) is scaled by the ratio of longer‑term realized volatility (120‑day) to short‑term realized volatility (50‑day). When short‑term volatility spikes, the denominator rises, reducing the size; when longer‑term volatility dominates, the ratio increases, allowing a modestly larger exposure.  

**Practical effect:** In high‑volatility regimes the position size contracts, limiting drawdown; in calm periods the size expands toward the `max_per_asset` ceiling of 6 %, preserving capital efficiency.  

---  

# Expected Behavior and Regime Sensitivity  
**Favorable regimes:**  
- Trending markets with moderate realized volatility.  
- Low tail‑risk environments where extreme moves are rare.  
- Periods of stable volatility clustering (volatility mean‑reverting).  

**Challenging regimes:**  
- Choppy, range‑bound markets that generate false trend signals.  
- Sudden spikes in realized volatility that trigger early exits.  
- Persistent high tail‑risk periods that suppress entry opportunities.  

**Insight:** Realized volatility exhibits clustering; the volatility‑scaled sizing naturally dampens exposure during volatility bursts, aligning risk with the underlying entropy dynamics of price movements.  

---  

# Factor Style Interpretation  
**Primary exposure:** Trend‑following (short‑term momentum).  

**Secondary exposures:** Realized volatility scaling, tail‑risk sensitivity.  

**Interpretation:** The strategy behaves like a classic momentum factor but is trimmed by a volatility‑adjusted risk budget and a tail‑risk filter, giving it a hybrid style that blends trend exposure with a defensive volatility hedge.  

---  

# Expected Trade Profile  
**Holding time:** Typically 2–10 days, bounded by the max‑duration rule.  

**Drawdown pattern:** Limited to the 2 % stop‑loss per trade; clusters of drawdowns may appear during volatility spikes before the volatility exit triggers.  

**Filter activity:** The tail‑risk filter blocks entries on roughly 20–30 % of assets in turbulent periods, while the volatility‑z‑score exit activates on about 5 % of open positions during spikes.  

---  

# Risk Diagnostics  
**Sensitivity:**  
- Model performance is sensitive to noise in short‑term slope and return estimates.  
- Regime shifts in volatility can increase exit frequency, reducing capacity.  
- Slippage may be higher on assets with rapidly changing volatility.  

**Structural risks:**  
- Prolonged low‑volatility environments may lead to over‑exposure as sizing inflates.  
- Extreme tail events that bypass the tail‑risk filter (e.g., black‑swans) can cause simultaneous stop‑losses across many positions.  

---  

# Assumptions and Limitations  
- Linear slope over 100 days reliably captures short‑term trend direction.  
- Tail‑risk metric (`tail_returns_200`) accurately reflects recent extreme downside pressure.  
- Realized volatility estimates (`rs_vol_50`, `rs_vol_120`) are stable and not contaminated by data lags.  
- The fixed stop‑loss and take‑profit thresholds are appropriate across all asset classes.  
- Model does not account for transaction costs or market impact, which may be material in high‑turnover environments.  

---  

# Source Alphas  
- **volatility_exit_signal_20251121_101437.yaml** – provides the `zscore(rs_vol_50) > 2` exit trigger.  
- **volatility_regime_20251121_101234.yaml** & **volatility_regime_20251121_101412.yaml** – inform the volatility scaling used in position sizing.  
- **tail_risk_filtered_trend.yaml** – defines the `tail_returns_200` filter that blocks extreme tail exposures.  
- **multi_horizon_trend_alignment.yaml** – underlies the `linear_slope_100` and `returns_100` momentum components.  
- **market_volatility_cross-affinity_20251121_102417.yaml** – contributes to the realized volatility calculations (`rs_vol_50`, `rs_vol_120`).  
- **volatility_regime_shift_signal_20251121_101259.yaml** & **volatility_regime_shift_indicator_20251121_101532.yaml** – support the dynamic adjustment of the `max_duration` and risk parameters in shifting regimes.  
- **low-volatility_trend_persistence_20251121_102707.yaml** – validates the persistence of trends in low‑vol environments, justifying the trend filter.  
- **volatility_conditioned_trend_carry.yaml** – reinforces the concept of scaling trend exposure by volatility ratios.