import numpy as np
import mne
import matplotlib.pyplot as plt


class PeakFinder:
    def naive_logical_find_peaks(signal, min_distance=1, error=1e-6, minimum_peak_height=None):
        """
        Find peaks in a 1D array.

        Parameters
        ----------
        signal       : 1D array
        min_distance : minimum distance between peaks in signal
        error        : scales the adjustment of the signal to account for order of dataset

        Returns
        -------
        ind : 1D array
            indices of the peaks in `signal`

        """
        size = signal.size

        # Padding the begginning and end of the signal with a value
        # this makes sure that the first and last values of the signal are not peaks
        # and fixes out-of-bound errors
        pad = np.zeros(size + 2 * min_distance)
        pad[:min_distance] = signal[0] - error
        pad[-min_distance:] = signal[-1] - error
        pad[min_distance : min_distance + size] = signal

        # Any value could be a peak candidate
        peak_candidate_bools = np.zeros(size)
        peak_candidate_bools[:] = True

        for i in range(min_distance):
            start_before = min_distance - i - 1
            start_central = min_distance
            start_after = min_distance + i + 1

            x_before = pad[start_before : start_before + size]
            x_central = pad[start_central : start_central + size]
            x_after = pad[start_after : start_after + size]

            # A point is a peak candidate if it is larger than the points before and after it
            #   x_central > x_before and x_central > x_after
            temp_bools = np.logical_and(x_central > x_before, x_central > x_after)
            peak_candidate_bools = np.logical_and(peak_candidate_bools, temp_bools)

        # Find the indices of the peak candidates
        #   non-zero values of peak_candidate are the indices of the peaks
        ind = np.argwhere(peak_candidate_bools)
        ind = ind.reshape(ind.size)

        if minimum_peak_height is not None:
            ind = ind[signal[ind] > minimum_peak_height]

        return ind

    def naive_mathematical_find_peaks(signal, threshold=0):
        """
        Performs peak detection on three steps:
            1. root mean square
            2. peak to average ratios
            3. first order logic.

        Parameters
        ----------
        signal : 1D array
        threshold : positive number, optional (default = 0)
            detect peaks that are greater than `threshold`
            in relation to their immediate neighbors.

        Returns
        -------
        peak_indexes : 1D array
            indices of the peaks in `signal`

        Notes
        -----
        Strong underlying assumption about the distribution of the signal being distributed properly.
        """

        if threshold == 0:
            threshold = (max(signal) - min(signal)) / 4

        root_mean_square = np.sqrt(np.sum(np.square(signal) / len(signal)))
        ratios = np.power(np.divide(signal, root_mean_square), 2)
        peaks = (ratios > np.roll(ratios, 1)) & (ratios > np.roll(ratios, -1)) & (ratios > threshold)

        peak_indexes = []
        for i in range(0, len(peaks)):
            if peaks[i]:
                peak_indexes.append(i)
        return peak_indexes

    def peak_typing_finder(x, minimum_height=None, minimum_distance=1, threshold=0, edge="rising"):
        """Detect peaks in data based on their amplitude and other features.

        Parameters
        ----------
        x : 1D array
            data.
        minimum_height : {None, number}, optional (default = None)
            detect peaks that are greater than minimum peak height.
        minimum_distance : positive integer, optional (default = 1)
            detect peaks that are at least separated by minimum peak distance (in
            number of data).
        threshold : positive number, optional (default = 0)
            detect peaks (valleys) that are greater (smaller) than `threshold`
            in relation to their immediate neighbors.
        edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
            for a flat peak, keep only the rising edge ('rising'), only the
            falling edge ('falling'), both edges ('both'), or don't detect a
            flat peak (None).

        Returns
        -------
        ind : 1D array
            indices of the peaks in `x`.

        Notes
        -----
        heavily based on https://nbviewer.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb
        """

        if threshold is None:
            threshold = (np.max(x) - np.min(x)) / 4
        # find indexes of all peaks
        diff = np.diff(x)

        ind_none_edge, ind_rising_edge, ind_falling_edge = np.array([[], [], []], dtype=int)
        if edge is None:
            ind_none_edge = np.where((np.hstack((diff, 0)) < 0) & (np.hstack((0, diff)) > 0))[0]
        else:
            if edge in ["rising", "both"]:
                ind_rising_edge = np.where((np.hstack((diff, 0)) <= 0) & (np.hstack((0, diff)) > 0))[0]
            if edge in ["falling", "both"]:
                ind_falling_edge = np.where((np.hstack((diff, 0)) < 0) & (np.hstack((0, diff)) >= 0))[0]
        ind = np.unique(np.hstack((ind_none_edge, ind_rising_edge, ind_falling_edge)))

        """ Removing peaks that do not fit parameters """

        # first and last values of x cannot be peaks
        if ind.size and ind[0] == 0:
            ind = ind[1:]
        if ind.size and ind[-1] == x.size - 1:
            ind = ind[:-1]
        # remove peaks < minimum peak height
        if ind.size and minimum_height is not None:
            ind = ind[x[ind] >= minimum_height]
        # remove peaks - neighbors < threshold
        if ind.size and threshold > 0:
            diff = np.min(np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
            ind = np.delete(ind, np.where(diff < threshold)[0])
        # detect small peaks closer than minimum peak distance
        if ind.size and minimum_distance > 1:
            ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
            ind_remove = np.zeros(ind.size, dtype=bool)
            for i in range(ind.size):
                if not ind_remove[i]:
                    ind_remove = ind_remove | (ind >= ind[i] - minimum_distance) & (ind <= ind[i] + minimum_distance)
                    ind_remove[i] = 0  # Keep current peak
            # remove the small peaks and sort back the indexes by their occurrence
            ind = np.sort(ind[~ind_remove])

        return ind
