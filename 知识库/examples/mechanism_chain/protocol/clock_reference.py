"""Continuous local clock anchor: physical drift and phase slew are separate."""
def slew_anchor(old_now,target_now,a_clock,a_fit,elapsed):
    # Values use seconds. The caller starts a new epoch on excessive phase errors.
    fit = min(1.0002,max(.9998,a_fit))
    limit = max(0,elapsed)*20e-6
    frequency = min(1.0002,max(.9998,a_clock+min(limit,max(-limit,fit-a_clock))))
    phase_rate = min(.01,max(-.01,target_now-old_now))
    return old_now,frequency+phase_rate,frequency
