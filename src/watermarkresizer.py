# This script inserts watermarks on images in many positions.
# You can put it on your crontab watching a specific folder, so you just need to put an image 
# there and wait 1 minute (cron job) to have the image with many watermarks on it.
# After that, choose one and discard the rest!



__author__="alex"
__date__ ="$09/11/2014 11:15:59$"

import sys
import os
from PIL import Image
import pprint as pp
import shutil



class WaterMarkResize:
    def __init__(self, rootDir):
        if not os.path.isdir(rootDir):
            print 'You must specif a valid directory name!'
            sys.exit(1)
            
        self.rootDir = rootDir.rstrip('/') + '/'
        
        '''
        try: shutil.rmtree(self.rootDir + 'output')
        except: pass
        '''
        
        self.outputDir = self.rootDir + 'output/'        
        if not os.path.exists(self.outputDir): os.makedirs(self.outputDir)
        
        self.backupDir = self.rootDir + 'original-backup/'        
        if not os.path.exists(self.backupDir): os.makedirs(self.backupDir)
        
        
        self.imageNumber = 0
        
        self.loadWaterMarks()
        self.loadInputImages()
        self.calcPositions()
        
        





            
    def loadWaterMarks(self):        
        watermarksDir = self.rootDir + 'watermarks/'
        print 'Directory to put watermarks in: %s ' % watermarksDir
        if not os.path.isdir(watermarksDir):
            print 'Could not find watermarks directory on root dir!'
            sys.exit(1)
            
        self.watermarks = []
        files = [watermarksDir + f for f in os.listdir(watermarksDir) if os.path.isfile(watermarksDir + f)]                
        for f in files:            
            try:
                wtm = Image.open(f)
                self.watermarks.append(wtm)                
                    
                wtm = wtm.convert('RGBA')
                r, g, b, a = wtm.split()            
                def invert(image):
                    return image.point(lambda p: 255 - p)            
                r, g, b = map(invert, (r, g, b))
                wtm_inv = Image.merge(wtm.mode, (r, g, b, a))
                self.watermarks.append(wtm_inv)
                
            except:
                print 'Could not load watermark file: ' + f
            
        if not len(self.watermarks): print 'No watermarks loaded. Only resizes will be made!'
        else: print('Total watermarks loaded: %d!' % len(self.watermarks))
        
        
        
        
        
        
    def loadInputImages(self):
        self.inputImages = []
        dir = self.rootDir
        files = [f for f in os.listdir(dir) if os.path.isfile(dir + f)]                
        for f in files:            
            try:                
                outputDirForFile = self.outputDir + f.replace('.','_') + '/'                
                self.inputImages.append([outputDirForFile, Image.open(dir + f).copy()])                
                # guarantee empty output dir                
                try: shutil.rmtree(outputDirForFile)                
                except: pass        
                os.makedirs(outputDirForFile, False)
                
            except:
                print 'Could not load input image file: ' + dir + f
                
            # backup the original loaded file
            command = 'mv "%s" "%s"' % (dir+f , self.backupDir+f )
            print command
            os.system(command)            
            #os.remove(dir + f)
                
        if not len(self.inputImages): 
            print 'No input images available in %s! \n Nothing to be done!' % self.rootDir
            sys.exit(0)
            
        print 'Total images to deal with: %d' % len(self.inputImages)
        
        
        
        
        
    def calcPositions(self):
        """Calculate each postion of im where a wm will be included
        """
        wmPositions = []
        for wm in self.watermarks:
            wm_w, wm_h = wm.size
            for inputImage in self.inputImages:                
                filename, im = inputImage                
                im_w, im_h = im.size                
                
                for ratio_logo in (4,6):
                    
                    logow = im_w / ratio_logo
                    ratio = logow / float(wm_w)
                    logoh = int(wm_h * ratio)

                    # centralized huge wm over im                
                    wm_image = self.resizeImage(wm, logow, logoh)
                    border_x = im_w / 20
                    border_y = im_h / 20

                    wmPositions.append((inputImage, wm_image, 
                        border_x,
                        border_y))

                    if 1:
                        wmPositions.append((inputImage, wm_image, 
                            im_w - border_x - logow ,
                            border_y))

                        wmPositions.append((inputImage, wm_image, 
                            border_x ,
                            im_h - border_y - logoh))

                        wmPositions.append((inputImage, wm_image,                     
                            im_w - border_x - logow, 
                            im_h - border_y - logoh))


                
        print len(wmPositions)
        i = 0
        for wmp in wmPositions: 
            i += 1
            print 'Watermarking %d of %d...' % (i, len(wmPositions))
            self.waterMarkImage(wmp[0], wmp[1], wmp[2], wmp[3])
                    


        
        
        
    def resizeImage(self, im, w , h):                
        new_size = (w,h)
        imr = im.copy().resize(new_size, Image.ANTIALIAS)
        return imr
        
        
        
        
        
    def waterMarkImage(self, inputImage, wm, x, y):
        """Put a watermark in a image
        
        Keyword arguments:
        im -- PIL image to put watermark in
        wm -- Watermark to be used        
        x - x pixel for wm in im (start from upper left pixel of wm)
        y - y pixel for wm in im
        """                
        
        outputDirForFile, img = inputImage
        
        im = img.copy()

        im.paste(wm,(x,y),mask=wm)
        
        outputFileName = outputDirForFile + '%d-%d-%d.jpg' % (self.imageNumber,x,y)
        
        im.save(outputFileName)

        # optimize the jpeg image
        os.system('jpegoptim --strip-all --preserve --totals --all-progressive --max=45 "%s"' % outputFileName)
        
        self.imageNumber += 1
        
        
        



if __name__ == "__main__":
    
    print "WaterMarkResize"
    
    if len(sys.argv) < 2:
        print 'Specify the root dir as the first parameter!'
        sys.exit(1)
        
    rootDir = sys.argv[1];
    
    wmr = WaterMarkResize(rootDir)
    exit()
