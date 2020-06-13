import pandas as pd
import numpy as np
from os import listdir, path, mkdir
from netCDF4 import Dataset
from satpy import Scene
from pyresample.geometry import AreaDefinition
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib.pyplot as plt
from matplotlib.colors import from_levels_and_colors
import matplotlib.cm as cm
import h5py
import random

def fnmatch(fname, viirs_folder):
    viirs_files = [file for file in listdir(viirs_folder) if file.endswith(".nc")]
    julian_day = fname.split('t')[0]
    time = fname.split('t')[1]
    VNP02file = [vf for vf in viirs_files if 'VNP02MOD.A' + julian_day + '.' + time in vf][0]
    VNP03file = [vf for vf in viirs_files if 'VNP03MOD.A' + julian_day + '.' + time in vf][0]
    return VNP02file, VNP03file

def dust_predictors():
    predictor_folder = 'I:\\viirs_north_africa_summer\\predictor\\'
    mask_folder = 'I:\\viirs_north_africa_summer\\mask\\'

    fnames = [file for file in listdir(predictor_folder)]

    aggr_predictor = []
    aggr_mask = []
    # load viirs all bands
    for fname in fnames:
        predictor_file = predictor_folder+fname
        predictor = np.load(predictor_file)
        predictor[np.isnan(predictor)] = 0
        # print(predictor.shape)
        predictor = predictor[:,:,:16]

        vectorized = predictor.reshape((-1, predictor.shape[2]))
        vectorized = np.float32(vectorized)
        aggr_predictor.append(vectorized)

        # load calipso dust mask
        mask_file = mask_folder + fname
        mask = np.transpose(np.load(mask_file))
        mask_vectorized = mask.reshape((-1))
        aggr_mask.append(mask_vectorized)

    aggr_predictor = np.concatenate(aggr_predictor, axis = 0)
    aggr_mask = np.concatenate(aggr_mask, axis=0)

    return aggr_predictor[aggr_mask == 1]

def plot_dust(plot_label, title):
    cmap, norm = from_levels_and_colors(np.linspace(-1.5, 5.5, num=8),['grey','white','orange','green','blue','purple','yellow'])
    plt.figure()
    plt.imshow(plot_label, cmap=cmap, norm=norm)
    plt.colorbar(ticks=np.arange(-1, 6))
    plt.title(title), plt.xticks([]), plt.yticks([])
    plt.show()

def plot_segmentation(labels_image, title):
    plt.figure()
    cmap = plt.get_cmap('RdBu', np.max(labels_image) - np.min(labels_image) + 1)
    im = plt.imshow(labels_image, cmap=cmap, vmin=np.min(labels_image) - .5, vmax=np.max(labels_image) + .5)
    cax = plt.colorbar(im, ticks=np.arange(np.min(labels_image), np.max(labels_image) + 1), fraction=0.05, pad=0.05)
    plt.title(title), plt.xticks([]), plt.yticks([])
    plt.show()

######################################## Step 0: Locate data and folder ########################################
# input folders/data:
validation_folder = 'C:\\Users\\mqy5198\\Box\\Others\\UMBC-Training\\Project\\validation\\'
cal_label_folder = 'I:\\cal_label\\'
viirs_folder = 'I:\\viirs_data\\'

dust_validation_list = pd.read_csv(validation_folder+'dust_validation_list.csv', header=None, index_col=False).values

f_index = 1
grandule_dt = dust_validation_list[f_index][0] #  e.g.,'2014213t1536'

######################################### Step 1. read the calipdo track ########################################
cal_label = np.load(cal_label_folder + grandule_dt + '.npz')
cal_lon = cal_label['lon']
cal_lat = cal_label['lat']
CALIOP_Alay_Aerosol_Type_Mode = cal_label['CALIOP_Alay_Aerosol_Type_Mode']
CALIOP_N_Clay_5km = cal_label['CALIOP_N_Clay_5km'][:]
CALIOP_N_Clay_1km = cal_label['CALIOP_N_Clay_1km'][:]
IGBP_SurfaceType = cal_label['IGBP_SurfaceType'][:]

