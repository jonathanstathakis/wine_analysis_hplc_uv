2023-11-05

XGBoost. Get it done.

- [x] get the data in memory
- [x] build the model
- [ ] analyse results

2023-11-05 18:56:37 - need to unpivot so that 'code_wine' and 'id' are labels and 'varietal' is a column

2023-11-06 08:50:20 - start with a 2 class problem, pinot noir vs shiraz. There are 11 of each in the dataset. Start with that then build up.

2023-11-06 09:28:41 - # recommended to use the scikit learn API: <https://www.kaggle.com/code/bextuychiev/20-burning-xgboost-faqs-answered-to-use-like-a-pro>

2023-11-06 09:48:38 - From wikipedia:

Multiclass classification solutions can be divided into one - vs. -rest (OvR) and one vs. one (OvO). OvR trains a classifier per class, OvO trains (K(K-1)/2), where K is the number of classes in the training set, and the classifiers are trained on pairs of classes from the training set.

2023-11-06 10:19:58 - Multiclass classification accuracy measures:

- Accuracy
- precision
- true positives
- true negatives
- false positives
- false negatives


<https://www.evidentlyai.com/classification-metrics/multi-class-metrics>:
- Accuracy is (correct predictions)/(all predictions)


2023-11-06 10:25:08 - problem 1: how to measure results?

2023-11-06 10:57:45 - all of the classifiers are producing the same mlogloss value of 0.69.., which is v. sus. To solve this im going to recreate a kaggle notebook with a similar problem and test my pipeline on that. Note that since im using a OOP pipeline, ive constructed it such that data acquisition and processing is seperate from modeling so that it swapping datasets should be straightforeward.

2023-11-06 11:50:23 - ok, for the iris set we're getting a 89% prediction accuracy. Now plug my dataset back in.

2023-11-06 12:18:12 - My trees are not building as expected, indicated by the lack of prediction variation. It is probably to do with how small the dataset size is vs the number of predictors, i.e. $p>>n$ where $p$ is columns and $n$ is rows.

Before looking into strategies to handle this, apply PCA to get the first x components and try modeling that. Strategies can be found at <https://machinelearningmastery.com/how-to-handle-big-p-little-n-p-n-in-machine-learning/>

2023-11-06 12:50:53 - working with dimensional data, $p>>n$ <https://carpentries-incubator.github.io/high-dimensional-stats-r/01-introduction-to-high-dimensional-data/index.html>

2023-11-06 13:11:34 - need to fit transformers to the train set distributions then transform both the train set and test set with that transformer instance seperately in order to have both sets in the same domain but avoid data leakage.

2023-11-06 13:12:30 - Even after PCA transformation reducing the set to 21 features we're getting the same results, an array of zeroes, meaning that all samples in the test set are always being predicted as pinot noir. what if we like.. double the size of the dataset.

2023-11-06 13:34:41 - duplicating the samples in my dataset of 'pinot noir', 'red_bordeaux blend', and 'shiraz' has produced a result! also, after multiple runs it appears to achieve a +70% accuracy. Not shabby for a first run. Now to instantiate a cross-validation to produce average performance scores, and see if we can explain why that worked. Note, removing the pca decomposition produces accuracy scores of +90%. We're overfitting so hard.

2023-11-06 13:43:39 - reducing the class size threshold to two which introduces 15 classes, for some reason the accuracy drops to 0.06 and all test samples are classified as CS even though its one of the smallest classes sizes. Weird. Going to three reduces the number of classes to 9, 

2023-11-06 13:59:03 - to implement CV with preprocessing, best way to do it is with scikit-learn pipelines. Will refactor the preprocessing to that API now.

2023-11-06 14:44:50 - I am getting absurdly high results both in and out of the pipeline, so I think it might be accurate for the dataset..

2023-11-06 14:47:04 - the manipulation of occurances of samples in the dataset is referred to as oversampling (as a verb) the opposite action - removing samples, is called undersampling. <https://www.techtarget.com/whatis/definition/over-sampling-and-under-sampling#:~:text=Over%20sampling%20is%20used%20when,occurrences%20in%20the%20minority%20class.> says that SMOTE is an approach to oversampling by cloning samples by feature distribution rather than direct duplication, apprently better.

2023-11-06 16:26:15 - `cross_validate` is the one to use, allows custom score selection amongst other options.

2023-11-06 16:28:22 - regarding the 0.5 result for the original dset, this post <https://datascience.stackexchange.com/questions/112642/why-xgboost-does-not-work-on-small-dataset> has the same result for a 1 feature dataset. Reply says `min_child_weight` modification helps. Says its happening because the model cant split the trees properly.

2023-11-06 17:46:28 - a range of 'min_child_weight' values had no effect on the outcome.
2023-11-06 19:23:46 - after initial broad grid search, still no effective splitting on the basic size dataset. Q: is total dataset size or class sizes?

