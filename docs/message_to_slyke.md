Hi Slyke,

Quick update on XELIS Vault — we've been testing heavily on devnet and the core logic works. However, we hit several VM-level storage bugs that block us from shipping production-ready contracts. Main ones:

- Storage writes silently get dropped when mixed with system calls like get_caller, require, or get_deposit_for_asset (order-dependent)
- Address.to_string() and Hash.to_hex() always fail with "Expected opaque value"
- Returning a parameter instead of a constant after Storage::store() also drops the write

We worked around them (separate read/write handles, call get_caller first, return constants), but on-chain ownership checks and deposit verification aren't possible until these are fixed.

Can you confirm whether the May 30 network upgrade will resolve these issues? Specifically, will get_caller, require, get_deposit_for_asset, Address.to_string, and Hash.to_hex all work reliably in any order with load/store after the upgrade?

Thanks,
Adrien