# categorize into dust related groups
category = np.zeros(len(cal_lat))
for k in range(cal_lat.shape[0]):
    if ((CALIOP_N_Clay_5km[k, 0] == 0) & (CALIOP_N_Clay_1km[k, 0] == 0) & (
            np.unique(CALIOP_Alay_Aerosol_Type_Mode[:, k]).size == 2) & (
            2 in CALIOP_Alay_Aerosol_Type_Mode[:, k])):
        # category 1: dust (dust only no cloud no other aerosols)
        category[k] = 1
        continue
    if ((CALIOP_N_Clay_5km[k, 0] == 0) & (CALIOP_N_Clay_1km[k, 0] == 0) & (
            np.unique(CALIOP_Alay_Aerosol_Type_Mode[:, k]).size == 2) & (
            5 in CALIOP_Alay_Aerosol_Type_Mode[:, k])):
        # category 2: pure polluted dust
        category[k] = 2
        continue
    if ((CALIOP_N_Clay_5km[k, 0] == 0) & (CALIOP_N_Clay_1km[k, 0] == 0) & (
            np.unique(CALIOP_Alay_Aerosol_Type_Mode[:, k]).size == 3) & (
            5 in CALIOP_Alay_Aerosol_Type_Mode[:, k]) & (
            2 in CALIOP_Alay_Aerosol_Type_Mode[:, k])):
        # category 3: dust with polluted dust
        category[k] = 3
        continue
    if ((CALIOP_N_Clay_5km[k, 0] == 0) & (CALIOP_N_Clay_1km[k, 0] == 0) & (
            np.unique(CALIOP_Alay_Aerosol_Type_Mode[:, k]).size > 2) & ((
            2 in CALIOP_Alay_Aerosol_Type_Mode[:, k])) or (
            5 in CALIOP_Alay_Aerosol_Type_Mode[:, k])):
        # category 4: dust or polluted dust with other aerosols
        category[k] = 4
        continue
    if ((CALIOP_N_Clay_5km[k, 0] == 0) & (CALIOP_N_Clay_1km[k, 0] == 0) & (
            np.unique(CALIOP_Alay_Aerosol_Type_Mode[:, k]).size > 2) & (
            2 not in CALIOP_Alay_Aerosol_Type_Mode[:, k]) & (
            5 not in CALIOP_Alay_Aerosol_Type_Mode[:, k])):
        # category 5: other aerosol only
        category[k] = 5
        continue

#########################################  Step 2. read the entire VIIRS granule  ########################################
fn1, fn2 = fnmatch(grandule_dt, viirs_folder)
# get all available bands
VNP02 = Dataset(viirs_folder + fn1)
available_bands = [key for key in VNP02['observation_data'].variables.keys() if len(key) == 3]
bands = ['M01', 'M02', 'M03', 'M04', 'M05', 'M06', 'M07', 'M08', 'M09', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'M16']

# predictors = np.array([])
# for band in bands:
#     if band in available_bands: # if band exists in this file
#         matrix_data = VNP02['observation_data'][band][()]
#     else:
#         matrix_data = np.full(VNP02['observation_data'][available_bands[0]].shape, np.nan)
#     if predictors.shape[0] == 0:
#         predictors = matrix_data
#     else:
#         predictors = np.dstack((predictors, matrix_data))
#
# # get geolocations
# VNP03 = Dataset(viirs_folder + fn2)
# viirs_lon = VNP03['geolocation_data']['longitude'][()]
# viirs_lat = VNP03['geolocation_data']['latitude'][()]

