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
2024-05-21 21:46:16 - back on track. Got distracted trying to upgrade to Python 3.12. Not fun. Done now. The next thing to do was to test the implementation of curve fit. To do that we'll need to save the test data to a file, then write a test to compare the code that generated the test data to the test data. if the code doesnt generate the same data, then that code has a bug, but it decouples downstream tests from that code dependency.
2024-05-21 22:53:19 - test data generation gtg. the test data generation script and an associated test module are complete. Next is to write the test data to an actual directory then test the curve fit function.
2024-05-22 08:11:15 - now I need to test curve fit. To do so I will generate p0 and bounds based on the input parameters that generated the test data in the first place. The bounds will be based on p0. So calculate p0 first as a random percentage between 10 and 30% + or - from the actual parameters, then the bounds as a further 30% of that. See how that goes. So itll require two objects - p0 and bounds, bounds being a container of two objects: lb and ub. Each of these will be a 4 element sequence of maxima, location, scale, skew. The two top level objects are passed to curve fit. The output is p_opt, whose skewnorms will then need to be calculated as individual peak signals. The peak signals will then need to be convolved (summed) again to produce the reconstructed signal. The reconstructed signal is then compared to the fitted signal. So that is three more functions after curve fit - skewnorm computer (producing the peak signals), model peak signal convoluter, and then fit assessor. That is also three more objects in  the main - the popt, the peak signals, the reconvolution, the fit report. The fit report will be based on AUC of the input signal vs. the reconstruction signal. AUC can be calculated with numpy trapz, inputting the x and y. Furthermore, we can use cremerlabs definition of the reconstruction score as (1+AUC_recon) / 1+ (AUC_inp).

to do:
-  [] test 1 curve fit:
       - [x] calculate test p0.
       - [x] calculate test bounds
       - [x] calculate popt
       - [x] compare popt to input, must be within threshold
 - [ ] test 2 reconstruction AUC analysis
       - [ ] write skewnorm computer
       - [ ] write reconstructor
       - [ ] write fit assessor
              - [ ] write area computer
              - [ ] write area comparer.