2023-11-07 08:33:58 - Have found that there are no trees grown for a range of hyperparameter settings, so we're now looking for references to solve this problem. Need to find a combination of hyperparameters which enable splitting. <https://www.kaggle.com/code/rafjaa/dealing-with-very-small-datasets> recommends restricting max depth, increasing values of gamma, `eta`, `reg_alpha`, and `reg_lambda`

2023-11-07 09:22:04 - from <https://towardsai.net/p/l/multi-class-model-evaluation-with-confusion-matrix-and-classification-report> and <https://datascience.stackexchange.com/questions/15989/micro-average-vs-macro-average-performance-in-a-multiclass-classification-settin>:

- 'Micro' metrics refer to calculations of performance without consideration for the class the sample belongs to, then 'aggregating' the results (?)
- 'Macro' is unweighted mean of the measure for each class, taking the measurement within each class then averaging across classes
- 'Weighted' refers to accounting for the number of samples in a class when making measurements

For sets with class imbalance it is recommended to use 'micro' scores        

2023-11-07 10:00:04 - I have established methods of producing a easy-to-read pandas dataframe confusion matrix and classification report, and plot of the tree.

2023-11-13 09:22:38 - multiclass confusion matrix displays the expected values as columns and predicted values as rows. The values are the number of samples in that location, Where the diagonal is TP <https://www.v7labs.com/blog/confusion-matrix-guide#confusion-matrix-for-multiple-classes>

2023-11-06 12:35:46 - Preprocessing should be done AFTER splitting otherwise there is data leakage through
the distribution. Refer to <https://stackoverflow.com/questions/45639915/split-x-into-test-train-before-pre-processing-and-dimension-reduction-or-after>

2023-11-15 09:46:03 - Code is at a point where I can return to solving the problem of model building. Because of the stochastic nature of SMOTE, I need to run multiple runs to generate multiple datasets and observe the response.

2023-11-15 10:37:31 - Integrating SMOTE into the Pipeline will be the best way of handling the randomness as a new dataset will be generated every fold. Is this correct to do? I would assume that you'd want to include the synthetic sets across the training and validation sets. However, [this](https://vch98.medium.com/preventing-data-leakage-standardscaler-and-smote-e7416c63259c) and [this](https://beckernick.github.io/oversampling-modeling/) suggest that generating the synthetic data from the full dataset causes data leakage, thus oversampling should be done on the training set only, i.e. within the Pipeline. Ill action that now.

2023-11-15 11:35:16 - Problem. Running SMOTE after splitting is resulting in training sets too small to.. build.. what? I need to investigate this further.

2023-11-15 12:19:11 - Ok so, we need to make a flow chart of the process so we can track changes to the dataset. For example, at the moment introducing SMOTE into the pipeline is resulting in fold sizes of 6 or less, sometimes 1, as we dont understand how the set is being split.

2023-11-15 12:46:12 - 1 more hour then call it quits on modeling. I need to perform a PCA analysis on the datasets, and compare the CUPRAC and Raw data at their intersect.

2023-11-15 13:44:31 - another discussion of why SMOTE should not be used before CV: https://datascience.stackexchange.com/questions/82073/why-you-shouldnt-upsample-before-cross-validation

2023-11-15 13:44:35 - Why am I using gridsearchCV followed by another validation? Seems like im wasting samples for nothing. [stack overflow](https://stackoverflow.com/questions/40617257/sklearn-gridsearchcv-how-to-get-classification-report) suggests that the flow should be to train GridSearchCV on the whole dataset, then split the dataset into test and train sets, then fit to the training set and predict on the test to generate the classification report.

2023-11-15 15:43:49 - Ok, I've successfully integrated SMOTE into the pipeline, and acknowledged that you cannot use the grid search parameters to test resampling strategies as it is integrated into the object instantiation rather than fit_resample.. which doesnt make sense, but ok, weird dev choice. Thats it then. I'll need to manually iterate over resampling strategies to find one that works, which means that I should swap to CV for the best estimator scoring rather than a single fit in order to balance out the stochastic nature of the split.

There are multiple CV functions in sklearn, what is the difference? The module is `model_selection` and there is:
  - `cross_validate`
  - `cross_val_predict`
  - `cross_val_score`

  - `cross_validate` - contains a `scoring` argument that accepts iterables of strings refering to scoring metrics. It returns a dict of scores.
  - `cross_val_predict` - 'returns the labels from several distinct models undistinguished'. Good for viz, and model blending. - from sklearn.
  - `cross_val_score` - takes an average over cross-validation folds. Differs from `cross_validate` in that only 1 score is permitted.

ergo `cross_validate` is the more powerful of the two.

2023-11-15 17:08:07 - @amazonmachinelearning_2023 says that macro F1 score is an appropriate measure for multiclass problems. döring_2018 suggests that the weighted average is acceptable as well. @baeldung_2020 suggests F1 score. says the F1 score is the harmonic mean of precision and recall. @bromberg_2023 of Investopaedia says that the harmonic mean is the arithmatic mean of the reciprocals, and is useful when calculating averages of rates or ratios.`