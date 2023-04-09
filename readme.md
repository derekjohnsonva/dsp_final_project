# DSP Final Project

What is the DSP method or algorithm that you plan to implement?
* Band pass filter - This will help us to isolate interesting frequency ranges. 
* Butterworth filter - We will experiment with using this to smooth out noise captured during data collection.
* Peak Finder - This will help us to identify the dominant frequencies in our EEG signal

Signal Data.
For now, we plan on applying these techniques to sleep stage EEG data. This data is taken from a study looking at “slow-wave microconfinuity” during sleep1.

## Installation
`pip install -r requirements.txt`

## Super Useful Links (see my md file for other useful links)
The link below uses the [apply_function](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.apply_function) to modify data in-place. See my .ipynb file for an example.
- https://www.nmr.mgh.harvard.edu/mne/0.14/auto_tutorials/plot_modifying_data_inplace.html