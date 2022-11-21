import os
from basicsr.archs.rrdbnet_arch import RRDBNet
from .realesrgan import RealESRGANer
from .realesrgan.archs.srvgg_arch import SRVGGNetCompact
import cv2


def algo(tile_size, upsampling_scale, animated, face_enhance_status, path_to_image):
    'Model names: RealESRGAN_x4plus | RealESRNet_x4plus | RealESRGAN_x4plus_anime_6B | RealESRGAN_x2plus | realesr-animevideov3'
    if animated:
        model_name = "RealESRGAN_x4plus_anime_6B"
        face_enhance = False
    else:
        model_name = "RealESRGAN_x4plus"
        if face_enhance_status:
            face_enhance = True
        else:
            face_enhance = False
    

    # determine models according to model names
    model_name = model_name.split('.')[0]
    if model_name in ['RealESRGAN_x4plus', 'RealESRNet_x4plus']:  # x4 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                        num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name in ['RealESRGAN_x4plus_anime_6B']:  # x4 RRDBNet model with 6 blocks
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                        num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name in ['RealESRGAN_x2plus']:  # x2 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                        num_block=23, num_grow_ch=32, scale=2)
        netscale = 2
    # x4 VGG-style model (XS size)
    elif model_name in ['realesr-animevideov3']:
        model = SRVGGNetCompact(
            num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu')
        netscale = 4

    # determine model paths
    model_path = os.path.join(
        'ai_upscaler/pretrained_models', model_name + '.pth')
    if not os.path.isfile(model_path):
        model_path = os.path.join(
            'ai_upscaler/realesrgan/weights', model_name + '.pth')
    if not os.path.isfile(model_path):
        raise ValueError(f'Model {model_name} does not exist.')


    tile_pad = int(10)
    pre_pad = int(0) # Pre padding size at each border
    fp32 = True # Use fp32 precision during inference. Default: fp16 (half precision).
    gpu_id = None # gpu device to use (default=None) can be 0,1,2 for multi-gpu

    img = cv2.imread(path_to_image, cv2.IMREAD_UNCHANGED)

    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        model=model,
        tile=tile_size,
        tile_pad=tile_pad,
        pre_pad=pre_pad,
        half=fp32,
        gpu_id=gpu_id)

    if face_enhance:  # Use GFPGAN for face enhancement
        from gfpgan import GFPGANer
        face_enhancer = GFPGANer(
            model_path='ai_upscaler/pretrained_models/GFPGANv1.3.pth',   
            upscale=upsampling_scale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=upsampler)

    try:
        if face_enhance:
            _, _, output = face_enhancer.enhance(
                img, has_aligned=False, only_center_face=False, paste_back=True)
        else:
            output, _ = upsampler.enhance(img, outscale=upsampling_scale)
        
        return output
    except RuntimeError:
        return 'memory_error'



# sdahdjssdasdasdasdasdasd
# sdasdasdasdasdasdasdasd
# sdasdasdasdasdasdasdasd
# sdasdasdasdasdasdasdasd

