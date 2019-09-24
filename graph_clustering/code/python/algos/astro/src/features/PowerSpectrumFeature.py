import numpy.fft as npfft
import numpy as np
from src.features.FeatureHelper import FeatureHelper
from src.helpers.radialprofile import RadialProfile

class PowerSpectrumFeature(FeatureHelper):

    def __init__(self, image_shape, radial_width):
        self.radial_profile = RadialProfile(image_shape=image_shape, bin_size=radial_width)

    def __get_patch_power_spectrum(self, patch):

        FA = npfft.fft2(patch)
        FA_FBconj = npfft.fftshift(FA * np.conjugate(FA))
        trans = np.real(FA_FBconj)

        #profile = self.radial_profile.azimuthal_average(trans, binsize=blk)
        profile2 = self.radial_profile.azimuthal_average_new(trans)

        return profile2

    def process_patches(self, patches):
        d_clip = np.array([])
        num_vals = 0
        for i in range(len(patches)):
            patch = patches[i]
            ps = self.__get_patch_power_spectrum(patch)
            num_vals = len(ps)
            ps = ps[0:-1]
            d_clip = np.concatenate((d_clip, ps), axis=0)
        return d_clip, num_vals - 1


class RiftFeature(FeatureHelper):

    def process_patches(self, patches):
        pass


class IntensitySpinFeature(FeatureHelper):

    def process_patches(self, patches):
        pass

