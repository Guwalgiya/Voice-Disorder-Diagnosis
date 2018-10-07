# =============================================================================
# Import Packages
from   keras                   import backend            as K
from   sklearn.model_selection import KFold
from   keras.models            import load_model
from   loadMelSpectrogram      import loadMelSpectrogram
from   loadMFCCs               import loadMFCCs
from   keras.models            import Model
from   math                    import ceil
import numpy                   as     np
import tensorflow              as     tf
import getCombination
import dataSplit
import autoencoder
import mySVM
import pickle
import CNN
import os


# =============================================================================
# Dataset Initialization
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
classes            = ["Normal", "Pathol"]
dataset_name       = "KayPentax"
dataset_path       = "/home/hguan/7100-Master-Project/Dataset-" + dataset_name
best_model_name    = "best_model_this_fold.hdf5"
val_loss_plot_name = "Val_Loss_Plot_"
monitor            = "val_loss"
num_folds          = 5   
train_percent      = 90
num_MFCCs          = 20
batch_size         = 1024


# =============================================================================
# Dsp Initialization
fs                  = 16000
snippet_length      = 500   #in milliseconds
snippet_hop         = 100   #in ms
fft_length          = 512
fft_hop             = 128
mel_length          = 128
dsp_package_1       = [fs, snippet_length, snippet_hop, fft_length, fft_hop, mel_length]
input_vector_length = mel_length * ceil(snippet_length / 1000 * fs / fft_hop)
vector_length       = 128
input_name_1        = "MelSpectrogram"
input_name_2        = "MFCCs"
dsp_package_2       = [fs, snippet_length, snippet_hop, fft_length, fft_hop, num_MFCCs * 2]
num_channel         = 1
num_rows            = 128
input_shape         = (int(num_rows / num_channel), ceil(snippet_length / 1000 * fs / fft_hop), num_channel)

# =============================================================================
# Autoencoder Initialization
encoding_dimension = 128
encoder_layer      = 5
decoder_layer      = 5
epoch_limit        = 100000
batch_auto         = 128
shuffle_choice     = True
loss_function      = 'mean_squared_error'
arch_bundle        = [encoder_layer, encoding_dimension, decoder_layer]
train_bundle_auto  = [epoch_limit, batch_auto, shuffle_choice, loss_function]


# =============================================================================
name_class_combo        = getCombination.main(dataset_path, classes)
normal_name_class_combo = [combo for combo in name_class_combo if combo[1] == "Normal"]
pathol_name_class_combo = [combo for combo in name_class_combo if combo[1] == "Pathol"]
normal_name_class_combo = np.asarray(normal_name_class_combo)
pathol_name_class_combo = np.asarray(pathol_name_class_combo)
num_normal              = len(normal_name_class_combo)
num_pathol              = len(pathol_name_class_combo)


# =============================================================================
normal_spliter      = KFold(n_splits = num_folds, shuffle = True)
normal_index_array  = np.arange(len(normal_name_class_combo))
normal_folds        = [(train_validate_index, test_index) for train_validate_index, test_index in normal_spliter.split(normal_index_array)]
pathol_spliter      = KFold(n_splits = num_folds, shuffle = True)
pathol_index_array  = np.arange(len(pathol_name_class_combo))
pathol_folds        = [(train_validate_index, test_index) for train_validate_index, test_index in pathol_spliter.split(pathol_index_array)]


# =============================================================================
file_results        = []
snippet_results     = []
total_file_con_mat  = np.array([[0,0],[0,0]])
total_snip_con_mat  = np.array([[0,0],[0,0]])


# =============================================================================
melSpec_file_name    = input_name_1 + "_" + str(snippet_length) + "ms_" + str(snippet_hop) + "ms" + "_block" + str(fft_length) + "_hop" + str(fft_hop) + "_mel" + str(mel_length)
MFCCs_file_name      = input_name_2 + "_" + str(snippet_length) + "ms_" + str(snippet_hop) + "ms" + "_block" + str(fft_length) + "_hop" + str(fft_hop) 
aug_dict_file_name   = "Dictionary_"      + str(snippet_length) + "ms_" + str(snippet_hop) + "ms"                   
unaug_dict_file_name = "Dictionary_"      + str(snippet_length) + "ms_" + str(snippet_hop) + "ms" + "_unaugmented" 

temp_file_1          = open(dataset_path + '/' + melSpec_file_name    + '.pickle', 'rb')  
temp_file_2          = open(dataset_path + '/' + MFCCs_file_name      + '.pickle', 'rb')
temp_file_3          = open(dataset_path + '/' + aug_dict_file_name   + '.pickle', 'rb')
temp_file_4          = open(dataset_path + '/' + unaug_dict_file_name + '.pickle', 'rb')

