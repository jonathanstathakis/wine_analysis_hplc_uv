# Wine Degredation Project - CUPRAC

*2023-06-21 14:11:56 more notes to be added here*

2023-05-09 - [Setting up Infinity Stack for CUPRAC](./project.hplc.cuprac.md#setting-up-infinity-stack-for-cuprac)

## Preparation for First Run

backlink: [mres logbook](./mres_logbook.md#preparation-for-first-cuprac-wine-deg-run)

2023-05-09 11:00:00

- [x] prepare vials
- [x] set methods/sequences.
- [x] prepare more reagent.
- [x] start sampling.

1 M ammonium acetate in water
7.5 mM neocuproine in methanol
10 mM copper chloride dihydrate in water

11.4 mL / sample. For an ambient run, 11.4 * 5 57 ml + 30 mL for purge etc, so 80 mL of CUPRAC

##### Planning CUPRAC Time Points

It would be useful to have the CUPRAC observation points at the same times as the raw uv/vis. To plan this:

- [x] get the wine data files.

#### Starting Cuprac Wine Deg Runs

2023-05-11 16:56:11

backlink: [mres logbook](mres_logbook.md#starting-cuprac-wine-deg-runs)

TODO:
- [x] prepare vials
- [x] prepare methods
- [x] prepare sequences
- [x] prepare file storage.
- [x]  to prepare the vials - same codes, just add c.
- [x] to prepare methods - same methods, just add iso pump, prefix with 'cuprac'.
- [x] to prepare sequences, same as above.
- [x] to prepare the file storage, copy the tree, delete the internal files, prefix with cuprac.

First ambient sqeuence - 

Ive got 200mL of CUPRAC. - 36mL from the three inital runs = 164mL.

(38 min runs + 2mins) * 0.3 = 12mL per run.

164 / 12 = 13.667 runs. Gotta be a multiple of 3, so 12 runs, or 4 time windows, total time = 8 hours.

Wanna space those runs out over time until someone gets in to shutdown the instrument, say 10am tomorrow.

Gotta do the single 3 runs first, so.. say 7:30pm start. 14.5hrs between then and 10pm, close enough to 16. thus I need to double the length of time between the runs.. while controlling for the flow.

12 runs in total, * 12ml CUPRAC per run = 144mL 

| time  | occurance | sequence | timedelta |
| ----- | --------- | -------- | --------- |
| 19:30 | start     | 1        | 00        |
| 23:30 | start     | 2        | 4:00      |
| 03:30 | start     | 3        | 4:00      |
| 07:30 | start     | 4        | 4:00      |
 
 5 freezer repeats

 cn0101 | ce0101
 cn0102 | ce0102
 cn0103 | ce0103
 cn0104 | ce0104
 cn0105 | ce0105
 cn0201 | ce0201
 cn0202 | ce0202
 cn0203 | ce0203
 cn0204 | ce0204
 cn0205 | ce0205
 cn0301 | ce0301
 cn0302 | ce0302
 cn0303 | ce0303
 cn0304 | ce0304
 cn0305 | ce0305
 
 2 ambient repeats

 ca0101
 ca0102
 ca0201
 ca0202
 ca0301 
 ca0302

2023-05-11 18:12:42

Start the first run.

2023-05-11 19:13:39

second wine started.

2023-05-11 20:08:15

third wine started.



TODO before I leave today:
- [x] top up cuprac
- [x] top up methanol
- [x] top up h2O
- [x] start overnight sequence.
- [x] clean up lab.

2023-05-11 20:57:47

ambient run first Sequence started.

Did a 100% methanol flush after the shiraz run and saw something come off the column. Seems as though the 2 min method flushes are not enough. increased the flush to 4min, bumping it up to 40 minutes, for each run. Since there are 24 runs itll now consume 0.6 * 24 = 14.4 ml extra. Just to double check, 24 runs * 40 minutes * 0.3 ml/min = 288 mls = 302.4..

2023-05-11 23:11:46

after starting the sequence (and topping up the bin pump phase solutions) there was a sawtooth pressure curve observed with an amplitude of ~100 psi. not great. see if it cleared up over the run.

2023-05-12 10:24:37

[SOP](chemistry_sop_cuprac.md#closing-sop)

2023-05-12 11:50:50

## CUPRAC Overnight Sequence Failure

Overnight sequence failed due to "not ready timeout". No clear indication of why, but the shutdown macro was not enabled, so the instrument kept running regardless.

2L of H2O at 0.95 ml/min provides me with 31 hours of runtime, btw.

Assuming that I am running 40 or so wines over the next 48 hours, I need to prep  864mL of CUPRAC reagents..

Start up has 7 minutes to go, need to:
- [x] prep 120mL of cuprac reagent.
[SOP](chemistry_sop_cuprac.md#closing-sop)
- [x] prep cuprac. 30 mins.
- [x] startup [SOP](#cuprac-sop) 30 mins.
- [x] run wine 3 ambient.

### Identifying Preciptate as Cause of Experiment Failure

So apparently precipitate formed and blocked the crud filter prior to the detector, causing the sequence to fail to engage. Because the shutdown macro was not enabled, the instrument just kept running.

### Dropping Injection Volume to 5uL

[mres logbook](mres_logbook.md#dropping-sample-injection-volume-for-cuprac-runs)

The solution is to drop the injection volume down to 5uL injection.

Tommorow ill be running approx 40 runs, which is 33.6 hours of runtime. at 0.3ml/min, that is 604mL of cuprac.

gna make a litre of each.

2023-05-12 13:11:30

|           | molar_mass | solvent | final_conc | required_vol | moles | mass (g) |
| :-------- | ---------: | :------ | ---------: | -----------: | ----: | -------: |
| cop_chlor |     170.48 | H2O     |       0.01 |            1 |  0.01 |   1.7048 |
| neocup    |     208.26 | MeOH    |      0.075 |            1 | 0.075 |  15.6195 |
| amac      |      77.08 | H2O     |          1 |            1 |     1 |    77.08 |

2023-05-12 14:06:26

Exiting lab.

I have started another run of ca0301, as I leave. I have asked corey to shut down the instrument once its done.

## CUPRAC Startup Methods

[mres_logbook](mres_logbook.md#establishing-cuprac-startup-methods)

2023-05-12 15:06:26

I have created ramp_up methods and sequences specific to CUPRAC which include the isopump being at 0.3ml/min steady. See how that goes.

## CUPRAC Reagent Batch

[mres logbook]

2023-05-12 15:08:26

I have prepared 3 x 1L volumetric flasks for CUPRAC reagent. Will ceate tomorrow, just needs a flush out with its specific solvent.

## Experiment Progress Update

[mres logbook](mres_logbook.md#cuprac-experiment-problem---sawtooth-pressurse-curve)

Have finished extreme freezer run 1. Had an issue with an air bubbl which delayed me for an hour. Have monopolized on this to make up 400mL of CUPRAC and set a swequence t run overnight.  it wil lontain all the normal freezer sequences + the misc wine selection from 2 weeks ago, the ones that got left out overnight. Its got a stop method at the end of the sequence and a post-sequence shutdown macro, either way as long as it gets there, itll shutdown. Sequence is called "WINE_DEG_NORM_FREEZER_AND_MISC_CUPRAC-.S". We will experiment with extracting the .D files and putting them in specific dirs, as this is a mix of experiments/research projects.