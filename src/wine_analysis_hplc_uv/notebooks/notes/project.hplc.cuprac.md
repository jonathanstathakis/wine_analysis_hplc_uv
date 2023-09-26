# CUPRAC

## SOP

[CUPRAC SOP](chemistry_sop_cuprac.md)

## CUPRAC Reagent Formula

2023-05-08 18:52:55

backlink: [mres logbook](./mres_logbook.md#cuprac-reagent-formula)

1:1:1 mixture

1 M ammonium acetate in water
7.5 mM neocuproine in methanol
10 mM copper chloride dihydrate in water

1. weigh each reagent out for desired final volume.
2. dissolve each, should dissolve instantly.
3. Thats it.

give 20 mins to degas.

#### Setting up Infinity Stack for CUPRAC

2023-05-09 09:00:00

backlink: [mres logbook](mres_logbook.md#setting-up-infinity-stack-for-cuprac)

Going to use Jake's column as PCD so first step is to validate it against my column using coffee

- [x] start instrument
- [x] prepare coffe sample
- [x] inject on 38 min method.
- [x] swap columns over.
- [x] thermal equilib column.
- [x] inject on 38 min method.

#### test CUPRAC

- [x] prepare CUPRAC reagent.
- [x] plumb cuprac reagent -> degasser -> iso pump.
- [x] set up CUPRAC method including iso pump
- [x] test

##### CUPRAC Purge

very important to purge the CUPRAC lines with methanol after runs to avoid precipitate, consequenlty need to prime wiht CUPRAC before new runs. Generally 5 mins of priming.

Make shelf stable reagents in bulk, prep PCD daily 3 x equal parts.

if gna make 1L volume of solution..

see [This python file](../reagent_calculator.py) for a cuprac reagent tabulator for making up quantities.

## Verifying Performance of CUPRAC on Agilent Infinity Stack

backlink: [mres logbook](mres_logbook.md#verifying-performance-of-cuprac-on-agilent-infinity-stack)

2023-05-11 10:04:54

Lab day. To achieve today:

CUPRAC verified.

1. verify jake column matches my column performance using ultimo coffee as comparison standard.

38 min run.

1. [x]  Start up instrument, equilib.
2. [x] Place jakes column in heater as well.
3. [x] prep coffee
4. [x] 30 min later, run 38 min run.
5. [x] swap over to jakes column.
6. [x] 10 min equilib.
7. [x] 30 min run.
8. [x] compare by overlay.
9. [x]  While comparing, setup iso pump.

Iso pump plumbing:

Methanol -> degasser -> iso pump -> detector. See if anything is detected.

to plumb, will need to prepare capillaries.

1. [x] plumb methanol to degasser.
2. [x] plumb degasser to iso pump.
3. [x] purge for 30 mins.
4. [x] After purge, connect to detector, observe detection on flow.
5. [x] verify a ok.
6. [x] connect to radial port of column.
7. [x] observe signal.


#### CUPRAC

1. [x] prepare reagent.
2. [x] swap inlet to CUPRAC
3. [x] start flow, observe signal.
4. [x] inject coffee, observe signal.
5. [x] inject wine, observe signal.

### CUPRAC SOP

[CUPRAC SOP](chemistry_sop_cuprac.md#cuprac-sop)

## Problem: Sawtooth Pressure Curve

[mres logbook](mres_logbook.md#cuprac-experiment-problem---sawtooth-pressurse-curve)

2023-05-16 13:08:00

First cuprac run has encountered a sawtooth pressure curve on the bin pump during run, increasing in amplitude proportionate to the flow gradient. Some sort of issue introduced by the methanol, either the increased voscity, or an air bubble in the methanol line. Have disconnected the line and purged, and swapped out the crud catcher for a new one.

## Update on CUPRAC Experiments

2023-05-22 08:26:06

Friday's run was a complete success. 20 wines completed in 13 hours or so.

Today I will take it one step further and run the rest of the presently held samples + ambients.

27 runs in total, taking 14.0 hours. For this I will require 529.2mL of CUPRAC.

TODO:

- [x] start todays sequence
  - [x] draw up sequence table
  - [x] prep samples
  - [x] begin injection
- [x] figure out what wines were which from fridays sequence.
- [x] pull current data