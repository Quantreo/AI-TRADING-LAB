# Relative Peaks Proportion Explanation
- **Purpose:** The relative peaks proportion measures the percentage of time a financial instrument's price exceeds its recent peak value, adjusted by a multiplier.
- **How it works:** This feature calculates the highest price within a given window, normalizes current prices against these peaks, and then determines the proportion of prices that surpass the peak, applying a multiplier and smoothing the result with a moving average.
- **Inputs & Parameters:** 
  * `df`: the input DataFrame containing price data
  * `high_col`: the column name for high prices (defaults to 'high')
  * `peak_multiplier`: a multiplier for the peak value (defaults to 1.2)
  * `window_size`: the size of the moving average window (defaults to 5)
- **Use case:** A trader might use this feature to identify when an asset's price is consistently breaking through recent highs, indicating potential upward momentum or a trend reversal.
- **Interpretation:** High values indicate that the price frequently exceeds recent peaks, suggesting strong upward pressure, while low values indicate that the price rarely surpasses recent highs, possibly indicating a lack of momentum or a downward trend.