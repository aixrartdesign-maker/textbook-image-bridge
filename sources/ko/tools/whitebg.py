import sys,glob,os
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
sess=ort.InferenceSession('/tmp/claude-0/-home-claude/0167432f-a877-5671-a0ae-ef5f130765fd/scratchpad/models/isnet.onnx',providers=['CPUExecutionProvider'])
inp=sess.get_inputs()[0].name
def matte(im):
    w,h=im.size
    x=np.asarray(im.convert('RGB').resize((1024,1024),Image.BILINEAR)).astype(np.float32)/255.0
    x=(x-0.5)/1.0
    x=x.transpose(2,0,1)[None]
    y=sess.run(None,{inp:x})[0][0][0]
    y=(y-y.min())/(y.max()-y.min()+1e-6)
    m=Image.fromarray((y*255).astype(np.uint8)).resize((w,h),Image.BILINEAR)
    return m
def whiten(src,dst):
    im=Image.open(src).convert('RGB'); a=np.asarray(im).astype(np.float32)
    m=np.asarray(matte(im)).astype(np.float32)/255.0
    # soft shadow: keep a faint, desaturated version of the original darkness under the object
    lum=a.mean(axis=2)
    # background estimate (border percentile)
    h,w=lum.shape; b=int(min(h,w)*0.04)
    border=np.concatenate([lum[:b].ravel(),lum[-b:].ravel(),lum[:,:b].ravel(),lum[:,-b:].ravel()])
    bg=np.percentile(border,60)
    shadow=np.clip((bg-lum)/bg,0,1)          # 0 where background, >0 where darker (shadows)
    shadow=np.asarray(Image.fromarray((shadow*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)/255.0
    bgcol=255-shadow[...,None]*70             # shadow max ~ 185 grey
    alpha=m[...,None]
    out=a*alpha+bgcol*(1-alpha)
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(dst,quality=93)
if __name__=='__main__':
    for src in sys.argv[1:]:
        whiten(src,'img_new/'+os.path.basename(src)); print('done',src)
