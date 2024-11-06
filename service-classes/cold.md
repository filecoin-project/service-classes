
# Status
* 2024-11-04: This is a placeholder service class to illustrate that there should be multiple service classes including one with slower retrievability than ["warm"](./service-classes/warm.md).  

# Intended Users
TBD

# SLOs
Dimension | SLI | Threshold
-- | -- | --
"(TBD) Durability" | ["(TBD) Sector Health Rate"](../service-level-indicators/sector-health-rate.md) | TBD% per day

* At least as of 202411, there isn't a "retrievability SLO" since it isn't known what sort of "retrievability" SLI should be created/used for the case where only a sealed copy is kept given there is no protocol-defined way for requesting an unseal operation to then do a retrieval check within a communicated-amount-of-time later.