# Reproject dust composite and visualize
scn = Scene(filenames=[viirs_folder + fn1, viirs_folder + fn2], reader='viirs_l1b')  # load VNP02 and VNP03 files together
scn.load(available_bands + ['dust'])
minlon, maxlon, minlat, maxlat = cal_lon.min(), cal_lon.max(), cal_lat.min(), cal_lat.max()
dst_area = AreaDefinition('crop_area', 'crop_area', 'crop_latlong', {'proj': 'latlong'},
                          (maxlon - minlon) / 0.0075, (maxlat - minlat) / 0.0075,
                          [minlon, minlat, maxlon, maxlat])
local_scn = scn.resample(dst_area)
local_scn.show('dust')
local_scn.save_dataset('dust', validation_folder+grandule_dt+'_dust.png')

try:
    scn.load(['true_color_raw'])
    local_scn = scn.resample(dst_area)
    local_scn.show('true_color_raw')
    local_scn.save_dataset('true_color_raw', validation_folder+grandule_dt+'_true_color.png')
except:
    print('no true color')

# retrieve 16 bands
if path.exists(validation_folder+grandule_dt+'_predictors.npy'):
    predictors = np.load(validation_folder+grandule_dt+'_predictors.npy',allow_pickle=True)
else:
    predictors = np.array([])
    for band in bands:
        if band in available_bands: # if band exists in this file
            matrix_data = local_scn[band].values
        else:
            matrix_data = np.full(local_scn[available_bands[0]].shape, np.nan)
        if predictors.shape[0] == 0:
            predictors = matrix_data
        else:
            predictors = np.dstack((predictors, matrix_data))
    np.save(validation_folder + grandule_dt + '_predictors', predictors)

# retrieve geolocations
if path.exists(validation_folder+grandule_dt+'_viirs_lon.npy'):
    viirs_lon = np.load(validation_folder+grandule_dt+'_viirs_lon.npy',allow_pickle=True)
    viirs_lat = np.load(validation_folder + grandule_dt + '_viirs_lat.npy', allow_pickle=True)
else:
    viirs_lon = local_scn[available_bands[0]].x.values
    viirs_lat = local_scn[available_bands[0]].y.values
    np.save(validation_folder + grandule_dt + '_viirs_lon', viirs_lon)
    np.save(validation_folder + grandule_dt + '_viirs_lat', viirs_lat)

#########################################  Step 3. Use K-means to cluster  ########################################
vectorized = predictors.reshape((-1, predictors.shape[2]))
vectorized = np.float32(vectorized)
#Initialize our model
K = 10
model = KMeans(n_clusters=K)
#Fit our model
model.fit(vectorized)
#Find which cluster each data-point belongs to
labels = model.predict(vectorized)
#Reshape the clusters back to image size
labels_image = labels.reshape(predictors.shape[0:2])
centroids = model.cluster_centers_
print(labels_image.shape)

# improve cluster determination based on dust predictors
if path.exists(validation_folder+'dust_profile_north_africa.npy'):
    dust_profiles = np.load(validation_folder+'dust_profile_north_africa.npy', allow_pickle=True)
else:
    dust_profiles = dust_predictors()

mean_distances = []
for i in range(K):
    # mean_distances.append([i, cdist(dust_profiles, predictor[labels_image == i], 'euclidean').mean()])
    mean_distances.append([i, np.linalg.norm(dust_profiles.mean(axis=0)-centroids[i])])
mean_distances = np.array(mean_distances)
min_mean_distance = min(mean_distances[:,1])
dust_label = np.where(mean_distances[:,1] == min(mean_distances[:,1]))[0][0]
# check if there are other clusters that have strong similarities with the dust predictors
potentials = []
for i in range(K):
    if i != dust_label:
        if (mean_distances[i, 1] - min_mean_distance) < 5:
            potentials.append(i)
print('all potential dust clusters:', dust_label, potentials)
if len(potentials) > 0:
    for p in potentials:
        labels_image[labels_image == p] = dust_label # assign this potential cluster to the original dust cluster

