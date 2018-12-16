# ===============================================
# Import Packages and Functions
import numpy   as     np
import librosa
import math


# ===============================================
# Main Functions
def loadMelSpectrogram(selected_combo, classes, dsp_package, num_rows, representation_type, data, work_on_augmented, snippet_dict):
 

    # ===============================================
    # Load Parameters
    fs, snippet_length, snippet_hop, fft_length, fft_hop, _ = dsp_package
    

    # ===============================================
    # Initialization  
    label_1, label_2, label_3, snippet_num_list, distribution = [], [], [], [], {}
    

    # ===============================================
    # Format: distribution = {"Normal": [xxx, xxxxxxx], "Pathol" : [yyy, yyyyyy]} xxx, yyy are integers
    for a_class in classes:
        distribution[a_class] = [0,0]
    

    # ===============================================  
    for a_combo in selected_combo:
        

        # ===============================================
        # Basic Information, for a_combo in selected_combo:
        cur_name  = a_combo[0]
        cur_class = a_combo[1]


        # ===============================================   
        # label_1: 1, label_2:[0,1], label_3: pathol   
        num_snippet = snippet_dict[cur_name][0]
        cur_label_1 = snippet_dict[cur_name][1]
        cur_label_2 = snippet_dict[cur_name][2]
        cur_label_3 = snippet_dict[cur_name][3]
        

        # ===============================================   
        # Use that to track loaded data   
        snippet_num_list.append(num_snippet)


        # ===============================================   
        label_1 = label_1 + [cur_label_1] * num_snippet
        label_2 = label_2 + [cur_label_2] * num_snippet
        label_3 = label_3 + [cur_label_3] * num_snippet


        # ===============================================   
        distribution[cur_class][0] = distribution[cur_class][0] + 1
        distribution[cur_class][1] = distribution[cur_class][1] + num_snippet
    

    # ===============================================   
    # Prepare to load data
    num_time_frame = math.ceil(snippet_length / 1000 * fs / fft_hop)
    loaded_data    = np.zeros((sum(snippet_num_list), num_rows, num_time_frame))
    start_index    = 0
    end_index      = 0    
    for combo in selected_combo:


        # ===============================================   
        # Basic Information, for a_combo in selected_combo
        cur_name  = combo[0]
        cur_class = combo[1]
        end_index = end_index + snippet_dict[cur_name][0]
        

        # ===============================================  
        # Load augmented data or not
        if work_on_augmented:
            melSpectrograms = [data_point[2] for data_point in data if (data_point[0] == cur_name)]
        else:
            melSpectrograms = [data_point[2] for data_point in data if (data_point[0] == cur_name and data_point[1] == "N0.0")]
         


        # ===============================================  
        # Load pre-saved melspectrogram, and compute a "MFCCs-gram" with 20 MFCCs
        if representation_type == "MFCCs":
            for i in np.arange(start_index, end_index):
                S              = melSpectrograms[i - start_index]
                loaded_data[i] = librosa.feature.mfcc(S = librosa.power_to_db(S), n_mfcc = 20)
        

        # ===============================================  
        # Load pre-saved melspectrogram, and do normalization for each one of them   
        else:
            for i in np.arange(start_index, end_index):
                S              = melSpectrograms[i - start_index]
                loaded_data[i] = S / S.max()
        

        # ===============================================  
        start_index  = start_index + snippet_dict[cur_name][0]
    
    
    # ===============================================
    return [loaded_data, label_1, label_2, label_3, distribution, snippet_num_list]