melSpec_data         = pickle.load(temp_file_1)
MFCCs_data           = pickle.load(temp_file_2)
aug_dict             = pickle.load(temp_file_3)
unaug_dict           = pickle.load(temp_file_4)

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.4)

sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
# =============================================================================
for fold_index in range(num_folds):
    print("---> Now Fold ", fold_index + 1,  " ----------------------------")
    

    # =============================================================================
    normal_train_validate_combo = normal_name_class_combo[normal_folds[fold_index][0]].tolist()
    normal_test_combo           = normal_name_class_combo[normal_folds[fold_index][1]].tolist()
    pathol_train_validate_combo = pathol_name_class_combo[pathol_folds[fold_index][0]].tolist()
    pathol_test_combo           = pathol_name_class_combo[pathol_folds[fold_index][1]].tolist()
    

    # =============================================================================
    [normal_train_combo, normal_validate_combo, _] = dataSplit.main(normal_train_validate_combo, train_percent, 100 - train_percent, 0)
    [pathol_train_combo, pathol_validate_combo, _] = dataSplit.main(pathol_train_validate_combo, train_percent, 100 - train_percent, 0)
    

    # =============================================================================
    train_combo    = normal_train_combo    + pathol_train_combo    
    validate_combo = normal_validate_combo + pathol_validate_combo
    test_combo     = normal_test_combo     + pathol_test_combo


    # =============================================================================
    train_package     = loadMelSpectrogram(train_combo,    classes, dsp_package_1, dataset_path, melSpec_data, True,  aug_dict)   
    validate_package  = loadMelSpectrogram(validate_combo, classes, dsp_package_1, dataset_path, melSpec_data, False, unaug_dict)   
    test_package      = loadMelSpectrogram(test_combo,     classes, dsp_package_1, dataset_path, melSpec_data, False, unaug_dict)

    # =============================================================================
    train_data,    train_label_1,     _, train_label_3,    train_dist,    _                       = train_package
    validate_data, validate_label_1,  _, validate_label_3, validate_dist, validate_augment_amount = validate_package
    test_data,     test_label_1,      _, test_label_3,     test_dist,     test_augment_amount     = test_package
    print(train_dist)
    print(validate_dist)
    print(test_dist)


    # =============================================================================
    train_data_auto    = train_data.reshape((len(train_data),       np.prod(train_data.shape[1:])),    order = 'F') 
    validate_data_auto = validate_data.reshape((len(validate_data), np.prod(validate_data.shape[1:])), order = 'F')
    test_data_auto     = test_data.reshape((len(test_data),         np.prod(test_data.shape[1:])),     order = 'F') 


    # =============================================================================
    _, history, encodeLayer_index = autoencoder.main(input_vector_length, train_data_auto, validate_data_auto, arch_bundle, train_bundle_auto)
    best_autoencoder              = load_model(best_model_name)
    best_encoder                  = Model(inputs  = best_autoencoder.inputs, outputs = best_autoencoder.layers[encodeLayer_index].output)
    
  
    # =============================================================================
    train_data_encoded     = best_encoder.predict(train_data_auto)
    validate_data_encoded  = best_encoder.predict(validate_data_auto)
    test_data_encoded      = best_encoder.predict(test_data_auto)
    

    # ==============================================================================
    train_data_CNN    = train_data.reshape(train_data.shape[0],       num_channel, int(train_data.shape[1]    / num_channel), train_data.shape[2])   
    validate_data_CNN = validate_data.reshape(validate_data.shape[0], num_channel, int(validate_data.shape[1] / num_channel), validate_data.shape[2]) 
    test_data_CNN     = test_data.reshape(test_data.shape[0],         num_channel, int(test_data.shape[1]     / num_channel), test_data.shape[2]) 
    

    # ==============================================================================
    train_data_CNN    = np.moveaxis(train_data_CNN,    1, -1)
    validate_data_CNN = np.moveaxis(validate_data_CNN, 1, -1)
    test_data_CNN     = np.moveaxis(test_data_CNN,     1, -1)


    # ==============================================================================
    #_, history = CNN.main(train_data_CNN, train_label_1, validate_data_CNN, validate_label_1, epoch_limit, batch_size, input_shape, monitor)
    #best_CNN   = load_model(best_model_name)
    #extractor  = Model(inputs  = best_CNN.input, outputs = best_CNN.layers[-2].output)
    

    # ==============================================================================
    #train_data_CNNed    = extractor.predict(train_data_CNN)
    #validate_data_CNNed = extractor.predict(validate_data_CNN)
    #test_data_CNNed     = extractor.predict(test_data_CNN)


    # ==============================================================================
    #train_package    = loadMFCCs(train_combo,    classes, dsp_package_2, dataset_path, MFCCs_data, True,  aug_dict)
    #validate_package = loadMFCCs(validate_combo, classes, dsp_package_2, dataset_path, MFCCs_data, False, unaug_dict)
    #test_package     = loadMFCCs(test_combo,     classes, dsp_package_2, dataset_path, MFCCs_data, False, unaug_dict)
    
   
    # ==============================================================================
    #train_data,    _,  _, _, _, _ = train_package
    #validate_data, _,  _, _, _, _ = validate_package
    #test_data,     _,  _, _, _, _ = test_package


    # =============================================================================
    #train_MFCCs_normalized    = np.zeros((train_data.shape))
    #validate_MFCCs_normalized = np.zeros((validate_data.shape))
    #test_MFCCs_normalized     = np.zeros((test_data.shape))


    # =============================================================================
    # standard_max_list  = [0] * num_MFCCs * 2
    # standard_min_list  = [0] * num_MFCCs * 2

    
    # for i in range(num_MFCCs * 2):

    #     # ==============================================================================
    #     standard_max = max(np.amax(train_data[:, i]), np.amax(validate_data[:, i]))
    #     standard_min = min(np.amin(train_data[:, i]), np.amin(validate_data[:, i]))

    #     standard_max_list[i] = round(standard_max, 3)
    #     standard_min_list[i] = round(standard_min, 3)
           
    #     train_MFCCs_normalized[:, i]    = (train_data[:, i]    - standard_min_list[i]) / (standard_max_list[i] - standard_min_list[i])
    #     validate_MFCCs_normalized[:, i] = (validate_data[:, i] - standard_min_list[i]) / (standard_max_list[i] - standard_min_list[i])

    
    # # ==============================================================================
    # for i in range(num_MFCCs * 2):
    #     test_MFCCs_normalized[:, i]    = (test_data[:, i]    - standard_min_list[i]) / (standard_max_list[i] - standard_min_list[i])
    #     test_MFCCs_normalized[:, i]    = np.clip(test_MFCCs_normalized[:, i], 0, 1)
    

    # ==============================================================================
    print(train_data_encoded.shape)
    #print(train_data_CNNed.shape)
    #print(train_MFCCs_normalized.shape)
    
   
    # ==============================================================================
    #train_features    = np.concatenate((train_MFCCs_normalized,    train_data_encoded),    axis = 1)    #train_MFCCs_normalized),    axis = 1)
    #validate_features = np.concatenate((validate_MFCCs_normalized, validate_data_encoded), axis = 1) #validate_MFCCs_normalized), axis = 1)
    #test_features     = np.concatenate((test_MFCCs_normalized,     test_data_encoded), axis = 1)     #test_MFCCs_normalized),     axis = 1)


    # =============================================================================
    fold_result_package  = mySVM.method1(train_data_encoded,    train_label_3, 
                                         validate_data_encoded, validate_label_3, 
                                         test_data_encoded,     test_label_3,
                                         test_combo,        test_augment_amount)
    
    
    # =============================================================================
    file_acc, file_con_mat, snippet_acc, snippet_con_mat = fold_result_package
    
    total_file_con_mat = total_file_con_mat + file_con_mat
    total_snip_con_mat = total_snip_con_mat + snippet_con_mat
    print(file_acc)
    print(snippet_acc)
    print(file_con_mat)
    print(snippet_con_mat)
    file_results.append(file_acc)
    snippet_results.append(snippet_acc)
    
    
    # ==============================================================================
    K.clear_session()
    tf.reset_default_graph()
    os.remove("best_model_this_fold.hdf5")
    # print("Memory Cleared, Saved Model Removed")


    # =============================================================================
    cur_possible_result = ((num_normal - total_file_con_mat[0][1]) / num_normal + (num_pathol - total_file_con_mat[1][0]) / num_pathol) / 2
    print('The best results we can get is:', cur_possible_result)



# =============================================================================
print('--------------------------------')
print('file results')
print(file_results)
print(sum(file_results) / len(file_results))
print('--------------------------------')
print('snippet results')
print(snippet_results)
print(sum(snippet_results) / len(snippet_results))
print('--------------------------------')
print('final file results')
print(total_file_con_mat)
acc = 0;
for i in range(len(total_file_con_mat[0])):
    acc = acc + total_file_con_mat[i][i] / sum(total_file_con_mat[i])
print(acc / 2)
print('--------------------------------')
print('final snippet results')
print(total_snip_con_mat)
acc = 0;
for i in range(len(total_snip_con_mat[0])):
    acc = acc + total_snip_con_mat[i][i] / sum(total_snip_con_mat[i])
print(acc / 2)    