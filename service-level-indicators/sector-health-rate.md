# Sector Health Rate <!-- omit from toc -->

- [Meta](#meta)
  - [Document Purpose](#document-purpose)
  - [Versions / Status](#versions--status)
  - [Support, Questions, and Feedback](#support-questions-and-feedback)
- [TL;DR](#tldr)
- [Metric Definition](#metric-definition)
- [Implementation Details](#implementation-details)
  - [Path 1: Lotus RPC Calls](#path-1-lotus-rpc-calls)
  - [Path 2: Lily Events](#path-2-lily-events)
- [Appendix](#appendix)
  - [Callouts/Concerns with this SLI](#calloutsconcerns-with-this-sli)
  - [Related Items](#related-items)


# Meta

## Document Purpose

This document is intended to become the canonical resource that is referenced in [the Storage Providers Market Dashboard](https://github.com/filecoin-project/filecoin-storage-providers-market) wherever the “(TBD) Sector Health” graphs are shown.  A reader of those graphs should be able to read this document and understand the "Sector Health SLO”.  The goal of this document is to explain fully and clearly “the rules of the game”.  With the “game rules”, we seek to empower market participants - onramps, aggregators and Storage Providers (SPs) - to “decide how they want to play the game”.

## Versions / Status
SLI Version | Status | Comment
-- | -- | --
v1.0.0 | ![wip](https://img.shields.io/badge/status-wip-orange.svg?style=flat-square) | 2024-11-04: this was started as a placeholder to start moving the exploration work from https://github.com/davidgasquez/filecoin-data-portal/issues/79 over and to seed this repo with more than one metric definition.  It needs more review, and particularly SP feedback on the caveats of this metric.  It is not decided that "Sector Health Rate" is the right name or that this should be under "durability".  Agains, this current iteration was done to move fast so there is more skeleton in this repo before FDS 5.


## Support, Questions, and Feedback
If you see errors in this document, please open a PR.
If you have a question that isn't answered by the document, then ...
If you want to discuss ideas for improving this proposoal, then ...

# TL;DR
Filecoin has a robust mechanism already for proving spacetime on chain for each sector.  The proportion of successful proofs over time gives indication of the "durability" of data stored on these sectors.

# Metric Definition

On a daily basis and for each SP compute:
* `Number of Active Sectors`
* `Number of Faulted Sectors`

An SP's daily sector health rate is then

$$\frac{\text{Number of Active Sectors - Number of Faulted Sectors}}{\text{Number of Active Sectors}}$$

# Implementation Details
There are multiple ways to compute this metric.  Multiple options are outlined as they differ in self-service local reproducibility vs. scale.  

## Path 1: Lotus RPC Calls
Below explains the way to compute this method when using Lotus RPC class.

* This metric is computed based on a single sampling per SP per day.  This works because:
  1. A sector that is faulted stays in the fault state for a duration that is a multiple of 24 hours given a sector's state transitions in in and out of faulted state happens during the providing dealine for the sector.
  2. New sectors in a given day may get missed until the next day, but sectors aren't are not a highly transient resource flipping into and out of existence.  Since sectors tend to have a lifespan of months or years, not counting them on their first day isn't a significant impact on the metric with tiem.
* `Number of Active Sectors` is computed by getting the SP's Raw Power divided by the SP's sector size.
* `Number of Faulted Sectors` is computed by daily querying for the [`StateMinerFaults`](https://lotus.filecoin.io/reference/lotus/state/#stateminerfaults) for each SP with sectors.  

## Path 2: Lily Events
Below explains hoe an Filecoin blockchain event indexer like Lily can be used.  

TODO: fill this in or link to the corresponding Lily query in FDP?

# Appendix

## Callouts/Concerns with this SLI

For full transparency, a list of potential issues or concerns about this SLI are presented below. 

1. TODO: add items here

## Related Items
* https://github.com/davidgasquez/filecoin-data-portal/issues/79 - This is where exploration for this SLI was first done.