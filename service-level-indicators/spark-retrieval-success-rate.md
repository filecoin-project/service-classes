# Spark Request-Based (Non-Committee) Global Retrieval Success Rate <!-- omit from toc -->

- [Meta](#meta)
  - [Document Purpose](#document-purpose)
  - [Versions](#versions)
    - [Spark v1.0](#spark-v10)
    - [Spark v2.0](#spark-v20)
  - [Support, Questions, and Feedback](#support-questions-and-feedback)
- [TL;DR](#tldr)
- [Spark Protocol](#spark-protocol)
  - [Deal Ingestion](#deal-ingestion)
    - [Deal Eligibility Criteria](#deal-eligibility-criteria)
  - [Task Sampling](#task-sampling)
  - [Retrieval Checks](#retrieval-checks)
  - [Reporting Measurements to Spark-API](#reporting-measurements-to-spark-api)
  - [Evaluating Measurements with Spark-Evaluate](#evaluating-measurements-with-spark-evaluate)
  - [On-chain Evaluation and Rewards](#on-chain-evaluation-and-rewards)
- [Spark RSR Calculations](#spark-rsr-calculations)
  - [High level Spark RSR Figure](#high-level-spark-rsr-figure)
  - [Spark RSR by SP](#spark-rsr-by-sp)
- [Appendix](#appendix)
  - [Terminology](#terminology)
    - [Clients](#clients)
    - [Checker / Checker Node](#checker--checker-node)
    - [Committee](#committee)
    - [Eligible Deal](#eligible-deal)
    - [Retrieval Task](#retrieval-task)
    - [Round Retrieval Task List](#round-retrieval-task-list)
    - [Retrieval Result](#retrieval-result)
    - [Retrieval Task Measurement](#retrieval-task-measurement)
    - [Committee Retrieval Task Measurements](#committee-retrieval-task-measurements)
    - [Accepted Retrieval Task Measurement](#accepted-retrieval-task-measurement)
    - [Committee Accepted Retrieval Task Measurements](#committee-accepted-retrieval-task-measurements)
    - [Provider Retrieval Result Stats](#provider-retrieval-result-stats)
  - [Callouts/Concerns with this SLI](#calloutsconcerns-with-this-sli)
  - [Retrieval Result Mapping to RSR](#retrieval-result-mapping-to-rsr)
  - [Per Request (non-committee) Score vs. Committee Scoring](#per-request-non-committee-score-vs-committee-scoring)
  - [FAQ](#faq)
    - [Why is GraphSync used?](#why-is-graphsync-used)
    - [What improvements are planned for Spark retrieval checking?](#what-improvements-are-planned-for-spark-retrieval-checking)
    - [Why do checkers report back the storage clients that made the deal?](#why-do-checkers-report-back-the-storage-clients-that-made-the-deal)
    - [Why do IPNI outages impact SP RSR?](#why-do-ipni-outages-impact-sp-rsr)


# Meta

## Document Purpose

This document is intended to become the canonical resource that is referenced in [the Storage Providers Market Dashboard](https://github.com/filecoin-project/filecoin-storage-providers-market) wherever the “Spark Retrievability” graphs are shown. A reader of those graphs should be able to read this document and understand the “Spark Retrievability SLO”. The goal of this document is to explain fully and clearly “the rules of the game”.  With the “game rules”, we seek to empower market participants - onramps, aggregators and Storage Providers (SPs) - to “decide how they want to play the game”.

## Versions

### Spark v1.0

| Component | Version(s) |
| - | - |
| [IE smart contract](https://github.com/filecoin-station/spark-impact-evaluator) | `0x8460766edc62b525fc1fa4d628fc79229dc73031`
| [RSR smart contract](https://github.com/filecoin-station/spark-rsr-contract) | `0x620bfc5AdE7eeEE90034B05DC9Bb5b540336ff90`
| [fil-deal-ingester](https://github.com/filecoin-station/fil-deal-ingester) | [latest](https://github.com/filecoin-station/fil-deal-ingester/tree/main) |
| [spark-api](https://github.com/filecoin-station/spark-api) | [latest](https://github.com/filecoin-station/spark-api/tree/main) |
| [spark-evaluate](https://github.com/filecoin-station/spark-evaluate) | [latest](https://github.com/filecoin-station/spark-evaluate/tree/main) |
| [spark checker](https://github.com/filecoin-station/spark) | [latest](https://github.com/filecoin-station/spark/tree/main) |

### Spark v2.0

Spark v2.0 will bring support for DDO deals, which requires breaking changes. Learn more in [Spark v2 design & migration](https://spacemeridian.notion.site/Spark-v2-design-migration-115cdd5cccdb804ca4d1e0694c613318).

## Support, Questions, and Feedback

If you see errors in this document, please open a pull request.

If you have a question that isn't answered by the document, then review the [known issues](https://github.com/filecoin-project/service-classes/issues) and open a new one if your question is not covered yet. Mention `@filecoin-project/space-meridian` in the issue description.

If you want to discuss ideas for improving this proposal, then review [existing discussions](https://github.com/filecoin-project/service-classes/discussions/) and open a new one if your ideas are not covered yet. Mention `@filecoin-project/space-meridian` in the text.

# TL;DR

FIL Spark is a proof of retrievability protocol for verifying the retrievability of unsealed data stored with Filecoin Storage Providers, for the case where that data is intended to be publicly and globally accessible. Very simply, Spark works by randomly sampling CIDs stored on Filecoin and then retrieving them. The results of whether files are retrievable or not are recorded and can be aggregated over to calculate the Spark retrieval success rate (RSR) scores.

For Filecoin, at a network-wide view, the Spark RSR score simply shows the percentage of valid retrieval attempts that succeeded. The data can then be aggregated by Storage Provider, by Allocator or by Client to show the Spark RSR scores over files linked to these entities.

We will now go through the Spark protocol in more depth to show exactly how the Spark RSR scores are created. Where needed, we will provide links to more in-depth descriptions, issues and discussions.

# Spark Protocol

## Deal Ingestion

The first step in the Spark protocol is to build a list of all files that should be available for “fast” retrieval. When we say “fast”, we mean that this file is stored unsealed so that it can be retrieved without needing to unseal the data first.

At least as of January 2025, every night, a service operated by Space Meridian automatically runs a deal ingestion process ([Github](https://github.com/filecoin-station/fil-deal-ingester)) that scans through all recently-made storage deals in the f05 storage market actor and stores them as [Eligible Deals](#eligible-deals) in an off-chain Spark database, hosted by Space Meridian, the independent team that is building Spark. An Eligible Deal is the tuple `(CID, Storage Provider)`, where the CID refers to a payload CID, as opposed to a piece CID or a deal CID. A payload CID is the root CID of some data like a file. An [Eligible Deal](#eligible-deal)  indicates that the `Storage Provider` should be able to serve a fast retrieval for the payload `CID`.

In the future, and when Spark is compatible with Direct Data Onboarding (DDO), there will be real-time deal ingestion into the Spark Eligible Deal database when storage deals are made ([GitHub tracking issue](https://github.com/space-meridian/roadmap/issues/144)). This will mean that new SPs will not need to wait for up to a week to get a Spark score.

The end result of the Deal Ingestion step is a database of all Eligible Deals that should be retrievable.

### Deal Eligibility Criteria

Spark considers a deal as eligible for retrieval testing if it meets the following criteria:

1. `DealProposal.Verified` is `true`
2. `DealProposal.PieceCID` is set
3. The deal has not expired yet (`DealProposal.EndEpoch` is in the future)
4. `DealProposal.Label` field contains a string starting with one of the following prefixes:
   - `bafy`
   - `bafk`
   - `Qm`

## Task Sampling

Each round of the Spark protocol is approximately 20 minutes. At the start of each round, the [Spark tasking service randomly selects a set of records](https://github.com/filecoin-station/spark-api/blob/f77aa4269ab8c19ff64b9b9ff22462c29a6b8514/api/lib/round-tracker.js#L310) from all [Eligible Deals](#eligible-deal). We refer to each of these records as a [Retrieval Task](#retrieval-task) and, specifically, it is the combination of an Eligible Deal and a Round Id. We will also refer to the set of Retrieval Tasks in the round as the [Round Retrieval Task List](#round-retrieval-task-list). 

It is important for the security of the protocol that the Retrieval Tasks in each round are chosen at random. This is to prevent Spark checkers from being able to choose their own tasks that may benefit them, such as if an SP wanted to run lots of tasks against itself. We don’t yet use drand for randomness for choosing the Round Retrieval Task List but we would like to introduce that to improve the end-to-end verifiability ([Github](https://github.com/space-meridian/roadmap/issues/182)).

During each round, the Spark Checkers are able to download the current Round Retrieval Task List. You can see the current Round Retrieval Task List here: [http://api.filspark.com/rounds/current](http://api.filspark.com/rounds/current). 

**Which of the tasks in the Round Retrieval Task List should each Checker perform?**

A simple approach for testing all tasks in the Round Retrieval Task List would be to ask all Spark Checkers (i.e., currently people who are running [Filecoin Station](https://filstation.app)) to check whether or not they can complete each Retrieval Task in the round, by attempting to retrieve the CID from the Storage Provider. However, there are many thousands of Spark Checkers and it would be wasteful to ask them all to test every task in each round. This would also create a lot of unnecessary load on the SPs.

At the other end of spectrum, the protocol could ask only one Spark Checker to complete each Retrieval Task in the Round Retrieval Task List. This is also not advisable as we cannot trust individual Spark Checkers to act honestly, and even if, there are other factors outside of both the checker's and the SP's control - for example network partitions. If we trusted the results of individual checkers then you can imagine an adversary, who wants only a certain SP to prosper, to report positive results for that SP, and negative results for all other SPs. We need multiple checkers to perform each Retrieval Task so that the results can be compared.

The current approach lies between these two ends of the spectrum. By asking a subset of Spark Checkers to perform each of the Retrieval Tasks in the round, we can test far more deals in each round, avoiding unnecessarily load-testing an SP for one CID, while having enough Checkers perform the same test to build confidence in the result. Specifically, our confidence here is based on assumptions about what percentage of the network of checkers is acting honestly.

**How does the protocol orchestrate the Spark Checkers to perform different tasks from each other at random  such that each Task is completed by at least $m$ checkers?**

As previously mentioned, the checkers start each round by downloading the Round Retrieval Task List. For each task that’s in the List, the checker calculates the task’s “key” by SHA256-hashing the task together with the current dRand randomness, fetched from the [dRand network API](https://github.com/filecoin-station/spark-evaluate/blob/a231822d3d78e3d096425a53a300f8c6c82ee01f/lib/drand-client.js#L29-L33). Leveraging the wonderful properties of cryptographic hash functions, these hash values will be randomly & uniformly distributed in the entire space of $2^{256}$ values. Also, by including the randomness in the input alongside the Eligible Deal details, we will get a different hash digest for a given Eligible Deal in each round. We can define the `taskKey` as

```jsx
taskKey = SHA256(payloadCid + miner_id + drand)
```

Each Spark Checker node can also calculate the SHA256 hash of its Station Id. This is fixed across rounds as it doesn’t depend on any round-specific inputs. In the future, the protocol may add the drand value into the hash input of the nodeKey too.

```jsx
nodeKey = SHA256(station_id)
```

The checker can then find its $k$ “closest” tasks, using XOR as the distance metric. These $k$ tasks are the Retrieval Tasks the Spark Checker node is eligible to complete. Any other tasks submitted by the checker are dismissed.

```jsx
dist = taskKey XOR nodeKey
```

Note that, at the start of each round, the protocol doesn’t know which Spark Checkers will participate as there are no uptime requirements on these checkers. This means the Spark protocol can’t centrally form groups of checkers and assign them a subset of the Round Retrieval Task List. The above approach doesn’t make any assumptions about which checkers are online, but instead relies on the fact that the `nodeKeys` will be evenly distributed around the SHA256 hash ring, so that enough nodes will be assigned each task.

Following the above approach, for each Retrieval Task, there are a set of Checkers who find this task among their $k$ closest and they will attempt the task in the round. We refer to the set of checkers who attempt a Retrieval Task as the “[Committee](#committee)” for that task..

**How many tasks should each checker do per round? What value is given to $k$?**

The choice of $k$ is determined by Spark protocol logic that aims to keep the overall number of Spark measurements completed by the total network per round fixed.
This is important because
- We don’t want the number of requests that Storage Providers need to deal with to go up as the number of Spark Checkers in the network increases
- There needs to be enough nodes in each committee for its result to be considered reliable

In each round, the [Round Retrieval Task List data object](http://api.filspark.com/rounds/current) specifies $k$ in a field called `maxTasksPerNode`. At the start of each round, the [spark-api](https://github.com/filecoin-station/spark-api) service looks at the number of measurements reported by the network in the previous round, compares it against the desired value, and adjusts both maxTaskPerNode $k$ and the length of the Round Retrieval Task List for the new round.

The choices in each round for $k$ and the length of the Round Retrieval Task List also influence the size of the committee for each Retrieval Task. This is how we ensure each task is completed by at least $m$ checkers; the committee for each task is designed to include [between 40 and 100 checkers](https://www.notion.so/745b0e1020bb4000ac77acafee09e683?pvs=21) to make sure there are enough Measurements to add mitigations against malicious actors, but not too many that we load test the Storage Providers.

The Spark Checkers that are members of each committee will go on to make the same [retrieval checks](#retrieval-checks) in the round. Each committee member then publishes their results to the Spark API (see [Reporting Measurements to Spark-API](#reporting-measurements-to-spark-api)), which then calculates the honest majority consensus about the result of the Retrieval Task (see [Evaluating Measurements with Spark-Evaluate](#evaluating-measurements-with-spark-evaluate)).

Only the $k$ tasks that the reproducible checker task selection algorithm picks in each round are treated as valid and included in the Spark RSR calculation, all others are ignored.

## Retrieval Checks

Once the Spark checkers have determined the list of retrieval tasks they must perform in the round, they begin to run their checks.

There is an in-depth discussion on how this part of the protocol works here: [https://blog.filstation.app/posts/how-spark-retrieves-content-stored-on-filecoin](https://blog.filstation.app/posts/how-spark-retrieves-content-stored-on-filecoin)

Here is a summary taken from the blog post: 

A Spark Checker’s retrieval test of `(CID, providerID)` is performed with the following steps:

1. Call Filecoin RPC API method `Filecoin.StateMinerInfo` to map `providerID` to `PeerID`.
2. Call [`https://cid.contact/cid/{CID}`](https://cid.contact/cid/%7BCID%7D) to obtain all retrieval providers for the given CID.
3. Filter the response to find the provider identified by `PeerID` found in Step 1 and obtain the multiaddr(s) where this provider serves retrievals.
4. Retrieve the root block of the content identified by `CID` from that multiaddr using GraphSync or the [IPFS Trustless Gateway protocol](https://specs.ipfs.tech/http-gateways/trustless-gateway/) (over HTTP). It uses the protocol advertised to IPNI for the retrieval. If both protocols are advertised, then it chooses HTTP.
5. Verify that the received block matches the `CID`.

## Reporting Measurements to Spark-API

When the Spark Checkers have completed a retrieval and determined whether or not the CID is retrievable by following the above steps, they report their result, which we call a measurement to the Spark-API service. Spark-API ingests these measurements, batches them into chunks of up to 100k measurements, uploads each chunk to [web3.storage](http://web.storage)/Storacha, and commits the batch CID to the Spark [smart contract](https://github.com/filecoin-station/spark-impact-evaluator). We call this the [Spark-Publish logic](https://github.com/filecoin-station/spark-api/tree/main/publish).

<aside>
ℹ️

Failed retrieval attempts are also reported with a reason code for the failure reason. Failure reasons and how they map to RSR are covered in [Retrieval Result Mapping to RSR](#retrieval-result-mapping-to-rsr).

</aside>

## Evaluating Measurements with Spark-Evaluate

[Spark-Evaluate](https://github.com/filecoin-station/spark-evaluate) is the Spark service that evaluates each measurement to decide whether or not it is valid, and then further processes the valid results for later consumption. It listens out for on-chain events that indicate that the Spark Publish logic has posted a commitment on chain. It then takes the CID of the on chain commitment and fetches the corresponding measurements from Storacha.

Once Spark-Evaluate retrieves the measurements, it does “fraud detection” to remove all unwanted [Retrieval Task Measurement](#retrieval-task-measurement)s as summarized below:

| [Retrieval Task Measurement](#retrieval-task-measurement)s which are removed | Why removed? |
| --- | --- |
| Those for [Eligible Deal](#eligible-deal)s not in the round | To prevent checkers from checking any [Eligible Deal](#eligible-deal) of their choosing either to inflate or tarnish an SP’s stats. |
| Those which are for [Retrieval Tasks](#retrieval-task) that are not within the $k$-closest for a checker | Same principle as above.  It’s not good enough to pick any [Retrieval Task](#retrieval-task) from the [Round Retrieval Task List](#round-retrieval-task-list). |
| Those which are submitted after the first $k$ measurements from a given IPV4 /24 subnet. (i.e, The first $k$ [Retrieval Task Measurement](#retrieval-task-measurement)  within a IPv4 /24 subnet are accepted.  Others are rejected.) | Prevent a malicious actor from creating tons of station ids that are then used to “stuff the ballot box” from one node. IPV4 /24 subnets are being used here as a scarce resource. |

With these [Committee Accepted Retrieval Task Measurements](#committee-accepted-retrieval-task-measurements) that passed fraud detection, Spark Evaluate then performs the honest majority consensus.  For each task, it calculates the honest majority result from the task’s committee, and it stores this aggregated result in Spark’s DB. These aggregate results are called [Provider Retrieval Result Stats](#provider-retrieval-result-stats).  They are packaged into a CAR which will is stored with Storacha, and the CID of this CAR is stored on chain.

## On-chain Evaluation and Rewards

There are two final steps in the Spark protocol that pertain to how Spark checkers get rewarded for their endeavors. However, this is not important for this page where we simply want to know how the Spark RSR is calculated. You can find more details about the reward steps at [https://docs.filspark.com](https://docs.filspark.com).

# Spark RSR Calculations

## High level Spark RSR Figure

At this point of the protocol, we have a set of valid measurements for each round stored off chain and committed to on chain for verifiability. From this we can calculate the Spark RSR values.

Given a specific time frame, the top level Spark RSR figure is calculated by taking the number of all successful valid retrievals made in that time frame and dividing it by the number of all “contributing” valid retrieval requests made in that time frame.  When we say “contributing” retrieval requests, we mean all valid successful retrieval requests as well as all the valid retrieval requests that failed due to some issue on the storage provider’s end or with IPNI.  (See [Retrieval Result Mapping to RSR](#retrieval-result-mapping-to-rsr) for a detailed breakdown of failure cases that are “contributing”.)

$$
RSR = {count(successful) \over count(successful) + count(failure)}
$$

However, as you may notice, we have not used the honest majority consensus results in this calculation. Here we are counting over all valid requests. This is because there is an intricacy when it comes to using the committee consensus results.

To give an example to explain this, let’s say that a Storage provider only serves 70% of retrieval requests. Assuming that all Spark checkers are acting honestly, when the Spark checkers make their checks, 70% of each committee reports that the CID is retrievable from the SP, while 30% report that is is unretrievable. With honest majority consensus, this file is deemed to be retrievable. If we use the results of the honest majority consensus rather than the raw measurements, we lose some fidelity in the retrievability of data from this SP. Specifically, instead of reporting a Spark RSR of 70%, we report a spark RSR of 100%, which seems misleading.

We believe that the 70% value is more accurate, yet we also need committees to prevent fraudulent behaviour. Currently, we are storing both the committee based score as well as the raw measurement score and we plan to use the committee results as a reputation score by which to weight the measurements from checkers in a committee ([GH tracking item](https://github.com/space-meridian/roadmap/issues/180)).

## Spark RSR by SP

To calculate a Spark RSR for an SP in a given time frame, the Spark protocol:

1. takes all retrieval tasks that are linked to a given `providerID` in the time frame.
2. counts the number of successful [Accepted Retrieval Task Measurement](#accepted-retrieval-task-measurement)s (numerator)
3. counts the number of [Accepted Retrieval Task Measurement](#accepted-retrieval-task-measurement)s that should map to RSR (denominator)
4. divides the numerator by the denominator.

# Appendix

## Terminology

### Clients

Storage Clients (not Stations) who received datacap and made deals using that datacap.

### Checker / Checker Node

Nodes that do retrievability checks.  In practice, these are primarily Station nodes running the Spark module.

### Committee

[Checker / Checker Node](#checker--checker-node)s that have performed the same [Retrieval Task](#retrieval-task)  in a round

- Committees aren’t formed during tasking. Nodes pick tasks based on the hash of their self-generated id. The scheduler doesn’t assign tasks to nodes, because at the beginning of the round it doesn’t yet know who will participate.  See [Task Sampling](#task-sampling) for more info.

### Eligible Deal

- `(providerId, payloadCID, clients)`
    - Note: in the context of this doc, these are eligible deals for retrieval testing
    - Created during [Deal Ingestion](#deal-ingestion).
    - Created by [fil-deal-ingester](https://github.com/filecoin-station/fil-deal-ingester)
    - Consumed by [Task Sampling](#task-sampling)
    - Callout: we only have some of the payloadCIDs.  While there is at least one for every deal, deals with multiple payload CIDs only have one payload CID in the Eligible Deals DB.

### Retrieval Task

- `(roundId, providerId, payloadCID)`
    - For each round, randomly sourced from Eligible deals
    - Created during [Task Sampling](#task-sampling)
    - Created by [Spark Tasking Service](https://github.com/filecoin-station/spark-api/blob/f77aa4269ab8c19ff64b9b9ff22462c29a6b8514/api/lib/round-tracker.js#L310)
    - Consumed by
        - [Checker / Checker Node](#checker--checker-node) for performing [Retrieval Checks](#retrieval-checks)
        - Spark-Evaluate as part of [Evaluating Measurements with Spark-Evaluate](#evaluating-measurements-with-spark-evaluate)

### Round Retrieval Task List

- `[Retrieval Task]`
    - The set of retrieval tasks that were selected for a given round.
    - Downloaded by Checkers as part of [Task Sampling](#task-sampling)
    - Note: creation/consumption is the same as [Retrieval Task](#retrieval-task)

### Retrieval Result

- `(providerId, indexerResult, protocol, providerAddress, startAt, statusCode, firstByteAt, byteLength, carTooLarge, carChecksum, endAt, timeout)`
- These are the outcome of [Retrieval Checks](#retrieval-checks) and is the key data structure in a [Retrieval Task Measurement](#retrieval-task-measurement) .
- Not every Retrieval Result leads to a Retrieval Task Measurement (see components)
- Components:
    - RPC API call to convert MinerID to PeerID. If this fails, then no Retrieval Task Measurement is produced.
    - IPNI query
    - CAR transfer (includes DNS and TCP errors)
    - CAR validation
- Created by [Checker / Checker Node](#checker--checker-node)
- Consumed by Spark-Evaluate to determine the `retrievalResultCode` .

### Retrieval Task Measurement

- `(roundId, providerId, payloadCID, checkerId, retrievalResult)`
    - This is what is submitted by a [Checker / Checker Node](#checker--checker-node) for [Reporting Measurements to Spark-API](#reporting-measurements-to-spark-api).
    - Created during [Retrieval Checks](#retrieval-checks) and [Reporting Measurements to Spark-API](#reporting-measurements-to-spark-api)
    - Created by [Checker / Checker Node](#checker--checker-node)
    - Spark-API receives measurements and store them in the publishing queue.
    - Spark-Publish uploads them to Storacha.
    - Spark-Evaluate downloads the measurements and process them as part of the round evaluation.
    - Consumed by Spark-API

### Committee Retrieval Task Measurements

- `(roundId, providerId, payloadCID, retrievalTaskMeasurements)`
    - This is the set of ALL [Retrieval Task Measurement](#retrieval-task-measurement)s submitted by the network for a [Committee](#committee), including invalid/fraudulent measurements.
    - Created at the end of [Reporting Measurements to Spark-API](#reporting-measurements-to-spark-api)
    - Created by multiple by [Checker / Checker Node](#checker--checker-node)s
    - Consumed by Spark-Evaluate

### Accepted Retrieval Task Measurement

- `(roundId, providerId, payloadCID, checkerId, retrievalResult, retrievalResultCode, clients)`
    - A [Retrieval Task Measurement](#retrieval-task-measurement) that passes the fraud detection checks during [Evaluating Measurements with Spark-Evaluate](#evaluating-measurements-with-spark-evaluate)
    - Created during [Evaluating Measurements with Spark-Evaluate](#evaluating-measurements-with-spark-evaluate)
    - Created by Spark-Evaluate
    - Consumed by Spark-Evaluate

### Committee Accepted Retrieval Task Measurements

- `(roundId, providerId, payloadCID, checkerId, retrievalResult, retrievalResultCode, clients)`
    - The [Accepted Retrieval Task Measurement](#accepted-retrieval-task-measurement)s for a [Committee](#committee).
    - Created during [Evaluating Measurements with Spark-Evaluate](#evaluating-measurements-with-spark-evaluate)s.  This is what is stored off chain, with a pointer on chain.
    - Created by Spark-Evaluate
    - Consumed by Spark-Evaluate

### Provider Retrieval Result Stats

```jsx
{
  "date": "<YYYY-MM-DD>",
  "meta": {
    "rounds": [
      {
        "index": "<roundIndex>",
        "contractAddress": "<contractAddress>",
        // This is the "Retrieval Task List" for the round.
        "details": { "/": "<cid>" }
        // These are the "Retrieval Task Measurements" that are uploaded as part of "Reporting Measurements to Spark-API".  
        "measurementBatches": [{ "/": "<cid>" }, ...],
        "sparkEvaluateVersion": {
          "gitCommit": "<hash>",
        },
      },
      ...
    ]
  },
  "providerRetrievalResultStats": [
    {
      "providerId": "<providerId>",
      "successful": <n>,
      "total": <n>
    },
    ...
  ]
}
```

- Created by X on a daily basis as part of Y
- Consumed by anyone wanting to analyze or display SP retrievability performance.

## Callouts/Concerns with this SLI

For full transparency, a list of potential issues or concerns about this SLI are presented below.  Some of these have technical solutions with corresponding backlog items, and others are the result of deliberate design decisions.

1. The Spark protocol [is dependent on GLIF RPC nodes](https://github.com/filecoin-station/spark-api/blob/f77aa4269ab8c19ff64b9b9ff22462c29a6b8514/publish/bin/spark-publish.js#L12) to function properly.
    1. Potential problems
        1. Single point of failure: If GLIF’s API is down then the Spark protocol is unable to function properly and Spark scores are not updated. This can be mitigated by having multiple RPC providers but there are currently no other options that suffice.
        2. Delegated trust: Even if there a multiple RPC providers that can be used by the Spark protocol, this amounts to a centralised component in the Spark protocol, whose the end goal is a completely trustless decentralised protocol.
    2. Why is this the case?
        1. In Spark team’s experience there unfortunately is no other reliable endpoint.
2. Spark Publish doesn’t have any AuthN/AuthZ: In an ideal future state, Spark Checkers would sign their measurements so that we can build confidence and reputation around Spark Checker (Station) Ids. Without AuthN/AuthZ, it is easy to impersonate another checker since all `checkerId` are publicly discoverable by processing the publicly retrievable [Retrieval Task Measurement](#retrieval-task-measurement)s. 
3. Spark only checks on deals stored with datacap using the f05 storage market actor and the deal must have a “payload CID” label.  This means Spark v1 excludes DDO deals, which when last checked in October 2024, means that Spark is checking about 56% of deals.  Spark v2 which will ship in early 2025 will include DDO deals.
4. Spark API is receiving, aggregating, and publishing the checker results which are discoverable on chain.  Spark’s code is open-sourced, but there is trust that Spark isn’t doing additional result modifying like adding results for a checker that didn’t actually submit results. An individual Spark checker can verify that their own measurements have been included and committed to on chain. They can also rerun the Spark evaluate logic with all the measurements from the round.  
5. An SP gets credit for a retrieval even if they fail [IPFS trustless gateway HTTP retrieval](https://specs.ipfs.tech/http-gateways/trustless-gateway/) but succeed with GraphSync retrieval.  The concern with GraphSync only support is that there aren’t active maintainers for the protocol and that it is harder for clients to use than HTTP.  (See [Why is GraphSync used?](#why-is-graphsync-used) )
6. Verified deals are indexed on a weekly basis. As a result, it’s possible that the payload CID of a verified deal will not get checked for a week plus after deal creation.
7. Spark station ids are self-generated.  This means a checker can potentially have many station ids and then report results using a station id that passes “[fraud checks](#fraud-checks)”.  The limit on duplicate IPv4 /24 subnets helps prevent “stuffing/overflowing the ballot box” but it doesn’t prevent one from “poisoning it” with some untruthful failed results.  There is a [backlog item](https://github.com/space-meridian/roadmap/issues/180) to weight results by to-be-determined “checker reputation”.
8. Storage Providers can currently go into “ghost mode” where they don’t get any retrieval results reported, regardless if they actually are or aren’t retrievable.  They accomplish this by keeping retrieval connections open for longer than the round by making a “byte of progress every 60 seconds”.  This is because Spark checkers currently only have a “progress timeout”, not a “max request duration” timeout.  There is a [backlog item to fix this](https://github.com/filecoin-station/spark/issues/99).
9. Spark makes retrievability checks assuming public global retrievability.  It doesn’t support network partitions or access-controlled data.  As a result, SPs in China with storage deals will have a 0 retrieval success rate. 
10. Spark can only check retrievability of data that has an unsealed copy.  There currently is no protocol-defined way for requesting an SP unseal a sector and then checking for retrievability later.   
11. Per [Retrieval Result Mapping to RSR](#retrieval-result-mapping-to-rsr), an SP’s RSR can be impacted by areas outside of their control like IPNI.  See also  [Why do IPNI outages impact SP RSR?](#why-do-ipni-outages-impact-sp-rsr).
12. Checker traffic is pretty easy to differentiate from real traffic for a Storage Provider given checker traffic only requests the `payloadCid`. A SP can look at the [Round Retrieval Task List](#round-retrieval-task-list), see which tasks they are the listed "minerId" for, and then just make sure to serve the corresponding `payloadCid`s in that 20 minute period.  This would enable them to have 100% RSR even if they don't serve any other retrievals.

## Retrieval Result Mapping to RSR

When [Retrieval Task Measurement](#retrieval-task-measurement)s  are submitted into the Spark API, they are stored in Storacha and committed on chain as part of [Reporting Measurements to Spark-API](#reporting-measurements-to-spark-api) . Spark Evaluate then runs logic to determine which measurements are valid and contribute to the Spark RSR and which are not valid. The following table shows which retrieval result codes are contributing to the RSR calculation.

<table>
  <thead>
    <tr>
      <th>Retrieval Result Code</th>
      <th>Situations That Yield This Result</th>
      <th>Contributes to RSR?</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>OK</td>
      <td>The retrieval was successful.</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>RPC Failure</td>
      <td>
        JSON RPC service is:
        <ol>
          <li>unreachable OR</li>
          <li>not returning results OR</li>
          <li>returning empty results for a storage provider’s peerId
          after multiple timeout-bound attempts (5) with exponential backoff.</li>
        </ol>
      </td>
      <td>NO</td>
    </tr>
    <tr>
      <td>TIMEOUT</td>
      <td>
        A request is marked as timed out if no progress has been made for 60 seconds, where progress occurs if:
        <ul>
          <li>The connection has been established</li>
          <li>A byte has been received</li>
        </ul>
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>CAR_TOO_LARGE</td>
      <td>
        The root block is bigger than 200MB.<br />
        Notes:
        <ul>
          <li>At least as of 2024-10-21, this error isn’t observed.</li>
          <li>If it feeds into RSR, it is a way to poison an SP’s stats by doing a deal with an SP that has a payloadCid that is “too large”.</li>
          <li>If it is discarded from RSR, it is a way for SP to go into “ghost mode” (no metrics reported).</li>
        </ul>
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>UNSUPPORTED_MULTIADDR_FORMAT</td>
      <td>
        (<em>Trustless HTTP GW retrievals only.</em>)<br />
        The checker node was not able to convert the multiaddr found in the IPNI advertisement to an HTTP(S) URL. 
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>HOSTNAME_DNS_ERROR</td>
      <td>
        (<em>Trustless HTTP GW retrievals only.</em>)<br />
        When making an HTTP request to the address found in the IPNI advertisement, the checker node was not able to resolve the hostname into an IP address.
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>CONNECTION_REFUSED</td>
      <td>
        (<em>Trustless HTTP GW retrievals only.</em>)<br />
        When making an HTTP request to the address found in the IPNI advertisement, the remote server refused the incoming connection.
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>UNKNOWN_FETCH_ERROR</td>
      <td>
        (<em>Trustless HTTP GW retrievals only.</em>)<br />
        The checker could not make the HTTP request for reasons we don’t recognise yet. (Recognised reasons: HOSTNAME_DNS_ERROR and CONNECTION_REFUSED.)
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>UNSUPPORTED_CID_HASH_ALGO</td>
      <td>The checker could not verify the received content matches the requested CID - the CID uses a hash algorithm we don’t support (yet).</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>CONTENT_VERIFICATION_FAILED</td>
      <td>When the payloadCID bytes received from a storage provider don’t match the CID.  </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>UNEXPECTED_CAR_BLOCK</td>
      <td>The CAR file returned by the provider includes other blocks than the requested one.</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>CANNOT_PARSE_CAR_FILE</td>
      <td>The provider returned a malformed/corrupted CAR file.</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>IPNI_NOT_QUERIED</td>
      <td>An outdated (or fraudulent) checker node did not report the result of the IPNI query in the measurement it submitted.</td>
      <td>NO</td>
    </tr>
    <tr>
      <td>IPNI_NO_VALID_ADVERTISEMENT</td>
      <td>After calling IPNI to obtain all retrieval providers, if when filtering the response to find the provider, the provider isn’t present.</td>
      <td></td>
    </tr>
    <tr>
      <td>IPNI_ERROR_FETCH</td>
      <td>
        The HTTP request to IPNI failed at the networking level (e.g. DNS resolution failed, connection refused, etc.)<br />
        Reference: https://github.com/filecoin-station/spark/blob/8214ca93fd6cbab79e14e31bbaa2e22b584fb587/lib/ipni-client.js#L16-L29
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>IPNI_ERROR_{number}</td>
      <td>
        IPNI responded with HTTP status code <code>{number}</code>.<br />
        <code>IPNI_ERROR_404</code> - nobody advertised retrievals for this payload CID. (This is similar to IPNI_NO_VALID_ADVERTISEMENT described above.)
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>IPNI_???</td>
      <td>IPNI is not responding with results within timeout / retry allotment.</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>HTTP_{number}</td>
      <td>
        When the checker requested the CAR bytes using the Trustless HTTP Gateway protocol, the server (storage provider) responded with HTTP status code <code>{number}</code>.<br />
        Example codes: <code>HTTP_502</code>, <code>HTTP_504</code>.
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>LASSIE_${number}</td>
      <td>
        When the checker made an HTTP request to the local Lassie daemon handling GraphSync retrievals for Spark, Lassie responded with HTTP status code <code>{number}</code>.<br />
        Example codes: <code>LASSIE_502</code>, <code>LASSIE_504</code>.<br />
        Documentation for Lassie HTTP response status codes:
        https://github.com/filecoin-project/lassie/blob/main/docs/HTTP_SPEC.md#response-status-codes
      </td>
      <td>YES</td>
    </tr>
    <tr>
      <td>LASSIE_504</td>
      <td>Lassie encountered timeout while fetching the data from the storage provider. This does not happen in practice, because we configure Lassie timeouts to one day (24 hours) and then trigger the timeout on the Spark side after 60 seconds.</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>UNKNOWN_ERROR</td>
      <td>The retrieval check failed for a reason different from the ones described above. (This is a generic “fallback” code.)</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>CommitteeCheckError</td>
      <td></td>
      <td>NO</td>
    </tr>
    <tr>
      <td>Checker to Spark Publish Failure</td>
      <td></td>
      <td>NO</td>
    </tr>
  </tbody>
</table>

## Per Request (non-committee) Score vs. Committee Scoring

<table>
  <thead>
    <tr>
      <th></th>
      <th>non-committee (per request) scoring</th>
      <th>committee scoring</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Description</td>
      <td>
        <p>Every request made by a Spark checker feeds into the metric (after doing basic “fraud” detection”), regardless of whether the checker’s result aligns with its committee.</p>
        <p>For every <code>&lt;round, providerId, payloadCid&gt;</code>, the number of data points feeding into the SLI should be close to the size of the committee.  Committee size p50 is ~80, but it ultimately depends on depends on which nodes participate in the round. The aim is to have most committee sizes in the range of 40 to 100.</p>
      </td>
      <td>
        <p>Only the committee’s honest majority result for a <code>&lt;round, providerId, payloadCid&gt;</code> feeds into the metric.</p>
        <p>For every <code>&lt;round, providerId, payloadCid&gt;</code>, there will be a single datapoint feeding into the SLI.  (This is ~80x less data points than the non-committee case.)</p>
      </td>
    </tr>
    <tr>
      <td>Currently used by FIL+</td>
      <td>Yes</td>
      <td>No</td>
    </tr>
    <tr>
      <td>What it is sensitive to vs. what it obscures</td>
      <td>
        <p>Con: If a bad actor has 1% of the Spark Checkers and they always report that SPs fail, they can effectively bring every SP’s Spark RSR down by 1 percentage point.</p>
        <p>That seems too sensitive.</p>
        <p>Pro: assuming most checkers are honest, it will differentiate the SPs that 80% of the time respond to requests with valid/correct results vs. those that give 99+%.</p>
      </td>
      <td>
        Pro: Bad actors would need to have 51% of the Spark Checkers in a given randomly generated committee to have impact.<br /><br />
        Con: It the worst case (from a visibility regard), an SP could fail retrieval for 49% of requests but still have 100% committee retrieval success rate.<br /><br />
        I can’t imagine saying, “store with us!  99.9% of the time if you store with us one of two retrieval requests will succeed”
      </td>
    </tr>
    <tr>
      <td>Mitigations</td>
      <td>
        <ol>
          <li>Spark checkers are only paid if their result is the same as the honest majority.  (That said, since the pay out is small, this is not a big incentive.)</li>
          <li>Any results in a <code>&lt;round, providerID, payloadCID&gt;</code> from the same IPv4 /24 subnet are discarded as part of “fraud detection”.  This means an attacker can’t simply spin up a plethora of nodes on one machine or their local network, but would need to distribute across multiple IP addresses.  (Note that in 202410, the <a href="https://dashboard.filspark.com/">Spark dashboard</a> shows ~7k daily active checkers.)</li>
        </ol>
      </td>
      <td></td>
    </tr>
    <tr>
      <td>
        web2 cloud analog<br /><br />
        S3 produces an “error rate” for each 5 minute bucket.  This error rate is a value between 0 (no errors) and 1 (all requests “errored”).  It then calculates an uptime percentage based on the average “error rate” across all 5 minute periods in the month.
      </td>
      <td>Sort of.  We could calculate a value for each 5 minute period, and it will be a value between zero and one.  That said, to ensure there’s enough data points, we publish an SP’s “Spark retrieval success rate” each day based.</td>
      <td>No.  If we view committee rounds to being similar to S3’s 5 minute buckets, the stark difference is that Spark committee scoring is 0 or 1., not a value in between.</td>
    </tr>
  </tbody>
</table>

## FAQ

### Why is GraphSync used?

Given no-one is invested in maintaining and developing GraphSync, why is it used a transfer protocol for retrieval checking?  In 202410, Spark observes 2/3 of successful retrievals happen over GraphSync because SPs don’t support [IPFS HTTP Trustless Gateway](https://specs.ipfs.tech/http-gateways/trustless-gateway/).  We assume that HTTP numbers could be bolstered by UX and/or lack of documentation for Boost operators.

Future versions of spark retrieval checking (see [What improvements are planned for Spark retrieval checking?](#what-improvements-are-planned-for-spark-retrieval-checking)) will focus on HTTP-based retrieval.

### What improvements are planned for Spark retrieval checking?

See https://www.notion.so/spacemeridian/Spark-v2-design-migration-115cdd5cccdb804ca4d1e0694c613318?pvs=4.

### Why do checkers report back the storage clients that made the deal?

To support the FIL+ allocator compliance process, Spark was asked to provide RSR for storage clients and FIL+ allocators. To do that, Spark needs to link accepted measurements to storage clients that made the deal to store the data we tried to retrieve, similarly to how we link accepted measurements to storage providers.

### Why do IPNI outages impact SP RSR?

Per [Per Request (non-committee) Score vs. Committee Scoring](#per-request-non-committee-score-vs-committee-scoring), IPNI being unavailable will affect an SP’s retrievability.  This is a tough once since IPNI availability is outside of an SP’s control.  However, the Spark retrievability protocol is about getting the network to perform well, and if SPs scores are affected by IPNI going down, then this pushes IPNI to be vigilant. A code change could certainly be made so that IPNI failures don’t impact SP RSR, but this is the current status as of 2024-11-01.
