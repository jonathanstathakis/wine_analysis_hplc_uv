# Project README

## !!IMPORTANT!!

1. Need to run `cs_wide_to_long` to retrieve the "expected" data from the database. See [here](./notes/etl.md#amendments-to-the-final-loading-state) for more info.

## devnotes

See [devnotes](notes/devnotes.md)

## ETL

See [ETL](notes/etl.md)

## Analysis

See [analysis](./notes/analysis.md)

## Deconvolution migration

2024-05-20

Notes pertaining to the migration of my developed deconvolution-integration module from my fork of hplc-py. My approach has deviated far enough from the base code as to be almost unrecognizable under the hood, and further maintenance as a fork is not something I want to support. Thus the code will be integrated into the main package. The following tasks will need to be completed:

1. migration of module(s)
2. migration of tests
3. commit.

Debugging will come later. 

### 1. Migration of Modules

As I have decided to implement baseline correction through pybaselines rather than a home-grown solution, I do not need to migrate that submodule. I also do not want to include any of the Pandera validation overhead. Even the peak map module is an over-engineered monstrosity. In fact, those 'solutions' became so burdensome that I was unable to complete what is in effect a rather simple operation. It is as follows, in revese order:

1. Integrate peaks. to do so I need to deconvolve them, otherwise the heights and widths are false.
2. Deconvolution. To deconvolve, it is necessary to fit each peak to a model. the skew norm model requires the peak height, time, half width, and skew. To fit the convolved peaks, we need to tell the peak fitting program how well its guess matches, thus we append the convolved peak parameters together and fit that array. But deconvolution is expensive, so breaking the signal into small windows is more efficient (read makes it possible). Windows are defined by convolution, with window bounds are marked where no peaks are present. This is defined as a region without a mapped peak.
3. To map the peaks, we identify maxima, and draw a line at the base to either side of the peak, until the signal curve is encountered. This requires that the baseline is cleanly subtracted, and floating point errors are handled.

Now, information from the peak map is shared between the window map and deconvolution submodules. It doesnt have to be, but for the sake of DRY, it should be. Thus that data is reused. We also need to pass the signal AND measurements about the signal to these functions. Furthermore the deconvolution routine will need a report submodule to gauge the fit from the users perspective. I will then proceed by copy pasting the code as I go and finding requirements, removing dross where possible. 40 minutes to go.

90 minutes later and it is very evident that I will not be completing this within the time frame. I need to unit test each module as I migrate across, starting with the deconvolution. Deconvolving a 2 peak signal will be a good start. But how does one generate the data? Through the `_compute_skewnorm` function.

skewnorm equation:

$$
       \frac{2}{\omega \sqrt{2 \pi}} e^{-\frac{(x-\xi)^2}{2 \omega^2}} \int_{-\infty}^{\alpha\left(\frac{x-\xi}{\omega}\right)} \frac{1}{\sqrt{2 \pi}} e^{-\frac{t^2}{2}} d t
       $$

## deconvolution module dev log

2024-05-20 14:49:23 - development approach. The windowing is a convenience to handle larger than ideal datasets, and therefore should be left for last, and in fact we should perhaps calculate the peak properties twice, once for the windowing, and again for parameter measurement, as a way of decoupling the modules. Especially as we will be testing on a 2 peak signal. The same goes for baseline correction. In that case, the flow is: input parameter measurememt -> curve fit -> fit assessment -> integration. Calculating the fit paramters requires measuring the peak location, maxima, and half height width. But we can first test least squares with the input parameters used to generate the dataset.