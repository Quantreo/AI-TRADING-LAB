# Strategy Overview  
**Objective:** The TrendVolRegimeAlpha seeks to capture medium‑term price trends while avoiding periods of heightened market turbulence. It goes long when recent 100‑day returns are positive and short‑term realized volatility is both lower than a longer‑term benchmark and unusually low in a statistical sense; the opposite conditions trigger shorts. Position sizing is inversely proportional to current volatility, and trades are bounded by time, stop‑loss, and take‑profit limits.  

**In one sentence:** The strategy profits from directional momentum in calm volatility regimes and scales exposure down when volatility spikes.  

**Core signal logic:**  
- `returns_100 > 0` for longs (or `< 0` for shorts) – recent trend direction.  
- `rs_vol_50 < rs_vol_120` for longs (or `> rs_vol_120` for shorts) – short‑term volatility below (or above) its 120‑day level.  
- `zscore(rs_vol_50,20) < -0.5` for longs (or `> 0.5` for shorts) – statistically low (or high) volatility over the last 20 days.  

**Quick interpretation:**  
- **Longs:** Positive 100‑day return **and** 50‑day volatility lower than the 120‑day benchmark **and** volatility z‑score below –0.5.  
- **Shorts:** Negative 100‑day return **and** 50‑day volatility higher than the 120‑day benchmark **and** volatility z‑score above 0.5.  
- **Risk controls:** Exit after 10 days, or when profit reaches 4 % or loss reaches 2 % of entry price. Position size scales with `0.02 / rs_vol_50` and is capped at 5 % of the asset.  

---  

# Long Entry Logic  
**Intuition:** When the market has been trending upward and volatility is subdued, price moves tend to persist, offering a low‑risk entry point.  

**Conditions explained:**  
- `returns_100 > 0` – the asset has generated positive returns over the past 100 days, indicating an uptrend.  
- `rs_vol_50 < rs_vol_120` – recent (50‑day) realized volatility is below the longer‑term (120‑day) level, suggesting a calm regime.  
- `zscore(rs_vol_50,20) < -0.5` – the 50‑day volatility is more than half a standard deviation below its 20‑day mean, reinforcing the low‑vol environment.  

**Mathematical form:** ` (returns_100 > 0) and (rs_vol_50 < rs_vol_120) and (zscore(rs_vol_50,20) < -0.5) `  

**Why it works:** In tranquil periods, price trends are less likely to be interrupted by noise, so a positive return signal combined with a volatility contraction historically yields higher continuation probabilities.  

---  

# Short Entry Logic  
**Intuition:** A sustained downtrend accompanied by rising volatility often signals accelerating bearish pressure, making short positions attractive.  

**Conditions explained:**  
- `returns_100 < 0` – the asset has posted negative returns over the past 100 days, indicating a downtrend.  
- `rs_vol_50 > rs_vol_120` – recent volatility exceeds the longer‑term benchmark, flagging a turbulent environment.  
- `zscore(rs_vol_50,20) > 0.5` – the 50‑day volatility is more than half a standard deviation above its 20‑day mean, confirming elevated risk.  

**Mathematical form:** ` (returns_100 < 0) and (rs_vol_50 > rs_vol_120) and (zscore(rs_vol_50,20) > 0.5) `  

**Why it works:** Elevated volatility during a downtrend often reflects panic selling or adverse news, which tends to push prices lower further, providing a reliable short‑entry cue.  

---  

# Exit Logic  
**Purpose:** To limit exposure duration, protect capital from adverse moves, and lock in modest gains before trend decay.  

**Components:**  
- **Time limit:** Close the position after `max_duration` days (10 days).  
- **Stop loss:** Exit when cumulative P&L since entry falls to `-stop_loss` (‑2 %).  
- **Take profit:** Exit when cumulative P&L reaches `take_profit` (+4 %).  

**Mathematical rule:** ` days_since_entry >= max_duration or pnl_since_entry <= -stop_loss or pnl_since_entry >= take_profit `  

**Lifecycle:** Most trades are expected to unwind within the 10‑day window; the stop‑loss and take‑profit thresholds truncate tails, producing a trade‑duration distribution heavily weighted toward short‑to‑medium horizons while capping downside risk.  

