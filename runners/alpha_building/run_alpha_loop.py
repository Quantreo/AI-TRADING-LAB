import os, time, random

focuses = ["trend", "volatility"]
for _ in range(10):
    f = random.choice(focuses)
    os.system(f"python run_alpha_chain.py --focus {f}")
    time.sleep(20)