2024-05-22 11:33:49 - swapping back to frames. Once you get beyond a few arrays/dicts it just becomes easier to handle frames rather than dicts/arrays, as viz comparison becomes so important. Gna have to swap back to that.. So in that case I'll need a table with the following columns: peak, param, p0, lb, ub. That will be in the test scope for now.
2024-05-22 16:29:21 - Organising test dependencies. we've reached a point where the number of objects dependent on the seed parameters has become unmanagable. I will organise the dependent tables into a class with the different dependencies as attributes. I could avoid writing a class by organising the function names in the module to provide interfaces, but the class structure is simply easier to read. It provides an intuition.
2024-05-23 09:33:41 - Todays work. As I am essentially rewriting the deconvolution module and its tests, somewhat from scratch, this is taking longer than just: copy paste. Again, I'm doing this because the hplc-py fork has become massively over engineered. To provide a reasonable expectation for the days output, I will simply require that the reconstruction function is complete before I go to work today at 2pm. I need to set what seems like a meager goal because the addition of testing has added extra burden and stress. The root of it is that I dont know how to organise the tests and fixtures in a scalable manner, and I have no good sources to rely on.
2024-05-23 09:49:37 - solving my dependency problem. The problem is that my tests rely on fixtures, and fixtures cannot be used as normal python objects in actual scripts. And I want to be able to write test data to files using the same objects which are also fixtures. So you end up either writing fixtures as wrappers around actual objects or never writing the test data to file. Writing the data to a file makes it less bitter in the event of a total fuckup. The alternative to writing data to file is to write parametrized fixtures that produce the test data. So for example if i am writing a test to check whether a function computes a sum correctly, the fixture providing the test data may be seeded with a base level fixture containing the seed values. Or furthermore, a class which handles that logic internally, and a fixture providing access to either the attribute of the class, or an instance of the class. In the example of my p0, lb and ub tables, a class handling the logic internally is a useful way to go. Provides a branching structure internally, and multiple interfaces on one object.
2024-05-23 10:55:59 - pytest caching. Caching of expensive computations can be achieved through the `pytestconfig` object, [see here](https://docs.pytest.org/en/latest/how-to/cache.html). @pytest, @testing, @caching
2024-05-23 10:57:48 - a eureka moment. With the addition of caching, one should never write data to external files, as the files can (will) become stale over time, and the management of these files adds unecessary overhead. Cache expensive computations, everything is a fixture. This is the way. @pytest, @caching, @devnotes, @progress
2024-05-23 11:49:01 - formatter wars. I recently upgraded the project to Python 3.12, which has caused a number of dependency problems as I didnt check whether they supported this version. One such case is Black, the most ubiquitous Python formatter, which only supports up to 3.12. Luckily, Ruff does. As I dont have much care for Black, i'll replace it now. The main issue is updating the pre-commit hooks. Which is now done, an easy drop in replacement. Hooks are specified at pre-commit-config.yaml, the `pre-commit` package handles the rest. @devnotes, @formatting, @ruff, @black, @python.
2024-05-23 11:57:51 - Whats next. Now I need to test the reconstruction, reporting, and deconvolution package as a whole.

## Deconvolution Package Outline

test strategies:
       - assert execution: simply assert that the tested object exists. This method simply ensures that the code executes without error. A good first base, but very shallow.
       - result inversion: first run an 'assert execution' test, save the output to clipboard, create a fixture containing the output as an independent object, then test equality between the fixture object and the output of the 'assert execution' test. Very specific, does not shed light on why a test might fail. The natural evolution of an 'assert execution' test.

- PDF Computation:
       - Description: Taking a number of skewnorm parameters describing peaks present in a time series, construct pdfs for each peak along the sampling points 'x'.
       - parameters: skewnorm parameters for each peak as a 1d array in specific ordering
       - subprocesses:
              - bound computation TODO
              - initial guess computation TODO
              - failure handling TODO
       - output: wide pdf tensor as a pl DataFrame containing only the pdf, excluding 'x'. User can choose to add 'x' afterwards.
       - testing strategy: execution assertion, result inverion
- Reconstruction:
       - Description: Take a peak signal tensor and sum horizontally to produce a convoluted signal.
       - parameters: pl DataFrame wide of peak pdfs. 1d arrays in a collection
       - output: the summation of the input, a 1d polars Series named 'reconv'
       - testing strategy: execution assertion, result inversion
- Fit Assessment:
       - Description: compare two signals for equality and compute a number of metrics to assess how closely the two arrays match. It can be broken down into a number of sub processes - equality by auc ratio, and missed peak detection through fano factor.
       - parameters: two 1D arrays `left` and `right`, sampling points `x` and sampling windowing labels `window_type`, `window_idx`.
       - output: report table containing fit metrics for each window.
       - testing strategy: exection assertoin, result inversion. A good testing regeime would have one windowed signal and two reconstructions - one a almost perfect match, the other a poor match, and assert that the results match the expectations. But creating that mock data becomes in itself a pain. To generate a realistically poor match we would need to get the pdf parameters for each peak in the signal, the nmodify them slightly, generate the pdfs, and convolute. In this sense, this cycle of parameters -> pdfs -> convolution becomes a dependency of deconvolution testing through test data generation, and should have its own tests. And we already have the pdf scrambler which we used to generate p0, just have to modify the bounds, and extend it to include the reconstruction.

Thus, deconvolution becomes:
- Deconvolution:
       - description: compute a tensor of peak signal pdfs from an input convoluted signal by first detecting the peaks to assemble pdf parameters, then optimize the pdf parameters by fitting the convoluted signal through least squares.
       - input: an array containing a convoluted signal and an array of sampling points, 
       - components:
              - peak detection - TODO.
              - pdf computation 
                     - bound computation TODO
                     - initial guess computation TODO
                     - curve fit
                            - failure handling TODO
              - reconstruction - TODO.
              - fit assessment - TODO.
       - Description: Take an array of and an array of sampling points and output a tensor of the pdfs 
       fitted to all detected peaks.

- 2024-05-23 14:37:16 - pytest caching. As mentioned earlier, it is possible to cache fixtures across test runs. As explained [in the tutorial](https://docs.pytest.org/en/6.2.x/cache.html#the-new-config-cache-object), the cache is established through the request fixture, specifically `request.config.cache.set`, and accessed through `get` method of the same object. Handling cache updating is left for the user. The cachce can be viewed through `pytest --cache-show` on the CLI, and can be cleared through `pytest --cache-clear`. An immediate problem I can see is that it will not automatically update the cache if the inputs change. Could store a hash in one cache file, and acess the second one if the hash is the same, or replace it. In that case there is three scenarios: 1. no hash key present: write hash cache, write object cache. 2. hashes dont match: replace cashed hash, cached object, warn user. 3. hashes match: return cache. Or just raise an error, fail loudly. Either way, need to be able to hash the object. And Polars delivers - there is a hash_rows function. A trip hazard though - Pythons native hash method uses a random seed every run. The suggestion is to use hashlib. An example from [the docs](https://docs.python.org/3/library/hashlib.html#usage) is as follows: `hashlib.sha256(obj).hexdigest()` which outputs the expected hash string.
2024-05-24 02:06:26 - finalising caching. bit of a headache, but the caching is good to go. Had an issue with dataframes not being directly serialisable, but its done. Had to create a hasher class, and functions to handle the IO as the json string is not directly convertable to dataframe. its now 02:13, and I am tired. Tomorrow I will move on to the reconstruction process.