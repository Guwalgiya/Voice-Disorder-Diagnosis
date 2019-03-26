# ===============================================
# Import Packages and Functions
from   os     import walk
import numpy  as     np
import pickle


# ===============================================
# Main function of this file
def compressVGGishInput(dataset_path, classes, snippet_length, snippet_hop, all_combo, slash):
    

    # ===============================================
    data = []


    # ===============================================
    # a_combo = [file_name, its_label], example: "[aaa, "Pathol"]"
    for a_combo in all_combo:


        # ===============================================
        cur_name = a_combo[0]


        # ===============================================
        sub_folder   = a_combo[1]   + "_"            + str(snippet_length) + "ms_"  + str(snippet_hop) + "ms"
        MFCCs_folder = a_combo[0]   + "_MFCCs_block" + str(fft_length)     + "_hop" + str(fft_hop) 
        MFCCs_path   = dataset_path + slash          + sub_folder          + slash  + MFCCs_folder


        # ===============================================
        MFCCs_name_list = []
        for (dirpath, dirnames, filenames) in walk(MFCCs_path):
            MFCCs_name_list.extend(filenames)
            break
        

        # ===============================================
        snippet_amount = 0
        for MFCCs_name in MFCCs_name_list:


            # ===============================================
            MFCCs = np.loadtxt(MFCCs_path + slash + MFCCs_name)


            # ===============================================
            snippet_amount = snippet_amount + 1


            # ===============================================
            # [file_name, pitch shift by semitone, mel_spectrogram] example: ["aaa", "N0.0", MFCCs]
            data.append([cur_name, MFCCs_name.split('_')[1], MFCCs])
        
        
    # ===============================================
    print(len(data))
    

    # ===============================================
    data_file_name = "VGGish_" + str(snippet_length) + "ms_" + str(snippet_hop) + "ms" + "_block" + str(fft_length) + "_hop" + str(fft_hop) 
    

    # ===============================================
    temp_file = open(dataset_path + slash + data_file_name + '.pickle', 'wb')
    
    
    # ===============================================
    pickle.dump(data, temp_file)

    
    # ===============================================
    print("MFCC data is saved as a Pickle File")