plot_segmentation(labels_image, 'Segmentation with K='+str(K))

######################################## Step 3.5 test silhouette scores of clusters ##############################
labels = labels_image.reshape((vectorized.shape[0], 1))

sample_index = random.sample(range(labels.shape[0]), 100000)
vectorized = vectorized[sample_index,:]
labels = labels[sample_index].reshape(vectorized.shape[0])

# Average Silhouette (Compute the silhouette scores for each data-point and average them)
silhouette_avg = silhouette_score(vectorized, labels)
print("For K =", K, "The average silhouette_score is :", silhouette_avg)

# Silhouette plots (silhouette score for each data-point of each cluster)
sample_silhouette_values = silhouette_samples(vectorized,labels)

fig, ax = plt.subplots(1, 1)
# fig.set_size_inches(10, 7)
# The silhouette coefficient can range from -1, 1 but in this example all lie within [-0.1, 1]
ax.set_xlim([-0.3, 1])
ax.set_ylim([0, len(vectorized) + (K + 1) * 500])

y_lower = 10
for i in range(K):
    # Aggregate the silhouette scores for samples belonging to cluster i, and sort them
    ith_cluster_silhouette_values = sample_silhouette_values[labels == i]
    ith_cluster_silhouette_values.sort()
    size_cluster_i = ith_cluster_silhouette_values.shape[0]
    y_upper = y_lower + size_cluster_i
    color = cm.nipy_spectral(float(i) / K)
    ax.fill_betweenx(np.arange(y_lower,y_upper),0,ith_cluster_silhouette_values,facecolor=color,edgecolor=color,alpha=.7)
    ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
    y_lower = y_upper + 10  # 10 for the 0 samples

ax.set_xlabel("The silhouette coefficient values")
ax.set_ylabel("Cluster label")
# The vertical line for average silhouette score of all the values
ax.axvline(x=silhouette_avg, color="red", linestyle="--")
ax.set_yticks([])  # Clear the yaxis labels / ticks
ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
# plt.suptitle(("Silhouette analysis for KMeans clustering on sample data " "with K = %d" % K),fontsize=14, fontweight='bold')
plt.show()

#########################################  Step 4. test on-track accuracy  ########################################
if path.exists(validation_folder+grandule_dt+'_mask.npy'):
    mask = np.load(validation_folder+grandule_dt+'_mask.npy',allow_pickle=True)
else:
    mask = np.zeros((len(viirs_lat), len(viirs_lon)))
    mask.fill(-1)
    for yj in range(labels_image.shape[0]):
        for xi in range(labels_image.shape[1]):
            for k in range(cal_lat.shape[0]):
                if cal_lon[k, 0] <= (viirs_lon[xi] + 0.0075 / 2) and cal_lon[k, 0] >= (viirs_lon[xi] - 0.0075 / 2) and cal_lat[
                    k, 0] <= (viirs_lat[yj] + 0.0075 / 2) and cal_lat[k, 0] >= (viirs_lat[yj] - 0.0075 / 2):
                    mask[yj, xi] = category[k]
    np.save(validation_folder + grandule_dt + '_mask', mask)
plot_dust(mask, "Dust mask along track")

y_pred = labels_image[mask >= 0]
y_pred[y_pred != dust_label] = -100
y_pred[y_pred == dust_label] = 100

y_pred[y_pred == -100] = 0
y_pred[y_pred == 100] = 1

y_true = mask[mask >= 0].flatten()
y_true[y_true == 1] = 1
y_true[y_true != 1] = 0

print('Pure dust detection report')
print(classification_report(y_true, y_pred))

print('Pure dust detection accuracy')
print(accuracy_score(y_true, y_pred))

print('Confusion matrix')
print(confusion_matrix(y_true, y_pred))

print('final dust plot')
dust = labels_image.copy()
dust[dust != dust_label] = -100
dust[dust == dust_label] = 100

