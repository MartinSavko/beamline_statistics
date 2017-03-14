#!/usr/bin/env python

import pickle
import numpy
import traceback
import pylab
import seaborn as sns
from matplotlib import rc

sns.set(color_codes=True)

rc('font', **{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

directories = ['2015_Run5',
               '2016_Run1',
               '2016_Run2',
               '2016_Run3',
               '2016_Run4',
               '2016_Run5',
               '2017_Run1',
               '2017_Run2']

attributes = ['/entry/instrument/detector/detectorSpecific/trigger_mode',
              '/entry/instrument/detector/detectorSpecific/compression',
              '/entry/instrument/detector/detectorSpecific/nimages',
              '/entry/instrument/detector/detectorSpecific/ntrigger',
              '/entry/instrument/detector/detectorSpecific/software_version',
              '/entry/instrument/detector/detectorSpecific/eiger_fw_version',
              '/entry/instrument/detector/detectorSpecific/data_collection_date',
              '/entry/instrument/detector/detector_distance',
              '/entry/instrument/detector/sensor_thickness',
              '/entry/instrument/detector/bit_depth_image',
              '/entry/instrument/detector/threshold_energy',
              '/entry/sample/goniometer/omega_increment',
              '/entry/sample/goniometer/phi_increment']


attributes2 = ['/entry/sample/goniometer/omega',
               '/entry/instrument/detector/goniometer/two_theta']

def sorter(a):
    return float(a[5])

r = pickle.load(open('results.pck'))

two_theta_problems = []
data_rates = []

data_rates_200_238 = []
data_rates_150_200 = []
data_rates_100_150 = []
data_rates_050_100 = []
data_rates_012_050 = []
data_rates_000_012 = []
bslz4 = 0
lz4 = 0
bslz4_compression = []
bslz4_c16 = []
bslz4_c32 = []
lz4_compression = []
exposures = []
size_rate_exposure_name = []
fps = []
sizes_bslz4 = []

for key in r:
    if 'orphaned' in key:
        continue
    if 'ref-' in key:
        continue
    try:
        nimages = r[key]['/entry/instrument/detector/detectorSpecific/nimages']
        ntrigger = r[key]['/entry/instrument/detector/detectorSpecific/ntrigger']
        nimages *= ntrigger
        length = r[key]['/entry/instrument/detector/goniometer/two_theta']
        if length > nimages and nimages!=1:
           two_theta_problems.append(key)
        compression = r[key]['/entry/instrument/detector/detectorSpecific/compression'] 
        sizes = r[key]['sizes']
        s = [s[1] for s in sizes if 'master' not in s[0]]
        s = numpy.array(s)
        frame_time = r[key]['/entry/instrument/detector/frame_time']
        frame_rate = 1./frame_time
        bit_depth_image = r[key]['/entry/instrument/detector/bit_depth_image']
        omega_increment = r[key]['/entry/sample/goniometer/omega_increment']
        s_sum = float(s.sum())
        #print nimages
        x_size = r[key]['/entry/instrument/detector/detectorSpecific/x_pixels_in_detector']
        y_size = r[key]['/entry/instrument/detector/detectorSpecific/y_pixels_in_detector']
        
        if compression == 'bslz4' and nimages >= 30:
            cr = x_size*y_size*(bit_depth_image/8.)/(s_sum/nimages)
            
            #print cr
            if cr < 70 and cr > 1:
                sizes_bslz4.append(s_sum)
                bslz4 += 1
                data_rate = s_sum/(nimages*frame_time)
                data_rates.append(data_rate)
                exposures.append(frame_time)
                if frame_rate >= 199.9:
                    data_rates_200_238.append(data_rate)
                elif frame_rate >= 150:
                    data_rates_150_200.append(data_rate)
                elif frame_rate >= 100:
                    data_rates_100_150.append(data_rate)
                elif frame_rate >= 50:
                    data_rates_050_100.append(data_rate)
                elif frame_rate >= 12:
                    data_rates_012_050.append(data_rate)
                else:
                    data_rates_000_012.append(data_rate)
                bslz4_compression.append(cr)
                fps.append(1./frame_time)
                if bit_depth_image == 16:
                    bslz4_c16.append(cr)
                else:
                    bslz4_c32.append(cr)
                    #if 'water' in key:
                size_rate_exposure_name.append(('%5.2f' % (s_sum/1024**2,),
                                                    '%4.2f' % (data_rate/1024.**2,), 
                                                    nimages, 
                                                    '%4.3f' % frame_time, 
                                                    omega_increment, 
                                                    '%4.2f' % cr, 
                                                    compression, 
                                                    bit_depth_image, 
                                                    key.replace('/nfs/ruchebis','')))
        if compression == 'lz4':
           lz4 += 1

    except:
        print traceback.print_exc()
print 'bslz4_compression'
#print bslz4_compression
bslz4_compression = numpy.array(bslz4_compression)
bslz4_c16 = numpy.array(bslz4_c16)
bslz4_c32 = numpy.array(bslz4_c32)
data_rates = numpy.array(data_rates)

#data_rates[data_rates>data_rates.mean()*100] = 0
#print two_theta_problems
print 'number of datasets with unequality between nimages and size of two_theta list %s' % len(two_theta_problems)
print 'number of bslz4 compressed datasets %s' % bslz4
print 'number of lz4 compressed datasets %s' % lz4    
print 'number of files considered %s, bslz4 maximum data rate %s, average data rate %s' % (len(data_rates), data_rates.max()/1024.**2, data_rates.mean()/1024.**2)
print 'n %s, bslz4 compression: max %s, mean %s, min %s' % (len(bslz4_compression), bslz4_compression.max(), bslz4_compression.mean(), bslz4_compression.min())
print 'n %s, bslz4 16 bit compression: max %s, mean %s, min %s' % (len(bslz4_c16), bslz4_c16.max(), bslz4_c16.mean(), bslz4_c16.min())
print 'n %s, bslz4 32 bit compression: max %s, mean %s, min %s' % (len(bslz4_c32), bslz4_c32.max(), bslz4_c32.mean(), bslz4_c32.min())
sizes_bslz4 = numpy.array(sizes_bslz4)
print 'n %s, sizes: max %s, mean %s' % (len(sizes_bslz4), sizes_bslz4.max(), sizes_bslz4.mean())
size_rate_exposure_name.sort(key=lambda x: -float(x[1]), reverse=False)
print 'size_rate_exposure_name'
#print size_rate_exposure_name
for k in range(20): #range(len(size_rate_exposure_name)):
    print size_rate_exposure_name[k]

pylab.figure(1,figsize=(16, 9))    
#pylab.hist(exposures, bins=100)
ax0 = sns.distplot(exposures, bins=100, kde=False)
for label in (ax0.get_xticklabels() + ax0.get_yticklabels()):
    #label.set_fontname('Arial')
    label.set_fontsize(16)
ax0.text(0.87, 0.95, '\# data sets: %d' %len(exposures), fontsize=14, transform=ax0.transAxes)
pylab.title('Eiger 9M, Proxima 2A, exposure times', fontsize=22)
pylab.xlabel('frame time [s]', fontsize=20)
pylab.savefig('oscillation_ranges_sep2016.png')

pylab.figure(2, figsize=(16, 9))
#pylab.hist(data_rates/1024**2, bins=75)
data_rates = data_rates[data_rates<1.8*1000000000]
ax1 = sns.distplot(data_rates/1024**2, bins=75, kde=False)
#ax1.set_xlim([0., 1800.])
for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
    #label.set_fontname('Arial')
    label.set_fontsize(16)
ax1.text(0.87, 0.95, '\# data sets: %d' %len(data_rates), fontsize=14, transform=ax1.transAxes)
#ax1.text(0.77, 0.90, '\# structures: %d' % n_structures, fontsize=14, transform=ax1.transAxes)
#ax1.text(0.77, 0.85, '\# data points: %d' % len(wavel), fontsize=14, transform=ax1.transAxes)

pylab.title('Eiger 9M, Proxima 2A, data rates in user operation', fontsize=22)
pylab.xlabel('data rate [MB/s]', fontsize=20)
pylab.savefig('data_rates_sep2016.png')

#pylab.figure(3)
#pylab.hist(numpy.array(data_rates_200_238)/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data rates in user operation, 199.9Hz < frame_rate')
#pylab.xlabel('data rate [MB/s]')
#pylab.savefig('data_rates_200_238.png')

#pylab.figure(4)
#pylab.hist(numpy.array(data_rates_150_200)/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data rates in user operation, 150Hz <= frame_rate < 199.9')
#pylab.xlabel('data rate [MB/s]')
#pylab.savefig('data_rates_150_200.png')

#pylab.figure(5)
#pylab.hist(numpy.array(data_rates_100_150)/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data rates in user operation, 100Hz <= frame_rate < 150Hz')
#pylab.xlabel('data rate [MB/s]')
#pylab.savefig('data_rates_100_150.png')

#pylab.figure(6)
#pylab.hist(numpy.array(data_rates_050_100)/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data rates in user operation, 50Hz <= frame_rate < 100Hz')
#pylab.xlabel('data rate [MB/s]')
#pylab.savefig('data_rates_050_100.png')

#pylab.figure(7)
#pylab.hist(numpy.array(data_rates_012_050)/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data rates in user operation, 12Hz < frame_rate < 50Hz ')
#pylab.xlabel('data rate [MB/s]')
#pylab.savefig('data_rates_012_050.png')

#pylab.figure(8)
#pylab.hist(numpy.array(data_rates_000_012)/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data rates in user operation, frame_rate < 12Hz')
#pylab.xlabel('data rate [MB/s]')
#pylab.savefig('data_rates_000_012.png')

comp = numpy.array(bslz4_compression)
comp[comp>30] = None
pylab.figure(9, figsize=(16, 9))
pylab.plot(fps, comp, 'bo')
pylab.title('Observed compression as function of frame rate', fontsize=22)
pylab.xlim([0.5, 240])
ax2 = pylab.gca()
for label in (ax2.get_xticklabels() + ax2.get_yticklabels()):
    #label.set_fontname('Arial')
    label.set_fontsize(16)
ax2.text(0.87, 0.95, '\# data sets: %d' %len(comp), fontsize=14, transform=ax2.transAxes)
pylab.xlabel('frame rate [Hz]', fontsize=20)
pylab.ylabel('compression ratio', fontsize=20)
pylab.savefig('compresssion_vs_fps_sep2016.png')

pylab.figure(10, figsize=(16, 9))
#pylab.hist(sizes_bslz4/1024**2, bins=75)
ax3 = sns.distplot(sizes_bslz4/1024**2, bins=75, kde=False)
#ax1.set_lim(
for label in (ax3.get_xticklabels() + ax3.get_yticklabels()):
    label.set_fontsize(16)
ax3.text(0.87, 0.95, '\# data sets: %d' %len(sizes_bslz4), fontsize=14, transform=ax1.transAxes)
pylab.title('Eiger 9M, Proxima 2A, data set sizes', fontsize=22)
pylab.xlabel('size of datasets [MB]', fontsize=20)
pylab.savefig('datasets_sizes_sep2016.png')

#pylab.figure(11)
#pylab.hist(sizes_bslz4/1024**2, bins=75)
#pylab.title('Eiger 9M, Proxima 2A, data set sizes')
#pylab.xlabel('size of datasets [MB]')
#pylab.savefig('datasets_sizes.png')

pylab.show()
