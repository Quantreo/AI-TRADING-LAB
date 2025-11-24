# Strategy Overview  
**Objective:** Capture sustained directional moves while filtering out spikes that are driven by extreme tail events. The strategy looks for aligned price momentum over a 100‑period horizon and backs it with a volatility‑scaled risk budget.  

**In one sentence:** Go long when both slope and recent returns are positive and tail returns are negative, and go short in the opposite configuration, exiting on time, stop‑loss or take‑profit limits.  

**Core signal logic:**  
- `linear_slope_100 > 0` and `returns_100 > 0` and `tail_returns_200 < 0` → long entry  
- `linear_slope_100 < 0` and `returns_100 < 0` and `tail_returns_200 > 0` → short entry  

**Quick interpretation:**  
- **Longs:** Positive trend slope + positive short‑term returns, provided the 200‑period tail return is not pulling the price up.  
- **Shorts:** Negative trend slope + negative short‑term returns, provided the 200‑period tail return is pushing the price up.  
- **Risk controls:** Fixed max holding of 10 days, 2 % stop‑loss, 4 % take‑profit, and size scaled by recent volatility.  

---  

# Long Entry Logic  
**Intuition:** A genuine upward move should exhibit consistent momentum (positive slope) and positive recent returns, while extreme tail spikes that could reverse quickly are excluded by requiring the longer‑term tail return to be negative.  

**Conditions explained:**  
- `linear_slope_100 > 0` – the 100‑period linear regression line is upward.  
- `returns_100 > 0` – price has risen over the last 100 periods.  
- `tail_returns_200 < 0` – the 200‑period tail‑risk metric is negative, indicating the move is not driven by a rare upward shock.  

**Mathematical form:** ` (linear_slope_100 > 0) and (returns_100 > 0) and (tail_returns_200 < 0) `  

**Why it works:** When momentum is confirmed across two horizons and tail risk is low, the price path tends to persist, reducing the likelihood of a sudden reversal caused by an outlier event.  

---  

# Short Entry Logic  
**Intuition:** Mirror the long logic: a genuine downtrend shows negative slope and returns, while a positive tail‑risk signal suggests the move is being amplified by an extreme downward shock, offering a shorting opportunity.  

**Conditions explained:**  
- `linear_slope_100 < 0` – the 100‑period regression line is downward.  
- `returns_100 < 0` – price has fallen over the last 100 periods.  
- `tail_returns_200 > 0` – the 200‑period tail‑risk metric is positive, indicating the decline is reinforced by a tail event.  

**Mathematical form:** ` (linear_slope_100 < 0) and (returns_100 < 0) and (tail_returns_200 > 0) `  

**Why it works:** Negative momentum paired with a tail‑driven boost signals a higher probability that the down move will continue, as extreme events often trigger cascading selling pressure.  

---  

# Exit Logic  
**Purpose:** Limit exposure duration and lock in gains or cut losses before tail‑driven reversals erode equity.  

**Components:**  
- Time‑based exit after a maximum of 10 days.  
- Stop‑loss trigger at a 2 % loss relative to entry.  
- Take‑profit trigger at a 4 % gain relative to entry.  

**Mathematical rule:** ` (days_since_entry >= max_duration) or (pnl_since_entry <= -stop_loss) or (pnl_since_entry >= take_profit) `  

**Lifecycle:** Most trades close within a few days as the profit target is hit; the time cap prevents lingering in stagnant markets, while the stop‑loss curtails tail‑risk blow‑outs.  

---  

# Position Sizing  
**Rule:** ` base_risk_fraction * (0.2 / rs_vol_50) `  

**Intuition:** Size is inversely proportional to the 50‑period realized volatility, so that risk‑adjusted exposure stays roughly constant across volatility regimes.  

**Practical effect:** In high‑volatility periods the denominator rises, shrinking the position; in calm markets the position expands up to the 5 % per‑asset ceiling.  

---  

# Expected Behavior and Regime Sensitivity  
**Favorable regimes:**  
- Trending markets with low to moderate tail‑risk signals.  
- Periods of stable realized volatility allowing larger positions.  

**Challenging regimes:**  
- Choppy or range‑bound markets where slope and returns frequently change sign.  
- Episodes of extreme tail spikes that flip the tail‑return sign, causing frequent signal suppression.  

**Insight:** Because tail‑risk metrics tend to cluster, the filter creates natural bursts of activity followed by quiet intervals, aligning the strategy with volatility clustering dynamics.  

---  

# Factor Style Interpretation  
**Primary exposure:** Trend following (price momentum).  

**Secondary exposures:** Realized volatility scaling, tail‑risk filtering (implicit convexity).  

**Interpretation:** The core momentum tilt captures the classic risk premium for bearing directional risk, while the volatility‑adjusted sizing adds a low‑volatility tilt and the tail filter introduces a modest bias toward assets with less extreme downside skew.  

---  

# Expected Trade Profile  
**Holding time:** Typically 3‑7 days; capped at 10 days.  

**Drawdown pattern:** Small, gradual drawdowns in volatile spikes; larger, abrupt losses only when tail‑risk filter fails to block a false signal.  

**Filter activity:** The tail‑return condition will block a noticeable fraction of otherwise qualifying entries during high‑tail‑risk periods, reducing turnover.  

---  

# Risk Diagnostics  
**Sensitivity:**  
- Model noise in slope and return estimates can generate false entries.  
- Regime shifts that alter tail‑risk dynamics may increase false positives.  
- Execution slippage, especially on the stop‑loss side, can erode the 2 % protection.  

**Structural risks:**  
- Prolonged low‑volatility environments may lead to oversized positions and hidden leverage.  
- Market crashes that simultaneously flip slope, returns, and tail metrics can produce simultaneous long and short signals, stressing risk limits.  

---  

# Assumptions and Limitations  
- Linear regression slope over 100 periods reliably captures trend direction.  
- Tail‑risk metric (`tail_returns_200`) accurately isolates extreme events.  
- Realized volatility (`rs_vol_50`) is a stable proxy for future risk.  
- No transaction cost model is embedded; high turnover in volatile regimes could impair net returns.  
- The fixed stop‑loss/take‑profit levels assume a roughly symmetric risk‑reward profile, which may not hold in all markets.  

---  

# Source Alphas  
- **tail_risk_filtered_trend.yaml** – provides the tail‑return filter used in entry logic.  
- **low-volatility_trend_persistence_20251121_102707.yaml** – informs the volatility‑scaled sizing.  
- **multi_horizon_trend_alignment.yaml** – contributes the 100‑period slope and return alignment.  
- **trend_persistence_20251121_171906.yaml** – reinforces the momentum premise.  
- **volatility_regime_shift_indicator_20251121_101532.yaml** – underlies the choice of a 50‑period realized volatility measure.  
- **trend_persistence_in_asset_sessions_20251121_171727.yaml** – supports the time‑based exit horizon.  
- **volatility_regime_20251121_101412.yaml** & **volatility_regime_20251121_101234.yaml** – validate the volatility scaling approach.  
- **entropy_conditioned_trend_follower.yaml** – adds conceptual backing for tail‑risk clustering.  
- **volatility_trend_momentum_20251121_101502.yaml** – complements the momentum‑volatility interaction.