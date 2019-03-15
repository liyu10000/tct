import cv2

import numpy as np
import mxnet as mx
from collections import namedtuple
from skimage import io
# from utils.logger import Logger


class DNAMeasureCore(object):

    '''
    prefix : prefix of model name  
    epoch : number of iterations of the model. model name = prefix + '-' + epoch + '.params'
    
    seg_data_shape : initialize the network with input shape
    batch_size : batch size
    ctx : select gpu (mx.gpu(0))
    
    return : the unet model
    '''
    def __init__(self, prefix='segnet_bb5_final', epoch=0, seg_data_shape=128, batch_size=1, gpu="0"):

        self.prefix = prefix
        self.epoch = epoch
        self.seg_data_shape = seg_data_shape
        self.batch_size = batch_size
        self.ctx = mx.gpu(int(gpu))

        # build model done
        self.model_ascus = self.load_model(prefix, 0, seg_data_shape, batch_size, mx.gpu(int(gpu)), "ascus")
        self.model_other = self.load_model(prefix, 0, seg_data_shape, batch_size, mx.gpu(int(gpu)), "other")

    @staticmethod
    def load_model(prefix, epoch, seg_data_shape, batch_size, ctx, key):
        sym, arg_params, aux_params = mx.model.load_checkpoint(prefix + "_" + key, epoch)
        mod = mx.mod.Module(symbol=sym, context=ctx, data_names=['data'], label_names=None)
        mod.bind(for_training=False, data_shapes=[('data', (batch_size, 3, seg_data_shape, seg_data_shape))], label_shapes=None)
        mod.set_params(arg_params=arg_params, aux_params=aux_params)
        return mod

    '''
        img : input original image 
        mod : unet model
        return : predicted results
    '''
    @staticmethod
    def seg_img(img, mod):
        Batch = namedtuple('Batch', ['data'])
        cls_mean_val = np.array([[[0]],[[0]],[[0]]])
        cls_std_scale = 1.0
        raw_img2 = (img - np.mean(img))/(np.max(img) - np.min(img))
        img = np.transpose(raw_img2, (2,0,1))
        img = img[np.newaxis, :]
        img = cls_std_scale * (img.astype(np.float32) - cls_mean_val)
    
        mod.forward(Batch([mx.nd.array(img)]))
        pred = mod.get_outputs()[0].asnumpy()
        pred = np.argmax(pred, axis=1)[0]
        
        return pred

    '''
        pred : predicted results from seg_img()
    '''
    @staticmethod
    def find_max_contour(pred):
        if cv2.__version__[0] == '3':
            _, contours, hierarchy = cv2.findContours(pred, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        elif cv2.__version__[0] == '4':
            contours, hierarchy = cv2.findContours(pred, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        mask_contour = np.zeros_like(pred)
        cv2.drawContours(mask_contour, contours, 0, color=255, thickness=-1)
        return mask_contour, contours

    @staticmethod
    def non_zero_mean(np_arr):
#        assert np.array(np_arr).any()
        np_arr = np.array(np_arr)
        exist = (np_arr > 0)
        numer = np.sum(np_arr)
        den = np.sum(exist)
        
        if den == 0:
            return 0
        
        return numer/den
    
    
    @staticmethod
    def calc_sc_means(p_areas, p_grays):
        if len(p_areas) != len(p_grays):
            print("p_areas length is not equals to p_grays")
            assert False
        scarea_nonzero_mean = DNAMeasureCore.non_zero_mean(p_areas)
        scgray_nonzero_mean = DNAMeasureCore.non_zero_mean(p_grays)
#        sc_area_m = DNAMeasureCore.non_zero_mean(p_areas*(p_areas > 0.5*scarea_nonzero_mean))
#        sc_gray_m = DNAMeasureCore.non_zero_mean(p_grays*(p_grays > 0.5*scgray_nonzero_mean))    
        return scarea_nonzero_mean, scgray_nonzero_mean
    
    @staticmethod
    def calc_sc_median(p_areas, p_grays):
        if len(p_areas) != len(p_grays):
            print("p_areas length is not equals to p_grays")
            assert False
        sc_area_m =  np.median(p_areas)
        sc_gray_m = np.median(p_grays)
        return sc_area_m, sc_gray_m
        
        
    
    '''
        calc_gray
        img : original image
        mask : predicted image
    '''
    @staticmethod
    def calc_gray(img, mask):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = mask[:, :]
        area = cv2.countNonZero(mask)
        pts = np.where(mask > 0)
        gray_contour = gray[pts[0], pts[1]]
    
        gray_amount = 255*len(gray_contour) - sum(gray_contour)
       
        return area, gray_amount
        
    '''
        img : original images list
        mask : predicted masks list
        return : mean of area of cells, mean of gray of cells. area for each cell, gray for each cell
    '''
    @staticmethod
    def calc_gray_images(imgs, masks, contours, cellType = "SC", thre_gray = 0.8):
        Area = []
        Gray_amount = []
        sc_num = 0
        if len(imgs) != len(masks):
            print("imgs length is not equals to masks")
            assert False
            
        if  (cellType == "SC")|(cellType == "HSIL_S"):
            thre = 0.25
        elif cellType == "ASCUS":
            thre = 0.02
        else:
            thre = 0.20
            
        for i in range(len(imgs)):
            
            img = imgs[i]
            mask = masks[i]
            n2 = np.nonzero(mask)
            if( (len(n2[0])/(img.shape[0]*img.shape[1])) > thre ):
                
                contour = contours[i][0]
                mask_contour = np.zeros_like(mask)
                huul = cv2.convexHull(contour)

                cv2.drawContours(mask_contour, [huul], 0, color=1, thickness=-1)
                n1 = np.nonzero(mask_contour)
                n2 = np.nonzero(mask)
                catio = len(n2[0])/len(n1[0])
                
                if catio >= thre_gray:
                    area, gray_amount = DNAMeasureCore.calc_gray(img, mask)
                    Area.append(area)
                    Gray_amount.append(gray_amount)
                    sc_num = sc_num + 1
#        sc_area_m, sc_gray_m = DNAMeasureCore.calc_sc_median(Area, Gray_amount)
        sc_area_m, sc_gray_m = DNAMeasureCore.calc_sc_means(Area, Gray_amount)
        return sc_area_m, sc_gray_m, sc_num
    
    ''' 
        img : original image
        a :  coefficient a, img * a + b
        b :  coefficient b, img * a + b
        return :  contrast enhanced  image  
    '''
    @staticmethod
    def contrast_brightness_image(img, a = 1.8, b = -110):
        h, w, ch = img.shape
        src2 = np.zeros([h, w, ch], img.dtype)
        dst = cv2.addWeighted(img, a, src2, 1-a, b) 
        return dst
        
    ''' 
        img : original image
        a :  coefficient a, img * a + b
        b :  coefficient b, img * a + b
        return :  contrast enhanced  image  
    '''
    @staticmethod
    def contrast_brightness_images(imgs, a = 1.8, b = -110):
        if len(imgs) == 0:
            print("The length of images input is 0.")
            assert False
        
        Dst = []
        for img in imgs:
            
            dst = DNAMeasureCore.contrast_brightness_image(img, a = a, b = b)
            Dst.append(dst)
        return Dst
    
    '''
        img : input original images list 
        mod : unet model 
        return : predicted results list
    '''
    @staticmethod
    def seg_imgs(imgs, mod):
        if len(imgs) == 0:
            print("The length of images input is 0.")
            assert False
        
        if mod == None:
            print("The input unet model is None.")
            assert False
        h, w, ch = imgs[0].shape
        assert (h != 0)&(w != 0)
        Mask = []
        
        for img in imgs:
            mask = DNAMeasureCore.seg_img(img, mod)
            Mask.append(mask)
#        cv2.imwrite("results.jpg", 255*mask)
        return Mask
    
    '''
        pred : masks list
        return : masks with Maximum Connected Region
    '''
    @staticmethod
    def find_max_contour_imgs(preds, sc_imgs):
        if len(preds) == 0:
            print("length of predicted input is 0.")
            assert False
        Preds = []
        Countours = []
        i = 0
        for pred in preds:
            pred1, countour = DNAMeasureCore.find_max_contour(pred.astype(np.uint8))
            Preds.append(pred1)
            Countours.append(countour)
            
#            cv2.drawContours(sc_imgs[i], countour, 0, color=(255,0,0), thickness=1)
#            io.imsave("/home/sakulaki/Development/rls/unet/valid/results9/cells_hsil/" + str(np.random.rand()) + ".jpg", sc_imgs[i])

            i = i+1
        return Preds, Countours
    
    @staticmethod
    def hull_Eliminate(contours, pred_max):
        mask_hul = np.zeros_like(pred_max)
        huul = cv2.convexHull(contours[0])
        
        cv2.drawContours(mask_hul, [huul], 0, color=1, thickness=-1)
        #io.imshow(mask_contour1)
        
        cv2.drawContours(pred_max, contours, 0, color=1, thickness=-1)
        n1 = np.nonzero(mask_hul)
        n2 = np.nonzero(pred_max)
        catio = len(n2[0])/len(n1[0])
        return catio
    
    @staticmethod
    def coarseness(image, kmax):
        	image = np.array(image)
        	w = image.shape[0]
        	h = image.shape[1]
        	kmax = kmax if (np.power(2,kmax) < w) else int(np.log(w) / np.log(2))
        	kmax = kmax if (np.power(2,kmax) < h) else int(np.log(h) / np.log(2))
        	average_gray = np.zeros([kmax,w,h])
        	horizon = np.zeros([kmax,w,h])
        	vertical = np.zeros([kmax,w,h])
        	Sbest = np.zeros([w,h])
        
        	for k in range(kmax):
        		window = np.power(2,k)
        		for wi in range(w)[window:(w-window)]:
        			for hi in range(h)[window:(h-window)]:
        				average_gray[k][wi][hi] = np.sum(image[wi-window:wi+window, hi-window:hi+window])
        		for wi in range(w)[window:(w-window-1)]:
        			for hi in range(h)[window:(h-window-1)]:
        				horizon[k][wi][hi] = average_gray[k][wi+window][hi] - average_gray[k][wi-window][hi]
        				vertical[k][wi][hi] = average_gray[k][wi][hi+window] - average_gray[k][wi][hi-window]
        		horizon[k] = horizon[k] * (1.0 / np.power(2, 2*(k+1)))
        		vertical[k] = horizon[k] * (1.0 / np.power(2, 2*(k+1)))
        
        	for wi in range(w):
        		for hi in range(h):
        			h_max = np.max(horizon[:,wi,hi])
        			h_max_index = np.argmax(horizon[:,wi,hi])
        			v_max = np.max(vertical[:,wi,hi])
        			v_max_index = np.argmax(vertical[:,wi,hi])
        			index = h_max_index if (h_max > v_max) else v_max_index
        			Sbest[wi][hi] = np.power(2,index)
        
        	fcrs = np.mean(Sbest)
        	return fcrs
    

    
    def do_predict(self, images_dict, sc_num=0, sc_gray_m=0):
        '''
                calculate dna_ratio of cell image
    
                INPUT: dict, 
                    {
                        "SC": [
                            {
                                "xception_data_path": "*.npz",  # image data path, format => npz, use np.load(image_dict["xception_data_path"])['arr_0'] to read image
                                "dna_ratio": 100, # the part which should by replace, default = 100,
    
                                ...
                            },
                            {
                                "xception_data_path": "*.npz",  
                                "dna_ratio": 100, 
                                
                                ...
                            }
    
                            ...
                        ],
    
                        "ASCUS": [
                            {
                                "xception_data_path": "*.npz",  # image data path, format => npz, use np.load(image_dict["xception_data_path"])['arr_0'] to read image
                                "dna_ratio": 100, # the part which should by replace, default = 100,
    
                                ...
                            },
                            {
                                "xception_data_path": "*.npz",  
                                "dna_ratio": 100, 
                                
                                ...
                            }
    
                            ...
                        ]
                    }
    
                OUTPUT: dict, just like INPUT, replace value of "dna_ratio" with calculate result of your model
            '''
        # calculate sc area mean and gray mean 
        sc_imgs = []
        if 'SC' not in images_dict.keys():
            return images_dict, sc_num, sc_gray_m
        for i in range(len(images_dict['SC'])):
            sc_img = np.load(images_dict['SC'][i]['xception_data_path'])['arr_0']
            sc_imgs.append(sc_img)
        if len(sc_imgs) == 0:
            return images_dict, sc_num, sc_gray_m
        sc_imgs_b =  DNAMeasureCore.contrast_brightness_images(sc_imgs)
        sc_preds =  DNAMeasureCore.seg_imgs(sc_imgs_b, self.model_other)
        sc_preds_maxarea, sc_maxcountour =  DNAMeasureCore.find_max_contour_imgs(sc_preds, sc_imgs)
        sc_area_m, sc_gray_m, sc_num =  DNAMeasureCore.calc_gray_images(sc_imgs, sc_preds_maxarea, sc_maxcountour)
        
        if (sc_area_m == 0)&(sc_gray_m == 0):
            return images_dict, sc_num, sc_gray_m
        # calculate DNA ratios
        for key in images_dict:
            if key == 'SC':
                continue
            elif key == "ASCUS":
                model = self.model_ascus
            else:
                model = self.model_other
            
            for i in range(len(images_dict[key])):
                
                try:
                    img = np.load(images_dict[key][i]['xception_data_path'])['arr_0']
                    img_b = DNAMeasureCore.contrast_brightness_image(img)
                    img_pred = DNAMeasureCore.seg_img(img_b, model).astype(np.uint8)
                    mask, contour = DNAMeasureCore.find_max_contour(img_pred)
                    catio = DNAMeasureCore.hull_Eliminate(contour, mask)
                    if catio >= 0.85:
                        area, gray_amount = DNAMeasureCore.calc_gray(img, mask)
                        images_dict[key][i]['dna_area_ratio'] = (area/sc_area_m).astype(np.float32)
                        images_dict[key][i]['dna_gray_ratio'] = (gray_amount/sc_gray_m).astype(np.float32)
                        cv2.drawContours(img, contour, 0, color=(255,0,0), thickness=1)
#                        io.imsave("/home/sakulaki/Development/rls/unet/valid/results9/华银第三次测试删除0.9以下测试/" + images_dict[key][i]['xception_data_path'].split('/')[-1].split('.npz')[0] + ".bmp", img)

                    else:
                        images_dict[key][i]['dna_area_ratio'] = -1
                        images_dict[key][i]['dna_gray_ratio'] = -1
                except:
                    print("detected nan")
                    images_dict[key][i]['dna_area_ratio'] = -1
                    images_dict[key][i]['dna_gray_ratio'] = -1
                    continue
            
        return images_dict, sc_num, sc_gray_m
    
#    @staticmethod
    def statisc_mean(self, images_dict):
        
        area_a = []
        gray_a = []
        
        area_h = []
        gray_h = []
        for key in images_dict:
            if key == 'SC':
                continue
            
            for i in range(len(images_dict[key])):
                dna_area_ratio = images_dict[key][i]['dna_area_ratio']
                dna_gray_ratio = images_dict[key][i]['dna_gray_ratio']
                if (dna_area_ratio > 0.3)&(dna_gray_ratio > 0.3):
                    if key == "ASCUS":
                        area_a.append(dna_area_ratio)
                        gray_a.append(dna_gray_ratio)
                    elif key == "HSIL_S":
                        area_h.append(dna_area_ratio)
                        gray_h.append(dna_gray_ratio)
        
        return np.mean(area_a), np.mean(gray_a), np.mean(area_h), np.mean(gray_h) 

    def statisc_single(self, images_dict, hsil_gray_thr=1.5, hsil_area_thr=1.5, ascus_gray_thr=2.5, ascus_area_thr=2.5):
        all_num = 0
        num_a = 0
        num_h = 0
        all_ascus = 0
        all_hsil = 0
#        if(len(images_dict["SC"]) == 0  and len(images_dict["ASCUS"]) == 0 and len(images_dict["HSIL_S"]) == 0 ):
#            return -1, -1
        for key in images_dict:
#            print(key)
            if key == 'SC':
                continue
            
            for i in range(len(images_dict[key])):
                dna_area_ratio = images_dict[key][i]['dna_area_ratio']
                dna_gray_ratio = images_dict[key][i]['dna_gray_ratio']
                if (dna_area_ratio > 0.0)&(dna_gray_ratio > 0.0):
                    all_num = all_num + 1
                    if key == "ASCUS":
                        all_ascus = all_ascus + 1
                        if (dna_area_ratio > ascus_area_thr)&(dna_gray_ratio > ascus_gray_thr):
                            num_a = num_a + 1
                    elif key == "HSIL_S":
                        all_hsil =all_hsil + 1
                        if (dna_area_ratio > hsil_area_thr)&(dna_gray_ratio > hsil_gray_thr):
                            num_h = num_h + 1
                
        return num_a, num_h, all_num, all_ascus, all_hsil

    
if __name__ == "__main__":
    dna = DNAMeasureCore(prefix='./segnet_bb_final')
    B = []
    D = []
    SC_num = [] 
    SC_gray_m = []
    a1 = 0
    a2 = 0
    Id = []
    for i in range(len(Images_dict)):
        if len(Images_dict[i]) == 0:
            continue
        if 'SC' not in Images_dict[i]:
            continue
        if len(Images_dict[i]["SC"]) == 0:
            continue

        ids = Images_dict[i][list(Images_dict[i].keys())[0]][0]['xception_data_path'].split('cells_test_0308/')[1].split('/SC')[0]
        Id.append(ids)
        sc_n = 0
        sc_g = 0
        a, sc_n, sc_g = dna.do_predict(Images_dict[i])
        D.append(a)
        SC_num.append(sc_n)
        SC_gray_m.append(sc_g)

    Num_a_25 = []
    Num_h_15 = []

    Num_a_3 = []
    Num_h_2 = []
    All_num = []

    Area_a = []
    Gray_a = []
    Area_h = []
    Gray_h = []   
    C1 = []
    All_ascus = []
    All_hsil = []
    for i in range(len(D)):
        num_a, num_h, all_num, all_ascus, all_hsil = dna.statisc_single(images_dict = D[i],  hsil_gray_thr=1.5, \
                                                        hsil_area_thr=1.5, ascus_gray_thr=2.5, ascus_area_thr=2.5)    
        area_a, gray_a, area_h, gray_h  = dna.statisc_mean(images_dict = D[i])
        Area_a.append(np.mean(area_a))
        Gray_a.append(np.mean(gray_a))
        Area_h.append(np.mean(area_h))
        Gray_h.append(np.mean(gray_h))
        Num_a_25.append(num_a)
        Num_h_15.append(num_h)
        All_ascus.append(all_ascus)
        All_hsil.append(all_hsil)
        C1.append(all_num)

        num_a, num_h, _, _, _ = dna.statisc_single(images_dict = D[i],  hsil_gray_thr=2, \
                                                        hsil_area_thr=2, ascus_gray_thr=3, ascus_area_thr=3) 
        Num_a_3.append(num_a)
        Num_h_2.append(num_h)

    #print(a)
    results = np.transpose(np.array([Id, SC_num, SC_gray_m, All_ascus, Num_a_25, Num_a_3, Gray_a, All_hsil, Num_h_15, Num_h_2, Gray_h]))    
    import csv
    import os
    if os.path.exists("./results.csv"):
        os.remove("./results.csv")

    out = open('./results.csv','a', newline='')

    csv_write = csv.writer(out,dialect='excel')
    head = ["病例 id", "SC数目", "SC灰度均值(中值)", "ASCUS数目", "ASCUS/SC大于2.5的个数", "ASCUS/SC大于3的个数", "ASCUS/SC灰度值均值", "HSIL数目", \
            "HSIL_S/SC灰度值大于1.5的个数", "HSIL_S/SC灰度值大于2的个数", "HSIL_S/SC灰度值"]
    csv_write.writerow(head)
    for i in  range(results.shape[0]):
        csv_write.writerow(results[i, :])
    out.flush()
    out.close()
