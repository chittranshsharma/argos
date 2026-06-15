import sys
import os
sys.path.append(os.getcwd())
from app.database import get_signals

signals = get_signals('ab4d1d45-dc2a-441f-8d85-c65e1d14cb99', limit=10)
for s in signals:
    print(f"[{s.get('agent')}] {s.get('signal_type')} -> {s.get('subtype')}")
    print(f"  Title: {s.get('title')}")
    print(f"  Conf: {s.get('confidence')} | Imp: {s.get('importance')}")
    print("-" * 40)
print(f"Total found: {len(signals)}")
