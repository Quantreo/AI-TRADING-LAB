import os, time, random

focuses = ["entry_signal","exit_signal","regime_indicator","risk_filter","position_sizing","volatility_regime", "trend_analysis"]
for _ in range(10):
    f = random.choice(focuses)
    os.system(f"python run_alpha_chain.py --focus {f}")
    time.sleep(20)
