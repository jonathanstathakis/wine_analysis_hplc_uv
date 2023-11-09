class SignalAnalyzer:
    def detect_peaks(
        self,
        df,
        grouper: str,
        target_col: str,
        peaks_colname: str,
        prom_ratio: float = 1,
        peak_finder_kws: dict = dict(),
    ):
        """
        implementation of scipy.signal.peak_finder to find peaks in a column by group. Provides a prominence coefficient in the form of 'prom_ratio' to define minimum prominence of peak as a ratio of the global maxima of the signal in question.

        args:

        df: long form dataframe with a column containing group labels to iterate over, and a column containing a signal with peaks

        target_col: the name of the column with the peaks

        peaks_colname: the name of the output column containing the peak maxima values aligned against the source column, i.e. a sparse column

        prom_ratio: peak prominance is defined as the distance of the projection between the peak and the slope of adjacent peaks (or a predefined window). Defining it as a ratio of the global maxima enables 'common sense' peak detection. Subjectively, 2% is where the peaks I expect to be counted are. See `scipy.signal.peak_prominances` for more information.

        peak_finder_kws: other `peak_finder` kws. see `scipy.signal.find_peaks`.
        """
        df = df.assign(
            **{
                peaks_colname: lambda df: df.groupby(grouper)[target_col].transform(
                    lambda x: x.iloc[
                        signal.find_peaks(
                            x, prominence=x.max() * prom_ratio, **peak_finder_kws
                        )[0]
                    ]
                )
            }
        )

        return df
