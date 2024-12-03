
# Status
* 2024-12-03: Placeholder SLO threshold values were set as a starting point before the 2024-12-03 "Client Success Working Group".  Input is needed on what other SLOs are needed, SLO target values, and the name.
* 2024-11-04: This is a sketch of a service class definition to represent data stored with Filecoin that also has an accompanying unsealed copy for retrieval. Key details like the threshold SLO values and even the name have not been determined or agreed upon.

# Intended Users
This service class is targeting users who 1) expect to retrieve at least some subset of their data at least weekly and 2) when they do retrieve, to have the first byte in under a second.

# SLOs
Dimension | SLI | Threshold
-- | -- | --
Retrievability | [Spark Retrieval Success Rate](../service-level-indicators/spark-retrieval-success-rate.md) | 90% per day
"(TBD) Durability" | ["(TBD) Sector Health Rate"](../service-level-indicators/sector-health-rate.md) | 95% per day

At least as of 202411, we're targeting a retrieval success rate of 90%, which seems low when compared to the "availability" guarantees that other cloud providers make.  This is for a few reasons:
1. Retrievability in this decentralized Filecoin context is quite different from availability in a web2 context.  Retrievability is being measured from a untrusted set of clients.  web2 availability is being measured from the server side, and thus has less uncontrollable variables.  
2. The [Spark Retrieval Success Rate docs](../service-level-indicators/spark-retrieval-success-rate.md) do a good job enumerating the various ways that results can be poisoned by malicious actors.  This lower-than-99+% target is to account for these possibilities.
3. This level of Spark RSR is already significantly higher than the level of retrievability that most SPs were offering in early 2024.  This SLO is moving SPs in a new direction, and it can be adjusted once a better threshold is determined.   

This "(TBD) sector health rat"e of 95% doesn't match the "durability" targets with many 9's that web2 providers have because:
1. They are different metrics.  web2 providers are looking at the durability of each byte written to their service which benefits from their infrastructure setup and erasure encoding.  
2. Often in the cases where a Storage Provider misses a PoSt, they meet it in future proving windows.  This means the data wasn't lost, but rather that a sector was not-proven to the network within its proving deadline.    
