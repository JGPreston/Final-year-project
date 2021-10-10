from skimage.metrics import _structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import numpy as np



def returnValues(original, compare):
	original = np.array(original)
	compare = np.array(compare)
	
	return (psnr(original,compare), ssim.structural_similarity(original, compare)*100)

