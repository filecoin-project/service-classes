# Filecoin Service Classes <!-- omit in toc -->

- [Purpose](#purpose)
- [Background](#background)
- [Service Classes](#service-classes)
- [Service Level Objectives](#service-level-objectives)
- [Service Level Indicators](#service-level-indicators)
- [Tenets](#tenets)
- [Conventions](#conventions)
  - [Abbreviations](#abbreviations)
- [Improvement Proposal Process](#improvement-proposal-process)
- [FAQ](#faq)
  - [Where is performance against a service class measured and presented?](#where-is-performance-against-a-service-class-measured-and-presented)
  - [How do SPs signal which service classes they are seeking conformance with?](#how-do-sps-signal-which-service-classes-they-are-seeking-conformance-with)
  - [How is "versioning" handled?](#how-is-versioning-handled)
  - [What is a "service class" vs. "storage class"?](#what-is-a-service-class-vs-storage-class)
  - [Why don't we use the term "SLA" currently?](#why-dont-we-use-the-term-sla-currently)


# Purpose
Houses definitions, discussions, and supporting materials/processes for Filecoin service classes, SLOs, and SLIs.

# Background

Storage clients have a diverse set of needs and as a result, storage providers like AWS, GCP, etc. have created a plethora of storage options to meet these needs.  At least as of 202410, Filecoin doesn’t articulate clearly what storage classes are supported, how we define them, and how we’re measuring against them.  Filecoin makes strong guarantees of replication with its daily spacetime proofs, but there are additional dimensions that storage clients want to have visibility into (e.g, retrievability,  performance).  This was a topic of conversation during [FIL Dev Summit #4](https://www.fildev.io/FDS-4), and a ["PMF Targets Working Group"](https://protocollabs.notion.site/Filecoin-PMF-Targets-Working-Group-111837df73d480b6a3a9e5bfd73063de?pvs=4) was started in 2024Q3 in an attempt to change this so storage clients can know what to expect and so the Filecoin ecosystem can clearly see opportunities to fill or improve.  In 202412, this work has shared with the "["Client Success Working Group"](https://protocollabs.notion.site/Filecoin-Client-Success-Working-Group-150837df73d480eabccff836d2553990?pvs=4) to get more feedback is what is needed by onramps and aggregators.  

# Service Classes

Service Class | Status
:--: | --
["(TBD) Warm"](./service-classes/warm.md) | 2024-12-03: This is a sketch of a service class definition to represent data stored with Filecoin that also has an accompanying unsealed copy for retrieval. Key details like the threshold SLO values have guessed placeholder values.  Input is needed on what other SLOs are needed, SLO target values, and the name.
["(TBD) Cold"](./service-classes/cold.md) | 2024-11-04: This is a placeholder service class to illustrate that there should be multiple service classes including one with slower retrievability than ["warm"](./service-classes/warm.md).  

* A service class is set of dimensions that define a type of storage.  “Archival” and “Hot” are a couple of examples with dimensions like "availability", "durability", and "performance".  These service class dimensions have various [SLOs](#service-level-objectives) that should be met to satisfy the needs of that service class.
* Service classes are defined in the [`service-classes` directory](./service-classes/).
* There are intended to be many service classes.  
* A service class should correspond with a set of expectations that a group of storage clients would have for certain data.  This group of storage clients would expect to see all the corresponding SLOs consistently met by an SP in order to store their corresponding data with that SP.  

# Service Level Objectives
* A Service Level Objective (SLO) is quality target for a service class.  It defines the “acceptable” value or threshold for a [SLI](#service-level-indicator).  They set expectations for a storage clients using the storage service, and then also give clear targets that storage providers need to hit and measure themselves against. 
* The SLO tuple of [SLI](#service-level-indicator-definitions) and corresponding threshold for a service classes are specified in the [`service-classes` directory](./service-classes/).
* The graph for an SLO should be the graph of the SLI and likely a horizontal line showing the threshold.

# Service Level Indicators

Service Level Indicator | Status
-- | --
[Spark Retrieval Success Rate v1](./service-level-indicators/spark-retrieval-success-rate.md) | ![review](https://img.shields.io/badge/status-review-yellow.svg?style=flat-square) this is the first SLI that has been worked to meet expectations both in terms of supporting documentation and being on chain.  It is expected to serve as an example for to-be-created SLIs.
["(TBD) Sector Health Rate"](./service-level-indicators/sector-health-rate.md) | ![wip](https://img.shields.io/badge/status-wip-orange.svg?style=flat-square) while this using the original proof of spacetime (PoSt) that has always been with Filecoin, the documentation for how the metric is computed and what it does and doesn't measure hasn't been developed.

* A Service Level Indicator (SLI) is a metric that measures compliance with an [SLO](#service-level-objectives). SLI is the actual measurement. To meet the SLO, the SLI will need to meet or exceed the promises made by the SLO.  
* SLIs are defined in the [`service-level-indicators` directory](./service-level-indicators/).

# Tenets
Below are tenets that have been guiding this work:

1. The "rules of the game" are knowable and discoverable - All participants in any markets created from this work should understand what is being measured, how it's being measured, what isn't being measured, etc. so they can reason appropriately about what something means and what actions to take if any.
2. Flowing from #1, SLIs must be on chain.  We are holding this line because:
   1. Forcing function for the data to actually get onchain.  Compromising to allow non-chain data to start has historically made it hard to then do the lift of actually get it on chain despite all the best intentions at the start.
   2. We get the benefit of onchain data, as in the immutability guarantees.  This is particularly important in an assumed future where these onchain “scores” will affect the reward structures of SPs.
3. Gatekeep on quality but not exploration - There isn't one group of people that knows what the authoritative list of service classes should be.  There should be room to explore,  Peer review and approval should be applied to make sure that proposed service classes and SLIs are well documented and explained more than deciding what are the right set.  
4. Make room for alternatives - This is related to exploration.  As a concrete example, we shouldn't discuss an unqualified "retrieval success rate" assuming there will only be a single SLI measuring retrieval.  Instead, SLIs should have proper qualification (e.g., "_Spark_ retrieval success rate") to make clear that there is opportunity for other "retrieval success rate" SLIs to emerge.

# Conventions
* If something has a placeholder name, it is usually wrapped in quotes and prefixed with `(TBD)` (e.g., "(TBD) Warm" for a to-be-named service class that stores data that is "warmer" than the "(TBD) cold" service class)

## Abbreviations
Throughout this repo, these abbreviations are used:
* SLI - [service level indicator](#service-level-indicators)
* SLO - [service level objective](#service-level-objectives)
* SP - storage provider, meaning the entity as defined in the Filecoin protocol with an individual id that commits sectors, accepts deals, etc.  We're not referring to a brand/company which might compose multiple providerIds/minderIds.

# Improvement Proposal Process
The process for proposing new service classes or SLIs, or modifying existing service classes and SLOs hasn't been determined yet.  This is something we hope to get more formalized during 202412 or 2025Q1.  ([Tracking issue](https://github.com/filecoin-project/service-classes/issues/11).)  

# FAQ
## Where is performance against a service class measured and presented?
The evaluation of an SP against a service class is expected to be done outside of this repo by any parties interested in doing so.  One example is https://github.com/filecoin-project/filecoin-storage-providers-market

## How do SPs signal which service classes they are seeking conformance with?
There currently isn't any way for an SP to opt in to some service classes and out of others.  We assume [measurement and presentation tools](#where-is-performance-against-a-service-class-measured-and-presented) will score SPs against all SPs and their historical performance will make clear what service classes they are actually targeting.

## How is "versioning" handled?
TODO; fill this in

## What is a "service class" vs. "storage class"?
The terms are synonymous in our context, but we are using the term "service class" since that is the industry norm.

## Why don't we use the term "SLA" currently?
“Service Level Agreement” is avoided for now because it means different things to different people.   For example, anyone in the storage world who uses S3 may have come to learn that [S3 only has one SLA](https://aws.amazon.com/s3/sla/), and it only pertains to service availability.  S3 has [other performance dimensions that it evaluates it storage products against](https://aws.amazon.com/s3/storage-classes/#Performance_across_the_S3_storage_classes), but there are no SLAs there.  An SLA is technically a legal contract that if breached will have financial penalty.  Filecoin the protocol doesn’t really have this currently except for proof of replication.  (Clients may have off-chain agreements with SPs.) To keep the conversation clearer for now, we’re focusing on service classes and their SLOs.  When there is actually reward and penalty for meeting these SLOs, we as a group can start introducing SLA terminology.  