dust[dust == -100] = 0
dust[dust == 100] = 1
plot_dust(dust, "Dust extent")

########################################  Step 5. test off-track accuracy ########################################
validation_fname = dust_validation_list[f_index][1] # e.g.,'GAERO-VAOOO_npp_d20140801_t1534159_e1539563_b14305_c20200530014634994575_noaa_ops'
aerosol_data = h5py.File(validation_folder + validation_fname+'.h5', 'r')

longitude = aerosol_data['All_Data']['VIIRS-Aeros-EDR-GEO_All']['Longitude'][()]
latitude = aerosol_data['All_Data']['VIIRS-Aeros-EDR-GEO_All']['Latitude'][()]

# convert integer AOI to float based on scale factors
AOT = aerosol_data['All_Data']['VIIRS-Aeros-EDR_All']['AerosolOpticalDepth_at_550nm'][()]
AOT_Factors = aerosol_data['All_Data']['VIIRS-Aeros-EDR_All']['AerosolOpticalDepthFactors'][()]
AOT_float = (AOT * AOT_Factors[0]) + AOT_Factors[1]

# Land Model Aerosol Index
# AOT at 550 nm > 0.15 and dust Land Aerosol Model selected (See EDR Quality Flags in Appendix A)
Land_Model_Aerosol_Index = aerosol_data['All_Data']['VIIRS-Aeros-EDR_All']['QF4_VIIRSAEROEDR'][()]

# ocean
# Small Mode Aerosol Model (ocean)	011 = 3 = Fine mode 4      010 = 2 = Fine mode 3      001 = 1 = Fine mode 2      000 = 0 = Fine mode 1 111 = 7 = NA (no ocean)
# AOT at 550 nm > 0.15 and fine mode fraction < 0.2
smallmodefraction = aerosol_data['All_Data']['VIIRS-Aeros-EDR_All']['SmallModeFraction'][()]

dust_index = np.zeros(aerosol_data['All_Data']['VIIRS-Aeros-EDR_All']['AerosolOpticalDepth_at_550nm'].shape)
for i in range(dust_index.shape[0]):
    for j in range(dust_index.shape[1]):
        if smallmodefraction[i, j] != 255:  # ocean
            if AOT_float[i, j] > 0.15 and smallmodefraction[i, j] < 0.2:
                dust_index[i, j] = 1
        else:  # land
            if Land_Model_Aerosol_Index[i, j] == 0 and AOT_float[i, j] > 0.15:
                dust_index[i, j] = 1
print(dust_index[dust_index == 1].shape)

# reshape as the image
new_dust_index = np.zeros((len(viirs_lat), len(viirs_lon)))
index_i, index_j = np.where((longitude <= max(viirs_lon)) & (longitude >= min(viirs_lon)) & (latitude <= max(viirs_lat)) & (latitude >= min(viirs_lat)))
print('Is there any dust pixel in the AOT data (1: yes, 0: no)?   ', dust_index[index_i, index_j].max())

if dust_index[index_i, index_j].max() == 1: # if there contains dust pixels then proceed
    if path.exists(validation_folder+grandule_dt+'_AOT_dust'):
        new_dust_index = np.load(validation_folder+grandule_dt+'_AOT_dust.npy', allow_pickle=True)
    else:
        for index in range(len(index_i)):
            i, j = index_i[index], index_j[index]
            for ix in range(len(viirs_lon)):
                for iy in range(len(viirs_lat)):
                    if viirs_lon[ix] <= longitude[i, j] + 0.125 and viirs_lon[ix] >= longitude[i, j] - 0.125 and viirs_lat[iy] <= latitude[
                        i, j] + 0.125 and viirs_lat[iy] >= latitude[i, j] - 0.125 and dust_index[i, j] == 1:
                        print(i, j, ix, iy)
                        new_dust_index[ix, iy] = 1
        np.save(validation_folder+grandule_dt+'_AOT_dust.npy', new_dust_index)

