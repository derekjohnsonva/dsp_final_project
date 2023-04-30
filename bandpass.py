import numpy as np
import mne
import matplotlib.pyplot as plt

class BandPassFilter:

    
    def filtering(rawData,lowerRange,upperRange,samplingFrequency):
        """
        Returns the time domain version of the input signal, with values outside of the specified frequency range filtered out
        
          Parameters
        ----------
        rawData    : time domain version of EEG data taken directly from the .get_data() method
        lowerRange : the lower band cutoff of the filter 
        upperRange : the higher band cutoff of the filter
        samplingFrequency : the sampling frequency of the signal

        Returns
        -------
        result : 1D array
            1D array of reconstructed and filtered time domain signal
        
        
        """
        signalLength=rawData.size
        
        #divide signalLength by sampling frequency to get len in seconds
        signalDuration = float(signalLength)/samplingFrequency

        eegFFT = np.fft.rfft(rawData)
        eegLen = eegFFT.size
        results = np.zeros((eegLen),dtype=np.complex_)
        
        startRange =int(lowerRange*signalDuration)
        endRange = int(upperRange*signalDuration)
        omegaK = (1+1j)

        for i in range((startRange-1),(endRange-1)):
            value = omegaK*eegFFT[i]
            results[i]=value
        inverseFFT = np.fft.irfft(results)
        return inverseFFT
        