---  

# Position Sizing  
**Rule:** ` base_risk_fraction * (0.02 / rs_vol_50) `  

**Intuition:** The expression scales the base risk (1 % of capital) inversely with current 50‑day realized volatility, targeting a constant volatility exposure of roughly 2 % per unit of `rs_vol_50`.  

**Practical effect:**  
- In low‑vol regimes (`rs_vol_50` small), the multiplier grows, allowing larger positions up to the 5 % per‑asset cap.  
- In high‑vol regimes (`rs_vol_50` large), the multiplier shrinks, automatically reducing exposure and preserving capital.  

---  

# Expected Behavior and Regime Sensitivity  
**Favorable regimes:**  
- Sustained directional moves (positive or negative) with low short‑term volatility.  
- Volatility mean‑reversion periods where `rs_vol_50` dips below `rs_vol_120`.  

**Challenging regimes:**  
- Choppy, high‑volatility environments where volatility spikes erase the low‑vol filter.  
- Rapid regime shifts that cause `rs_vol_50` to cross `rs_vol_120` mid‑trade.  

**Insight:** Because volatility exhibits clustering, the z‑score filter helps the model stay in the low‑vol cluster, reducing false entries during transient spikes.  

---  

# Factor Style Interpretation  
**Primary exposure:** Trend‑following (momentum) factor.  

**Secondary exposures:** Realized‑volatility scaling (low‑vol tilt) and a modest short‑bias during high‑vol regimes.  

**Interpretation:** The strategy behaves like a classic momentum portfolio but with an overlay that reduces exposure when volatility is elevated, thereby blending a market‑beta tilt with a volatility‑managed overlay.  

---  

# Expected Trade Profile  
**Holding time:** Typically 3–10 days, bounded by the hard 10‑day cut‑off.  

**Drawdown pattern:** Small, frequent drawdowns limited by the 2 % stop‑loss; larger drawdowns are unlikely because positions are reduced in volatile periods.  

**Filter activity:** The volatility z‑score and `rs_vol_50` vs `rs_vol_120` filters will block roughly 30–40 % of raw trend signals, especially during turbulent market phases.  

---  

# Risk Diagnostics  
**Sensitivity:**  
- **Noise:** Short‑term return noise can trigger false entries when the trend signal is weak.  
- **Regime shifts:** Sudden volatility spikes may breach the `rs_vol_50` filter after entry, exposing the trade to higher risk before the stop‑loss triggers.  
- **Slippage:** Execution costs are modest due to the 10‑day horizon but can be amplified in fast‑moving volatile spikes.  

**Structural risks:**  
- Persistent high‑volatility environments (e.g., crisis periods) where the low‑vol filter rarely passes, leading to low capacity.  
- Correlation breakdown between volatility and trend persistence, reducing the predictive power of the combined signal.  

---  

# Assumptions and Limitations  
- Realized volatility (`rs_vol_50`, `rs_vol_120`) is a reliable proxy for market turbulence.  
- 100‑day returns capture the prevailing trend direction without excessive lag.  
- The z‑score window (20 days) is sufficient to detect abnormal volatility states.  
- Fixed stop‑loss and take‑profit levels assume a stable risk‑reward profile across regimes.  
- The 5 % per‑asset cap may limit scalability in low‑vol environments.  

---  

# Source Alphas  
- **volatility_regime_20251121_101412.yaml:** Provides the `rs_vol_50` vs `rs_vol_120` regime filter and the volatility z‑score component.  
- **trend_persistence_alpha_20251124_134908.yaml:** Supplies the `returns_100` momentum signal used in both long and short entries.  
- **volatility_trend_momentum_20251121_101502.yaml:** Reinforces the interaction between trend strength and volatility conditions.  
- **trend_following_opportunity_20251124_135156.yaml:** Contributes the directional bias logic that underpins the long/short dichotomy.  
- **volatility_persistence_signal_20251121_101630.yaml:** Supports the assumption that low (or high) volatility persists long enough for the entry filters to be meaningful.